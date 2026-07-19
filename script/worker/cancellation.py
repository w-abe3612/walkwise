from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/worker/cancellation.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-WORKER-002
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-WORKER-002', 'CancellationToken.requested()/raise_if_cancelled()', 'cooperative cancelを提供する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-WORKER-002-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'cooperative cancel', 'given': '長処理中にcancel', 'when': 'runtime', 'then': 'cancel_requested→cancelled eventで停止', 'test_file': '`tests/test_worker_cancellation.py`'},
    {'id': 'TC-WORKER-002-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'timeout', 'given': 'handlerが期限超過', 'when': 'runtime', 'then': 'timeout errorとcleanupを実行', 'test_file': '`tests/test_worker_runtime_failures.py`'},
    {'id': 'TC-WORKER-002-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': '異常終了', 'given': '一時file作成後process kill', 'when': 'recover', 'then': '正式成果物へ登録せず既存成果物を保持', 'test_file': '`tests/test_worker_cancellation.py`'},
    {'id': 'TC-WORKER-002-04', 'priority': 'P1', 'layer': 'unit', 'title': 'grace period', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CancellationToken.requested()/raise_if_cancelled()`を通じて「grace period」を実行する', 'then': '「grace period」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_runtime_failures.py`'},
    {'id': 'TC-WORKER-002-05', 'priority': 'P1', 'layer': 'unit', 'title': 'force terminate契約', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CancellationToken.requested()/raise_if_cancelled()`を通じて「force terminate契約」を実行する', 'then': '「force terminate契約」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_cancellation.py`'},
    {'id': 'TC-WORKER-002-06', 'priority': 'P1', 'layer': 'unit', 'title': '途中終了', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CancellationToken.requested()/raise_if_cancelled()`を通じて「途中終了」を実行する', 'then': '「途中終了」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_runtime_failures.py`'},
    {'id': 'TC-WORKER-002-07', 'priority': 'P1', 'layer': 'unit', 'title': '既存正常成果物保持', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CancellationToken.requested()/raise_if_cancelled()`を通じて「既存正常成果物保持」を実行する', 'then': '「既存正常成果物保持」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_worker_cancellation.py`'},
    {'id': 'TC-WORKER-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`CancellationToken.requested()/raise_if_cancelled()`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_worker_runtime_failures.py`'},
    {'id': 'TC-WORKER-002-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`CancellationToken.requested()/raise_if_cancelled()`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_worker_cancellation.py`'},
    {'id': 'TC-WORKER-002-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_worker_runtime_failures.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/worker/cancellation.py)")

class CancellationToken:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def requested(self) -> Any:
        """cooperative cancelを提供する。

        Public contract: ``CancellationToken.requested()/raise_if_cancelled()``.
        """
        _step4_unimplemented('CancellationToken.requested')
    def raise_if_cancelled(self) -> Any:
        """cooperative cancelを提供する。

        Public contract: ``CancellationToken.requested()/raise_if_cancelled()``.
        """
        _step4_unimplemented('CancellationToken.raise_if_cancelled')
