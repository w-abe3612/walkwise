"""script/services/build_requests.py — 公開契約: BuildRequestService.create, serialize_output_formats.

Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
Spec: docs/db/03-build-requests-table.md
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from script.core.errors import AppError, ErrorCode
from script.domain.enums import BuildStatus
from script.domain.models import BuildRequest
from script.domain.validation import canonicalize_output_formats, validate_build_request
from script.persistence.repositories import ProjectRepository
from script.persistence.unit_of_work import SqliteUnitOfWork


@dataclass(frozen=True)
class CreateBuildRequest:
    """Build Request作成の入力。"""

    build_request_id: str
    project_id: str
    output_formats: Sequence[str]
    voice_profile_id: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialize_output_formats(values: Sequence[str]) -> str:
    """`["mp3","text"]`等の空白なしJSONへ変換する。"""
    canonical = canonicalize_output_formats(values)
    return json.dumps(list(canonical), separators=(",", ":"))


class BuildRequestService:
    """MP3/textの複数選択、canonical JSON、voice必須条件を検証しBuild Requestを保存する。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        if connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
        self._connection = connection

    def create(self, command: CreateBuildRequest) -> BuildRequest:
        """形式をcanonical JSON化しdraftとして保存する。"""
        if command is None or not command.build_request_id or not command.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "build_request_id and project_id are required")

        canonical_formats = canonicalize_output_formats(command.output_formats)
        validate_build_request(canonical_formats, command.voice_profile_id)

        if ProjectRepository(self._connection).find(command.project_id) is None:
            raise AppError(ErrorCode.NOT_FOUND, f"project not found: {command.project_id}")

        now = _now_iso()
        build_request = BuildRequest(
            build_request_id=command.build_request_id,
            project_id=command.project_id,
            output_formats=canonical_formats,
            status=BuildStatus.DRAFT,
            created_at=now,
            updated_at=now,
            voice_profile_id=command.voice_profile_id,
        )

        with SqliteUnitOfWork(self._connection) as uow:
            uow.build_requests.insert(build_request)

        return build_request
