"""script/pipelines/semantic_review.py — 公開契約:
SemanticReview.compare(source, transformed) -> SemanticReviewResult.

Contract: docs/test-cases/TASK-NARRATION-001-narration-transformations-and-verified-script.md
Spec: docs/specifications/05-script-segment-schema.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from script.core.errors import AppError, ErrorCode
from script.schemas.script import ScriptDocument

# 意味差(数値・否定・条件)を決定的に検出するための最小マーカー集合。
# 自然言語のfact-checking自体は対象外であり、明白な差異の検出だけを扱う。
_NEGATION_MARKERS = ("not ", "n't", "never", "no longer", "without", "cannot", "can not")
_CONDITION_MARKERS = ("if ", "unless", "only when", "except")
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


class SemanticReviewStatus(str, Enum):
    PASS = "pass"
    REVIEW_REQUIRED = "review_required"
    FAIL = "fail"


@dataclass(frozen=True)
class SemanticDifference:
    segment_id: str
    category: str
    detail: str


@dataclass(frozen=True)
class SemanticReviewResult:
    """SemanticReview.compare()の戻り値。"""

    status: SemanticReviewStatus
    differences: tuple[SemanticDifference, ...] = ()


class SemanticReview:
    """変換前後のScriptDocumentから意味差、条件削除、数値変化を検出する。"""

    def compare(self, source: ScriptDocument, transformed: ScriptDocument) -> SemanticReviewResult:
        """意味差、条件削除、数値変化を検出する。"""
        if source is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source is required")
        if transformed is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "transformed is required")

        source_by_id = {segment.segment_id: segment for segment in source.segments}
        transformed_by_id = {segment.segment_id: segment for segment in transformed.segments}
        if source_by_id.keys() != transformed_by_id.keys():
            raise AppError(ErrorCode.VALIDATION_ERROR, "source and transformed must reference the same segment_ids")

        differences: list[SemanticDifference] = []
        for segment_id, source_segment in source_by_id.items():
            transformed_segment = transformed_by_id[segment_id]
            differences.extend(self._compare_segment(segment_id, source_segment.text, transformed_segment.text))

        if not differences:
            return SemanticReviewResult(status=SemanticReviewStatus.PASS)
        return SemanticReviewResult(status=SemanticReviewStatus.REVIEW_REQUIRED, differences=tuple(differences))

    @staticmethod
    def _compare_segment(segment_id: str, source_text: str, transformed_text: str) -> list[SemanticDifference]:
        differences: list[SemanticDifference] = []

        source_numbers = set(_NUMBER_RE.findall(source_text))
        transformed_numbers = set(_NUMBER_RE.findall(transformed_text))
        if source_numbers != transformed_numbers:
            differences.append(
                SemanticDifference(
                    segment_id=segment_id,
                    category="numeric_change",
                    detail=f"{sorted(source_numbers)} -> {sorted(transformed_numbers)}",
                )
            )

        source_lower = source_text.lower()
        transformed_lower = transformed_text.lower()

        for marker in _NEGATION_MARKERS:
            if (marker in source_lower) != (marker in transformed_lower):
                differences.append(SemanticDifference(segment_id=segment_id, category="negation_change", detail=marker))
                break

        for marker in _CONDITION_MARKERS:
            if (marker in source_lower) != (marker in transformed_lower):
                differences.append(SemanticDifference(segment_id=segment_id, category="condition_change", detail=marker))
                break

        return differences
