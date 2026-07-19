from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/epub/models.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-EPUB-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-EPUB-001', 'EpubChapter/EpubExtractionReport', 'spine順、章、annotation、locatorを保持する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-EPUB-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'DRM拒否', 'given': '暗号化EPUB', 'when': 'extractする', 'then': '解除せずunsupported_drmで停止する', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'spine順', 'given': 'manifest順とfile名順が異なるEPUB', 'when': 'extractする', 'then': 'spine順を採用する', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'footnote保持', 'given': 'annotation/footnoteを含むEPUB', 'when': 'extractする', 'then': '別構造で保持し本文へ自動挿入しない', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'EPUB2/3判定', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`EpubChapter/EpubExtractionReport`を通じて「EPUB2/3判定」を実行する', 'then': '「EPUB2/3判定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'container/OPF/spine解決', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`EpubChapter/EpubExtractionReport`を通じて「container/OPF/spine解決」を実行する', 'then': '入力の論理順を維持し、再実行しても同じ順序になる。順序重複・欠落は検出する。', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '章/節locator', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`EpubChapter/EpubExtractionReport`を通じて「章/節locator」を実行する', 'then': '「章/節locator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'annotation分離', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`EpubChapter/EpubExtractionReport`を通じて「annotation分離」を実行する', 'then': '「annotation分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`EpubChapter/EpubExtractionReport`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`EpubChapter/EpubExtractionReport`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_epub_extraction.py`'},
    {'id': 'TC-EPUB-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_epub_extraction.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/epub/models.py)")

class EpubChapter:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class EpubExtractionReport:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
