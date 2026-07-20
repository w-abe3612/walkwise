"""script/domain/models.py — 公開契約: Project, Source, BuildRequest, Job, Artifact.

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Spec: docs/db/01-projects-table.md 〜 05-artifacts-table.md
"""

from __future__ import annotations

from dataclasses import dataclass

from script.domain.enums import ArtifactType, BuildStatus, JobStatus, PlanningStage, SourceStatus
from script.domain.validation import _assert_relative_path, canonicalize_output_formats, validate_build_request


@dataclass(frozen=True)
class Project:
    project_id: str
    title: str
    domain: str
    planning_stage: PlanningStage
    content_revision: int
    plan_file_path: str
    created_at: str
    updated_at: str
    archived_at: str | None = None

    def __post_init__(self) -> None:
        _assert_relative_path("plan_file_path", self.plan_file_path)


@dataclass(frozen=True)
class Source:
    source_id: str
    project_id: str
    media_type: str
    status: SourceStatus
    original_file_path: str
    content_hash: str
    created_at: str
    updated_at: str

    def __post_init__(self) -> None:
        _assert_relative_path("original_file_path", self.original_file_path)


@dataclass(frozen=True)
class BuildRequest:
    build_request_id: str
    project_id: str
    output_formats: tuple[str, ...]
    status: BuildStatus
    created_at: str
    updated_at: str
    voice_profile_id: str | None = None

    def __post_init__(self) -> None:
        canonical = canonicalize_output_formats(self.output_formats)
        object.__setattr__(self, "output_formats", canonical)
        validate_build_request(canonical, self.voice_profile_id)


@dataclass(frozen=True)
class Job:
    job_id: str
    build_request_id: str
    job_type: str
    status: JobStatus
    parent_job_id: str | None = None
    progress_current: int | None = None
    progress_total: int | None = None
    last_message: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    job_id: str
    project_id: str
    artifact_type: ArtifactType
    file_path: str
    version_number: int
    content_hash: str
    created_at: str

    def __post_init__(self) -> None:
        _assert_relative_path("file_path", self.file_path)
