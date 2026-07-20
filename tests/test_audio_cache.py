"""STEP4 test implementation for TASK-AUDIO-001: partial regeneration / internal part split.

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Release scope: MVP
"""

from __future__ import annotations

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


def _script_with_texts(text_1: str, text_2: str) -> ScriptDocument:
    segments = (
        ScriptSegment(segment_id="ch01-seg001", order=1, speaker=_speaker(), segment_type="explanation", text=text_1),
        ScriptSegment(segment_id="ch01-seg002", order=2, speaker=_speaker(), segment_type="explanation", text=text_2),
    )
    return ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="verified", segments=segments)


@pytest.mark.integration_mock
def test_tc_audio_001_02() -> None:
    """TC-AUDIO-001-02 — 部分再生成: 1segmentだけ変更したら対象segmentだけclientを呼ぶ。"""
    client = _FakeTTSClient()
    cache = AudioCache()
    synthesizer = SegmentSynthesizer(tts_client=client, cache=cache)
    profile = _voice_profile()

    script_v1 = _script_with_texts("A loop repeats.", "It does not stop early.")
    synthesizer.synthesize(script_v1, profile)
    calls_after_first_run = len(client.requests)
    assert calls_after_first_run == 2  # 1 part per segment

    script_v2 = _script_with_texts("A loop repeats.", "It stops after N iterations.")  # seg002だけ変更
    results_v2 = synthesizer.synthesize(script_v2, profile)

    new_calls = client.requests[calls_after_first_run:]
    assert len(new_calls) == 1
    assert new_calls[0].request_id.startswith("ch01-seg002")

    seg001_result = next(result for result in results_v2 if result.segment_id == "ch01-seg001")
    assert seg001_result.cache_hit is True
    seg002_result = next(result for result in results_v2 if result.segment_id == "ch01-seg002")
    assert seg002_result.cache_hit is False


@pytest.mark.unit
def test_tc_audio_001_05() -> None:
    """TC-AUDIO-001-05 — 300文字超internal part: 長いsegmentは複数partへ分割される。"""
    client = _FakeTTSClient()
    synthesizer = SegmentSynthesizer(tts_client=client)
    long_text = "これはテストの文章です。" * 40  # 300文字を大きく超える
    script = _script_with_texts("short text", long_text)

    results = synthesizer.synthesize(script, _voice_profile())

    seg002_result = next(result for result in results if result.segment_id == "ch01-seg002")
    assert len(seg002_result.parts) > 1
    assert seg002_result.parts[0].part_id == "ch01-seg002-part001"
    assert seg002_result.parts[1].part_id == "ch01-seg002-part002"


@pytest.mark.unit
def test_tc_audio_001_08() -> None:
    """TC-AUDIO-001-08 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError):
        SegmentSynthesizer(tts_client=None)  # type: ignore[arg-type]

    client = _FakeTTSClient()
    synthesizer = SegmentSynthesizer(tts_client=client)
    profile = _voice_profile()

    with pytest.raises(AppError):
        synthesizer.synthesize(None, profile)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        synthesizer.synthesize(_script_with_texts("a", "b"), None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        AudioCache().key(text="", tts_text=None, voice_profile_id="v1", voice_content_hash="hash")

    assert client.requests == []
