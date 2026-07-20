"""script/schemas/claims.py — 公開契約: Claim/SourceEvidence/FactCheckReport.

Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
Spec: docs/specifications/06-claims-and-sources.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from script.core.errors import AppError, ErrorCode


class ClaimType(str, Enum):
    TECHNICAL_FACT = "technical_fact"
    DEFINITION = "definition"
    NUMERIC_FACT = "numeric_fact"
    VERSION_SPECIFIC_BEHAVIOR = "version_specific_behavior"
    LIMITATION = "limitation"
    COMPARISON = "comparison"
    CAUSAL_CLAIM = "causal_claim"
    GENERATED_ANALOGY = "generated_analogy"
    GENERATED_EXPLANATION = "generated_explanation"
    OPINION = "opinion"


class ClaimStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    CONFLICT = "conflict"
    UNSUPPORTED = "unsupported"
    REJECTED = "rejected"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


# 06-claims-and-sources.md 6節: generated_analogy/generated_explanation/opinionは
# 事実主張とは別の検査を行うため、verified化にsource_evidenceを必須としない。
FACTUAL_CLAIM_TYPES = frozenset(
    {
        ClaimType.TECHNICAL_FACT,
        ClaimType.DEFINITION,
        ClaimType.NUMERIC_FACT,
        ClaimType.VERSION_SPECIFIC_BEHAVIOR,
        ClaimType.LIMITATION,
        ClaimType.COMPARISON,
        ClaimType.CAUSAL_CLAIM,
    }
)


@dataclass(frozen=True)
class SourceLocator:
    """06-claims-and-sources.md 11節: 出典の粒度。"""

    chapter: str | None = None
    section: str | None = None
    page: int | None = None


@dataclass(frozen=True)
class SourceEvidence:
    """claims.yamlのsource_evidence[]の1件。"""

    source_id: str
    locator: SourceLocator | None = None
    support: str = "direct"

    def __post_init__(self) -> None:
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")


@dataclass(frozen=True)
class ClaimConflict:
    """06-claims-and-sources.md 9節: 資料間の矛盾。システムは黙って一方を選ばない。"""

    source_ids: tuple[str, ...]
    resolution: str = "human_review_required"

    def __post_init__(self) -> None:
        if len(self.source_ids) < 2:
            raise AppError(ErrorCode.VALIDATION_ERROR, "conflict requires at least two source_ids")


@dataclass(frozen=True)
class Claim:
    """claims.yamlの1件。"""

    claim_id: str
    statement: str
    claim_type: ClaimType
    segment_id: str | None = None
    status: ClaimStatus = ClaimStatus.PENDING
    source_evidence: tuple[SourceEvidence, ...] = ()
    conflict: ClaimConflict | None = None
    verified_by_human: bool = False

    def __post_init__(self) -> None:
        if not self.claim_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "claim_id is required")
        if not self.statement:
            raise AppError(ErrorCode.VALIDATION_ERROR, "statement is required")

        if self.status is ClaimStatus.CONFLICT and self.conflict is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "conflict status requires a conflict record")

        if self.status is ClaimStatus.VERIFIED:
            # 9.1節: 高性能モデルを使用しても、AI出力だけでverifiedにしてはならない。
            if not self.verified_by_human:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    "verified status requires human approval (verified_by_human=True)",
                )
            if self.claim_type in FACTUAL_CLAIM_TYPES and not self.source_evidence:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    "verified factual claims require at least one source_evidence",
                )


@dataclass(frozen=True)
class FactCheckReport:
    """claims.pyの`verify()`戻り値。chapters/<chapter_id>/reports/fact-check.json相当の内容。"""

    claims: tuple[Claim, ...]

    def __post_init__(self) -> None:
        if not self.claims:
            raise AppError(ErrorCode.VALIDATION_ERROR, "claims must not be empty")
