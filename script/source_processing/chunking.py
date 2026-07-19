from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/chunking.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-SOURCE-002
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-SOURCE-002', 'chunk_structured_source(source, *, soft_limit=2000) -> list[SourceChunk]', 'locatorを保持して決定的chunkを作る。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-SOURCE-002-01', 'priority': 'P0', 'layer': 'unit', 'title': '低リスク正規化', 'given': '改行・Unicode・反復headerがある', 'when': 'normalizeする', 'then': '決定的修正とbefore/after hash/diffを返す', 'test_file': '`tests/test_source_normalization.py`'},
    {'id': 'TC-SOURCE-002-02', 'priority': 'P0', 'layer': 'unit', 'title': 'soft chunk', 'given': '2000文字付近の段落', 'when': 'chunkする', 'then': '意味境界を優先しlocatorを失わない', 'test_file': '`tests/test_source_chunking.py`'},
    {'id': 'TC-SOURCE-002-03', 'priority': 'P0', 'layer': 'unit', 'title': '参照整合', 'given': 'chunk manifestとtopic index', 'when': 'validateする', 'then': '全chunk IDが存在し重複がない', 'test_file': '`tests/test_source_manifest.py`'},
    {'id': 'TC-SOURCE-002-04', 'priority': 'P1', 'layer': 'unit', 'title': 'Unicode/改行/空白の決定的正規化', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`normalize_text(text, rules) -> NormalizationResult`を通じて「Unicode/改行/空白の決定的正規化」を実行する', 'then': '「Unicode/改行/空白の決定的正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_normalization.py`'},
    {'id': 'TC-SOURCE-002-05', 'priority': 'P1', 'layer': 'unit', 'title': '繰返しheader/footer除去', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`normalize_text(text, rules) -> NormalizationResult`を通じて「繰返しheader/footer除去」を実行する', 'then': '「繰返しheader/footer除去」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_chunking.py`'},
    {'id': 'TC-SOURCE-002-06', 'priority': 'P1', 'layer': 'unit', 'title': 'footnote分離', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`normalize_text(text, rules) -> NormalizationResult`を通じて「footnote分離」を実行する', 'then': '「footnote分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_manifest.py`'},
    {'id': 'TC-SOURCE-002-07', 'priority': 'P1', 'layer': 'unit', 'title': 'structured Markdown/YAML/JSON', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`normalize_text(text, rules) -> NormalizationResult`を通じて「structured Markdown/YAML/JSON」を実行する', 'then': '「structured Markdown/YAML/JSON」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_normalization.py`'},
    {'id': 'TC-SOURCE-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`normalize_text(text, rules) -> NormalizationResult`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_source_chunking.py`'},
    {'id': 'TC-SOURCE-002-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`normalize_text(text, rules) -> NormalizationResult`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_source_manifest.py`'},
    {'id': 'TC-SOURCE-002-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_source_normalization.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/chunking.py)")

class SourceChunk:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

def chunk_structured_source(source: Any, *, soft_limit: Any = 2000) -> list[SourceChunk]:
    """locatorを保持して決定的chunkを作る。

    Public contract: ``chunk_structured_source(source, *, soft_limit=2000) -> list[SourceChunk]``.
    """
    _step4_unimplemented('chunk_structured_source')
