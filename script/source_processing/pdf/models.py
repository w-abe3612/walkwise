"""script/source_processing/pdf/models.py — 公開契約: PdfPage/PdfExtractionReport.

Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
Spec: docs/specifications/pdf-direct-text-extraction.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class TextBlock:
    """1つのtext blockのbboxと読み順候補(pdf-direct-text-extraction.md 5.3節)。"""

    bbox: tuple[float, float, float, float]
    reading_order: int


@dataclass(frozen=True)
class PdfPage:
    """1ページ分の抽出結果、locator、品質指標を保持する。"""

    page_number: int
    text: str
    blocks: tuple[TextBlock, ...]
    printable_char_ratio: float
    duplicate_ratio: float
    extraction_method: str
    extractor: str
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "page_number must be 1 or greater")
        if not self.extraction_method:
            raise AppError(ErrorCode.VALIDATION_ERROR, "extraction_method is required")
        if not self.extractor:
            raise AppError(ErrorCode.VALIDATION_ERROR, "extractor is required")


@dataclass(frozen=True)
class PdfExtractionReport:
    """PDF全体の抽出結果、metadata、ページ単位品質レポート。"""

    source_path: str
    page_count: int
    pages: tuple[PdfPage, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    extractor: str = "pymupdf"

    def __post_init__(self) -> None:
        if not self.source_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_path is required")
        if self.page_count < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "page_count must not be negative")
