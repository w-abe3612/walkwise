"""script/schemas/source_review.py — 公開契約: SourceReviewIssue/CorrectionPatch/ReviewDecision.

Contract: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
Spec: docs/specifications/source-preprocessing.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from script.core.errors import AppError, ErrorCode


class ReviewIssueCategory(str, Enum):
    """review_required判定の主な発生元(TASK-OCR-001/TASK-PDF-001/TASK-IMAGE-002由来)。"""

    LOW_CONFIDENCE = "low_confidence"
    HIGH_RISK_ELEMENT = "high_risk_element"
    OCR_FALLBACK_REQUIRED = "ocr_fallback_required"
    BLANK_PAGE_CANDIDATE = "blank_page_candidate"
    OTHER = "other"


class ReviewIssueStatus(str, Enum):
    """review issueの状態(source-preprocessing.md 5.9節/9節)。"""

    OPEN = "open"
    RESOLVED = "resolved"
    CORRECTED = "corrected"
    REPROCESSING_REQUESTED = "reprocessing_requested"


@dataclass(frozen=True)
class SourceReviewLocator:
    """元ページlocator。すべて任意項目(source-storage-and-common-schema.md 5.5節と同型)。"""

    page: int | None = None
    chapter: str | None = None
    section: str | None = None


@dataclass(frozen=True)
class SourceReviewIssue:
    """review_required箇所1件のreview item model。"""

    issue_id: str
    source_id: str
    category: ReviewIssueCategory
    locator: SourceReviewLocator
    status: ReviewIssueStatus = ReviewIssueStatus.OPEN
    description: str = ""

    def __post_init__(self) -> None:
        if not self.issue_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "issue_id is required")
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")


@dataclass(frozen=True)
class CorrectionPatch:
    """手動修正差分。raw/extractedは不変のまま、修正後本文だけを新revisionへ渡す。"""

    issue_id: str
    after_text: str
    corrected_by: str
    corrected_at: str
    before_text: str = ""

    def __post_init__(self) -> None:
        if not self.issue_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "issue_id is required")
        if not self.after_text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "after_text is required")
        if not self.corrected_by:
            raise AppError(ErrorCode.VALIDATION_ERROR, "corrected_by is required")
        if not self.corrected_at:
            raise AppError(ErrorCode.VALIDATION_ERROR, "corrected_at is required")


@dataclass(frozen=True)
class ReviewDecision:
    """「問題なし」人間承認の記録。"""

    issue_id: str
    decided_by: str
    decided_at: str
    comment: str = ""

    def __post_init__(self) -> None:
        if not self.issue_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "issue_id is required")
        if not self.decided_by:
            raise AppError(ErrorCode.VALIDATION_ERROR, "decided_by is required")
        if not self.decided_at:
            raise AppError(ErrorCode.VALIDATION_ERROR, "decided_at is required")
