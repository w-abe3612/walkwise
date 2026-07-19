from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/core/errors.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-CORE-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-CORE-001', 'AppError(code: ErrorCode, message: str, technical_detail: str', 'None = None)`'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-CORE-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '設定優先順位', 'given': '既定値・env・明示値が異なる', 'when': 'AppConfigを読込む', 'then': '明示値>env>既定値の順で採用する', 'test_file': '`tests/test_core_config.py`'},
    {'id': 'TC-CORE-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '公開エラー分離', 'given': 'technical detailにstack/pathがある', 'when': '公開dictへ変換する', 'then': '利用者向けmessageには技術情報を混入しない', 'test_file': '`tests/test_core_errors.py`'},
    {'id': 'TC-CORE-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'ログredaction', 'given': 'API keyを含むcontextがある', 'when': 'ログを出力する', 'then': 'keyを伏せ、timestampはtimezone付きISO 8601になる', 'test_file': '`tests/test_core_logging.py`'},
    {'id': 'TC-CORE-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '設定読込の優先順位', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AppConfig.load(env: Mapping[str, str] \\', 'then': 'None = None) -> AppConfig`を通じて「設定読込の優先順位」を実行する', 'test_file': '「設定読込の優先順位」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。'},
    {'id': 'TC-CORE-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '機密値をログへ出さない', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AppConfig.load(env: Mapping[str, str] \\', 'then': 'None = None) -> AppConfig`を通じて「機密値をログへ出さない」を実行する', 'test_file': '「機密値をログへ出さない」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。'},
    {'id': 'TC-CORE-001-06', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`AppConfig.load(env: Mapping[str, str] \\', 'then': 'None = None) -> AppConfig`を実行する', 'test_file': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。'},
    {'id': 'TC-CORE-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`AppConfig.load(env: Mapping[str, str] \\', 'then': 'None = None) -> AppConfig`を2回実行する', 'test_file': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。'},
    {'id': 'TC-CORE-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_core_errors.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/core/errors.py)")

class AppError(RuntimeError):
    """Public error placeholder declared by the STEP2 contract."""

class ErrorCode:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
