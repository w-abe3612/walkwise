"""script/persistence/repositories.py — 公開契約: 5 Repository + map_integrity_error.

Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
Spec: docs/db/00-database-overview.md, docs/db/01〜05-*-table.md
"""

from __future__ import annotations

import json
import sqlite3

from script.core.errors import AppError, ErrorCode
from script.domain.enums import ArtifactType, BuildStatus, JobStatus, PlanningStage, SourceStatus
from script.domain.models import Artifact, BuildRequest, Job, Project, Source
from script.domain.validation import canonicalize_output_formats


def map_integrity_error(error: sqlite3.IntegrityError) -> AppError:
    """FK・unique・check違反を安定error codeへ変換する。"""
    message = str(error)
    if "FOREIGN KEY constraint failed" in message:
        return AppError(ErrorCode.VALIDATION_ERROR, "referenced record does not exist", technical_detail=message)
    if "UNIQUE constraint failed" in message:
        return AppError(ErrorCode.CONFLICT, "record already exists", technical_detail=message)
    if "CHECK constraint failed" in message:
        return AppError(ErrorCode.VALIDATION_ERROR, "value violates a database constraint", technical_detail=message)
    return AppError(ErrorCode.VALIDATION_ERROR, "database constraint violation", technical_detail=message)


def _require_connection(connection: sqlite3.Connection | None) -> sqlite3.Connection:
    if connection is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
    return connection


class ProjectRepository:
    """projectsテーブルの型付きrepository。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = _require_connection(connection)

    def insert(self, project: Project) -> None:
        try:
            self._connection.execute(
                "INSERT INTO projects "
                "(project_id, title, domain, planning_stage, content_revision, plan_file_path, "
                "created_at, updated_at, archived_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    project.project_id, project.title, project.domain, project.planning_stage.value,
                    project.content_revision, project.plan_file_path, project.created_at,
                    project.updated_at, project.archived_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def find(self, project_id: str) -> Project | None:
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        row = self._connection.execute(
            "SELECT * FROM projects WHERE project_id = ?", (project_id,)
        ).fetchone()
        return self._to_model(row) if row is not None else None

    def list_all(self) -> list[Project]:
        rows = self._connection.execute("SELECT * FROM projects ORDER BY project_id").fetchall()
        return [self._to_model(row) for row in rows]

    def update(self, project: Project) -> None:
        try:
            cursor = self._connection.execute(
                "UPDATE projects SET title=?, domain=?, planning_stage=?, content_revision=?, "
                "plan_file_path=?, updated_at=?, archived_at=? WHERE project_id=?",
                (
                    project.title, project.domain, project.planning_stage.value, project.content_revision,
                    project.plan_file_path, project.updated_at, project.archived_at, project.project_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc
        if cursor.rowcount == 0:
            raise AppError(ErrorCode.NOT_FOUND, f"project not found: {project.project_id}")

    @staticmethod
    def _to_model(row: sqlite3.Row) -> Project:
        return Project(
            project_id=row["project_id"],
            title=row["title"],
            domain=row["domain"],
            planning_stage=PlanningStage(row["planning_stage"]),
            content_revision=row["content_revision"],
            plan_file_path=row["plan_file_path"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            archived_at=row["archived_at"],
        )


class SourceRepository:
    """sourcesテーブルの型付きrepository。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = _require_connection(connection)

    def insert(self, source: Source) -> None:
        try:
            self._connection.execute(
                "INSERT INTO sources "
                "(source_id, project_id, media_type, status, original_file_path, content_hash, "
                "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    source.source_id, source.project_id, source.media_type, source.status.value,
                    source.original_file_path, source.content_hash, source.created_at, source.updated_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def find(self, source_id: str) -> Source | None:
        if not source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")
        row = self._connection.execute(
            "SELECT * FROM sources WHERE source_id = ?", (source_id,)
        ).fetchone()
        return self._to_model(row) if row is not None else None

    def list_by_project(self, project_id: str) -> list[Source]:
        rows = self._connection.execute(
            "SELECT * FROM sources WHERE project_id = ? ORDER BY source_id", (project_id,)
        ).fetchall()
        return [self._to_model(row) for row in rows]

    def update(self, source: Source) -> None:
        try:
            cursor = self._connection.execute(
                "UPDATE sources SET media_type=?, status=?, original_file_path=?, content_hash=?, "
                "updated_at=? WHERE source_id=?",
                (
                    source.media_type, source.status.value, source.original_file_path,
                    source.content_hash, source.updated_at, source.source_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc
        if cursor.rowcount == 0:
            raise AppError(ErrorCode.NOT_FOUND, f"source not found: {source.source_id}")

    @staticmethod
    def _to_model(row: sqlite3.Row) -> Source:
        return Source(
            source_id=row["source_id"],
            project_id=row["project_id"],
            media_type=row["media_type"],
            status=SourceStatus(row["status"]),
            original_file_path=row["original_file_path"],
            content_hash=row["content_hash"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class BuildRequestRepository:
    """build_requestsテーブルの型付きrepository。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = _require_connection(connection)

    def insert(self, build_request: BuildRequest) -> None:
        try:
            self._connection.execute(
                "INSERT INTO build_requests "
                "(build_request_id, project_id, output_formats_json, voice_profile_id, status, "
                "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    build_request.build_request_id, build_request.project_id,
                    _dump_output_formats(build_request.output_formats), build_request.voice_profile_id,
                    build_request.status.value, build_request.created_at, build_request.updated_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def find(self, build_request_id: str) -> BuildRequest | None:
        if not build_request_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "build_request_id is required")
        row = self._connection.execute(
            "SELECT * FROM build_requests WHERE build_request_id = ?", (build_request_id,)
        ).fetchone()
        return self._to_model(row) if row is not None else None

    def list_by_project(self, project_id: str) -> list[BuildRequest]:
        rows = self._connection.execute(
            "SELECT * FROM build_requests WHERE project_id = ? ORDER BY build_request_id", (project_id,)
        ).fetchall()
        return [self._to_model(row) for row in rows]

    def update(self, build_request: BuildRequest) -> None:
        try:
            cursor = self._connection.execute(
                "UPDATE build_requests SET output_formats_json=?, voice_profile_id=?, status=?, "
                "updated_at=? WHERE build_request_id=?",
                (
                    _dump_output_formats(build_request.output_formats), build_request.voice_profile_id,
                    build_request.status.value, build_request.updated_at, build_request.build_request_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc
        if cursor.rowcount == 0:
            raise AppError(ErrorCode.NOT_FOUND, f"build request not found: {build_request.build_request_id}")

    @staticmethod
    def _to_model(row: sqlite3.Row) -> BuildRequest:
        return BuildRequest(
            build_request_id=row["build_request_id"],
            project_id=row["project_id"],
            output_formats=_load_output_formats(row["output_formats_json"]),
            status=BuildStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            voice_profile_id=row["voice_profile_id"],
        )


class JobRepository:
    """jobsテーブルの型付きrepository。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = _require_connection(connection)

    def insert(self, job: Job) -> None:
        try:
            self._connection.execute(
                "INSERT INTO jobs "
                "(job_id, build_request_id, job_type, status, parent_job_id, progress_current, "
                "progress_total, last_message, started_at, finished_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    job.job_id, job.build_request_id, job.job_type, job.status.value, job.parent_job_id,
                    job.progress_current, job.progress_total, job.last_message, job.started_at,
                    job.finished_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def find(self, job_id: str) -> Job | None:
        if not job_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id is required")
        row = self._connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return self._to_model(row) if row is not None else None

    def list_by_build_request(self, build_request_id: str) -> list[Job]:
        rows = self._connection.execute(
            "SELECT * FROM jobs WHERE build_request_id = ? ORDER BY job_id", (build_request_id,)
        ).fetchall()
        return [self._to_model(row) for row in rows]

    def update(self, job: Job) -> None:
        try:
            cursor = self._connection.execute(
                "UPDATE jobs SET status=?, progress_current=?, progress_total=?, last_message=?, "
                "started_at=?, finished_at=? WHERE job_id=?",
                (
                    job.status.value, job.progress_current, job.progress_total, job.last_message,
                    job.started_at, job.finished_at, job.job_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc
        if cursor.rowcount == 0:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {job.job_id}")

    @staticmethod
    def _to_model(row: sqlite3.Row) -> Job:
        return Job(
            job_id=row["job_id"],
            build_request_id=row["build_request_id"],
            job_type=row["job_type"],
            status=JobStatus(row["status"]),
            parent_job_id=row["parent_job_id"],
            progress_current=row["progress_current"],
            progress_total=row["progress_total"],
            last_message=row["last_message"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
        )


class ArtifactRepository:
    """artifactsテーブルの型付きrepository。挿入専用(update不可)。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = _require_connection(connection)

    def insert(self, artifact: Artifact) -> None:
        try:
            self._connection.execute(
                "INSERT INTO artifacts "
                "(artifact_id, job_id, project_id, artifact_type, file_path, version_number, "
                "content_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    artifact.artifact_id, artifact.job_id, artifact.project_id,
                    artifact.artifact_type.value, artifact.file_path, artifact.version_number,
                    artifact.content_hash, artifact.created_at,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise map_integrity_error(exc) from exc

    def find(self, artifact_id: str) -> Artifact | None:
        if not artifact_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "artifact_id is required")
        row = self._connection.execute(
            "SELECT * FROM artifacts WHERE artifact_id = ?", (artifact_id,)
        ).fetchone()
        return self._to_model(row) if row is not None else None

    def list_by_project(self, project_id: str) -> list[Artifact]:
        rows = self._connection.execute(
            "SELECT * FROM artifacts WHERE project_id = ? ORDER BY artifact_type, version_number",
            (project_id,),
        ).fetchall()
        return [self._to_model(row) for row in rows]

    def update(self, artifact: Artifact) -> None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "artifact records are insert-only and cannot be updated")

    @staticmethod
    def _to_model(row: sqlite3.Row) -> Artifact:
        return Artifact(
            artifact_id=row["artifact_id"],
            job_id=row["job_id"],
            project_id=row["project_id"],
            artifact_type=ArtifactType(row["artifact_type"]),
            file_path=row["file_path"],
            version_number=row["version_number"],
            content_hash=row["content_hash"],
            created_at=row["created_at"],
        )


def _dump_output_formats(formats: tuple[str, ...]) -> str:
    return json.dumps(list(formats), separators=(",", ":"))


def _load_output_formats(value: str) -> tuple[str, ...]:
    return canonicalize_output_formats(tuple(json.loads(value)))
