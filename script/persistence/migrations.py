from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/persistence/migrations.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-DB-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-DB-001', 'MigrationRunner.apply_all(connection, migrations_dir, *, backup_path=None) -> list[str]', '未適用migrationを順序どおり適用しchecksumを記録する。'),
    ('TASK-DB-001', 'MigrationRunner.verify_applied_checksums(...) -> None', '適用済みファイル改変を検出して停止する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-DB-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': '初期schema', 'given': '空SQLite DB', 'when': '全migrationを適用する', 'then': '6テーブル・FK・index・checkが作成される', 'test_file': '`tests/test_database_connection.py`'},
    {'id': 'TC-DB-001-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': '冪等適用', 'given': '適用済みDB', 'when': 'apply_allを再実行する', 'then': '新規適用0件でschemaと履歴が変わらない', 'test_file': '`tests/test_migration_runner.py`'},
    {'id': 'TC-DB-001-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'checksum改変', 'given': '適用済みmigration fileの内容を変更', 'when': 'checksum検証する', 'then': '起動停止相当errorとなる', 'test_file': '`tests/test_initial_schema.py`'},
    {'id': 'TC-DB-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'SQLite接続factory', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`connect_database(path: Path) -> sqlite3.Connection`を通じて「SQLite接続factory」を実行する', 'then': '「SQLite接続factory」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_database_connection.py`'},
    {'id': 'TC-DB-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'PRAGMA foreign_keys', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`connect_database(path: Path) -> sqlite3.Connection`を通じて「PRAGMA foreign_keys」を実行する', 'then': '「PRAGMA foreign_keys」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_migration_runner.py`'},
    {'id': 'TC-DB-001-06', 'priority': 'P1', 'layer': 'integration_mock', 'title': 'migration discovery/order', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`connect_database(path: Path) -> sqlite3.Connection`を通じて「migration discovery/order」を実行する', 'then': '入力の論理順を維持し、再実行しても同じ順序になる。順序重複・欠落は検出する。', 'test_file': '`tests/test_initial_schema.py`'},
    {'id': 'TC-DB-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '0001 initial schema', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`connect_database(path: Path) -> sqlite3.Connection`を通じて「0001 initial schema」を実行する', 'then': '「0001 initial schema」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_database_connection.py`'},
    {'id': 'TC-DB-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`connect_database(path: Path) -> sqlite3.Connection`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_migration_runner.py`'},
    {'id': 'TC-DB-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`connect_database(path: Path) -> sqlite3.Connection`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_initial_schema.py`'},
    {'id': 'TC-DB-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_database_connection.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/persistence/migrations.py)")

class MigrationRunner:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def apply_all(self, connection: Any, migrations_dir: Any, *, backup_path: Any = None) -> list[str]:
        """未適用migrationを順序どおり適用しchecksumを記録する。

        Public contract: ``MigrationRunner.apply_all(connection, migrations_dir, *, backup_path=None) -> list[str]``.
        """
        _step4_unimplemented('MigrationRunner.apply_all')
    def verify_applied_checksums(self, *args: Any, **kwargs: Any) -> None:
        """適用済みファイル改変を検出して停止する。

        Public contract: ``MigrationRunner.verify_applied_checksums(...) -> None``.
        """
        _step4_unimplemented('MigrationRunner.verify_applied_checksums')
