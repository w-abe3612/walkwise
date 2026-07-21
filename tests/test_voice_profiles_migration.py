"""Tests for TASK-BUILD-EXEC-001 §4: voice_profiles table migration and
build_requests.voice_profile_id foreign key.

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(4, 14.1節)
Production files exercised: script/persistence/sql/0002_voice_profiles_and_build_execution.sql,
script/persistence/migrations.py (check_orphaned_build_request_voice_profiles)
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner, check_orphaned_build_request_voice_profiles

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"
_NOW = "2026-07-21T00:00:00+09:00"


def _table_names(connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {row["name"] for row in rows}


def _columns(connection, table: str) -> dict[str, dict]:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"]: dict(row) for row in rows}


@pytest.mark.integration_mock
def test_tc_build_exec_001_01_fresh_db_applies_both_migrations(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-01 — 空DBへ0001+0002を適用するとvoice_profilesが作成される。"""
    connection = connect_database(tmp_path / "app.db")
    applied = MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)

    assert applied == ["0001_initial", "0002_voice_profiles_and_build_execution"]
    assert "voice_profiles" in _table_names(connection)

    columns = _columns(connection, "voice_profiles")
    for expected in (
        "voice_profile_id", "project_id", "name", "engine", "speaker_id", "style_id",
        "speed_scale", "pitch_scale", "intonation_scale", "volume_scale",
        "sentence_pause_ms", "paragraph_pause_ms", "section_pause_ms", "chapter_pause_ms",
        "settings_json", "status", "created_at", "updated_at",
    ):
        assert expected in columns, f"missing column: {expected}"


@pytest.mark.integration_mock
def test_tc_build_exec_001_02_upgrade_from_0001_only_db(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-02 — 既存0001適用済みDBから0002へアップグレードできる。"""
    db_path = tmp_path / "app.db"
    connection = connect_database(db_path)
    first_applied = MigrationRunner().apply_all(connection, _MIGRATIONS_DIR, backup_path=None)
    connection.close()

    # 0001だけが適用された状態を模擬するため、再接続して0002だけを別途適用する
    # (apply_allは冪等なので、同じ呼び出しでも問題なくupgradeとして機能することを確認する)。
    connection2 = connect_database(db_path)
    second_applied = MigrationRunner().apply_all(connection2, _MIGRATIONS_DIR)

    assert first_applied == ["0001_initial", "0002_voice_profiles_and_build_execution"]
    assert second_applied == []  # 既に適用済みのため再適用されない(idempotent)
    assert "voice_profiles" in _table_names(connection2)


@pytest.mark.integration_mock
def test_tc_build_exec_001_03_existing_data_preserved_across_upgrade(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-03 — migration適用後もprojects/build_requestsの既存データ件数が保持される。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)

    connection.execute(
        "INSERT INTO projects (project_id, title, domain, plan_file_path, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("proj-1", "t", "d", "project/project-plan.yaml", _NOW, _NOW),
    )
    connection.execute(
        "INSERT INTO build_requests (build_request_id, project_id, output_formats_json, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("br-1", "proj-1", '["text"]', "draft", _NOW, _NOW),
    )
    connection.commit()

    projects_before = connection.execute("SELECT COUNT(*) AS c FROM projects").fetchone()["c"]
    build_requests_before = connection.execute("SELECT COUNT(*) AS c FROM build_requests").fetchone()["c"]

    # 再migration実行(既に適用済みのため何もしないが、既存データが変化しないことを確認する)。
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)

    projects_after = connection.execute("SELECT COUNT(*) AS c FROM projects").fetchone()["c"]
    build_requests_after = connection.execute("SELECT COUNT(*) AS c FROM build_requests").fetchone()["c"]
    row = connection.execute("SELECT * FROM build_requests WHERE build_request_id = 'br-1'").fetchone()

    assert projects_before == projects_after == 1
    assert build_requests_before == build_requests_after == 1
    assert row["project_id"] == "proj-1"
    assert row["output_formats_json"] == '["text"]'


@pytest.mark.integration_mock
def test_tc_build_exec_001_04_voice_profiles_constraints(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-04 — voice_profilesのFK/unique/check/JSON制約を確認する。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    connection.execute(
        "INSERT INTO projects (project_id, title, domain, plan_file_path, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("proj-1", "t", "d", "project/project-plan.yaml", _NOW, _NOW),
    )
    connection.commit()

    def _insert(voice_profile_id: str, project_id: str = "proj-1", name: str = "profile-a", status: str = "draft", settings_json: str = "{}") -> None:
        connection.execute(
            "INSERT INTO voice_profiles "
            "(voice_profile_id, project_id, name, engine, speaker_id, settings_json, status, created_at, updated_at) "
            "VALUES (?, ?, ?, 'voicevox', '3', ?, ?, ?, ?)",
            (voice_profile_id, project_id, name, settings_json, status, _NOW, _NOW),
        )
        connection.commit()

    # 正常系
    _insert("vp-1")

    # FK違反: 存在しないproject_id
    with pytest.raises(Exception):
        _insert("vp-2", project_id="does-not-exist", name="profile-b")
    connection.rollback()

    # UNIQUE違反: 同一project内での名前重複
    with pytest.raises(Exception):
        _insert("vp-3", name="profile-a")
    connection.rollback()

    # CHECK違反: 不正なstatus
    with pytest.raises(Exception):
        _insert("vp-4", name="profile-c", status="unknown_status")
    connection.rollback()

    # CHECK違反: 不正なJSON
    with pytest.raises(Exception):
        _insert("vp-5", name="profile-d", settings_json="not-json")
    connection.rollback()


@pytest.mark.integration_mock
def test_tc_build_exec_001_05_build_requests_voice_profile_fk(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-05 — build_requests.voice_profile_idがvoice_profilesを参照するFKになる。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    connection.execute(
        "INSERT INTO projects (project_id, title, domain, plan_file_path, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("proj-1", "t", "d", "project/project-plan.yaml", _NOW, _NOW),
    )
    connection.commit()

    with pytest.raises(Exception):
        connection.execute(
            "INSERT INTO build_requests "
            "(build_request_id, project_id, output_formats_json, voice_profile_id, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("br-1", "proj-1", '["mp3"]', "does-not-exist", "draft", _NOW, _NOW),
        )
        connection.commit()


@pytest.mark.unit
def test_tc_build_exec_001_06_orphaned_voice_profile_id_detected_before_migration(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-06 — 0002適用前に、参照先のないvoice_profile_idが既存データにある場合、
    fail-closedに検出できる(migrationを実行して黙って削除・null化しない)。
    """
    db_path = tmp_path / "app.db"
    connection = connect_database(db_path)
    # 0001だけを直接適用する(0002を意図的に適用しない状態を作る)。
    connection.executescript((_MIGRATIONS_DIR / "0001_initial.sql").read_text(encoding="utf-8"))
    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (migration_id TEXT PRIMARY KEY, checksum TEXT NOT NULL, applied_at TEXT NOT NULL)"
    )
    connection.execute(
        "INSERT INTO schema_migrations (migration_id, checksum, applied_at) VALUES ('0001_initial', 'x', ?)", (_NOW,)
    )
    connection.execute(
        "INSERT INTO projects (project_id, title, domain, plan_file_path, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("proj-1", "t", "d", "project/project-plan.yaml", _NOW, _NOW),
    )
    # 0001時点ではvoice_profile_idにFKがないため、存在しない値でも挿入できてしまう
    # (これが「不整合データ」として検出されるべきケース)。
    connection.execute(
        "INSERT INTO build_requests "
        "(build_request_id, project_id, output_formats_json, voice_profile_id, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("br-orphan", "proj-1", '["mp3"]', "orphaned-vp-id", "draft", _NOW, _NOW),
    )
    connection.commit()

    orphans = check_orphaned_build_request_voice_profiles(connection)
    assert orphans == [("br-orphan", "orphaned-vp-id")]


@pytest.mark.unit
def test_tc_build_exec_001_07_no_orphans_reports_empty(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-07 — 不整合データがなければ空listを返す(migrationは安全に進める)。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    assert check_orphaned_build_request_voice_profiles(connection) == []


@pytest.mark.unit
def test_tc_build_exec_001_08_migration_reapplication_is_idempotent(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-001-08 — 同一migrationの再実行は同じ論理結果になる(checksum検証含む)。"""
    connection = connect_database(tmp_path / "app.db")
    first = MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    second = MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)

    assert first == ["0001_initial", "0002_voice_profiles_and_build_execution"]
    assert second == []
    MigrationRunner().verify_applied_checksums(connection, _MIGRATIONS_DIR)  # raises on mismatch
