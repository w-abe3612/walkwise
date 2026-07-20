"""STEP4 test implementation for TASK-PROFILE-001: CharacterProfileRepository / cross-cutting profile checks.

Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode
from script.profiles.characters import CharacterProfileRepository
from script.profiles.voices import VoiceProfileRepository
from script.schemas.profiles import (
    CharacterProfile,
    CharacterProfileStatus,
    EngineIdentity,
    VoiceProfile,
    VoiceProfileStatus,
    VoiceSpeaker,
)

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_profile_001_01() -> None:
    """TC-PROFILE-001-01 — ID分離: 同名character/engine speakerでもIDを別保持する。"""
    shared_name = "tsumugi"
    character = CharacterProfile(
        character_id=shared_name,
        display_name="つむぎ(中立解説)",
        status=CharacterProfileStatus.APPROVED,
    )
    voice = VoiceProfile(
        voice_profile_id="kasukabe-tsumugi-voicevox-default",
        engine="voicevox",
        speaker=VoiceSpeaker(id=shared_name, style_id="3"),
        character_id=shared_name,
        engine_identity=EngineIdentity(speaker_uuid=shared_name, engine_version="0.14.0"),
        status=VoiceProfileStatus.APPROVED,
        audition_approved=True,
    )

    character_repo = CharacterProfileRepository((character,))
    voice_repo = VoiceProfileRepository((voice,))

    loaded_character = character_repo.load(shared_name)
    loaded_voice = voice_repo.load("kasukabe-tsumugi-voicevox-default")

    assert loaded_character.character_id == shared_name
    assert loaded_voice.voice_profile_id == "kasukabe-tsumugi-voicevox-default"
    assert loaded_voice.character_id == shared_name
    # engineのspeaker.idと外部engine_identity.speaker_uuidは同じ文字列でも別の保持領域。
    assert loaded_voice.speaker.id == shared_name
    assert loaded_voice.engine_identity.speaker_uuid == shared_name
    assert loaded_voice.voice_profile_id != loaded_character.character_id


@pytest.mark.unit
def test_tc_profile_001_03() -> None:
    """TC-PROFILE-001-03 — 未承認選択: candidate/rejected profileのselectは拒否する。"""
    candidate = CharacterProfile(
        character_id="candidate-narrator",
        display_name="候補ナレーター",
        status=CharacterProfileStatus.CANDIDATE,
    )
    rejected = CharacterProfile(
        character_id="rejected-narrator",
        display_name="不採用ナレーター",
        status=CharacterProfileStatus.REJECTED,
    )
    repo = CharacterProfileRepository((candidate, rejected))

    with pytest.raises(AppError) as excinfo_candidate:
        repo.select("candidate-narrator")
    assert excinfo_candidate.value.code is ErrorCode.PERMISSION_DENIED

    with pytest.raises(AppError) as excinfo_rejected:
        repo.select("rejected-narrator")
    assert excinfo_rejected.value.code is ErrorCode.PERMISSION_DENIED


@pytest.mark.unit
def test_tc_profile_001_05() -> None:
    """TC-PROFILE-001-05 — provisional/selected: provisional voice profileはdeliverables選択を拒否される。"""
    provisional = VoiceProfile(
        voice_profile_id="ouka-miko-voicevox-default",
        engine="voicevox",
        speaker=VoiceSpeaker(id="ouka-miko", style_id="1"),
        status=VoiceProfileStatus.PROVISIONAL,
    )
    approved = VoiceProfile(
        voice_profile_id="ouka-miko-voicevox-approved",
        engine="voicevox",
        speaker=VoiceSpeaker(id="ouka-miko", style_id="1"),
        engine_identity=EngineIdentity(engine_version="0.14.0"),
        status=VoiceProfileStatus.APPROVED,
        audition_approved=True,
    )
    repo = VoiceProfileRepository((provisional, approved))

    with pytest.raises(AppError) as excinfo:
        repo.select("ouka-miko-voicevox-default")
    assert excinfo.value.code is ErrorCode.PERMISSION_DENIED

    selected = repo.select("ouka-miko-voicevox-approved")
    assert selected.status is VoiceProfileStatus.APPROVED


@pytest.mark.unit
def test_tc_profile_001_07() -> None:
    """TC-PROFILE-001-07 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as excinfo:
        CharacterProfile(character_id="", display_name="x")
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        CharacterProfile(character_id="c1", display_name="")

    with pytest.raises(AppError):
        CharacterProfileRepository(())

    with pytest.raises(AppError):
        CharacterProfileRepository(
            (CharacterProfile(character_id="c1", display_name="x", status=CharacterProfileStatus.APPROVED),)
        ).load("")

    with pytest.raises(AppError):
        VoiceProfile(voice_profile_id="", engine="voicevox", speaker=VoiceSpeaker(id="s1"))


@pytest.mark.unit
def test_tc_profile_001_09() -> None:
    """TC-PROFILE-001-09 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    approved = CharacterProfile(
        character_id="neutral-explainer",
        display_name="中立解説者",
        status=CharacterProfileStatus.APPROVED,
    )
    rejected = CharacterProfile(
        character_id="rejected-narrator",
        display_name="不採用ナレーター",
        status=CharacterProfileStatus.REJECTED,
    )
    repo = CharacterProfileRepository((approved, rejected))

    before = repo.select("neutral-explainer")
    with pytest.raises(AppError):
        repo.select("rejected-narrator")

    after = repo.load("neutral-explainer")
    assert after == before
    assert after.status is CharacterProfileStatus.APPROVED
