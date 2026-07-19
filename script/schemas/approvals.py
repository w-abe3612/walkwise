from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/schemas/approvals.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-APPROVAL-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-APPROVAL-001', 'ApprovalBundle/ApprovalRecord/ChangeRequest', '4承認地点と対象hashを型付けする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-APPROVAL-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '4gate', 'given': '4承認がすべてcurrent hashでapproved', 'when': 'assert_gateを行う', 'then': '該当後工程を許可する', 'test_file': '`tests/test_approval_workflow.py`'},
    {'id': 'TC-APPROVAL-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '変更による無効化', 'given': 'approved対象のhashを変更', 'when': 'invalidateを行う', 'then': '関連承認だけinvalidatedにする', 'test_file': '`tests/test_approval_invalidation.py`'},
    {'id': 'TC-APPROVAL-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '差し戻し理由', 'given': '理由空でrequest_changes', 'when': '実行する', 'then': '拒否し状態を変えない', 'test_file': '`tests/test_approval_workflow.py`'},
    {'id': 'TC-APPROVAL-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'approvals.yaml load/save', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「approvals.yaml load/save」を実行する', 'then': '必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。', 'test_file': '`tests/test_approval_invalidation.py`'},
    {'id': 'TC-APPROVAL-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'bundle hash', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「bundle hash」を実行する', 'then': '同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。', 'test_file': '`tests/test_approval_workflow.py`'},
    {'id': 'TC-APPROVAL-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '合法な状態遷移', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「合法な状態遷移」を実行する', 'then': '承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。', 'test_file': '`tests/test_approval_invalidation.py`'},
    {'id': 'TC-APPROVAL-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'change request', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ApprovalBundle/ApprovalRecord/ChangeRequest`を通じて「change request」を実行する', 'then': '「change request」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_approval_workflow.py`'},
    {'id': 'TC-APPROVAL-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ApprovalBundle/ApprovalRecord/ChangeRequest`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_approval_invalidation.py`'},
    {'id': 'TC-APPROVAL-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ApprovalBundle/ApprovalRecord/ChangeRequest`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_approval_workflow.py`'},
    {'id': 'TC-APPROVAL-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_approval_invalidation.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/schemas/approvals.py)")

class ApprovalBundle:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ApprovalRecord:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ChangeRequest:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
