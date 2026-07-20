"""script/services/sources.py — 公開契約: SourceService.register/transition/list_for_project.

Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
Spec: docs/db/02-sources-table.md
"""

from __future__ import annotations

import dataclasses
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from script.core.errors import AppError, ErrorCode
from script.domain.enums import SourceStatus
from script.domain.models import Source
from script.persistence.files import copy_immutable
from script.persistence.paths import ProjectPaths
from script.persistence.repositories import SourceRepository
from script.persistence.unit_of_work import SqliteUnitOfWork
from script.schemas.source_metadata import SourceMetadata

_LEGAL_TRANSITIONS: dict[SourceStatus, set[SourceStatus]] = {
    SourceStatus.REGISTERED: {SourceStatus.PROCESSING, SourceStatus.FAILED},
    SourceStatus.PROCESSING: {SourceStatus.READY, SourceStatus.REVIEW_REQUIRED, SourceStatus.FAILED},
    SourceStatus.READY: set(),
    SourceStatus.REVIEW_REQUIRED: {SourceStatus.READY, SourceStatus.FAILED},
    SourceStatus.FAILED: {SourceStatus.REGISTERED},
}


@dataclass(frozen=True)
class RegisterSource:
    """Source登録の入力。"""

    project_id: str
    source_id: str
    source_path: Path
    destination_relative: str | None = None
    media_type: str | None = None


@dataclass(frozen=True)
class SourceRegistrationResult:
    """登録結果。同一hashの既存Sourceがある場合はduplicate_of経由で通知する。"""

    source: Source
    duplicate_of: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SourceService:
    """Source原本のimmutable登録・状態遷移・一覧を提供する。"""

    def __init__(self, data_root: Path, connection: sqlite3.Connection) -> None:
        if not data_root or connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root and connection are required")
        self._data_root = Path(data_root)
        self._connection = connection

    def register(self, command: RegisterSource) -> SourceRegistrationResult:
        """原本をimmutable copyしDBへ登録、重複hashはwarningとして返す。"""
        if command is None or not command.project_id or not command.source_id or not command.source_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id, source_id and source_path are required")

        paths = ProjectPaths.for_root(self._data_root, command.project_id)
        source_path = Path(command.source_path)
        destination_relative = command.destination_relative or f"sources/originals/{source_path.name}"

        metadata = SourceMetadata.from_file(
            source_path,
            project_paths=paths,
            destination_relative=destination_relative,
            media_type=command.media_type,
        )

        destination_path = paths.resolve_relative(destination_relative)
        copy_immutable(source_path, destination_path)

        now = _now_iso()
        source = Source(
            source_id=command.source_id,
            project_id=command.project_id,
            media_type=metadata.media_type,
            status=metadata.status,
            original_file_path=destination_relative,
            content_hash=metadata.content_hash,
            created_at=now,
            updated_at=now,
        )

        with SqliteUnitOfWork(self._connection) as uow:
            uow.sources.insert(source)

        duplicate_of = self._find_duplicate_hash(command.project_id, metadata.content_hash, command.source_id)
        return SourceRegistrationResult(source=source, duplicate_of=duplicate_of)

    def transition(self, source_id: str, target_status: SourceStatus) -> Source:
        """合法な状態遷移だけを許可する。"""
        if not source_id or target_status is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id and target_status are required")

        repository = SourceRepository(self._connection)
        current = repository.find(source_id)
        if current is None:
            raise AppError(ErrorCode.NOT_FOUND, f"source not found: {source_id}")

        allowed = _LEGAL_TRANSITIONS.get(current.status, set())
        if target_status not in allowed:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"illegal status transition: {current.status.value} -> {target_status.value}",
            )

        updated = dataclasses.replace(current, status=target_status, updated_at=_now_iso())
        repository.update(updated)
        self._connection.commit()
        return updated

    def list_for_project(self, project_id: str) -> list[Source]:
        """Project配下を登録順で返す。"""
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        rows = self._connection.execute(
            "SELECT * FROM sources WHERE project_id = ? ORDER BY rowid", (project_id,)
        ).fetchall()
        return [SourceRepository._to_model(row) for row in rows]

    def _find_duplicate_hash(self, project_id: str, content_hash: str, exclude_source_id: str) -> str | None:
        repository = SourceRepository(self._connection)
        for existing in repository.list_by_project(project_id):
            if existing.source_id != exclude_source_id and existing.content_hash == content_hash:
                return existing.source_id
        return None
