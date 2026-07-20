"""script/worker/commands.py — 公開契約: build_default_registry(data_root, connection) -> HandlerRegistry.

TASK-WORKER-001の`HandlerRegistry`は単体では空(job_typeが1件も登録されて
いない)ため、`python -m script.worker.cli`をsubprocessとして起動しても
`health`すら`unknown_job_type`で拒否されていた(TASK-REVIEW-001監査 2.2節)。

本moduleは、Electron main(`electron/main/ipc/*.ts`)が必要とするIPC操作を、
既存の承認済みservice(TASK-PROJECT-001, TASK-SOURCE-001, TASK-APPROVAL-001,
TASK-BUILD-001, TASK-JOB-001, TASK-ARTIFACT-001)へ委譲するhandlerとして接続
するだけであり、新しい業務ロジックは一切追加しない。

Contract: docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md(3.3, 4節)
Spec: docs/specifications/21-electron-python-worker-interface.md
"""

from __future__ import annotations

import dataclasses
import sqlite3
import uuid
from collections.abc import Callable, Iterator
from enum import Enum
from pathlib import Path
from typing import Any

import script.persistence as _persistence_pkg
from script.core.errors import AppError, ErrorCode
from script.domain.enums import SourceStatus
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ArtifactRepository, BuildRequestRepository, JobRepository
from script.schemas.approvals import ApprovalGate, ApprovalStatus
from script.services.approvals import ApprovalService
from script.services.artifacts import ArtifactService
from script.services.build_requests import BuildRequestService, CreateBuildRequest
from script.services.jobs import JobService
from script.services.projects import CreateProject, ProjectService
from script.services.sources import RegisterSource, SourceService
from script.tts_clients.base import TTSClientError
from script.tts_clients.voicevox.client import VoicevoxHttpClient
from script.worker.handlers import HandlerRegistry
from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest

MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"

Log = Callable[[str], None]
Handler = Callable[[WorkerRequest, Log], Iterator[WorkerEvent]]

_REQUIRED_APPROVAL_GATES_FOR_BUILD = (ApprovalGate.VERIFIED_SCRIPT, ApprovalGate.PREVIEW_AUDIO)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _serialize(value: Any) -> Any:
    """dataclass/Enumを、JSON Linesへそのまま載せられる素の値へ変換する。"""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _serialize(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def _param(request: WorkerRequest, name: str, *, required: bool = True) -> Any:
    value = request.parameters.get(name)
    if required and (value is None or (isinstance(value, str) and not value.strip())):
        raise WorkerError("invalid_request", f"parameter {name} is required")
    return value


def _wrap_app_error(exc: AppError) -> WorkerError:
    return WorkerError(exc.code.value, exc.message)


def _approval_gate_satisfied_for_build(
    approval_service: ApprovalService,
    build_request_repository_find: Callable[[str], Any],
    build_request_id: str,
) -> bool:
    """07-approval-workflow.mdに基づき、build開始前に必須gateがapproved済みかを
    確認する(fail-closed: build_request/projectが見つからなければFalse)。
    """
    build_request = build_request_repository_find(build_request_id)
    if build_request is None:
        return False
    try:
        bundle = approval_service.get_bundle(build_request.project_id)
    except AppError:
        return False
    return all(
        bundle.approvals[gate].status is ApprovalStatus.APPROVED for gate in _REQUIRED_APPROVAL_GATES_FOR_BUILD
    )


def build_default_registry(data_root: Path, connection: sqlite3.Connection) -> HandlerRegistry:
    """Electron mainが必要とするIPC操作すべてを処理できるregistryを返す。

    `data_root`と`connection`はWorker起動時に一度だけ確立し、以降のrequestは
    すべて同じconnection上で処理する(TASK-DESKTOP-002のWorkerManagerは単一の
    常駐subprocessとして1connectionを再利用する設計と一致する)。
    """
    if not data_root:
        raise AppError(ErrorCode.VALIDATION_ERROR, "data_root is required")
    if connection is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")

    data_root = Path(data_root)
    registry = HandlerRegistry()

    project_service = ProjectService(data_root, connection)
    source_service = SourceService(data_root, connection)
    approval_service = ApprovalService(data_root)
    build_request_service = BuildRequestService(connection)
    job_repository = JobRepository(connection)
    build_request_repository = BuildRequestRepository(connection)
    artifact_repository = ArtifactRepository(connection)

    def _approval_gate_check(build_request_id: str) -> bool:
        return _approval_gate_satisfied_for_build(approval_service, build_request_repository.find, build_request_id)

    job_service = JobService(connection, approval_gate_check=_approval_gate_check)
    artifact_service = ArtifactService(data_root, connection)

    def health(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        log("health check requested")
        return {"status": "ok"}
        yield  # pragma: no cover - unreachable, keeps this a generator function

    def db_migrate(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        try:
            applied = MigrationRunner().apply_all(connection, MIGRATIONS_DIR)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        log(f"migrations applied: {applied}")
        return {"applied": applied}
        yield  # pragma: no cover

    def job_recover_stale(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        recovered = job_service.recover_stale()
        return {"recovered_job_ids": [job.job_id for job in recovered]}
        yield  # pragma: no cover

    def project_list(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        try:
            projects = project_service.list_active()
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"projects": [_serialize(project) for project in projects]}
        yield  # pragma: no cover

    def project_get(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        try:
            project = project_service.get(project_id)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"project": _serialize(project)}
        yield  # pragma: no cover

    def project_create(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        command = CreateProject(
            project_id=_param(request, "project_id"),
            title=_param(request, "title"),
            domain=_param(request, "domain"),
            purpose=_param(request, "purpose"),
            usage_purpose=_param(request, "usage_purpose", required=False) or "personal_learning",
        )
        try:
            project = project_service.create(command)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        log(f"project created: {project.project_id}")
        return {"project": _serialize(project)}
        yield  # pragma: no cover

    def source_register(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        command = RegisterSource(
            project_id=_param(request, "project_id"),
            source_id=_param(request, "source_id", required=False) or _new_id("source"),
            source_path=Path(_param(request, "source_path")),
            media_type=_param(request, "media_type", required=False),
        )
        try:
            result = source_service.register(command)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        log(f"source registered: {result.source.source_id}")
        return {"source": _serialize(result.source), "duplicate_of": result.duplicate_of}
        yield  # pragma: no cover

    def source_list(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        try:
            sources = source_service.list_for_project(project_id)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"sources": [_serialize(source) for source in sources]}
        yield  # pragma: no cover

    def source_retry(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        source_id = _param(request, "source_id")
        try:
            source = source_service.transition(source_id, SourceStatus.REGISTERED)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"source": _serialize(source)}
        yield  # pragma: no cover

    def approval_list(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        try:
            bundle = approval_service.get_bundle(project_id)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        approvals = [
            {"gate": gate.value, "status": record.status.value, "comment": record.comment}
            for gate, record in bundle.approvals.items()
        ]
        return {"approvals": approvals}
        yield  # pragma: no cover

    def approval_approve(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        gate = _param(request, "gate")
        approved_by = _param(request, "approved_by")
        try:
            record = approval_service.approve(project_id, gate, approved_by=approved_by)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"gate": record.gate.value, "status": record.status.value, "comment": record.comment}
        yield  # pragma: no cover

    def approval_request_changes(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        gate = _param(request, "gate")
        reason = _param(request, "reason")
        try:
            record = approval_service.request_changes(project_id, gate, reason=reason)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"gate": record.gate.value, "status": record.status.value, "comment": record.comment}
        yield  # pragma: no cover

    def build_request_create(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        command = CreateBuildRequest(
            build_request_id=_param(request, "build_request_id", required=False) or _new_id("build-request"),
            project_id=_param(request, "project_id"),
            output_formats=_param(request, "output_formats"),
            voice_profile_id=_param(request, "voice_profile_id", required=False),
        )
        try:
            build_request = build_request_service.create(command)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"build_request": _serialize(build_request)}
        yield  # pragma: no cover

    def build_request_approval_gate_satisfied(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        build_request_id = _param(request, "build_request_id")
        satisfied = _approval_gate_check(build_request_id)
        return {"satisfied": satisfied}
        yield  # pragma: no cover

    def job_start(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        build_request_id = _param(request, "build_request_id")
        job_id = _param(request, "job_id", required=False) or _new_id("job")
        try:
            job_service.enqueue(job_id, build_request_id, job_type="build")
            started = job_service.start_next()
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        log(f"job enqueued: {job_id}")
        result_job = started if started is not None and started.job_id == job_id else job_repository.find(job_id)
        return {"job": _serialize(result_job)}
        yield  # pragma: no cover

    def job_get(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        job_id = _param(request, "job_id")
        job = job_repository.find(job_id)
        if job is None:
            raise WorkerError("not_found", f"job not found: {job_id}")
        return {"job": _serialize(job)}
        yield  # pragma: no cover

    def job_list(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        rows = connection.execute(
            "SELECT j.* FROM jobs j "
            "JOIN build_requests br ON j.build_request_id = br.build_request_id "
            "WHERE br.project_id = ? ORDER BY j.job_id",
            (project_id,),
        ).fetchall()
        jobs = [JobRepository._to_model(row) for row in rows]
        return {"jobs": [_serialize(job) for job in jobs]}
        yield  # pragma: no cover

    def job_cancel(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        job_id = _param(request, "job_id")
        try:
            job = job_service.request_cancel(job_id)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"job": _serialize(job)}
        yield  # pragma: no cover

    def job_retry(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        parent_job_id = _param(request, "parent_job_id")
        new_job_id = _param(request, "new_job_id", required=False) or _new_id("job")
        try:
            job = job_service.retry(parent_job_id, new_job_id=new_job_id)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"job": _serialize(job)}
        yield  # pragma: no cover

    def artifact_list(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        project_id = _param(request, "project_id")
        try:
            artifacts = artifact_service.list_latest(project_id)
        except AppError as exc:
            raise _wrap_app_error(exc) from exc
        return {"artifacts": [_serialize(artifact) for artifact in artifacts]}
        yield  # pragma: no cover

    def artifact_get(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        artifact_id = _param(request, "artifact_id")
        artifact = artifact_repository.find(artifact_id)
        if artifact is None:
            raise WorkerError("not_found", f"artifact not found: {artifact_id}")
        return {"artifact": _serialize(artifact)}
        yield  # pragma: no cover

    def voice_list_engines(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        client = VoicevoxHttpClient()
        connectivity = client.check_connectivity()
        health = {"engine": "voicevox", "available": connectivity.available, "detail": connectivity.detail or None}
        speakers: list[dict[str, Any]] = []
        if connectivity.available:
            try:
                speakers = [
                    {"speakerId": speaker.speaker_id, "displayName": speaker.display_name, "styleIds": list(speaker.style_ids)}
                    for speaker in client.list_speakers()
                ]
            except TTSClientError as exc:
                health = {"engine": "voicevox", "available": False, "detail": str(exc)}
        return {"health": health, "speakers": speakers}
        yield  # pragma: no cover

    def voice_preview(request: WorkerRequest, log: Log) -> Iterator[WorkerEvent]:
        speaker_id = _param(request, "speaker_id")
        text = _param(request, "text")
        speed_scale = request.parameters.get("speed_scale")
        client = VoicevoxHttpClient()
        try:
            query = client.create_audio_query(text=text, speaker_id=int(speaker_id))
            if speed_scale is not None:
                query["speedScale"] = float(speed_scale)
            wav_bytes = client.synthesize_wave(audio_query=query, speaker_id=int(speaker_id))
        except TTSClientError as exc:
            raise WorkerError("external_unavailable", str(exc)) from exc

        preview_id = _new_id("preview")
        relative_path = f"previews/{preview_id}.wav"
        output_path = data_root / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(wav_bytes)
        log(f"voice preview generated: {relative_path}")
        return {"previewId": preview_id, "outputPath": relative_path}
        yield  # pragma: no cover

    registry.register("health", health)
    registry.register("db.migrate", db_migrate)
    registry.register("job.recover_stale", job_recover_stale)
    registry.register("project.list", project_list)
    registry.register("project.get", project_get)
    registry.register("project.create", project_create)
    registry.register("source.register", source_register)
    registry.register("source.list", source_list)
    registry.register("source.retry", source_retry)
    registry.register("approval.list", approval_list)
    registry.register("approval.approve", approval_approve)
    registry.register("approval.request_changes", approval_request_changes)
    registry.register("build_request.create", build_request_create)
    registry.register("build_request.approval_gate_satisfied", build_request_approval_gate_satisfied)
    registry.register("job.start", job_start)
    registry.register("job.list", job_list)
    registry.register("job.get", job_get)
    registry.register("job.cancel", job_cancel)
    registry.register("job.retry", job_retry)
    registry.register("artifact.list", artifact_list)
    registry.register("artifact.get", artifact_get)
    registry.register("voice.list_engines", voice_list_engines)
    registry.register("voice.preview", voice_preview)

    return registry


def bootstrap_worker_registry(database_path: Path, *, data_root: Path | None = None) -> HandlerRegistry:
    """subprocess entrypoint(`script/worker/cli.py`)用のfactory。

    `database_path`のDBを開き(存在しなければ新規作成)、`data_root`(既定は
    `database_path`の親)を使ってregistryを構築する。
    """
    connection = connect_database(Path(database_path))
    resolved_data_root = Path(data_root) if data_root is not None else Path(database_path).resolve().parent
    return build_default_registry(resolved_data_root, connection)
