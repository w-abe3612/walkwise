"""script/persistence/migrations.py — 公開契約: MigrationRunner.apply_all/verify_applied_checksums,
check_orphaned_build_request_voice_profiles.

Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
Spec: docs/db/00-database-overview.md (5.5節), docs/db/90-schema-migrations-table.md,
      docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(4.3節)
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from script.core.errors import AppError, ErrorCode

_FILENAME_PATTERN = re.compile(r"^(\d{4})_.*\.sql$")

_SCHEMA_MIGRATIONS_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_id TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL
)
"""


def _discover_migrations(migrations_dir: Path) -> list[Path]:
    migrations_dir = Path(migrations_dir)
    files = sorted(migrations_dir.glob("*.sql"))
    seen: dict[str, Path] = {}
    for file in files:
        match = _FILENAME_PATTERN.match(file.name)
        if not match:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid migration filename: {file.name}")
        order = match.group(1)
        if order in seen:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"duplicate migration order {order}: {seen[order].name} and {file.name}",
            )
        seen[order] = file
    return files


def _database_file_path(connection: sqlite3.Connection) -> Path | None:
    row = connection.execute("PRAGMA database_list").fetchone()
    if row is None:
        return None
    file_value = row["file"] if isinstance(row, sqlite3.Row) else row[2]
    return Path(file_value) if file_value else None


class MigrationRunner:
    """SQLite migrationの発見・適用・checksum検証を行う。"""

    def verify_applied_checksums(self, connection: sqlite3.Connection, migrations_dir: Path) -> None:
        """適用済みファイル改変を検出して停止する。"""
        if connection is None or migrations_dir is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection and migrations_dir are required")

        connection.execute(_SCHEMA_MIGRATIONS_DDL)
        applied = {
            row["migration_id"]: row["checksum"]
            for row in connection.execute("SELECT migration_id, checksum FROM schema_migrations")
        }
        for file in _discover_migrations(migrations_dir):
            migration_id = file.stem
            if migration_id not in applied:
                continue
            current_checksum = hashlib.sha256(file.read_bytes()).hexdigest()
            if current_checksum != applied[migration_id]:
                raise AppError(
                    ErrorCode.CONFLICT,
                    f"migration file has been modified after being applied: {migration_id}",
                )

    def apply_all(
        self,
        connection: sqlite3.Connection,
        migrations_dir: Path,
        *,
        backup_path: Path | None = None,
    ) -> list[str]:
        """未適用migrationを順序どおり適用しchecksumを記録する。"""
        if connection is None or migrations_dir is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection and migrations_dir are required")

        connection.execute(_SCHEMA_MIGRATIONS_DDL)
        connection.commit()

        self.verify_applied_checksums(connection, migrations_dir)

        applied_ids = {
            row["migration_id"] for row in connection.execute("SELECT migration_id FROM schema_migrations")
        }
        pending = [file for file in _discover_migrations(migrations_dir) if file.stem not in applied_ids]

        if pending and backup_path is not None:
            db_path = _database_file_path(connection)
            if db_path is not None and db_path.exists():
                Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(db_path, backup_path)

        newly_applied: list[str] = []
        for file in pending:
            script = file.read_text(encoding="utf-8")
            checksum = hashlib.sha256(file.read_bytes()).hexdigest()
            try:
                connection.executescript(script)
                connection.execute(
                    "INSERT INTO schema_migrations (migration_id, checksum, applied_at) VALUES (?, ?, ?)",
                    (file.stem, checksum, datetime.now(timezone.utc).isoformat()),
                )
                connection.commit()
            except sqlite3.DatabaseError as exc:
                connection.rollback()
                raise AppError(
                    ErrorCode.INTERNAL_ERROR,
                    f"failed to apply migration {file.stem}",
                    technical_detail=str(exc),
                ) from exc
            newly_applied.append(file.stem)

        return newly_applied


def check_orphaned_build_request_voice_profiles(connection: sqlite3.Connection) -> list[tuple[str, str]]:
    """TASK-BUILD-EXEC-001 4.3節: `0002_voice_profiles_and_build_execution`適用前に、
    既存`build_requests.voice_profile_id`のうち`voice_profiles`テーブルに参照先が
    ないもの(黙って削除・null化してはならない不整合データ)を検出する。

    `voice_profiles`テーブルがまだ存在しない場合(0002適用前の通常の状態)、
    `build_requests`に非NULLの`voice_profile_id`を持つ行があれば、それはすべて
    参照先不在として扱う(このmigration以前は`voice_profile_id`を検証する仕組みが
    一切なかったため)。戻り値は空なら安全、非空なら
    `[(build_request_id, voice_profile_id), ...]`を安全な情報(build_request_id/
    voice_profile_idのみ、他の秘密値は含まない)として返す。呼び出し側が
    このリストが空であることを確認してからmigrationを適用すること。
    """
    if connection is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")

    tables = {
        row["name"] if isinstance(row, sqlite3.Row) else row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if "build_requests" not in tables:
        return []  # build_requestsテーブル自体が存在しない(初回起動前)場合は対象外。

    if "voice_profiles" not in tables:
        rows = connection.execute(
            "SELECT build_request_id, voice_profile_id FROM build_requests WHERE voice_profile_id IS NOT NULL"
        ).fetchall()
    else:
        rows = connection.execute(
            "SELECT br.build_request_id, br.voice_profile_id FROM build_requests br "
            "WHERE br.voice_profile_id IS NOT NULL "
            "AND br.voice_profile_id NOT IN (SELECT voice_profile_id FROM voice_profiles)"
        ).fetchall()

    return [
        (
            row["build_request_id"] if isinstance(row, sqlite3.Row) else row[0],
            row["voice_profile_id"] if isinstance(row, sqlite3.Row) else row[1],
        )
        for row in rows
    ]
