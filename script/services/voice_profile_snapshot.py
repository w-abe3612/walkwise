"""script/services/voice_profile_snapshot.py — 公開契約: capture_voice_profile_snapshot.

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(10, 14.4節)

VoiceProfileはJob開始時に一度だけDBから読み込み、Job全体で不変なsnapshotとして
扱う(Job途中でのProfile更新は反映しない)。呼び出し側(Build Execution
Orchestrator)は、Job開始時にこの関数を1回だけ呼び出し、以後は戻り値の
VoiceProfileSnapshotだけを参照すること。
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from script.core.hashing import canonical_sha256
from script.services.voice_profiles import VoiceProfileService

_HASHED_FIELDS = (
    "engine", "speaker_id", "style_id",
    "speed_scale", "pitch_scale", "intonation_scale", "volume_scale",
    "sentence_pause_ms", "paragraph_pause_ms", "section_pause_ms", "chapter_pause_ms",
)


@dataclass(frozen=True)
class VoiceProfileSnapshot:
    """Job開始時点のVoiceProfileを凍結した不変表現(14-audio-packaging.md manifest埋め込み用)。"""

    voice_profile_id: str
    voice_profile_name: str
    project_id: str
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
    voice_profile_updated_at: str
    voice_profile_config_hash: str
    style_id: str | None = None


def _compute_config_hash(*, settings: dict[str, object], **fields: object) -> str:
    payload = dict(fields)
    payload["settings"] = settings
    return canonical_sha256(payload)


def capture_voice_profile_snapshot(
    connection: sqlite3.Connection, project_id: str, voice_profile_id: str
) -> VoiceProfileSnapshot:
    """approved・同一Project所属を確認したうえで、DBから一度だけ読み込みsnapshot化する。"""
    record = VoiceProfileService(connection).assert_usable_for_build(voice_profile_id, project_id)

    settings = json.loads(record.settings_json)
    config_hash = _compute_config_hash(
        settings=settings,
        **{field: getattr(record, field) for field in _HASHED_FIELDS},
    )

    return VoiceProfileSnapshot(
        voice_profile_id=record.voice_profile_id,
        voice_profile_name=record.name,
        project_id=record.project_id,
        engine=record.engine,
        speaker_id=record.speaker_id,
        style_id=record.style_id,
        speed_scale=record.speed_scale,
        pitch_scale=record.pitch_scale,
        intonation_scale=record.intonation_scale,
        volume_scale=record.volume_scale,
        sentence_pause_ms=record.sentence_pause_ms,
        paragraph_pause_ms=record.paragraph_pause_ms,
        section_pause_ms=record.section_pause_ms,
        chapter_pause_ms=record.chapter_pause_ms,
        settings_json=record.settings_json,
        voice_profile_updated_at=record.updated_at,
        voice_profile_config_hash=config_hash,
    )
