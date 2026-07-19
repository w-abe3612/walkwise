from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/worker/handlers.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-WORKER-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-WORKER-001', 'HandlerRegistry.register/dispatch', 'command名でhandlerを選択し未知commandを拒否する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-WORKER-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'JSON Lines', 'given': '2requestをstdinへ投入', 'when': 'mainを実行', 'then': 'requestごとのeventを行単位・flush順で出す', 'test_file': '`tests/test_worker_protocol.py`'},
    {'id': 'TC-WORKER-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '未知command', 'given': '未登録command', 'when': 'dispatch', 'then': 'error eventを返しprocessを継続', 'test_file': '`tests/test_worker_dispatch.py`'},
    {'id': 'TC-WORKER-001-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'stdout汚染', 'given': 'handlerがlogを出す', 'when': '実行', 'then': 'protocol stdoutへ非JSONを出さずstderr/fileへ分離', 'test_file': '`tests/test_worker_protocol.py`'},
    {'id': 'TC-WORKER-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'handler registry', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`WorkerRequest/WorkerEvent/WorkerError`を通じて「handler registry」を実行する', 'then': '「handler registry」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_dispatch.py`'},
    {'id': 'TC-WORKER-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '1行1JSON', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`WorkerRequest/WorkerEvent/WorkerError`を通じて「1行1JSON」を実行する', 'then': '「1行1JSON」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_protocol.py`'},
    {'id': 'TC-WORKER-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'progress', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`WorkerRequest/WorkerEvent/WorkerError`を通じて「progress」を実行する', 'then': 'current/totalとmessageを単調・順序どおりに通知し、完了後に進捗を逆行させない。', 'test_file': '`tests/test_worker_dispatch.py`'},
    {'id': 'TC-WORKER-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'artifact', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`WorkerRequest/WorkerEvent/WorkerError`を通じて「artifact」を実行する', 'then': '「artifact」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_protocol.py`'},
    {'id': 'TC-WORKER-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`WorkerRequest/WorkerEvent/WorkerError`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_worker_dispatch.py`'},
    {'id': 'TC-WORKER-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`WorkerRequest/WorkerEvent/WorkerError`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_worker_protocol.py`'},
    {'id': 'TC-WORKER-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_worker_dispatch.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/worker/handlers.py)")

class HandlerRegistry:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def register(self) -> Any:
        """command名でhandlerを選択し未知commandを拒否する。

        Public contract: ``HandlerRegistry.register/dispatch``.
        """
        _step4_unimplemented('HandlerRegistry.register')
    def dispatch(self) -> Any:
        """command名でhandlerを選択し未知commandを拒否する。

        Public contract: ``HandlerRegistry.register/dispatch``.
        """
        _step4_unimplemented('HandlerRegistry.dispatch')
