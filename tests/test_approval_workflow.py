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
from script.schemas.approvals import ApprovalGate, ApprovalTarget, ChangeRequest, compute_bundle_hash
from script.services.approvals import ApprovalService

pytestmark = pytest.mark.mvp


def _target(content_hash: str = "a" * 64) -> ApprovalTarget:
    return ApprovalTarget(paths=("project/plan.yaml",), content_hash=content_hash)


@pytest.mark.unit
def test_tc_approval_001_01(tmp_path: Path) -> None:
    """TC-APPROVAL-001-01 — 4gate

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P0
    Layer: unit
    Given: 4承認がすべてcurrent hashでapproved
    When: assert_gateを行う
    Then: 該当後工程を許可する
    """
    service = ApprovalService(tmp_path)
    project_id = "project-approval-01"

    for gate in ApprovalGate:
        service.submit(project_id, gate, target=_target())
        service.approve(project_id, gate, approved_by="reviewer-1")

    for gate in ApprovalGate:
        service.assert_gate(project_id, gate)


@pytest.mark.unit
def test_tc_approval_001_03(tmp_path: Path) -> None:
    """TC-APPROVAL-001-03 — 差し戻し理由

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P0
    Layer: unit
    Given: 理由空でrequest_changes
    When: 実行する
    Then: 拒否し状態を変えない
    """
    service = ApprovalService(tmp_path)
    project_id = "project-approval-03"
    gate = ApprovalGate.PLANNING
    service.submit(project_id, gate, target=_target())

    with pytest.raises(AppError) as excinfo:
        service.request_changes(project_id, gate, reason="")
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        service.request_changes(project_id, gate, reason="   ")

    bundle = service.get_bundle(project_id)
    assert bundle.approvals[gate].status.value == "review_pending"


@pytest.mark.unit
def test_tc_approval_001_05() -> None:
    """TC-APPROVAL-001-05 — bundle hash

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「bundle hash」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    """
    paths = ("project/plan.yaml", "project/chapters/01.yaml")
    hashes = ("a" * 64, "b" * 64)

    first = compute_bundle_hash(paths, hashes)
    second = compute_bundle_hash(paths, hashes)
    assert first == second
    assert len(first) == 64

    changed = compute_bundle_hash(paths, ("a" * 64, "c" * 64))
    assert changed != first


@pytest.mark.unit
def test_tc_approval_001_07() -> None:
    """TC-APPROVAL-001-07 — change request

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「change request」を実行する
    Then: 「change request」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    first = ChangeRequest(
        request_id="cr-0001",
        gate=ApprovalGate.VERIFIED_SCRIPT,
        category="script_text_changed",
        severity="major",
        comment="誤字を修正してください",
    )
    second = ChangeRequest(
        request_id="cr-0001",
        gate=ApprovalGate.VERIFIED_SCRIPT,
        category="script_text_changed",
        severity="major",
        comment="誤字を修正してください",
    )
    assert first == second

    with pytest.raises(AppError) as excinfo:
        ChangeRequest(
            request_id="cr-0002",
            gate=ApprovalGate.VERIFIED_SCRIPT,
            category="script_text_changed",
            severity="major",
            comment="",
        )
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_approval_001_09(tmp_path: Path) -> None:
    """TC-APPROVAL-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ApprovalBundle/ApprovalRecord/ChangeRequest`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    service = ApprovalService(tmp_path)
    project_id = "project-approval-09"
    gate = ApprovalGate.MATERIALS_CURRICULUM
    service.submit(project_id, gate, target=_target())
    service.approve(project_id, gate, approved_by="reviewer-1")

    first_read = service.get_bundle(project_id).to_mapping()
    second_read = service.get_bundle(project_id).to_mapping()
    assert first_read == second_read

    with pytest.raises(AppError) as excinfo_a:
        service.approve(project_id, gate, approved_by="reviewer-1")
    with pytest.raises(AppError) as excinfo_b:
        service.approve(project_id, gate, approved_by="reviewer-1")
    assert excinfo_a.value.code is excinfo_b.value.code is ErrorCode.CONFLICT
