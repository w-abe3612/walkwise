from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/persistence/repositories.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-DB-002
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-DB-002', 'ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository', '型付きinsert/find/list/update契約を提供する。'),
    ('TASK-DB-002', 'map_integrity_error(error) -> AppError', 'FK・unique・check違反を安定error codeへ変換する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-DB-002-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'transaction rollback', 'given': '2つ目の書込みでconstraint errorを発生', 'when': 'UnitOfWorkを終了する', 'then': '1つ目を含め全変更がrollbackされる', 'test_file': '`tests/test_repositories.py`'},
    {'id': 'TC-DB-002-02', 'priority': 'P0', 'layer': 'unit', 'title': 'Artifact追記専用', 'given': '既存Artifactをupdateしようとする', 'when': 'Repository APIを呼ぶ', 'then': '操作を拒否し既存行を変更しない', 'test_file': '`tests/test_unit_of_work.py`'},
    {'id': 'TC-DB-002-03', 'priority': 'P1', 'layer': 'unit', 'title': 'Project/Source/BuildRequest/Job/Artifact repository契約', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「Project/Source/BuildRequest/Job/Artifact repository契約」を実行する', 'then': '「Project/Source/BuildRequest/Job/Artifact repository契約」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_repositories.py`'},
    {'id': 'TC-DB-002-04', 'priority': 'P1', 'layer': 'unit', 'title': 'insert/find/list/updateの許可範囲', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「insert/find/list/updateの許可範囲」を実行する', 'then': '必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。', 'test_file': '`tests/test_unit_of_work.py`'},
    {'id': 'TC-DB-002-05', 'priority': 'P1', 'layer': 'unit', 'title': 'FK/constraint例外変換', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「FK/constraint例外変換」を実行する', 'then': '「FK/constraint例外変換」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_repositories.py`'},
    {'id': 'TC-DB-002-06', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_unit_of_work.py`'},
    {'id': 'TC-DB-002-07', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_repositories.py`'},
    {'id': 'TC-DB-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_unit_of_work.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/persistence/repositories.py)")

class AppError(RuntimeError):
    """Public error placeholder declared by the STEP2 contract."""

class ArtifactRepository:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class BuildRequestRepository:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class JobRepository:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ProjectRepository:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SourceRepository:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

def map_integrity_error(error: Any) -> AppError:
    """FK・unique・check違反を安定error codeへ変換する。

    Public contract: ``map_integrity_error(error) -> AppError``.
    """
    _step4_unimplemented('map_integrity_error')
