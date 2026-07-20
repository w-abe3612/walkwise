"""script/persistence/database.py — 公開契約: connect_database(path) -> sqlite3.Connection.

Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
Spec: docs/db/00-database-overview.md (5.4節 foreign key有効化)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from script.core.errors import AppError, ErrorCode


def connect_database(path: Path) -> sqlite3.Connection:
    """接続直後にforeign_keysを有効化しrow factoryを設定する。"""
    if not path:
        raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")

    path = Path(path)
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
