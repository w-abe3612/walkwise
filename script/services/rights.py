"""script/services/rights.py — 公開契約: RightsService.evaluate_*, build_credit_manifest.

Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
Spec: docs/specifications/rights-and-license-management.md (5.3節, 5.6節, 5.7節)
"""

from __future__ import annotations

from collections.abc import Sequence

from script.core.errors import AppError, ErrorCode
from script.schemas.rights import CreditEntry, DistributionDecision, GateDecision, RightsRecord


class RightsService:
    """個人ローカル生成と配布を別gateで判定する。"""

    def evaluate_local_generation(self, record: RightsRecord) -> DistributionDecision:
        """個人ローカル用途は未確認でも条件付き許可できる。"""
        if record is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "record is required")

        decision = record.gate_decision()
        if decision is GateDecision.BLOCKED:
            return DistributionDecision(
                allowed=False,
                reasons=(f"{record.source_id}: blocked for {record.usage_purpose.value}",),
            )
        return DistributionDecision(allowed=True, review_required=decision is GateDecision.REVIEW_REQUIRED)

    def evaluate_distribution(self, records: Sequence[RightsRecord]) -> DistributionDecision:
        """未確認・禁止・credit不足があればhard blockする。"""
        if not records:
            raise AppError(ErrorCode.VALIDATION_ERROR, "records must not be empty")

        blocked_reasons: list[str] = []
        review_reasons: list[str] = []
        for record in records:
            decision = record.gate_decision()
            if decision is GateDecision.BLOCKED:
                blocked_reasons.append(
                    f"{record.source_id}: rights.status={record.status.value} does not permit "
                    f"{record.usage_purpose.value}"
                )
            elif decision is GateDecision.REVIEW_REQUIRED:
                review_reasons.append(f"{record.source_id}: requires human review before distribution")

        if blocked_reasons:
            return DistributionDecision(allowed=False, reasons=tuple(blocked_reasons))
        if review_reasons:
            return DistributionDecision(allowed=False, review_required=True, reasons=tuple(review_reasons))
        return DistributionDecision(allowed=True)


def build_credit_manifest(records: Sequence[RightsRecord]) -> dict:
    """人間確認済みcreditだけを決定的順序で出力する。"""
    if records is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "records is required")

    seen: set[str] = set()
    entries: list[CreditEntry] = []
    for record in sorted(records, key=lambda r: r.source_id):
        if record.source_id in seen:
            continue
        if record.confirmed_by is None or record.confirmed_by.type != "human":
            continue
        display_text = record.evidence.license_name or "Public Domain"
        entries.append(
            CreditEntry(
                source_id=record.source_id,
                display_text=display_text,
                required_by_license=record.evidence.license_name is not None,
            )
        )
        seen.add(record.source_id)

    return {
        "schema_version": "1.0",
        "credits": [
            {
                "source_id": entry.source_id,
                "display_text": entry.display_text,
                "required_by_license": entry.required_by_license,
            }
            for entry in entries
        ],
    }
