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
from script.source_processing.pdf.extract import PdfTextExtractor

pytestmark = pytest.mark.mvp


def _make_pdf(path: Path, texts: list[str], *, metadata: dict[str, str] | None = None) -> None:
    doc = fitz.open()
    for text in texts:
        page = doc.new_page()
        if text:
            page.insert_text((72, 100), text)
    if metadata:
        doc.set_metadata(metadata)
    doc.save(str(path))
    doc.close()


@pytest.mark.integration_mock
def test_tc_pdf_001_02(tmp_path: Path) -> None:
    """TC-PDF-001-02 — ページ順/locator

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: integration_mock
    Given: 3ページPDF
    When: extractする
    Then: 1..3順でpage locatorを保持する
    """
    source = tmp_path / "three_pages.pdf"
    _make_pdf(
        source,
        [
            "First page has enough printable text content for direct extraction quality checks.",
            "Second page also has enough printable text content for direct extraction quality checks.",
            "Third page also has enough printable text content for direct extraction quality checks.",
        ],
    )

    report = PdfTextExtractor().extract(source)

    assert report.page_count == 3
    assert [page.page_number for page in report.pages] == [1, 2, 3]
    assert "First page" in report.pages[0].text
    assert "Second page" in report.pages[1].text
    assert "Third page" in report.pages[2].text

    for page in report.pages:
        assert len(page.blocks) >= 1
        assert page.blocks[0].reading_order == 1


@pytest.mark.unit
def test_tc_pdf_001_04(tmp_path: Path) -> None:
    """TC-PDF-001-04 — PyMuPDF primary adapter

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PdfPage/PdfExtractionReport`を通じて「PyMuPDF primary adapter」を実行する
    Then: 「PyMuPDF primary adapter」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    source = tmp_path / "primary.pdf"
    _make_pdf(source, ["Primary adapter default routing check with sufficient printable content."])

    # extractorを明示しない既定constructionはPyMuPDFをprimaryとして使う。
    report = PdfTextExtractor().extract(source)

    assert report.extractor == "pymupdf"
    assert report.pages[0].extractor == "pymupdf"
    assert report.pages[0].extraction_method == "direct_text"


@pytest.mark.unit
def test_tc_pdf_001_06(tmp_path: Path) -> None:
    """TC-PDF-001-06 — metadata

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PdfPage/PdfExtractionReport`を通じて「metadata」を実行する
    Then: 「metadata」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    source = tmp_path / "with_metadata.pdf"
    _make_pdf(
        source,
        ["Metadata extraction check with sufficient printable content on this page."],
        metadata={"title": "Walkwise Test Document", "author": "Walkwise QA"},
    )

    report = PdfTextExtractor().extract(source)
    assert report.metadata.get("title") == "Walkwise Test Document"
    assert report.metadata.get("author") == "Walkwise QA"


@pytest.mark.unit
def test_tc_pdf_001_08(tmp_path: Path) -> None:
    """TC-PDF-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `PdfPage/PdfExtractionReport`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    extractor = PdfTextExtractor()

    with pytest.raises(AppError) as excinfo_path:
        extractor.extract(None)
    assert excinfo_path.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_missing:
        extractor.extract(tmp_path / "does_not_exist.pdf")
    assert excinfo_missing.value.code is ErrorCode.NOT_FOUND

    with pytest.raises(AppError) as excinfo_extractor:
        PdfTextExtractor(extractor="unknown")
    assert excinfo_extractor.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_pdf_001_10(tmp_path: Path) -> None:
    """TC-PDF-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    good = tmp_path / "good.pdf"
    _make_pdf(good, ["Immutability check with sufficient printable content on this single page."])
    good_bytes_before = good.read_bytes()
    good_hash_before = hashlib.sha256(good_bytes_before).hexdigest()

    extractor = PdfTextExtractor()
    extractor.extract(good)

    assert good.read_bytes() == good_bytes_before
    assert hashlib.sha256(good.read_bytes()).hexdigest() == good_hash_before

    # 意図的な失敗(存在しないPDF)を発生させても、既存の正常入力には影響しない。
    with pytest.raises(AppError):
        extractor.extract(tmp_path / "missing.pdf")

    assert good.read_bytes() == good_bytes_before
