"""script/profiles/characters.py — 公開契約: CharacterProfileRepository.load/select.

Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
Spec: docs/specifications/08-character-profile-schema.md
"""

from __future__ import annotations

from collections.abc import Sequence

from script.core.errors import AppError, ErrorCode
from script.schemas.profiles import CharacterProfile, CharacterProfileStatus


class CharacterProfileRepository:
    """project/characters/配下のcharacter profileを読み込み、承認状態を検証して選択する。"""

    def __init__(self, profiles: Sequence[CharacterProfile]) -> None:
        if not profiles:
            raise AppError(ErrorCode.VALIDATION_ERROR, "profiles must not be empty")

        by_id: dict[str, CharacterProfile] = {}
        for profile in profiles:
            if profile.character_id in by_id:
                raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate character_id: {profile.character_id}")
            by_id[profile.character_id] = profile
        self._by_id = by_id

    def load(self, character_id: str) -> CharacterProfile:
        """character_idからcharacter profileを読み込む(承認状態は検証しない)。"""
        if not character_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "character_id is required")
        try:
            return self._by_id[character_id]
        except KeyError as exc:
            raise AppError(ErrorCode.NOT_FOUND, f"unknown character_id: {character_id}") from exc

    def select(self, character_id: str) -> CharacterProfile:
        """承認済み(approved)のcharacter profileだけを選択可能にする。"""
        profile = self.load(character_id)
        if profile.status is not CharacterProfileStatus.APPROVED:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"character profile is not approved for selection: {character_id} (status={profile.status.value})",
            )
        return profile
