from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/services/sources.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-SOURCE-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-SOURCE-001', 'SourceService.register(command: RegisterSource) -> SourceRegistrationResult', '原本をimmutable copyしDBへ登録、重複hashはwarningとして返す。'),
    ('TASK-SOURCE-001', 'SourceService.transition(source_id, target_status) -> Source', '合法な状態遷移だけを許可する。'),
    ('TASK-SOURCE-001', 'SourceService.list_for_project(project_id) -> list[Source]', 'Project配下を登録順で返す。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-SOURCE-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'text即ready', 'given': 'UTF-8 textを登録', 'when': 'registerする', 'then': 'immutable原本、hash、status readyが作成される', 'test_file': '`tests/test_source_service.py`'},
    {'id': 'TC-SOURCE-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'PDF/image processing', 'given': 'PDFまたは画像を登録', 'when': 'registerする', 'then': 'status registered/processingとなり後続Jobへ渡せる', 'test_file': '`tests/test_source_status_transitions.py`'},
    {'id': 'TC-SOURCE-001-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': '重複hash warning', 'given': '同一bytesを2回登録', 'when': 'registerする', 'then': '2件を追跡可能に保存しwarningを返す', 'test_file': '`tests/test_source_service.py`'},
    {'id': 'TC-SOURCE-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'SHA-256', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceMetadata.from_file(...) -> SourceMetadata`を通じて「SHA-256」を実行する', 'then': '「SHA-256」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_status_transitions.py`'},
    {'id': 'TC-SOURCE-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'Project相対path', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceMetadata.from_file(...) -> SourceMetadata`を通じて「Project相対path」を実行する', 'then': '保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。', 'test_file': '`tests/test_source_service.py`'},
    {'id': 'TC-SOURCE-001-06', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`SourceMetadata.from_file(...) -> SourceMetadata`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_source_status_transitions.py`'},
    {'id': 'TC-SOURCE-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`SourceMetadata.from_file(...) -> SourceMetadata`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_source_service.py`'},
    {'id': 'TC-SOURCE-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_source_status_transitions.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/services/sources.py)")

class RegisterSource:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class Source:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SourceRegistrationResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SourceService:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def register(self, command: RegisterSource) -> SourceRegistrationResult:
        """原本をimmutable copyしDBへ登録、重複hashはwarningとして返す。

        Public contract: ``SourceService.register(command: RegisterSource) -> SourceRegistrationResult``.
        """
        _step4_unimplemented('SourceService.register')
    def transition(self, source_id: Any, target_status: Any) -> Source:
        """合法な状態遷移だけを許可する。

        Public contract: ``SourceService.transition(source_id, target_status) -> Source``.
        """
        _step4_unimplemented('SourceService.transition')
    def list_for_project(self, project_id: Any) -> list[Source]:
        """Project配下を登録順で返す。

        Public contract: ``SourceService.list_for_project(project_id) -> list[Source]``.
        """
        _step4_unimplemented('SourceService.list_for_project')
