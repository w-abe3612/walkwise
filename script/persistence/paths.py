from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/persistence/paths.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-FILE-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-FILE-001', 'ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths', 'Project配下の相対・決定的な保存先を生成する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-FILE-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'atomic write失敗', 'given': '既存正常ファイルがありreplace前に例外を注入', 'when': 'atomic_writeを実行する', 'then': '旧ファイルが完全に残り一時ファイルをcleanupする', 'test_file': '`tests/test_persistence_paths.py`'},
    {'id': 'TC-FILE-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'lock競合', 'given': '同じProject lockを保持中', 'when': '2つ目のlockを取得する', 'then': '競合errorとなり既存lockを壊さない', 'test_file': '`tests/test_atomic_file_write.py`'},
    {'id': 'TC-FILE-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'root escape拒否', 'given': '`../outside`を含む相対候補', 'when': 'Project pathを解決する', 'then': 'Project root外を拒否する', 'test_file': '`tests/test_project_locking.py`'},
    {'id': 'TC-FILE-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '最低1世代backup', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「最低1世代backup」を実行する', 'then': '失敗前の正常状態をbackupから復旧でき、復旧対象のhashを検証する。', 'test_file': '`tests/test_persistence_paths.py`'},
    {'id': 'TC-FILE-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '入力原本のimmutable保存', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「入力原本のimmutable保存」を実行する', 'then': '処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。', 'test_file': '`tests/test_atomic_file_write.py`'},
    {'id': 'TC-FILE-001-06', 'priority': 'P1', 'layer': 'integration_mock', 'title': '絶対パスのDB保存禁止', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「絶対パスのDB保存禁止」を実行する', 'then': '保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。', 'test_file': '`tests/test_project_locking.py`'},
    {'id': 'TC-FILE-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_persistence_paths.py`'},
    {'id': 'TC-FILE-001-08', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_atomic_file_write.py`'},
    {'id': 'TC-FILE-001-09', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_project_locking.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/persistence/paths.py)")

class ProjectPaths:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def for_root(self, data_root: Path, project_id: str) -> ProjectPaths:
        """Project配下の相対・決定的な保存先を生成する。

        Public contract: ``ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths``.
        """
        _step4_unimplemented('ProjectPaths.for_root')
