"""script/schemas/rights.py — 公開契約: RightsRecord/CreditEntry/DistributionDecision.

Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
Spec: docs/specifications/rights-and-license-management.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from script.core.errors import AppError, ErrorCode


class RightsStatus(str, Enum):
    UNVERIFIED = "unverified"
    USER_ASSERTED_PRIVATE_USE = "user_asserted_private_use"
    VERIFIED_OPEN_LICENSE = "verified_open_license"
    VERIFIED_PUBLIC_DOMAIN = "verified_public_domain"
    LICENSED_PRIVATE_USE = "licensed_private_use"
    RESTRICTED = "restricted"
    NEEDS_LEGAL_REVIEW = "needs_legal_review"
    REJECTED = "rejected"


class UsagePurpose(str, Enum):
    PERSONAL_LEARNING = "personal_learning"
    INTERNAL_USE = "internal_use"
    PUBLIC_DISTRIBUTION = "public_distribution"
    COMMERCIAL_DISTRIBUTION = "commercial_distribution"


class GateDecision(str, Enum):
    ALLOWED = "allowed"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


_HUMAN_CONFIRMED_STATUSES = {
    RightsStatus.VERIFIED_OPEN_LICENSE,
    RightsStatus.VERIFIED_PUBLIC_DOMAIN,
    RightsStatus.LICENSED_PRIVATE_USE,
}

# docs/specifications/rights-and-license-management.md 5.3節 利用目的別ゲート表
_GATE_TABLE: dict[RightsStatus, dict[UsagePurpose, GateDecision]] = {
    RightsStatus.UNVERIFIED: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.ALLOWED,
        UsagePurpose.INTERNAL_USE: GateDecision.BLOCKED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.BLOCKED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.BLOCKED,
    },
    RightsStatus.USER_ASSERTED_PRIVATE_USE: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.ALLOWED,
        UsagePurpose.INTERNAL_USE: GateDecision.REVIEW_REQUIRED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.BLOCKED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.BLOCKED,
    },
    RightsStatus.VERIFIED_OPEN_LICENSE: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.ALLOWED,
        UsagePurpose.INTERNAL_USE: GateDecision.ALLOWED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.ALLOWED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.REVIEW_REQUIRED,
    },
    RightsStatus.VERIFIED_PUBLIC_DOMAIN: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.ALLOWED,
        UsagePurpose.INTERNAL_USE: GateDecision.ALLOWED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.ALLOWED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.ALLOWED,
    },
    RightsStatus.LICENSED_PRIVATE_USE: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.ALLOWED,
        UsagePurpose.INTERNAL_USE: GateDecision.REVIEW_REQUIRED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.BLOCKED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.BLOCKED,
    },
    RightsStatus.RESTRICTED: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.REVIEW_REQUIRED,
        UsagePurpose.INTERNAL_USE: GateDecision.BLOCKED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.BLOCKED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.BLOCKED,
    },
    RightsStatus.NEEDS_LEGAL_REVIEW: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.REVIEW_REQUIRED,
        UsagePurpose.INTERNAL_USE: GateDecision.BLOCKED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.BLOCKED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.BLOCKED,
    },
    RightsStatus.REJECTED: {
        UsagePurpose.PERSONAL_LEARNING: GateDecision.BLOCKED,
        UsagePurpose.INTERNAL_USE: GateDecision.BLOCKED,
        UsagePurpose.PUBLIC_DISTRIBUTION: GateDecision.BLOCKED,
        UsagePurpose.COMMERCIAL_DISTRIBUTION: GateDecision.BLOCKED,
    },
}


@dataclass(frozen=True)
class Evidence:
    """ライセンス証拠(5.4節)。"""

    license_name: str | None = None
    license_version: str | None = None
    source_url: str | None = None
    retrieved_at: str | None = None
    evidence_file: str | None = None


@dataclass(frozen=True)
class ConfirmedBy:
    """状態確認の実施者。AIはverified_*へ確定できない。"""

    type: str
    name: str | None = None
    confirmed_at: str | None = None


@dataclass(frozen=True)
class RightsRecord:
    """利用目的、権利確認状態、証拠を型付けする。"""

    source_id: str
    status: RightsStatus
    usage_purpose: UsagePurpose
    evidence: Evidence = field(default_factory=Evidence)
    confirmed_by: ConfirmedBy | None = None

    def __post_init__(self) -> None:
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")

        if self.status in _HUMAN_CONFIRMED_STATUSES:
            if self.confirmed_by is None or self.confirmed_by.type != "human":
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"{self.status.value} requires confirmed_by.type == 'human'",
                )
            if self.status == RightsStatus.VERIFIED_OPEN_LICENSE and not self.evidence.license_name:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    "verified_open_license requires evidence.license_name",
                )

    def gate_decision(self) -> GateDecision:
        """5.3節ゲート表に基づく判定を返す。"""
        return _GATE_TABLE[self.status][self.usage_purpose]


@dataclass(frozen=True)
class CreditEntry:
    """クレジット表記候補(5.7節)。"""

    source_id: str
    display_text: str
    required_by_license: bool = False


@dataclass(frozen=True)
class DistributionDecision:
    """配布gate判定結果。"""

    allowed: bool
    reasons: tuple[str, ...] = ()
    review_required: bool = False
