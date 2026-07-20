"""script/services/source_review.py — 公開契約: SourceReviewService.apply_correction/mark_resolved/require_reprocessing.

Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
Spec: docs/specifications/source-preprocessing.md
"""

from __future__ import annotations

import dataclasses
import difflib
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.schemas.source_review import (
    CorrectionPatch,
    ReviewDecision,
    ReviewIssueStatus,
    SourceReviewIssue,
)

# review issueの合法な状態遷移(いずれもopenからだけ開始し、終端状態への逆行はない)。
_TRANSITIONS: dict[ReviewIssueStatus, frozenset[ReviewIssueStatus]] = {
    ReviewIssueStatus.OPEN: frozenset(
        {ReviewIssueStatus.RESOLVED, ReviewIssueStatus.CORRECTED, ReviewIssueStatus.REPROCESSING_REQUESTED}
    ),
    ReviewIssueStatus.RESOLVED: frozenset(),
    ReviewIssueStatus.CORRECTED: frozenset(),
    ReviewIssueStatus.REPROCESSING_REQUESTED: frozenset(),
}


def _can_transition(current: ReviewIssueStatus, target: ReviewIssueStatus) -> bool:
    return target in _TRANSITIONS.get(current, frozenset())


@dataclass(frozen=True)
class ApplyCorrection:
    """apply_correctionへの入力。"""

    source_id: str
    original_path: Path
    issue: SourceReviewIssue
    patch: CorrectionPatch


@dataclass(frozen=True)
class ReviewResult:
    """apply_correctionの戻り値。raw不変で新revision・diff・provenanceを保持する。"""

    source_id: str
    new_revision: int
    corrected_path: str
    diff: tuple[str, ...]
    provenance: dict[str, Any]
    issue: SourceReviewIssue


@dataclass(frozen=True)
class ReprocessingRequest:
    """require_reprocessingが作る新Job候補(実際のJob起動は呼び出し側の責務)。"""

    issue_id: str
    new_job_id: str
    reason: str
    previous_status: str


def _write_revision_idempotent(destination: Path, data: bytes) -> None:
    """destinationへ書込む。同一内容の再実行は冪等成功、異なる内容の上書きは拒否する。"""
    if destination.exists():
        existing_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
        new_hash = hashlib.sha256(data).hexdigest()
        if existing_hash != new_hash:
            raise AppError(
                ErrorCode.CONFLICT,
                f"cannot overwrite existing revision with different content: {destination}",
            )
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)


class SourceReviewService:
    """review issueを原本/抽出/修正版の差分として管理し、人間承認後に新revisionを作る。"""

    def __init__(self, destination_dir: Path) -> None:
        if not destination_dir:
            raise AppError(ErrorCode.VALIDATION_ERROR, "destination_dir is required")
        self._destination_dir = Path(destination_dir)

    def _next_revision(self, source_id: str) -> int:
        source_dir = self._destination_dir / source_id
        if not source_dir.exists():
            return 2
        existing = list(source_dir.glob("revision-*.md"))
        if not existing:
            return 2
        numbers = [int(path.stem.split("-")[-1]) for path in existing]
        return max(numbers) + 1

    def apply_correction(self, command: ApplyCorrection) -> ReviewResult:
        """rawを変えず修正版とdiffを新revisionへ保存する。"""
        if (
            command is None
            or not command.source_id
            or not command.original_path
            or command.issue is None
            or command.patch is None
        ):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "source_id, original_path, issue and patch are required",
            )

        original_path = Path(command.original_path)
        if not original_path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"original source file does not exist: {original_path}")

        if not _can_transition(command.issue.status, ReviewIssueStatus.CORRECTED):
            raise AppError(
                ErrorCode.CONFLICT,
                f"cannot apply correction: issue is not open (current status: {command.issue.status.value})",
            )

        original_bytes_before = original_path.read_bytes()
        original_text = original_bytes_before.decode("utf-8")

        next_revision = self._next_revision(command.source_id)
        destination = self._destination_dir / command.source_id / f"revision-{next_revision:04d}.md"
        corrected_bytes = command.patch.after_text.encode("utf-8")
        _write_revision_idempotent(destination, corrected_bytes)

        # raw/extracted(原本)は処理前後でbyte不変であることを確認する。
        if original_path.read_bytes() != original_bytes_before:
            raise AppError(ErrorCode.INTERNAL_ERROR, "raw/extracted source must not be modified during correction")

        diff = tuple(
            difflib.unified_diff(
                original_text.splitlines(),
                command.patch.after_text.splitlines(),
                lineterm="",
            )
        )

        provenance = {
            "issue_id": command.issue.issue_id,
            "corrected_by": command.patch.corrected_by,
            "corrected_at": command.patch.corrected_at,
            "before_hash": hashlib.sha256(original_bytes_before).hexdigest(),
            "after_hash": hashlib.sha256(corrected_bytes).hexdigest(),
        }

        updated_issue = dataclasses.replace(command.issue, status=ReviewIssueStatus.CORRECTED)

        return ReviewResult(
            source_id=command.source_id,
            new_revision=next_revision,
            corrected_path=str(destination),
            diff=diff,
            provenance=provenance,
            issue=updated_issue,
        )

    def mark_resolved(self, issue: SourceReviewIssue, decision: ReviewDecision) -> SourceReviewIssue:
        """問題なし(解消済み)の人間承認を記録する。"""
        if issue is None or decision is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "issue and decision are required")
        if issue.issue_id != decision.issue_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "decision.issue_id must match issue.issue_id")

        if not _can_transition(issue.status, ReviewIssueStatus.RESOLVED):
            raise AppError(
                ErrorCode.CONFLICT,
                f"cannot mark resolved: issue is not open (current status: {issue.status.value})",
            )

        return dataclasses.replace(issue, status=ReviewIssueStatus.RESOLVED)

    def require_reprocessing(
        self,
        issue: SourceReviewIssue,
        *,
        reason: str,
        new_job_id: str,
    ) -> tuple[SourceReviewIssue, ReprocessingRequest]:
        """再処理(再OCR等)を要求し、旧正常結果を残したまま新Job候補を作る。"""
        if issue is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "issue is required")
        if not reason or not reason.strip():
            raise AppError(ErrorCode.VALIDATION_ERROR, "reason is required to request reprocessing")
        if not new_job_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "new_job_id is required")

        if not _can_transition(issue.status, ReviewIssueStatus.REPROCESSING_REQUESTED):
            raise AppError(
                ErrorCode.CONFLICT,
                f"cannot require reprocessing: issue is not open (current status: {issue.status.value})",
            )

        updated_issue = dataclasses.replace(issue, status=ReviewIssueStatus.REPROCESSING_REQUESTED)
        request = ReprocessingRequest(
            issue_id=issue.issue_id,
            new_job_id=new_job_id,
            reason=reason,
            previous_status=issue.status.value,
        )
        return updated_issue, request
