"""script/persistence/unit_of_work.py — 公開契約: SqliteUnitOfWork.

Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
Spec: docs/db/00-database-overview.md (5.12節 transaction境界)
"""

from __future__ import annotations

import sqlite3
from types import TracebackType

from script.core.errors import AppError, ErrorCode
from script.persistence.repositories import (
    ArtifactRepository,
    BuildRequestRepository,
    JobRepository,
    ProjectRepository,
    SourceRepository,
    VoiceProfileRepository,
    map_integrity_error,
)


class SqliteUnitOfWork:
    """context managerでcommit/rollbackし各Repositoryを共有接続へ束ねる。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        if connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
        self.connection = connection
        self.projects = ProjectRepository(connection)
        self.sources = SourceRepository(connection)
        self.build_requests = BuildRequestRepository(connection)
        self.jobs = JobRepository(connection)
        self.artifacts = ArtifactRepository(connection)
        # TASK-BUILD-EXEC-001: 既存transaction境界(5.12節)を壊さない、後方互換な追加。
        self.voice_profiles = VoiceProfileRepository(connection)

    def __enter__(self) -> "SqliteUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            try:
                self.connection.commit()
            except sqlite3.IntegrityError as integrity_error:
                self.connection.rollback()
                raise map_integrity_error(integrity_error) from integrity_error
        else:
            self.connection.rollback()
        return False

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()
