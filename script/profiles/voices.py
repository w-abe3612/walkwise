"""script/profiles/voices.py — 公開契約: VoiceProfileRepository.load/select/list_available.

Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
Spec: docs/specifications/09-voice-profile-schema.md
"""

from __future__ import annotations

from collections.abc import Sequence

from script.core.errors import AppError, ErrorCode
from script.schemas.profiles import DELIVERABLE_VOICE_PROFILE_STATUSES, VoiceProfile, VoiceProfileStatus

# TASK-COEIR-001は永久にblockedのため、MVPではVOICEVOXだけを利用可能一覧へ出す。
_MVP_AVAILABLE_ENGINE = "voicevox"


class VoiceProfileRepository:
    """project/voices/配下のvoice profileを読み込み、承認状態を検証して選択する。"""

    def __init__(self, profiles: Sequence[VoiceProfile]) -> None:
        if not profiles:
            raise AppError(ErrorCode.VALIDATION_ERROR, "profiles must not be empty")

        by_id: dict[str, VoiceProfile] = {}
        for profile in profiles:
            if profile.voice_profile_id in by_id:
                raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate voice_profile_id: {profile.voice_profile_id}")
            by_id[profile.voice_profile_id] = profile
        self._by_id = by_id

    def load(self, voice_profile_id: str) -> VoiceProfile:
        """voice_profile_idからvoice profileを読み込む(承認状態は検証しない)。"""
        if not voice_profile_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id is required")
        try:
            return self._by_id[voice_profile_id]
        except KeyError as exc:
            raise AppError(ErrorCode.NOT_FOUND, f"unknown voice_profile_id: {voice_profile_id}") from exc

    def select(self, voice_profile_id: str) -> VoiceProfile:
        """正式成果物に使用できる状態(approved/approved_for_limited_use)だけを選択可能にする。"""
        profile = self.load(voice_profile_id)
        if profile.status not in DELIVERABLE_VOICE_PROFILE_STATUSES:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"voice profile is not approved for deliverable use: {voice_profile_id} (status={profile.status.value})",
            )
        return profile

    def list_available(self) -> tuple[VoiceProfile, ...]:
        """MVPではVOICEVOXだけを利用可能一覧へ出す(COEIROINKはTASK-COEIR-001がblockedのため対象外)。"""
        return tuple(
            profile
            for profile in self._by_id.values()
            if profile.engine == _MVP_AVAILABLE_ENGINE and profile.status is VoiceProfileStatus.APPROVED
        )
