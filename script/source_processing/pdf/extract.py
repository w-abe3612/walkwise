from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/pdf/extract.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-PDF-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-PDF-001', 'PdfTextExtractor.extract(path: Path) -> PdfExtractionReport', '非保護PDFをページ順で抽出し入力を変更しない。'),
    ('TASK-PDF-001', 'should_fallback_to_ocr(report) -> bool', '空・極少文字等を根拠にOCR候補を判定する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-PDF-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'password拒否', 'given': 'password protected PDF', 'when': 'extractする', 'then': '解除を試みずunsupported_password_protected_pdf', 'test_file': '`tests/test_pdf_direct_extraction.py`'},
    {'id': 'TC-PDF-001-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'ページ順/locator', 'given': '3ページPDF', 'when': 'extractする', 'then': '1..3順でpage locatorを保持する', 'test_file': '`tests/test_pdf_extraction_fallback.py`'},
    {'id': 'TC-PDF-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'OCR fallback', 'given': '空または極少文字pageを含むPDF', 'when': 'fallback判定', 'then': '該当pageだけOCR候補となる', 'test_file': '`tests/test_pdf_direct_extraction.py`'},
    {'id': 'TC-PDF-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'PyMuPDF primary adapter', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PdfPage/PdfExtractionReport`を通じて「PyMuPDF primary adapter」を実行する', 'then': '「PyMuPDF primary adapter」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_pdf_extraction_fallback.py`'},
    {'id': 'TC-PDF-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'pypdf secondary adapter境界', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PdfPage/PdfExtractionReport`を通じて「pypdf secondary adapter境界」を実行する', 'then': '「pypdf secondary adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_pdf_direct_extraction.py`'},
    {'id': 'TC-PDF-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'metadata', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PdfPage/PdfExtractionReport`を通じて「metadata」を実行する', 'then': '「metadata」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_pdf_extraction_fallback.py`'},
    {'id': 'TC-PDF-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '空/極少文字ページflag', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PdfPage/PdfExtractionReport`を通じて「空/極少文字ページflag」を実行する', 'then': '「空/極少文字ページflag」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_pdf_direct_extraction.py`'},
    {'id': 'TC-PDF-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`PdfPage/PdfExtractionReport`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_pdf_extraction_fallback.py`'},
    {'id': 'TC-PDF-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`PdfPage/PdfExtractionReport`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_pdf_direct_extraction.py`'},
    {'id': 'TC-PDF-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_pdf_extraction_fallback.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/pdf/extract.py)")

class PdfExtractionReport:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class PdfTextExtractor:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def extract(self, path: Path) -> PdfExtractionReport:
        """非保護PDFをページ順で抽出し入力を変更しない。

        Public contract: ``PdfTextExtractor.extract(path: Path) -> PdfExtractionReport``.
        """
        _step4_unimplemented('PdfTextExtractor.extract')

def should_fallback_to_ocr(report: Any) -> bool:
    """空・極少文字等を根拠にOCR候補を判定する。

    Public contract: ``should_fallback_to_ocr(report) -> bool``.
    """
    _step4_unimplemented('should_fallback_to_ocr')
