"""Implementation for TASK-DB-001: SQLite接続・migration runner・初期schema (migration runner).

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
def test_tc_db_001_02(tmp_path: Path) -> None:
    """TC-DB-001-02 — 冪等適用

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: integration_mock
    Given: 適用済みDB
    When: apply_allを再実行する
    Then: 新規適用0件でschemaと履歴が変わらない
    """
    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()

    first_run = runner.apply_all(connection, _MIGRATIONS_DIR)
    # TASK-BUILD-EXEC-001で0002_voice_profiles_and_build_executionを追加したため、
    # 空DBへは0001に続けて0002も適用される。
    assert first_run == ["0001_initial", "0002_voice_profiles_and_build_execution"]

    history_before = list(
        connection.execute("SELECT migration_id, checksum, applied_at FROM schema_migrations")
    )

    second_run = runner.apply_all(connection, _MIGRATIONS_DIR)
    assert second_run == []

    history_after = list(
        connection.execute("SELECT migration_id, checksum, applied_at FROM schema_migrations")
    )
    assert [dict(row) for row in history_before] == [dict(row) for row in history_after]


@pytest.mark.unit
def test_tc_db_001_05(tmp_path: Path) -> None:
    """TC-DB-001-05 — PRAGMA foreign_keys

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「PRAGMA foreign_keys」を実行する
    Then: 「PRAGMA foreign_keys」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    connection_a = connect_database(tmp_path / "a.db")
    connection_b = connect_database(tmp_path / "b.db")
    assert connection_a.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert connection_b.execute("PRAGMA foreign_keys").fetchone()[0] == 1


@pytest.mark.unit
def test_tc_db_001_08(tmp_path: Path) -> None:
    """TC-DB-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `connect_database(path: Path) -> sqlite3.Connection`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    existing_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError):
        connect_database(None)  # type: ignore[arg-type]

    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()
    with pytest.raises(AppError):
        runner.apply_all(connection, None)  # type: ignore[arg-type]

    remaining = [p for p in sorted(tmp_path.iterdir()) if p.name != "app.db"]
    assert remaining == existing_before
