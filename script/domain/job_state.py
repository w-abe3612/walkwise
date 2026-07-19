from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/domain/job_state.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-JOB-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-JOB-001', 'can_transition(current: JobStatus, target: JobStatus) -> bool', '状態遷移表を純粋関数で判定する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-JOB-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'FIFO', 'given': 'queued Jobが3件', 'when': 'start_nextを繰り返す', 'then': 'created/enqueued順で1件ずつrunningになる', 'test_file': '`tests/test_job_lifecycle.py`'},
    {'id': 'TC-JOB-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '不正遷移', 'given': 'cancelled Job', 'when': 'runningへ遷移', 'then': '拒否し状態を維持する', 'test_file': '`tests/test_job_queue.py`'},
    {'id': 'TC-JOB-001-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'stale復旧', 'given': '起動前からrunningのJob', 'when': 'recover_staleする', 'then': 'failedと異常終了messageへ更新する', 'test_file': '`tests/test_stale_job_recovery.py`'},
    {'id': 'TC-JOB-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '状態遷移表', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「状態遷移表」を実行する', 'then': '承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。', 'test_file': '`tests/test_job_lifecycle.py`'},
    {'id': 'TC-JOB-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'parent_job_id再試行', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「parent_job_id再試行」を実行する', 'then': '再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。', 'test_file': '`tests/test_job_queue.py`'},
    {'id': 'TC-JOB-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'approval gate hook', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「approval gate hook」を実行する', 'then': '必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。', 'test_file': '`tests/test_stale_job_recovery.py`'},
    {'id': 'TC-JOB-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'finished_at規則', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「finished_at規則」を実行する', 'then': '「finished_at規則」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_job_lifecycle.py`'},
    {'id': 'TC-JOB-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`can_transition(current: JobStatus, target: JobStatus) -> bool`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_job_queue.py`'},
    {'id': 'TC-JOB-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`can_transition(current: JobStatus, target: JobStatus) -> bool`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_stale_job_recovery.py`'},
    {'id': 'TC-JOB-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_job_lifecycle.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/domain/job_state.py)")

class JobStatus:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

def can_transition(current: JobStatus, target: JobStatus) -> bool:
    """状態遷移表を純粋関数で判定する。

    Public contract: ``can_transition(current: JobStatus, target: JobStatus) -> bool``.
    """
    _step4_unimplemented('can_transition')
