from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/ai/routing.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-AI-002
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-AI-002', 'AIRouter.resolve(task_class, policy) -> ModelSelection', '論理層から物理provider/modelを解決し黙った降格をしない。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-AI-002-01', 'priority': 'P0', 'layer': 'unit', 'title': '高保証未設定', 'given': 'high_assurance taskでmodel未設定', 'when': 'routeする', 'then': 'standardへ降格せずblocked/human review', 'test_file': '`tests/test_ai_routing.py`'},
    {'id': 'TC-AI-002-02', 'priority': 'P0', 'layer': 'unit', 'title': 'cache hit', 'given': '同一task/model/prompt/input hash', 'when': '2回実行', 'then': '2回目はclientを呼ばない', 'test_file': '`tests/test_ai_cache.py`'},
    {'id': 'TC-AI-002-03', 'priority': 'P0', 'layer': 'unit', 'title': '予算停止', 'given': '残予算0', 'when': 'AI実行を要求', 'then': 'API呼出し前にbudget_exceeded', 'test_file': '`tests/test_ai_budget.py`'},
    {'id': 'TC-AI-002-04', 'priority': 'P1', 'layer': 'unit', 'title': 'model policy load', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「model policy load」を実行する', 'then': '「model policy load」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ai_routing.py`'},
    {'id': 'TC-AI-002-05', 'priority': 'P1', 'layer': 'unit', 'title': 'token/usage記録', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「token/usage記録」を実行する', 'then': '「token/usage記録」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ai_cache.py`'},
    {'id': 'TC-AI-002-06', 'priority': 'P1', 'layer': 'unit', 'title': '推測値と実測値の区別', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「推測値と実測値の区別」を実行する', 'then': '「推測値と実測値の区別」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ai_budget.py`'},
    {'id': 'TC-AI-002-07', 'priority': 'P1', 'layer': 'unit', 'title': '予算上限', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「予算上限」を実行する', 'then': '予算不足を外部API呼出し前に検出し、usageを実測値と推測値で混同しない。', 'test_file': '`tests/test_ai_routing.py`'},
    {'id': 'TC-AI-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`AIRouter.resolve(task_class, policy) -> ModelSelection`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_ai_cache.py`'},
    {'id': 'TC-AI-002-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`AIRouter.resolve(task_class, policy) -> ModelSelection`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_ai_budget.py`'},
    {'id': 'TC-AI-002-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_ai_routing.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/ai/routing.py)")

class ModelSelection:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class AIRouter:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def resolve(self, task_class: Any, policy: Any) -> ModelSelection:
        """論理層から物理provider/modelを解決し黙った降格をしない。

        Public contract: ``AIRouter.resolve(task_class, policy) -> ModelSelection``.
        """
        _step4_unimplemented('AIRouter.resolve')
