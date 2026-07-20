"""STEP3->STEP4 test suite for TASK-PDF-001: PDF直接テキスト抽出.

Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
Spec: docs/specifications/pdf-direct-text-extraction.md
Production files:
- script/source_processing/pdf/extract.py
- script/source_processing/pdf/models.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import fitz
import pytest

from script.core.errors import AppError, ErrorCode
from script.source_processing.pdf.extract import PdfTextExtractor, should_fallback_to_ocr

pytestmark = pytest.mark.mvp


def _make_pdf(path: Path, texts: list[str]) -> None:
    doc = fitz.open()
    for text in texts:
        page = doc.new_page()
        if text:
            page.insert_text((72, 100), text)
    doc.save(str(path))
    doc.close()


def _make_password_pdf(path: Path, text: str = "secret content") -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text)
    doc.save(str(path), encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="owner-pw", user_pw="user-pw")
    doc.close()


@pytest.mark.integration_mock
def test_tc_pdf_001_01(tmp_path: Path) -> None:
    """TC-PDF-001-01 — password拒否

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: integration_mock
    Given: password protected PDF
    When: extractする
    Then: 解除を試みずunsupported_password_protected_pdf
    """
    protected = tmp_path / "protected.pdf"
    _make_password_pdf(protected)
    original_bytes = protected.read_bytes()

    for extractor_name in ("pymupdf", "pypdf"):
        extractor = PdfTextExtractor(extractor=extractor_name)
        with pytest.raises(AppError) as excinfo:
            extractor.extract(protected)
        assert excinfo.value.code is ErrorCode.VALIDATION_ERROR
        assert "unsupported_password_protected_pdf" in excinfo.value.message

    # パスワード解除を一切試みていないため、入力fileは変化しない。
    assert protected.read_bytes() == original_bytes


@pytest.mark.unit
def test_tc_pdf_001_03(tmp_path: Path) -> None:
    """TC-PDF-001-03 — OCR fallback

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: unit
    Given: 空または極少文字pageを含むPDF
    When: fallback判定
    Then: 該当pageだけOCR候補となる
    """
    mixed = tmp_path / "mixed.pdf"
    _make_pdf(
        mixed,
        [
            "This page has plenty of normal printable text content for direct extraction to succeed cleanly.",
            "",  # 空page
        ],
    )

    extractor = PdfTextExtractor()
    report = extractor.extract(mixed)
    assert report.page_count == 2

    assert should_fallback_to_ocr(report.pages[0]) is False
    assert should_fallback_to_ocr(report.pages[1]) is True


@pytest.mark.unit
def test_tc_pdf_001_05(tmp_path: Path) -> None:
    """TC-PDF-001-05 — pypdf secondary adapter境界

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PdfPage/PdfExtractionReport`を通じて「pypdf secondary adapter境界」を実行する
    Then: 「pypdf secondary adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    source = tmp_path / "single.pdf"
    _make_pdf(source, ["Secondary adapter boundary check with sufficient printable content."])

    extractor = PdfTextExtractor(extractor="pypdf")
    report = extractor.extract(source)

    assert report.extractor == "pypdf"
    assert report.page_count == 1
    assert report.pages[0].extractor == "pypdf"
    assert "Secondary adapter boundary check" in report.pages[0].text

    with pytest.raises(AppError) as excinfo:
        PdfTextExtractor(extractor="not_a_real_extractor")
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_pdf_001_07(tmp_path: Path) -> None:
    """TC-PDF-001-07 — 空/極少文字ページflag

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PdfPage/PdfExtractionReport`を通じて「空/極少文字ページflag」を実行する
    Then: 「空/極少文字ページflag」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    sparse = tmp_path / "sparse.pdf"
    _make_pdf(sparse, ["Hi"])  # 20文字未満の極少文字page

    report = PdfTextExtractor().extract(sparse)
    assert len(report.pages[0].text.strip()) < 20
    assert should_fallback_to_ocr(report.pages[0]) is True


@pytest.mark.unit
def test_tc_pdf_001_09(tmp_path: Path) -> None:
    """TC-PDF-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `PdfPage/PdfExtractionReport`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    source = tmp_path / "repeat.pdf"
    _make_pdf(source, ["Determinism check with stable printable content across repeated extraction calls."])

    extractor = PdfTextExtractor()
    first = extractor.extract(source)
    second = extractor.extract(source)

    assert first == second
