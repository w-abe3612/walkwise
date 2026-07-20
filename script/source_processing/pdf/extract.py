"""script/source_processing/pdf/extract.py — 公開契約: PdfTextExtractor.extract, should_fallback_to_ocr.

Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
Spec: docs/specifications/pdf-direct-text-extraction.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.source_processing.pdf.models import PdfExtractionReport, PdfPage, TextBlock

_SUPPORTED_EXTRACTORS = frozenset({"pymupdf", "pypdf"})

# pdf-direct-text-extraction.md 5.4節: 閾値はprovisional(代表PDFでの実測前の暫定値)。
_MIN_PRINTABLE_CHAR_RATIO = 0.85
_MAX_DUPLICATE_RATIO = 0.3
_MIN_EXTRACTED_CHARS_PER_PAGE = 20


def _quality_metrics(text: str) -> tuple[float, float]:
    if not text:
        return 0.0, 0.0

    printable_count = sum(1 for char in text if char.isprintable() or char.isspace())
    printable_ratio = printable_count / len(text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        duplicate_ratio = 0.0
    else:
        unique_lines = len(set(lines))
        duplicate_ratio = (len(lines) - unique_lines) / len(lines)

    return printable_ratio, duplicate_ratio


def should_fallback_to_ocr(page: PdfPage) -> bool:
    """空・極少文字等を根拠にOCR候補を判定する。"""
    if page is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "page is required")

    if len(page.text.strip()) < _MIN_EXTRACTED_CHARS_PER_PAGE:
        return True
    if page.printable_char_ratio < _MIN_PRINTABLE_CHAR_RATIO:
        return True
    if page.duplicate_ratio > _MAX_DUPLICATE_RATIO:
        return True
    return False


class PdfTextExtractor:
    """非保護PDFをページ順で抽出し入力を変更しない。"""

    def __init__(self, *, extractor: str = "pymupdf") -> None:
        if extractor not in _SUPPORTED_EXTRACTORS:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown extractor: {extractor!r}")
        self._extractor = extractor

    def extract(self, path: Path) -> PdfExtractionReport:
        """非保護PDFをページ順で抽出し入力を変更しない。"""
        if not path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")

        path = Path(path)
        if not path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"pdf file does not exist: {path}")

        original_bytes = path.read_bytes()

        if self._extractor == "pymupdf":
            report = self._extract_with_pymupdf(path)
        else:
            report = self._extract_with_pypdf(path)

        if path.read_bytes() != original_bytes:
            raise AppError(ErrorCode.INTERNAL_ERROR, "pdf input must not be modified during extraction")

        return report

    def _extract_with_pymupdf(self, path: Path) -> PdfExtractionReport:
        import fitz

        try:
            doc = fitz.open(path)
        except Exception as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"cannot open pdf: {path}", technical_detail=str(exc)) from exc

        try:
            # pdf-direct-text-extraction.md 5.6節: 提供有無を問わず検出時点でblockedとする。
            if doc.needs_pass or doc.is_encrypted:
                raise AppError(ErrorCode.VALIDATION_ERROR, "unsupported_password_protected_pdf")

            metadata = {key: value for key, value in (doc.metadata or {}).items() if value}
            pages: list[PdfPage] = []
            for page_index in range(doc.page_count):
                pdf_page = doc[page_index]
                raw_blocks = pdf_page.get_text("blocks")
                ordered_blocks = sorted(raw_blocks, key=lambda block: (round(block[1]), block[0]))

                text_blocks: list[TextBlock] = []
                text_parts: list[str] = []
                for order, block in enumerate(ordered_blocks, start=1):
                    x0, y0, x1, y1, text = block[0], block[1], block[2], block[3], block[4]
                    text_parts.append(text)
                    text_blocks.append(TextBlock(bbox=(x0, y0, x1, y1), reading_order=order))

                page_text = "".join(text_parts)
                printable_ratio, duplicate_ratio = _quality_metrics(page_text)
                pages.append(
                    PdfPage(
                        page_number=page_index + 1,
                        text=page_text,
                        blocks=tuple(text_blocks),
                        printable_char_ratio=printable_ratio,
                        duplicate_ratio=duplicate_ratio,
                        extraction_method="direct_text",
                        extractor="pymupdf",
                    )
                )

            return PdfExtractionReport(
                source_path=str(path),
                page_count=doc.page_count,
                pages=tuple(pages),
                metadata=metadata,
                extractor="pymupdf",
            )
        finally:
            doc.close()

    def _extract_with_pypdf(self, path: Path) -> PdfExtractionReport:
        import pypdf

        try:
            reader = pypdf.PdfReader(path)
        except pypdf.errors.DependencyError as exc:
            # pypdfは暗号化PDFのmetadata検査自体に復号backend(cryptography)を要求する。
            # 復号は一切試みない方針のため、backend欠如も含めて即座にblockedとする。
            raise AppError(ErrorCode.VALIDATION_ERROR, "unsupported_password_protected_pdf") from exc
        except Exception as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"cannot open pdf: {path}", technical_detail=str(exc)) from exc

        # pdf-direct-text-extraction.md 5.6節: 提供有無を問わず検出時点でblockedとする。
        if reader.is_encrypted:
            raise AppError(ErrorCode.VALIDATION_ERROR, "unsupported_password_protected_pdf")

        raw_metadata = reader.metadata or {}
        metadata: dict[str, Any] = {
            str(key).lstrip("/"): str(value) for key, value in raw_metadata.items() if value
        }

        pages: list[PdfPage] = []
        for page_index, pdf_page in enumerate(reader.pages):
            page_text = pdf_page.extract_text() or ""
            printable_ratio, duplicate_ratio = _quality_metrics(page_text)
            pages.append(
                PdfPage(
                    page_number=page_index + 1,
                    text=page_text,
                    blocks=(),
                    printable_char_ratio=printable_ratio,
                    duplicate_ratio=duplicate_ratio,
                    extraction_method="direct_text",
                    extractor="pypdf",
                )
            )

        return PdfExtractionReport(
            source_path=str(path),
            page_count=len(reader.pages),
            pages=tuple(pages),
            metadata=metadata,
            extractor="pypdf",
        )
