"""STEP4 test implementation for TASK-TTS-001: TTSClientRegistry / models.

Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode
from script.tts_clients.base import MockTTSClient, TTSClientError, TTSErrorCode
from script.tts_clients.models import EngineCapabilities, SpeakerInfo, SynthesisRequest, SynthesisResult
from script.tts_clients.registry import TTSClientRegistry

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_tts_001_02() -> None:
    """TC-TTS-001-02 — 未知engine: 未登録名のgetはunsupported_engineにする。"""
    registry = TTSClientRegistry()
    registry.register("voicevox", MockTTSClient())

    with pytest.raises(TTSClientError) as excinfo:
        registry.get("unregistered-engine")

    assert excinfo.value.code is TTSErrorCode.UNSUPPORTED_ENGINE
    assert excinfo.value.engine_detail == "unregistered-engine"


@pytest.mark.unit
def test_tc_tts_001_04() -> None:
    """TC-TTS-001-04 — request/result型: 型が正しく保持され、同一入力から同一値を再現できる。"""
    request_1 = SynthesisRequest(request_id="r1", engine="mock", text="hello", speaker_id="s1")
    request_2 = SynthesisRequest(request_id="r1", engine="mock", text="hello", speaker_id="s1")
    assert request_1 == request_2

    result = SynthesisResult(
        request_id="r1", engine="mock", speaker_id="s1", output_path="out.wav", duration_seconds=1.0, sample_rate_hz=24000
    )
    assert result.channels == 1

    speaker = SpeakerInfo(speaker_id="s1", display_name="Speaker One", engine="mock")
    assert speaker.speaker_id == "s1"

    capabilities = EngineCapabilities(engine="mock")
    assert capabilities.recommended_max_text_length == 300


@pytest.mark.unit
def test_tc_tts_001_06() -> None:
    """TC-TTS-001-06 — list_speakers: 表示名でなくengineのspeaker_idで解決し、不在はspeaker_not_found。"""
    speaker = SpeakerInfo(speaker_id="kasukabe-tsumugi-style-3", display_name="春日部つむぎ", engine="mock")
    client = MockTTSClient(speakers=(speaker,))

    speakers = client.list_speakers()
    assert speakers[0].speaker_id == "kasukabe-tsumugi-style-3"

    # 表示名では解決できない(speaker_idだけが解決キー)。
    request_by_display_name = SynthesisRequest(
        request_id="r1", engine="mock", text="hello", speaker_id="春日部つむぎ"
    )
    with pytest.raises(TTSClientError) as excinfo:
        client.synthesize(request_by_display_name)
    assert excinfo.value.code is TTSErrorCode.SPEAKER_NOT_FOUND

    request_by_speaker_id = SynthesisRequest(
        request_id="r2", engine="mock", text="hello", speaker_id="kasukabe-tsumugi-style-3"
    )
    result = client.synthesize(request_by_speaker_id)
    assert result.speaker_id == "kasukabe-tsumugi-style-3"


@pytest.mark.unit
def test_tc_tts_001_08() -> None:
    """TC-TTS-001-08 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as excinfo:
        SynthesisRequest(request_id="", engine="mock", text="hello", speaker_id="s1")
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        SynthesisRequest(request_id="r1", engine="mock", text="", speaker_id="s1")

    with pytest.raises(AppError):
        SpeakerInfo(speaker_id="", display_name="x", engine="mock")

    with pytest.raises(AppError):
        EngineCapabilities(engine="")

    registry = TTSClientRegistry()
    with pytest.raises(AppError):
        registry.register("", MockTTSClient())
    with pytest.raises(AppError):
        registry.get("")


@pytest.mark.unit
def test_tc_tts_001_10() -> None:
    """TC-TTS-001-10 — 入力・既存成果物の不変性: 失敗を試みても既存登録は変化しない。"""
    registry = TTSClientRegistry()
    client = MockTTSClient()
    registry.register("voicevox", client)

    before = registry.get("voicevox")

    with pytest.raises(TTSClientError):
        registry.get("unknown-engine")

    after = registry.get("voicevox")
    assert after is before is client
