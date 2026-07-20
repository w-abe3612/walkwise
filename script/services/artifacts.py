"""script/services/artifacts.py — 公開契約: ArtifactService.register/list_latest/list_versions.

Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
Spec: docs/db/05-artifacts-table.md
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from script.core.errors import AppError, ErrorCode
from script.domain.enums import ArtifactType
from script.domain.models import Artifact
from script.persistence.files import copy_immutable
from script.persistence.paths import ProjectPaths
from script.persistence.repositories import (
    ArtifactRepository,
    BuildRequestRepository,
    JobRepository,
    ProjectRepository,
)


@dataclass(frozen=True)
class RegisterArtifact:
    """Artifact登録の入力。"""

    artifact_id: str
    job_id: str
    project_id: str
    artifact_type: ArtifactType
    source_path: Path
    destination_relative: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ArtifactService:
    """生成済みファイルを追記専用Artifactとして登録し、version系列と一覧取得を提供する。"""

    def __init__(self, data_root: Path, connection: sqlite3.Connection) -> None:
        if not data_root or connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root and connection are required")
        self._data_root = Path(data_root)
        self._connection = connection

    def register(self, command: RegisterArtifact) -> Artifact:
        """ファイル存在・hash・Job/Project整合を確認し次versionで追記する。"""
        if (
            command is None
            or not command.artifact_id
            or not command.job_id
            or not command.project_id
            or not command.source_path
            or not command.destination_relative
        ):
            raise AppError(ErrorCode.VALIDATION_ERROR, "artifact_id, job_id, project_id, source_path and destination_relative are required")

        source_path = Path(command.source_path)
        if not source_path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"artifact source file does not exist: {source_path}")

        job = JobRepository(self._connection).find(command.job_id)
        if job is None:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {command.job_id}")

        project = ProjectRepository(self._connection).find(command.project_id)
        if project is None:
            raise AppError(ErrorCode.NOT_FOUND, f"project not found: {command.project_id}")

        build_request = BuildRequestRepository(self._connection).find(job.build_request_id)
        if build_request is None or build_request.project_id != command.project_id:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"job {command.job_id} does not belong to project {command.project_id}",
            )

        paths = ProjectPaths.for_root(self._data_root, command.project_id)
        destination_path = paths.resolve_relative(command.destination_relative)
        if destination_path.exists():
            raise AppError(
                ErrorCode.CONFLICT,
                f"artifact destination already exists (artifacts are append-only): {command.destination_relative}",
            )

        version_number = self._next_version(command.project_id, command.artifact_type)
        digest = copy_immutable(source_path, destination_path)

        artifact = Artifact(
            artifact_id=command.artifact_id,
            job_id=command.job_id,
            project_id=command.project_id,
            artifact_type=command.artifact_type,
            file_path=command.destination_relative,
            version_number=version_number,
            content_hash=digest.value,
            created_at=_now_iso(),
        )

        ArtifactRepository(self._connection).insert(artifact)
        self._connection.commit()
        return artifact

    def list_latest(self, project_id: str) -> list[Artifact]:
        """artifact typeごとの最新versionを返す。"""
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")

        all_versions = ArtifactRepository(self._connection).list_by_project(project_id)
        latest_by_type: dict[str, Artifact] = {}
        for artifact in all_versions:
            key = artifact.artifact_type.value
            existing = latest_by_type.get(key)
            if existing is None or artifact.version_number > existing.version_number:
                latest_by_type[key] = artifact
        return [latest_by_type[key] for key in sorted(latest_by_type)]

    def list_versions(self, project_id: str, artifact_type: ArtifactType) -> list[Artifact]:
        """全versionを降順で返す。"""
        if not project_id or artifact_type is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id and artifact_type are required")

        matching = [
            artifact
            for artifact in ArtifactRepository(self._connection).list_by_project(project_id)
            if artifact.artifact_type == artifact_type
        ]
        return sorted(matching, key=lambda artifact: artifact.version_number, reverse=True)

    def _next_version(self, project_id: str, artifact_type: ArtifactType) -> int:
        existing = self.list_versions(project_id, artifact_type)
        return (existing[0].version_number + 1) if existing else 1
