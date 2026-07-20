"""STEP4 test implementation for TASK-AUDIO-001: SegmentSynthesizer / AudioCache.key.

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Release scope: MVP
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.audio.cache import AudioCache
from script.audio.synthesis import SegmentSynthesizer
from script.core.errors import AppError
from script.schemas.profiles import EngineIdentity, VoiceProfile, VoiceProfileStatus, VoiceSpeaker
from script.schemas.script import ScriptDocument, ScriptSegment, SpeakerRef
from script.tts_clients.models import EngineCapabilities, SynthesisRequest, SynthesisResult

pytestmark = pytest.mark.mvp


class _FakeTTSClient:
    engine_name = "mock"

    def __init__(self) -> None:
        self.requests: list[SynthesisRequest] = []

    def check_connectivity(self) -> bool:
        return True

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(engine="mock")

    def list_speakers(self) -> list:
        return []

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        self.requests.append(request)
        return SynthesisResult(
            request_id=request.request_id,
            engine=request.engine,
            speaker_id=request.speaker_id,
            output_path=request.output_path or f"mock/{request.request_id}.wav",
            duration_seconds=round(max(0.1, len(request.text) * 0.05), 3),
            sample_rate_hz=24000,
            channels=1,
            audio_bytes=request.text.encode("utf-8"),
        )


def _speaker() -> SpeakerRef:
    return SpeakerRef(character_id="neutral-explainer", role="explainer")


def _voice_profile() -> VoiceProfile:
    return VoiceProfile(
        voice_profile_id="mock-voice-default",
        engine="mock",
        speaker=VoiceSpeaker(id="8"),
        engine_identity=EngineIdentity(engine_version="0.1.0"),
        status=VoiceProfileStatus.APPROVED,
        audition_approved=True,
    )


def _verified_script(*, text_2: str = "It does not stop early.", tts_text_2: str | None = None) -> ScriptDocument:
    segments = (
        ScriptSegment(segment_id="ch01-seg001", order=1, speaker=_speaker(), segment_type="explanation", text="A loop repeats."),
        ScriptSegment(
            segment_id="ch01-seg002", order=2, speaker=_speaker(), segment_type="explanation", text=text_2, tts_text=tts_text_2
        ),
    )
    return ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="verified", segments=segments)


@pytest.mark.unit
def test_tc_audio_001_01() -> None:
    """TC-AUDIO-001-01 — cache key: text同一でvoice revision差なら異なるkeyになる。"""
    cache = AudioCache()

    key_rev1 = cache.key(text="hello", tts_text=None, voice_profile_id="v1", voice_content_hash="hash-rev1")
    key_rev2 = cache.key(text="hello", tts_text=None, voice_profile_id="v1", voice_content_hash="hash-rev2")
    key_rev1_again = cache.key(text="hello", tts_text=None, voice_profile_id="v1", voice_content_hash="hash-rev1")

    assert key_rev1 != key_rev2
    assert key_rev1 == key_rev1_again


@pytest.mark.unit
def test_tc_audio_001_04() -> None:
    """TC-AUDIO-001-04 — tts_text優先: tts_textがあればtextではなくそちらを合成に使う。"""
    client = _FakeTTSClient()
    synthesizer = SegmentSynthesizer(tts_client=client)
    script = _verified_script(text_2="It does not stop early.", tts_text_2="It does not stop early, reading adjusted.")

    synthesizer.synthesize(script, _voice_profile())

    seg002_requests = [request for request in client.requests if request.request_id.startswith("ch01-seg002")]
    assert seg002_requests
    assert all(request.text == "It does not stop early, reading adjusted." for request in seg002_requests)


@pytest.mark.unit
def test_tc_audio_001_07(tmp_path: Path) -> None:
    """TC-AUDIO-001-07 — atomic output: 一時ファイル経由でatomicにwavを書き込む。"""
    client = _FakeTTSClient()
    synthesizer = SegmentSynthesizer(tts_client=client, output_dir=tmp_path)
    script = _verified_script()

    results = synthesizer.synthesize(script, _voice_profile())

    written_files = sorted(tmp_path.glob("*.wav"))
    assert written_files
    assert not list(tmp_path.glob("*.tmp"))
    for result in results:
        for part in result.parts:
            written_path = tmp_path / f"{part.part_id}.wav"
            assert written_path.exists()


@pytest.mark.unit
def test_tc_audio_001_10() -> None:
    """TC-AUDIO-001-10 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    client = _FakeTTSClient()
    synthesizer = SegmentSynthesizer(tts_client=client)
    script = _verified_script()
    profile = _voice_profile()

    results = synthesizer.synthesize(script, profile)
    before = tuple((result.segment_id, result.output_path, result.duration_seconds) for result in results)

    draft_script = ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=script.segments)
    with pytest.raises(AppError):
        synthesizer.synthesize(draft_script, profile)

    after = tuple((result.segment_id, result.output_path, result.duration_seconds) for result in results)
    assert before == after
    assert script.stage == "verified"
