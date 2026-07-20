"""STEP4 test implementation for TASK-PROFILE-001: VoiceProfileRepository.

Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.profiles.voices import VoiceProfileRepository
from script.schemas.profiles import EngineIdentity, VoiceParameters, VoiceProfile, VoiceProfileStatus, VoiceSpeaker

pytestmark = pytest.mark.mvp


def _approved_voicevox(voice_profile_id: str, speaker_id: str, **overrides: object) -> VoiceProfile:
    fields: dict[str, object] = dict(
        voice_profile_id=voice_profile_id,
        engine="voicevox",
        speaker=VoiceSpeaker(id=speaker_id, style_id="1"),
        engine_identity=EngineIdentity(engine_version="0.14.0"),
        status=VoiceProfileStatus.APPROVED,
        audition_approved=True,
    )
    fields.update(overrides)
    return VoiceProfile(**fields)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_profile_001_02() -> None:
    """TC-PROFILE-001-02 — MVP engine filter: MVPでは承認済みVOICEVOXだけ表示。"""
    approved_voicevox = _approved_voicevox("kasukabe-tsumugi-voicevox-default", "kasukabe-tsumugi")
    provisional_voicevox = VoiceProfile(
        voice_profile_id="ouka-miko-voicevox-default",
        engine="voicevox",
        speaker=VoiceSpeaker(id="ouka-miko"),
        status=VoiceProfileStatus.PROVISIONAL,
    )
    approved_coeiroink = VoiceProfile(
        voice_profile_id="lilin-chan-coeiroink-default",
        engine="coeiroink",
        speaker=VoiceSpeaker(id="lilin-chan"),
        engine_identity=EngineIdentity(engine_version="1.0.0"),
        status=VoiceProfileStatus.APPROVED,
        audition_approved=True,
    )
    repo = VoiceProfileRepository((approved_voicevox, provisional_voicevox, approved_coeiroink))

    available = repo.list_available()

    assert [profile.voice_profile_id for profile in available] == ["kasukabe-tsumugi-voicevox-default"]
    assert all(profile.engine == "voicevox" for profile in available)
    assert all(profile.status is VoiceProfileStatus.APPROVED for profile in available)


@pytest.mark.unit
def test_tc_profile_001_04() -> None:
    """TC-PROFILE-001-04 — revision/hash: 同一の正規化入力から同一SHA-256を返し、内容差分でhashが変化する。"""
    profile_a = _approved_voicevox("v1", "kasukabe-tsumugi")
    profile_b = _approved_voicevox("v1", "kasukabe-tsumugi")
    profile_different_speed = _approved_voicevox(
        "v1", "kasukabe-tsumugi", parameters=VoiceParameters(speed_scale=1.1)
    )

    assert profile_a.content_hash() == profile_b.content_hash()
    assert profile_a.content_hash() != profile_different_speed.content_hash()


@pytest.mark.unit
def test_tc_profile_001_06() -> None:
    """TC-PROFILE-001-06 — 作品別既定: 単一の全作品共通既定を強制せず、作品ごとに異なる既定を選択できる。"""
    repo = VoiceProfileRepository(
        (
            _approved_voicevox("kasukabe-tsumugi-voicevox-default", "kasukabe-tsumugi"),
            _approved_voicevox("tohoku-kiritan-voicevox-default", "tohoku-kiritan"),
        )
    )

    project_a_default_voice_profile_id = "kasukabe-tsumugi-voicevox-default"
    project_b_default_voice_profile_id = "tohoku-kiritan-voicevox-default"

    selected_a = repo.select(project_a_default_voice_profile_id)
    selected_b = repo.select(project_b_default_voice_profile_id)

    assert selected_a.voice_profile_id != selected_b.voice_profile_id


@pytest.mark.unit
def test_tc_profile_001_08() -> None:
    """TC-PROFILE-001-08 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    repo = VoiceProfileRepository((_approved_voicevox("kasukabe-tsumugi-voicevox-default", "kasukabe-tsumugi"),))

    result_1 = repo.select("kasukabe-tsumugi-voicevox-default")
    result_2 = repo.select("kasukabe-tsumugi-voicevox-default")

    assert result_1 == result_2
    assert repo.list_available() == repo.list_available()
