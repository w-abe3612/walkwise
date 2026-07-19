from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/services/build_requests.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-BUILD-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-BUILD-001', 'BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest', '形式をcanonical JSON化しdraftとして保存する。'),
    ('TASK-BUILD-001', 'serialize_output_formats(values) -> str', '`["mp3","text"]`等の空白なしJSONへ変換する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-BUILD-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'text-only', 'given': 'formats=[text], voiceなし', 'when': 'Build Requestを作成', 'then': 'draftとして成功する', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'mp3+text', 'given': 'formats=[text,mp3], voiceあり', 'when': '作成する', 'then': 'JSONは["mp3","text"]になる', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '空・未知・重複', 'given': '空、epub、mp3重複をそれぞれ渡す', 'when': '作成する', 'then': '副作用前に拒否する', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'output_formatsの1件以上/許可値/重複禁止/order', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を通じて「output_formatsの1件以上/許可値/重複禁止/order」を実行する', 'then': '重複を検出し、仕様で許可されない重複は安定したvalidation errorとして副作用前に拒否する。', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'Project存在確認', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を通じて「Project存在確認」を実行する', 'then': '「Project存在確認」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-06', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_build_request_service.py`'},
    {'id': 'TC-BUILD-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_build_request_service.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/services/build_requests.py)")

class BuildRequest:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class CreateBuildRequest:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class BuildRequestService:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def create(self, command: CreateBuildRequest) -> BuildRequest:
        """形式をcanonical JSON化しdraftとして保存する。

        Public contract: ``BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest``.
        """
        _step4_unimplemented('BuildRequestService.create')

def serialize_output_formats(values: Any) -> str:
    """`["mp3","text"]`等の空白なしJSONへ変換する。

    Public contract: ``serialize_output_formats(values) -> str``.
    """
    _step4_unimplemented('serialize_output_formats')
