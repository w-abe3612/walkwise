"""script/schemas/profiles.py — 公開契約: CharacterProfile/VoiceProfile/EngineIdentity.

Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
Spec: docs/specifications/08-character-profile-schema.md, docs/specifications/09-voice-profile-schema.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum

from script.core.errors import AppError, ErrorCode


class CharacterProfileStatus(str, Enum):
    """character profileの採用状態。08-character-profile-schema.mdは状態名を定義しないため、
    「未承認profile選択拒否」(扱う範囲)を満たす最小の3値とした。"""

    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"


class CharacterStrength(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class CharacterProfile:
    """project/characters/<character_id>.yaml相当。"""

    character_id: str
    display_name: str
    content_revision: int = 1
    status: CharacterProfileStatus = CharacterProfileStatus.CANDIDATE
    style_enabled: bool = False
    default_strength: CharacterStrength = CharacterStrength.LOW
    maximum_consecutive_styled_endings: int = 0
    role_defaults: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.character_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "character_id is required")
        if not self.display_name:
            raise AppError(ErrorCode.VALIDATION_ERROR, "display_name is required")
        if self.content_revision < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_revision must be 1 or greater")
        if self.maximum_consecutive_styled_endings < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "maximum_consecutive_styled_endings must not be negative")

    def content_hash(self) -> str:
        """正規化した内容からSHA-256を決定的に計算する(revision/hash)。"""
        payload = "|".join(
            [
                self.character_id,
                self.display_name,
                str(self.style_enabled),
                self.default_strength.value,
                str(self.maximum_consecutive_styled_endings),
                ",".join(self.role_defaults),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class VoiceProfileStatus(str, Enum):
    """09-voice-profile-schema.md 4節。"""

    PROVISIONAL = "provisional"
    APPROVED = "approved"
    APPROVED_FOR_LIMITED_USE = "approved_for_limited_use"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


# 09-voice-profile-schema.md 4節: 正式成果物に使用できるのはapprovedと
# 使用条件を満たすapproved_for_limited_useのみ。
DELIVERABLE_VOICE_PROFILE_STATUSES = frozenset(
    {VoiceProfileStatus.APPROVED, VoiceProfileStatus.APPROVED_FOR_LIMITED_USE}
)


@dataclass(frozen=True)
class EngineIdentity:
    """内部IDと分離した、外部engineが認識する識別情報。"""

    speaker_uuid: str | None = None
    engine_version: str | None = None
    engine_display_name: str | None = None


@dataclass(frozen=True)
class VoiceSpeaker:
    """09-voice-profile-schema.md 9節: speaker IDは文字列で共通保持する。"""

    id: str
    style_id: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speaker.id is required")


@dataclass(frozen=True)
class VoiceParameters:
    speed_scale: float = 1.0
    pitch_scale: float = 0.0
    intonation_scale: float = 1.0
    volume_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.speed_scale <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speed_scale must be greater than 0")
        if self.volume_scale <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "volume_scale must be greater than 0")


@dataclass(frozen=True)
class VoicePauses:
    sentence_ms: int = 250
    paragraph_ms: int = 600
    section_ms: int = 1000
    chapter_ms: int = 1500

    def __post_init__(self) -> None:
        if any(value < 0 for value in (self.sentence_ms, self.paragraph_ms, self.section_ms, self.chapter_ms)):
            raise AppError(ErrorCode.VALIDATION_ERROR, "pause values must not be negative")


@dataclass(frozen=True)
class VoiceProfile:
    """project/voices/<voice_profile_id>.yaml相当。"""

    voice_profile_id: str
    engine: str
    speaker: VoiceSpeaker
    character_id: str | None = None
    display_name: str = ""
    content_revision: int = 1
    status: VoiceProfileStatus = VoiceProfileStatus.PROVISIONAL
    engine_identity: EngineIdentity = field(default_factory=EngineIdentity)
    parameters: VoiceParameters = field(default_factory=VoiceParameters)
    pause: VoicePauses = field(default_factory=VoicePauses)
    sample_rate_hz: int = 24000
    audition_approved: bool = False

    def __post_init__(self) -> None:
        if not self.voice_profile_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id is required")
        if not self.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        if self.content_revision < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_revision must be 1 or greater")
        if self.sample_rate_hz <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "sample_rate_hz must be greater than 0")

        if self.status is VoiceProfileStatus.APPROVED:
            # 09-voice-profile-schema.md 11節: approvedなのにengine version/試聴承認欠落はerror。
            if not self.engine_identity.engine_version:
                raise AppError(ErrorCode.VALIDATION_ERROR, "approved voice profile requires engine_identity.engine_version")
            if not self.audition_approved:
                raise AppError(ErrorCode.VALIDATION_ERROR, "approved voice profile requires audition_approved=True")

    def content_hash(self) -> str:
        """正規化した内容からSHA-256を決定的に計算する(revision/hash)。"""
        payload = "|".join(
            [
                self.engine,
                self.speaker.id,
                self.speaker.style_id or "",
                repr(self.parameters.speed_scale),
                repr(self.parameters.pitch_scale),
                repr(self.parameters.intonation_scale),
                repr(self.parameters.volume_scale),
                str(self.pause.sentence_ms),
                str(self.pause.paragraph_ms),
                str(self.pause.section_ms),
                str(self.pause.chapter_ms),
                str(self.sample_rate_hz),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
