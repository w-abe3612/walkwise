"""script/services/voice_profiles.py — 公開契約:
VoiceProfileService.create/get/get_for_project/list_by_project/update/archive/assert_usable_for_build.

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(5.3, 6節)
Spec: docs/db/06-voice-profiles-table.md

VoiceProfileの正本はSQLite(`voice_profiles`テーブル)であり、YAMLを正本として
新設しない。物理削除は実装しない(`archive`によるstatus遷移のみ、参照済み
Profileは履歴ごと保持される)。
"""

from __future__ import annotations

import dataclasses
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from script.core.errors import AppError, ErrorCode
from script.domain.enums import VoiceProfileRecordStatus
from script.domain.models import VoiceProfileRecord
from script.persistence.repositories import ProjectRepository, VoiceProfileRepository

_DEFAULT_SETTINGS_JSON = "{}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CreateVoiceProfile:
    """VoiceProfile新規作成の入力。"""

    voice_profile_id: str
    project_id: str
    name: str
    engine: str
    speaker_id: str
    style_id: str | None = None
    speed_scale: float = 1.0
    pitch_scale: float = 0.0
    intonation_scale: float = 1.0
    volume_scale: float = 1.0
    sentence_pause_ms: int = 250
    paragraph_pause_ms: int = 600
    section_pause_ms: int = 1000
    chapter_pause_ms: int = 1500
    settings_json: str = _DEFAULT_SETTINGS_JSON


@dataclass(frozen=True)
class UpdateVoiceProfile:
    """VoiceProfile更新の入力。Noneのfieldは現在値を維持する。"""

    voice_profile_id: str
    name: str | None = None
    engine: str | None = None
    speaker_id: str | None = None
    style_id: str | None = None
    speed_scale: float | None = None
    pitch_scale: float | None = None
    intonation_scale: float | None = None
    volume_scale: float | None = None
    sentence_pause_ms: int | None = None
    paragraph_pause_ms: int | None = None
    section_pause_ms: int | None = None
    chapter_pause_ms: int | None = None
    settings_json: str | None = None
    status: VoiceProfileRecordStatus | None = None


class VoiceProfileService:
    """Project所属検証・同一Project内name重複検証・status遷移を伴うVoiceProfile CRUD。"""

    def __init__(self, connection: sqlite3.Connection) -> None:
        if connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
        self._connection = connection
        self._repository = VoiceProfileRepository(connection)
        self._projects = ProjectRepository(connection)

    def _assert_name_not_taken(self, project_id: str, name: str, *, exclude_voice_profile_id: str | None = None) -> None:
        for existing in self._repository.list_by_project(project_id):
            if existing.voice_profile_id == exclude_voice_profile_id:
                continue
            if existing.name == name:
                raise AppError(
                    ErrorCode.CONFLICT,
                    f"voice profile name already exists in this project: {name}",
                )

    def create(self, command: CreateVoiceProfile) -> VoiceProfileRecord:
        """draft状態で新規作成する(承認はupdateで別途行う)。"""
        if command is None or not command.voice_profile_id or not command.project_id or not command.name:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id, project_id and name are required")
        if not command.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")

        if self._projects.find(command.project_id) is None:
            raise AppError(ErrorCode.NOT_FOUND, f"project not found: {command.project_id}")

        self._assert_name_not_taken(command.project_id, command.name)

        now = _now_iso()
        record = VoiceProfileRecord(
            voice_profile_id=command.voice_profile_id,
            project_id=command.project_id,
            name=command.name,
            engine=command.engine,
            speaker_id=command.speaker_id,
            style_id=command.style_id,
            speed_scale=command.speed_scale,
            pitch_scale=command.pitch_scale,
            intonation_scale=command.intonation_scale,
            volume_scale=command.volume_scale,
            sentence_pause_ms=command.sentence_pause_ms,
            paragraph_pause_ms=command.paragraph_pause_ms,
            section_pause_ms=command.section_pause_ms,
            chapter_pause_ms=command.chapter_pause_ms,
            settings_json=command.settings_json,
            status=VoiceProfileRecordStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self._repository.insert(record)
        self._connection.commit()
        return record

    def get(self, voice_profile_id: str) -> VoiceProfileRecord:
        """存在しないIDは`voice_profile_not_found`(NOT_FOUND)へ変換する。"""
        if not voice_profile_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id is required")
        record = self._repository.find(voice_profile_id)
        if record is None:
            raise AppError(ErrorCode.NOT_FOUND, f"voice_profile_not_found: {voice_profile_id}")
        return record

    def get_for_project(self, voice_profile_id: str, project_id: str) -> VoiceProfileRecord:
        """指定Projectに所属するVoiceProfileだけを返す(別Project参照は拒否)。"""
        record = self.get(voice_profile_id)
        if record.project_id != project_id:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"voice_profile_project_mismatch: {voice_profile_id} does not belong to project {project_id}",
            )
        return record

    def list_by_project(self, project_id: str) -> list[VoiceProfileRecord]:
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        return self._repository.list_by_project(project_id)

    def update(self, command: UpdateVoiceProfile) -> VoiceProfileRecord:
        """archived状態のProfileは更新できない(`voice_profile_archived`)。"""
        if command is None or not command.voice_profile_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id is required")

        current = self.get(command.voice_profile_id)
        if current.status is VoiceProfileRecordStatus.ARCHIVED:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"voice_profile_archived: {command.voice_profile_id} is archived and cannot be updated",
            )

        if command.name is not None and command.name != current.name:
            self._assert_name_not_taken(current.project_id, command.name, exclude_voice_profile_id=current.voice_profile_id)

        overrides = {
            key: value
            for key, value in dataclasses.asdict(command).items()
            if key != "voice_profile_id" and value is not None
        }
        # dataclasses.asdictはEnumをそのまま保持しないことがあるため、statusは明示的に扱う。
        if command.status is not None:
            overrides["status"] = command.status
        updated = dataclasses.replace(current, **overrides, updated_at=_now_iso())

        self._repository.update(updated)
        self._connection.commit()
        return updated

    def archive(self, voice_profile_id: str) -> VoiceProfileRecord:
        """物理削除はしない。statusをarchivedへ遷移させ、履歴として保持する(冪等)。"""
        current = self.get(voice_profile_id)
        if current.status is VoiceProfileRecordStatus.ARCHIVED:
            return current

        updated = dataclasses.replace(current, status=VoiceProfileRecordStatus.ARCHIVED, updated_at=_now_iso())
        self._repository.update(updated)
        self._connection.commit()
        return updated

    def assert_usable_for_build(self, voice_profile_id: str, project_id: str) -> VoiceProfileRecord:
        """Build開始前に使用可能(同一Project・approved・非archived)であることを検証する。"""
        record = self.get_for_project(voice_profile_id, project_id)
        if record.status is VoiceProfileRecordStatus.ARCHIVED:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"voice_profile_archived: {voice_profile_id}")
        if record.status is not VoiceProfileRecordStatus.APPROVED:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"voice_profile_not_approved: {voice_profile_id} (status={record.status.value})",
            )
        return record
