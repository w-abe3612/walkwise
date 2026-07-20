"""Implementation for TASK-DB-001: SQLite接続・migration runner・初期schema (connection).

Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
Production files exercised: script/persistence/database.py, script/persistence/migrations.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


@pytest.mark.integration_mock
def test_tc_db_001_01(tmp_path: Path) -> None:
    """TC-DB-001-01 — 初期schema

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: integration_mock
    Given: 空SQLite DB
    When: 全migrationを適用する
    Then: 6テーブル・FK・index・checkが作成される
    """
    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()

    applied = runner.apply_all(connection, _MIGRATIONS_DIR)
    assert applied == ["0001_initial"]

    tables = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert tables == {
        "schema_migrations", "projects", "sources", "build_requests", "jobs", "artifacts",
    }

    indexes = {
        row["name"]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='index'")
    }
    assert "idx_sources_project_id" in indexes
    assert "idx_artifacts_project_id" in indexes

    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO sources "
            "(source_id, project_id, media_type, status, original_file_path, content_hash, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "src-1", "does-not-exist", "text", "registered",
                "sources/originals/src-1.txt", "sha256:x",
                "2026-07-19T00:00:00+00:00", "2026-07-19T00:00:00+00:00",
            ),
        )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO projects "
            "(project_id, title, domain, planning_stage, content_revision, plan_file_path, created_at, updated_at) "
            "VALUES (?, ?, 'database', 'not-a-real-stage', 1, 'project/project-plan.yaml', ?, ?)",
            ("db-foundations", "タイトル", "2026-07-19T00:00:00+00:00", "2026-07-19T00:00:00+00:00"),
        )


@pytest.mark.unit
def test_tc_db_001_04(tmp_path: Path) -> None:
    """TC-DB-001-04 — SQLite接続factory

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「SQLite接続factory」を実行する
    Then: 「SQLite接続factory」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    db_path = tmp_path / "nested" / "app.db"
    connection = connect_database(db_path)

    assert isinstance(connection, sqlite3.Connection)
    assert db_path.is_file()
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    connection.execute("CREATE TABLE t (id TEXT PRIMARY KEY)")
    connection.execute("INSERT INTO t (id) VALUES ('a')")
    row = connection.execute("SELECT id FROM t").fetchone()
    assert row["id"] == "a"  # row_factory must support name-based access


@pytest.mark.unit
def test_tc_db_001_07(tmp_path: Path) -> None:
    """TC-DB-001-07 — 0001 initial schema

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「0001 initial schema」を実行する
    Then: 「0001 initial schema」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()
    runner.apply_all(connection, _MIGRATIONS_DIR)

    now = "2026-07-19T21:00:00+09:00"
    connection.execute(
        "INSERT INTO projects "
        "(project_id, title, domain, planning_stage, content_revision, plan_file_path, created_at, updated_at) "
        "VALUES (?, ?, 'database', 'registered', 1, 'project/project-plan.yaml', ?, ?)",
        ("database-foundations", "データベース基礎", now, now),
    )
    connection.execute(
        "INSERT INTO build_requests "
        "(build_request_id, project_id, output_formats_json, voice_profile_id, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 'draft', ?, ?)",
        ("br-0001", "database-foundations", '["mp3","text"]', "sample-voicevox-profile", now, now),
    )
    connection.commit()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO build_requests "
            "(build_request_id, project_id, output_formats_json, voice_profile_id, status, created_at, updated_at) "
            "VALUES (?, ?, ?, NULL, 'draft', ?, ?)",
            ("br-0002", "database-foundations", '["mp3"]', now, now),
        )


@pytest.mark.unit
def test_tc_db_001_10(tmp_path: Path) -> None:
    """TC-DB-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    migration_file = _MIGRATIONS_DIR / "0001_initial.sql"
    content_before = migration_file.read_bytes()

    connection = connect_database(tmp_path / "app.db")
    runner = MigrationRunner()
    runner.apply_all(connection, _MIGRATIONS_DIR)

    with pytest.raises(AppError):
        connect_database(None)  # type: ignore[arg-type]

    assert migration_file.read_bytes() == content_before
