from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/core/identifiers.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-CORE-002
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-CORE-002', 'validate_identifier(value: str) -> str', '`^[a-z0-9]+(?:-[a-z0-9]+)*$`へ適合するIDだけを返す。'),
    ('TASK-CORE-002', 'normalize_unit_id(value: str) -> str', '`full_book`を`book`へ正規化し、新規値は変えない。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-CORE-002-01', 'priority': 'P0', 'layer': 'unit', 'title': 'ID境界', 'given': '正常IDと空白・underscore・日本語・slashを含むIDがある', 'when': 'validate_identifierを呼ぶ', 'then': '正常だけを返し不正値はvalidation error', 'test_file': '`tests/test_identifiers.py`'},
    {'id': 'TC-CORE-002-02', 'priority': 'P0', 'layer': 'unit', 'title': 'canonical hash', 'given': 'mapping key順・CRLF/NFDだけが異なる同値data', 'when': 'canonical_sha256を計算する', 'then': '同じhashになる。配列順差は別hashになる', 'test_file': '`tests/test_hashing.py`'},
    {'id': 'TC-CORE-002-03', 'priority': 'P0', 'layer': 'unit', 'title': '未知schema version', 'given': '未知majorと未知minorを読む', 'when': 'structured fileをloadする', 'then': '未知majorはerror、読める未知minorはwarning', 'test_file': '`tests/test_serialization.py`'},
    {'id': 'TC-CORE-002-04', 'priority': 'P1', 'layer': 'unit', 'title': 'UTF-8/NFC/LF正規化', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`validate_identifier(value: str) -> str`を通じて「UTF-8/NFC/LF正規化」を実行する', 'then': '「UTF-8/NFC/LF正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_identifiers.py`'},
    {'id': 'TC-CORE-002-05', 'priority': 'P1', 'layer': 'unit', 'title': '安全なYAML/JSON load/dump', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`validate_identifier(value: str) -> str`を通じて「安全なYAML/JSON load/dump」を実行する', 'then': '「安全なYAML/JSON load/dump」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_hashing.py`'},
    {'id': 'TC-CORE-002-06', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`validate_identifier(value: str) -> str`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_serialization.py`'},
    {'id': 'TC-CORE-002-07', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`validate_identifier(value: str) -> str`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_identifiers.py`'},
    {'id': 'TC-CORE-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_hashing.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/core/identifiers.py)")

def validate_identifier(value: str) -> str:
    """`^[a-z0-9]+(?:-[a-z0-9]+)*$`へ適合するIDだけを返す。

    Public contract: ``validate_identifier(value: str) -> str``.
    """
    _step4_unimplemented('validate_identifier')

def normalize_unit_id(value: str) -> str:
    """`full_book`を`book`へ正規化し、新規値は変えない。

    Public contract: ``normalize_unit_id(value: str) -> str``.
    """
    _step4_unimplemented('normalize_unit_id')
