"""Implementation for TASK-DB-001: SQLite接続・migration runner・初期schema (schema/discovery).

Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
Production files exercised: script/persistence/migrations.py, script/persistence/database.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


@pytest.mark.integration_mock
def test_tc_db_001_03(tmp_path: Path) -> None:
    """TC-DB-001-03 — checksum改変

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: integration_mock
    Given: 適用済みmigration fileの内容を変更
    When: checksum検証する
    Then: 起動停止相当errorとなる
    """
    working_migrations_dir = tmp_path / "sql"
    working_migrations_dir.mkdir()
    original = (_MIGRATIONS_DIR / "0001_initial.sql").read_text(encoding="utf-8")
    migration_copy = working_migrations_dir / "0001_initial.sql"
    migration_copy.write_text(original, encoding="utf-8")

    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()
    runner.apply_all(connection, working_migrations_dir)

    migration_copy.write_text(original + "\n-- tampered after being applied\n", encoding="utf-8")

    with pytest.raises(AppError):
        runner.verify_applied_checksums(connection, working_migrations_dir)

    with pytest.raises(AppError):
        runner.apply_all(connection, working_migrations_dir)


@pytest.mark.integration_mock
def test_tc_db_001_06(tmp_path: Path) -> None:
    """TC-DB-001-06 — migration discovery/order

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「migration discovery/order」を実行する
    Then: 入力の論理順を維持し、再実行しても同じ順序になる。順序重複・欠落は検出する。
    """
    working_migrations_dir = tmp_path / "sql"
    working_migrations_dir.mkdir()
    (working_migrations_dir / "0001_initial.sql").write_text(
        (_MIGRATIONS_DIR / "0001_initial.sql").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (working_migrations_dir / "0002_add_note.sql").write_text(
        "CREATE TABLE IF NOT EXISTS notes (note_id TEXT PRIMARY KEY, body TEXT NOT NULL);\n",
        encoding="utf-8",
    )

    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()

    first_run = runner.apply_all(connection, working_migrations_dir)
    assert first_run == ["0001_initial", "0002_add_note"]

    second_connection = connect_database(tmp_path / "app2.db")
    second_runner = MigrationRunner()
    second_run = second_runner.apply_all(second_connection, working_migrations_dir)
    assert second_run == first_run

    (working_migrations_dir / "0002_duplicate.sql").write_text(
        "CREATE TABLE IF NOT EXISTS notes2 (note_id TEXT PRIMARY KEY);\n", encoding="utf-8"
    )
    third_connection = connect_database(tmp_path / "app3.db")
    third_runner = MigrationRunner()
    with pytest.raises(AppError):
        third_runner.apply_all(third_connection, working_migrations_dir)


@pytest.mark.unit
def test_tc_db_001_09(tmp_path: Path) -> None:
    """TC-DB-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `connect_database(path: Path) -> sqlite3.Connection`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    connection_first = connect_database(tmp_path / "app.db")
    fk_first = connection_first.execute("PRAGMA foreign_keys").fetchone()[0]
    connection_first.close()

    connection_second = connect_database(tmp_path / "app.db")
    fk_second = connection_second.execute("PRAGMA foreign_keys").fetchone()[0]
    connection_second.close()

    assert fk_first == fk_second == 1
