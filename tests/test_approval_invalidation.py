"""STEP3->STEP4 test suite for TASK-APPROVAL-001: 4段階承認・差し戻し・無効化.

Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
Spec: docs/specifications/07-approval-workflow.md
Production files:
- script/services/approvals.py
- script/schemas/approvals.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.core.errors import AppError, ErrorCode
from script.schemas.approvals import ApprovalGate, ApprovalTarget
from script.services.approvals import ApprovalService

pytestmark = pytest.mark.mvp


def _target(content_hash: str = "a" * 64) -> ApprovalTarget:
    return ApprovalTarget(paths=("project/chapters/01.yaml",), content_hash=content_hash)


@pytest.mark.unit
def test_tc_approval_001_02(tmp_path: Path) -> None:
    """TC-APPROVAL-001-02 — 変更による無効化

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P0
    Layer: unit
    Given: approved対象のhashを変更
    When: invalidateを行う
    Then: 関連承認だけinvalidatedにする
    """
    service = ApprovalService(tmp_path)
    project_id = "project-approval-02"

    service.submit(project_id, ApprovalGate.PLANNING, target=_target())
    service.approve(project_id, ApprovalGate.PLANNING, approved_by="reviewer-1")
    service.submit(project_id, ApprovalGate.VERIFIED_SCRIPT, target=_target())
    service.approve(project_id, ApprovalGate.VERIFIED_SCRIPT, approved_by="reviewer-1")
    # PREVIEW_AUDIO is left in draft: not approved, so invalidation must be a no-op for it.

    invalidated = service.invalidate_changed_targets(project_id, "chapter_spec_changed")

    assert invalidated == [ApprovalGate.VERIFIED_SCRIPT.value]

    bundle = service.get_bundle(project_id)
    assert bundle.approvals[ApprovalGate.VERIFIED_SCRIPT].status.value == "invalidated"
    assert bundle.approvals[ApprovalGate.PLANNING].status.value == "approved"
    assert bundle.approvals[ApprovalGate.PREVIEW_AUDIO].status.value == "draft"

    service.assert_gate(project_id, ApprovalGate.PLANNING)
    with pytest.raises(AppError) as excinfo:
        service.assert_gate(project_id, ApprovalGate.VERIFIED_SCRIPT)
    assert excinfo.value.code is ErrorCode.PERMISSION_DENIED


@pytest.mark.unit
def test_tc_approval_001_04(tmp_path: Path) -> None:
    """TC-APPROVAL-001-04 — approvals.yaml load/save

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「approvals.yaml load/save」を実行する
    Then: 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。
    """
    project_id = "project-approval-04"
    gate = ApprovalGate.PREVIEW_AUDIO

    writer = ApprovalService(tmp_path)
    writer.submit(project_id, gate, target=_target())
    writer.approve(project_id, gate, approved_by="reviewer-1")

    reader = ApprovalService(tmp_path)
    persisted = reader.get_bundle(project_id)
    assert persisted.approvals[gate].status.value == "approved"
    assert persisted.approvals[gate].approved_by == "reviewer-1"

    approvals_path = tmp_path / "library" / project_id / "approvals.yaml"
    assert approvals_path.exists()

    # 未承認gate -> stable error
    with pytest.raises(AppError) as excinfo_draft:
        reader.assert_gate(project_id, ApprovalGate.PLANNING)
    assert excinfo_draft.value.code is ErrorCode.PERMISSION_DENIED

    # changes_requested -> stable error
    writer.submit(project_id, ApprovalGate.MATERIALS_CURRICULUM, target=_target())
    writer.request_changes(project_id, ApprovalGate.MATERIALS_CURRICULUM, reason="要修正")
    with pytest.raises(AppError) as excinfo_changes:
        reader.assert_gate(project_id, ApprovalGate.MATERIALS_CURRICULUM)
    assert excinfo_changes.value.code is ErrorCode.PERMISSION_DENIED

    # invalidated -> stable error
    invalidated = writer.invalidate_changed_targets(project_id, "tts_engine_version_changed")
    assert invalidated == [ApprovalGate.PREVIEW_AUDIO.value]
    with pytest.raises(AppError) as excinfo_invalidated:
        reader.assert_gate(project_id, gate)
    assert excinfo_invalidated.value.code is ErrorCode.PERMISSION_DENIED


@pytest.mark.unit
def test_tc_approval_001_06(tmp_path: Path) -> None:
    """TC-APPROVAL-001-06 — 合法な状態遷移

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「合法な状態遷移」を実行する
    Then: 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。
    """
    service = ApprovalService(tmp_path)
    project_id = "project-approval-06"
    gate = ApprovalGate.VERIFIED_SCRIPT

    # draft -> approved is illegal (must go through review_pending first).
    with pytest.raises(AppError) as excinfo:
        service.approve(project_id, gate, approved_by="reviewer-1")
    assert excinfo.value.code is ErrorCode.CONFLICT

    approvals_path = tmp_path / "library" / project_id / "approvals.yaml"
    assert not approvals_path.exists()

    service.submit(project_id, gate, target=_target())
    service.approve(project_id, gate, approved_by="reviewer-1")

    # approved -> invalidated is the only legal transition out of approved; review_pending is not.
    with pytest.raises(AppError) as excinfo_illegal:
        service.submit(project_id, gate, target=_target())
    assert excinfo_illegal.value.code is ErrorCode.CONFLICT
    assert service.get_bundle(project_id).approvals[gate].status.value == "approved"

    invalidated = service.invalidate_changed_targets(project_id, "chapter_spec_changed")
    assert invalidated == [gate.value]

    # invalidated must never go directly back to approved.
    with pytest.raises(AppError) as excinfo_reapprove:
        service.approve(project_id, gate, approved_by="reviewer-1")
    assert excinfo_reapprove.value.code is ErrorCode.CONFLICT


@pytest.mark.unit
def test_tc_approval_001_08(tmp_path: Path) -> None:
    """TC-APPROVAL-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ApprovalBundle/ApprovalRecord/ChangeRequest`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    service = ApprovalService(tmp_path)

    with pytest.raises(AppError) as excinfo_project:
        service.submit("", ApprovalGate.PLANNING, target=_target())
    assert excinfo_project.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_target:
        service.submit("project-approval-08", ApprovalGate.PLANNING, target=None)
    assert excinfo_target.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_paths:
        ApprovalTarget(paths=(), content_hash="a" * 64)
    assert excinfo_paths.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_gate:
        service.assert_gate("project-approval-08", "not_a_real_gate")
    assert excinfo_gate.value.code is ErrorCode.VALIDATION_ERROR

    approvals_path = tmp_path / "library" / "project-approval-08" / "approvals.yaml"
    assert not approvals_path.exists()


@pytest.mark.unit
def test_tc_approval_001_10(tmp_path: Path) -> None:
    """TC-APPROVAL-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    service = ApprovalService(tmp_path)
    project_id = "project-approval-10"

    service.submit(project_id, ApprovalGate.MATERIALS_CURRICULUM, target=_target())
    service.approve(project_id, ApprovalGate.MATERIALS_CURRICULUM, approved_by="reviewer-1")

    approvals_path = tmp_path / "library" / project_id / "approvals.yaml"
    before_bytes = approvals_path.read_bytes()

    # Intentional failure: illegal transition for a different gate must not touch existing content.
    with pytest.raises(AppError):
        service.approve(project_id, ApprovalGate.PLANNING, approved_by="reviewer-1")

    after_bytes = approvals_path.read_bytes()
    assert before_bytes == after_bytes

    bundle = service.get_bundle(project_id)
    assert bundle.approvals[ApprovalGate.MATERIALS_CURRICULUM].status.value == "approved"
    assert bundle.approvals[ApprovalGate.MATERIALS_CURRICULUM].approved_by == "reviewer-1"
