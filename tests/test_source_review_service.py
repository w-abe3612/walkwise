"""STEP3->STEP4 test suite for TASK-SOURCE-003: 資料レビュー・修正差分・再処理.

Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
Spec: docs/specifications/source-preprocessing.md
Production files:
- script/services/source_review.py
- script/schemas/source_review.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.core.errors import AppError, ErrorCode
from script.schemas.source_review import (
    CorrectionPatch,
    ReviewDecision,
    ReviewIssueCategory,
    ReviewIssueStatus,
    SourceReviewIssue,
    SourceReviewLocator,
)
from script.services.source_review import ApplyCorrection, SourceReviewService

pytestmark = pytest.mark.mvp


def _issue(issue_id: str = "issue-0001", *, status: ReviewIssueStatus = ReviewIssueStatus.OPEN) -> SourceReviewIssue:
    return SourceReviewIssue(
        issue_id=issue_id,
        source_id="source-1",
        category=ReviewIssueCategory.LOW_CONFIDENCE,
        locator=SourceReviewLocator(page=12),
        status=status,
    )


@pytest.mark.integration_mock
def test_tc_source_003_01(tmp_path: Path) -> None:
    """TC-SOURCE-003-01 — 修正revision

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P0
    Layer: integration_mock
    Given: review issueへ手動修正
    When: apply_correction
    Then: raw不変で新revision・diff・provenanceを作る
    """
    original = tmp_path / "extracted.md"
    original.write_bytes("誤った本分です。\n".encode("utf-8"))
    original_bytes_before = original.read_bytes()

    service = SourceReviewService(destination_dir=tmp_path / "revisions")
    patch = CorrectionPatch(
        issue_id="issue-0001",
        after_text="正しい本文です。\n",
        corrected_by="reviewer-1",
        corrected_at="2026-07-20T00:00:00+09:00",
        before_text="誤った本分です。\n",
    )

    result = service.apply_correction(
        ApplyCorrection(source_id="source-1", original_path=original, issue=_issue(), patch=patch)
    )

    # rawは変更されない。
    assert original.read_bytes() == original_bytes_before

    # 新revisionが作られ、diff・provenanceを保持する。
    corrected_path = Path(result.corrected_path)
    assert corrected_path.exists()
    assert corrected_path.read_text(encoding="utf-8") == "正しい本文です。\n"
    assert result.new_revision == 2
    assert len(result.diff) > 0
    assert result.provenance["corrected_by"] == "reviewer-1"
    assert result.provenance["issue_id"] == "issue-0001"
    assert result.issue.status is ReviewIssueStatus.CORRECTED


@pytest.mark.unit
def test_tc_source_003_02(tmp_path: Path) -> None:
    """TC-SOURCE-003-02 — 再処理

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P0
    Layer: unit
    Given: OCR設定変更を要求
    When: require_reprocessing
    Then: 旧正常結果を残し新Job候補を作る
    """
    service = SourceReviewService(destination_dir=tmp_path / "revisions")
    issue = _issue()

    updated_issue, request = service.require_reprocessing(issue, reason="OCR言語設定を変更", new_job_id="job-0002")

    assert updated_issue.status is ReviewIssueStatus.REPROCESSING_REQUESTED
    assert request.new_job_id == "job-0002"
    assert request.reason == "OCR言語設定を変更"
    assert request.previous_status == "open"

    # 旧正常結果(destination_dir)には一切書込みが発生していない。
    assert not (tmp_path / "revisions").exists()


@pytest.mark.unit
def test_tc_source_003_03() -> None:
    """TC-SOURCE-003-03 — review item model

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「review item model」を実行する
    Then: 「review item model」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    issue = _issue()
    assert issue.status is ReviewIssueStatus.OPEN
    assert issue.category is ReviewIssueCategory.LOW_CONFIDENCE

    with pytest.raises(AppError) as excinfo_issue_id:
        SourceReviewIssue(
            issue_id="",
            source_id="source-1",
            category=ReviewIssueCategory.OTHER,
            locator=SourceReviewLocator(),
        )
    assert excinfo_issue_id.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_source_id:
        SourceReviewIssue(
            issue_id="issue-0001",
            source_id="",
            category=ReviewIssueCategory.OTHER,
            locator=SourceReviewLocator(),
        )
    assert excinfo_source_id.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_source_003_04() -> None:
    """TC-SOURCE-003-04 — 元ページlocator

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「元ページlocator」を実行する
    Then: 「元ページlocator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    # page/chapter/sectionはすべて任意項目であり、完全に空でも許可される
    # (source-storage-and-common-schema.md 5.5節: locatorが空なのはwarning対象であってErrorではない)。
    empty_locator = SourceReviewLocator()
    assert empty_locator.page is None
    assert empty_locator.chapter is None
    assert empty_locator.section is None

    full_locator = SourceReviewLocator(page=42, chapter="3", section="3.2")
    issue = SourceReviewIssue(
        issue_id="issue-0002",
        source_id="source-1",
        category=ReviewIssueCategory.HIGH_RISK_ELEMENT,
        locator=full_locator,
    )
    assert issue.locator == full_locator
    assert issue.locator.page == 42


@pytest.mark.integration_mock
def test_tc_source_003_05(tmp_path: Path) -> None:
    """TC-SOURCE-003-05 — manual correction file

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「manual correction file」を実行する
    Then: 「manual correction file」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    original = tmp_path / "extracted.md"
    original.write_bytes("original text\n".encode("utf-8"))

    service = SourceReviewService(destination_dir=tmp_path / "revisions")
    patch = CorrectionPatch(
        issue_id="issue-0001",
        after_text="corrected text\n",
        corrected_by="reviewer-1",
        corrected_at="2026-07-20T00:00:00+09:00",
    )

    result = service.apply_correction(
        ApplyCorrection(source_id="source-1", original_path=original, issue=_issue(), patch=patch)
    )

    manual_correction_file = Path(result.corrected_path)
    assert manual_correction_file.parent == (tmp_path / "revisions" / "source-1")
    assert manual_correction_file.name == "revision-0002.md"
    assert manual_correction_file.read_text(encoding="utf-8") == "corrected text\n"


@pytest.mark.unit
def test_tc_source_003_06(tmp_path: Path) -> None:
    """TC-SOURCE-003-06 — 再OCR要求

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「再OCR要求」を実行する
    Then: 「再OCR要求」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    service = SourceReviewService(destination_dir=tmp_path / "revisions")

    with pytest.raises(AppError) as excinfo_empty_reason:
        service.require_reprocessing(_issue(), reason="", new_job_id="job-0002")
    assert excinfo_empty_reason.value.code is ErrorCode.VALIDATION_ERROR

    already_resolved = _issue(status=ReviewIssueStatus.RESOLVED)
    with pytest.raises(AppError) as excinfo_illegal:
        service.require_reprocessing(already_resolved, reason="再OCRが必要", new_job_id="job-0003")
    assert excinfo_illegal.value.code is ErrorCode.CONFLICT


@pytest.mark.unit
def test_tc_source_003_07(tmp_path: Path) -> None:
    """TC-SOURCE-003-07 — 問題なし承認

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「問題なし承認」を実行する
    Then: 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。
    """
    service = SourceReviewService(destination_dir=tmp_path / "revisions")
    decision = ReviewDecision(issue_id="issue-0001", decided_by="reviewer-1", decided_at="2026-07-20T00:00:00+09:00")

    resolved = service.mark_resolved(_issue(), decision)
    assert resolved.status is ReviewIssueStatus.RESOLVED

    # issue_idが一致しないdecisionは拒否する。
    with pytest.raises(AppError) as excinfo_mismatch:
        service.mark_resolved(_issue(issue_id="issue-9999"), decision)
    assert excinfo_mismatch.value.code is ErrorCode.VALIDATION_ERROR

    # 既にresolved/corrected/reprocessing_requestedのissueは再承認できない(安定errorで停止)。
    for status in (ReviewIssueStatus.RESOLVED, ReviewIssueStatus.CORRECTED, ReviewIssueStatus.REPROCESSING_REQUESTED):
        with pytest.raises(AppError) as excinfo_illegal:
            service.mark_resolved(_issue(status=status), decision)
        assert excinfo_illegal.value.code is ErrorCode.CONFLICT


@pytest.mark.unit
def test_tc_source_003_08(tmp_path: Path) -> None:
    """TC-SOURCE-003-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_destination:
        SourceReviewService(destination_dir=None)
    assert excinfo_destination.value.code is ErrorCode.VALIDATION_ERROR

    service = SourceReviewService(destination_dir=tmp_path / "revisions")

    with pytest.raises(AppError) as excinfo_command:
        service.apply_correction(None)
    assert excinfo_command.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_patch_text:
        CorrectionPatch(
            issue_id="issue-0001",
            after_text="",
            corrected_by="reviewer-1",
            corrected_at="2026-07-20T00:00:00+09:00",
        )
    assert excinfo_patch_text.value.code is ErrorCode.VALIDATION_ERROR

    # 検証失敗前に副作用(destination_dirへの書込み)が発生していない。
    assert not (tmp_path / "revisions").exists()


@pytest.mark.unit
def test_tc_source_003_09(tmp_path: Path) -> None:
    """TC-SOURCE-003-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `SourceReviewIssue/CorrectionPatch/ReviewDecision`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    service = SourceReviewService(destination_dir=tmp_path / "revisions")
    decision = ReviewDecision(issue_id="issue-0001", decided_by="reviewer-1", decided_at="2026-07-20T00:00:00+09:00")

    first_resolved = service.mark_resolved(_issue(), decision)
    second_resolved = service.mark_resolved(_issue(), decision)
    assert first_resolved == second_resolved

    _, first_request = service.require_reprocessing(_issue(), reason="reason", new_job_id="job-x")
    _, second_request = service.require_reprocessing(_issue(), reason="reason", new_job_id="job-x")
    assert first_request == second_request


@pytest.mark.unit
def test_tc_source_003_10(tmp_path: Path) -> None:
    """TC-SOURCE-003-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    original = tmp_path / "extracted.md"
    original.write_bytes("original text\n".encode("utf-8"))
    original_bytes_before = original.read_bytes()

    service = SourceReviewService(destination_dir=tmp_path / "revisions")
    patch = CorrectionPatch(
        issue_id="issue-0001",
        after_text="corrected text\n",
        corrected_by="reviewer-1",
        corrected_at="2026-07-20T00:00:00+09:00",
    )
    result = service.apply_correction(
        ApplyCorrection(source_id="source-1", original_path=original, issue=_issue(), patch=patch)
    )
    good_revision_path = Path(result.corrected_path)
    good_revision_bytes = good_revision_path.read_bytes()

    # 意図的な失敗: 存在しないoriginal_pathで別issueへ修正を適用しようとする。
    missing_patch = CorrectionPatch(
        issue_id="issue-0002",
        after_text="unreachable\n",
        corrected_by="reviewer-1",
        corrected_at="2026-07-20T00:00:00+09:00",
    )
    with pytest.raises(AppError):
        service.apply_correction(
            ApplyCorrection(
                source_id="source-1",
                original_path=tmp_path / "does_not_exist.md",
                issue=_issue(issue_id="issue-0002"),
                patch=missing_patch,
            )
        )

    # 既存の正常成果物(revision)と入力(original)は変化しない。
    assert original.read_bytes() == original_bytes_before
    assert good_revision_path.read_bytes() == good_revision_bytes
