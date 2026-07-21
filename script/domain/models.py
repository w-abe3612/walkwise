"""script/domain/models.py — 公開契約: Project, Source, BuildRequest, Job, Artifact, VoiceProfileRecord.

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Spec: docs/db/01-projects-table.md 〜 05-artifacts-table.md, 06-voice-profiles-table.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from script.core.errors import AppError, ErrorCode
from script.domain.enums import ArtifactType, BuildStatus, JobStatus, PlanningStage, SourceStatus, VoiceProfileRecordStatus
from script.domain.validation import _assert_relative_path, canonicalize_output_formats, validate_build_request
from script.schemas.profiles import VoiceParameters, VoicePauses


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
    # TASK-BUILD-EXEC-001 12節: 失敗時の安定エラーコード・失敗段階・詳細
    # (秘密値・原稿全文・絶対pathを含まない)。
    error_code: str | None = None
    error_stage: str | None = None
    error_detail_json: str | None = None


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


@dataclass(frozen=True)
class VoiceProfileRecord:
    """`voice_profiles`テーブル(DB正本、TASK-BUILD-EXEC-001)の1行。

    `script/schemas/profiles.py`の`VoiceParameters`/`VoicePauses`が持つ数値範囲
    検証を、`__post_init__`内で一時インスタンス化して再利用する(重複実装しない)。
    """

    voice_profile_id: str
    project_id: str
    name: str
    engine: str
    speaker_id: str
    speed_scale: float
    pitch_scale: float
    intonation_scale: float
    volume_scale: float
    sentence_pause_ms: int
    paragraph_pause_ms: int
    section_pause_ms: int
    chapter_pause_ms: int
    settings_json: str
    status: VoiceProfileRecordStatus
    created_at: str
    updated_at: str
    style_id: str | None = None

    def __post_init__(self) -> None:
        if not self.voice_profile_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id is required")
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.name:
            raise AppError(ErrorCode.VALIDATION_ERROR, "name is required")
        if not self.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        if not self.speaker_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speaker_id is required")

        # 数値範囲検証(既存VoiceParameters/VoicePausesの制約を再利用する)。
        VoiceParameters(
            speed_scale=self.speed_scale,
            pitch_scale=self.pitch_scale,
            intonation_scale=self.intonation_scale,
            volume_scale=self.volume_scale,
        )
        VoicePauses(
            sentence_ms=self.sentence_pause_ms,
            paragraph_ms=self.paragraph_pause_ms,
            section_ms=self.section_pause_ms,
            chapter_ms=self.chapter_pause_ms,
        )

        try:
            parsed = json.loads(self.settings_json)
        except (TypeError, ValueError) as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"settings_json must be valid JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise AppError(ErrorCode.VALIDATION_ERROR, "settings_json must be a JSON object")
