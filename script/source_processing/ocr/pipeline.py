"""script/source_processing/ocr/pipeline.py — 公開契約: OcrPipeline.process_pages(pages, context) -> OcrManifest.

Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
Spec: docs/specifications/ocr-and-scanned-pdf.md
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.source_processing.ocr.client import OcrClient, OcrOptions, OcrPageResult

# ocr-and-scanned-pdf.md 10節「confidence全体が閾値未満 -> review_required」の
# provisional閾値。信頼度閾値の実測調整は14節の未決定事項。
_LOW_CONFIDENCE_THRESHOLD = 0.6

# ocr-and-scanned-pdf.md 5.4節: 高リスク領域は自動確定せず常にreview_requiredとする。
_HIGH_RISK_HINTS = frozenset({"formula", "code", "table", "diagram", "figure"})


@dataclass(frozen=True)
class OcrPageRequest:
    """OcrPipelineへの1ページ分の入力。"""

    image_path: str
    options: OcrOptions
    high_risk_hint: str | None = None

    def __post_init__(self) -> None:
        if not self.image_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "image_path is required")
        if self.options is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "options is required")
        if self.high_risk_hint is not None and self.high_risk_hint not in _HIGH_RISK_HINTS:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown high_risk_hint: {self.high_risk_hint!r}")


@dataclass(frozen=True)
class OcrPageOutcome:
    """1ページ分の処理結果(成功/失敗どちらも保持する)。"""

    image_path: str
    status: str
    result: OcrPageResult | None = None
    error: dict[str, str] | None = None
    review_required: bool = False
    review_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class OcrManifest:
    """ページ単位結果・review flagを集約したmanifest。"""

    runtime_available: bool
    pages: tuple[OcrPageOutcome, ...]


class OcrPipeline:
    """ページ単位結果・confidence・review flagを集約し失敗を分離する。"""

    def __init__(self, client: OcrClient) -> None:
        if client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "client is required")
        self._client = client

    def process_pages(
        self,
        pages: Sequence[OcrPageRequest],
        context: Mapping[str, Any] | None = None,
    ) -> OcrManifest:
        """ページ単位結果・confidence・review flagを集約し失敗を分離する。"""
        if not pages:
            raise AppError(ErrorCode.VALIDATION_ERROR, "pages must not be empty")

        health = self._client.check_runtime()
        if not health.available:
            # ocr-and-scanned-pdf.md: runtime不在時は疎通確認で停止し、
            # 各pageをfailed/reviewableとして記録する(subprocessを個別に試行しない)。
            outcomes = tuple(
                OcrPageOutcome(
                    image_path=page.image_path,
                    status="failed",
                    result=None,
                    error={
                        "code": ErrorCode.EXTERNAL_UNAVAILABLE.value,
                        "message": health.error or "tesseract runtime unavailable",
                    },
                    review_required=True,
                    review_reasons=("tesseract_runtime_unavailable",),
                )
                for page in pages
            )
            return OcrManifest(runtime_available=False, pages=outcomes)

        outcomes: list[OcrPageOutcome] = []
        for page in pages:
            try:
                result = self._client.recognize(Path(page.image_path), page.options)
            except AppError as exc:
                outcomes.append(
                    OcrPageOutcome(
                        image_path=page.image_path,
                        status="failed",
                        result=None,
                        error=exc.to_public_dict(),
                        review_required=True,
                        review_reasons=("ocr_failed",),
                    )
                )
                continue

            review_reasons: list[str] = []
            if page.high_risk_hint:
                # 5.4節: 高リスク領域は自動確定せず常にhuman reviewへ送る。
                review_reasons.append(f"high_risk_{page.high_risk_hint}")
            if result.confidence < _LOW_CONFIDENCE_THRESHOLD:
                review_reasons.append("low_confidence")
            if not result.text.strip():
                review_reasons.append("empty_ocr_result")

            outcomes.append(
                OcrPageOutcome(
                    image_path=page.image_path,
                    status="success",
                    result=result,
                    error=None,
                    review_required=bool(review_reasons),
                    review_reasons=tuple(review_reasons),
                )
            )

        return OcrManifest(runtime_available=True, pages=tuple(outcomes))
