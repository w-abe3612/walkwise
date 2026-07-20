"""STEP4 test implementation for TASK-VOICEVOX-001: VoicevoxAdapter.

Contract: docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md
Release scope: MVP
"""

from __future__ import annotations

import io
import wave

import pytest

from script.core.errors import AppError
from script.tts_clients.base import TTSClientError
from script.tts_clients.models import SynthesisParameters, SynthesisRequest
from script.tts_clients.voicevox.adapter import VoicevoxAdapter
from script.tts_clients.voicevox.client import VoicevoxHttpClient

pytestmark = pytest.mark.mvp


def _make_wav_bytes(*, framerate: int = 24000, nchannels: int = 1, sampwidth: int = 2, nframes: int = 100) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(nchannels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(framerate)
        wav_file.writeframes(b"\x00" * (nframes * sampwidth * nchannels))
    return buffer.getvalue()


class _FakeResponse:
    def __init__(self, *, status_code: int = 200, json_data: object = None, content: bytes = b"", headers: dict | None = None) -> None:
        self.status_code = status_code
        self._json_data = json_data
        self.content = content
        self.headers = headers or {}

    def json(self) -> object:
        if self._json_data is None:
            raise ValueError("response body is not valid JSON")
        return self._json_data


def _fake_client(*, audio_query_calls: list, synthesis_calls: list) -> VoicevoxHttpClient:
    def fake_post(url: str, params: dict | None = None, timeout: object = None, headers: object = None, json: object = None) -> _FakeResponse:
        if url.endswith("/audio_query"):
            audio_query_calls.append(dict(params or {}))
            return _FakeResponse(status_code=200, json_data={"accent_phrases": []})
        if url.endswith("/synthesis"):
            synthesis_calls.append(dict(json or {}))
            return _FakeResponse(status_code=200, content=_make_wav_bytes(), headers={"Content-Type": "audio/wav"})
        raise AssertionError(f"unexpected url: {url}")

    return VoicevoxHttpClient(session_post=fake_post)


def _speakers_json() -> list[dict]:
    return [{"speaker_uuid": "uuid-1", "name": "春日部つむぎ", "styles": [{"id": 8, "name": "ノーマル"}]}]


@pytest.mark.integration_mock
def test_tc_voicevox_001_02() -> None:
    """TC-VOICEVOX-001-02 — 合成mock: parameter mappingとRIFF validationを行う。"""
    audio_query_calls: list[dict] = []
    synthesis_calls: list[dict] = []
    client = _fake_client(audio_query_calls=audio_query_calls, synthesis_calls=synthesis_calls)
    adapter = VoicevoxAdapter(client=client)

    request = SynthesisRequest(
        request_id="r1",
        engine="voicevox",
        text="hello world",
        speaker_id="3",
        parameters=SynthesisParameters(speed_scale=1.2, pitch_scale=0.1, intonation_scale=1.1, volume_scale=0.9),
    )

    result = adapter.synthesize(request)

    assert result.sample_rate_hz == 24000
    assert result.request_id == "r1"
    assert synthesis_calls[0]["speedScale"] == 1.2
    assert synthesis_calls[0]["pitchScale"] == 0.1
    assert synthesis_calls[0]["intonationScale"] == 1.1
    assert synthesis_calls[0]["volumeScale"] == 0.9


@pytest.mark.unit
def test_tc_voicevox_001_04() -> None:
    """TC-VOICEVOX-001-04 — /speakers health/list: 壊れた応答は局所disable(例外にしない)。"""

    def fake_get_malformed(url: str, timeout: object = None) -> _FakeResponse:
        return _FakeResponse(json_data=[{"name": "no uuid", "styles": []}])

    malformed_client = VoicevoxHttpClient(session_get=fake_get_malformed)
    result_malformed = malformed_client.check_connectivity()
    assert result_malformed.available is False

    def fake_get_valid(url: str, timeout: object = None) -> _FakeResponse:
        return _FakeResponse(json_data=_speakers_json())

    valid_client = VoicevoxHttpClient(session_get=fake_get_valid)
    result_valid = valid_client.check_connectivity()
    assert result_valid.available is True
    assert result_valid.speaker_count == len(_speakers_json())


@pytest.mark.unit
def test_tc_voicevox_001_06() -> None:
    """TC-VOICEVOX-001-06 — /synthesis: 正常なrequestからSynthesisResultを生成する。"""
    audio_query_calls: list[dict] = []
    synthesis_calls: list[dict] = []
    client = _fake_client(audio_query_calls=audio_query_calls, synthesis_calls=synthesis_calls)
    adapter = VoicevoxAdapter(client=client)

    request = SynthesisRequest(request_id="r2", engine="voicevox", text="short text", speaker_id="8")
    result = adapter.synthesize(request)

    assert result.engine == "voicevox"
    assert result.speaker_id == "8"
    assert result.duration_seconds > 0
    assert len(audio_query_calls) == len(synthesis_calls)


@pytest.mark.unit
def test_tc_voicevox_001_08() -> None:
    """TC-VOICEVOX-001-08 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    adapter = VoicevoxAdapter()

    with pytest.raises(AppError):
        adapter.synthesize(None)  # type: ignore[arg-type]

    wrong_engine_request = SynthesisRequest(request_id="r1", engine="coeiroink", text="hi", speaker_id="1")
    with pytest.raises(AppError):
        adapter.synthesize(wrong_engine_request)

    non_numeric_speaker_request = SynthesisRequest(
        request_id="r1", engine="voicevox", text="hi", speaker_id="not-a-number"
    )
    with pytest.raises(TTSClientError):
        adapter.synthesize(non_numeric_speaker_request)


@pytest.mark.unit
def test_tc_voicevox_001_10() -> None:
    """TC-VOICEVOX-001-10 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    audio_query_calls: list[dict] = []
    synthesis_calls: list[dict] = []
    client = _fake_client(audio_query_calls=audio_query_calls, synthesis_calls=synthesis_calls)
    adapter = VoicevoxAdapter(client=client)

    good_request = SynthesisRequest(request_id="r1", engine="voicevox", text="hello", speaker_id="8")
    result = adapter.synthesize(good_request)
    before = (result.request_id, result.output_path, result.duration_seconds)

    bad_request = SynthesisRequest(request_id="r2", engine="voicevox", text="hi", speaker_id="not-a-number")
    with pytest.raises(TTSClientError):
        adapter.synthesize(bad_request)

    assert (result.request_id, result.output_path, result.duration_seconds) == before


@pytest.mark.integration_live
def test_tc_voicevox_001_12(voicevox_connectivity_gate) -> None:
    """TC-VOICEVOX-001-12 — VOICEVOX Engine APIの実機能テスト

    Contract: docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md
    Priority: P1
    Layer: integration_live
    Given: `voicevox_connectivity_gate`が成功済み
    When: 疎通成功後、短い固定文で`/audio_query`→`/synthesis`を1回実行し、RIFF/WAVEとして読める音声を確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    assert voicevox_connectivity_gate.available is True

    client = VoicevoxHttpClient()
    speakers = client.list_speakers()
    assert speakers

    adapter = VoicevoxAdapter(client=client)
    request = SynthesisRequest(
        request_id="live-smoke-r0001",
        engine="voicevox",
        text="こんにちは。",
        speaker_id=speakers[0].speaker_id,
    )
    result = adapter.synthesize(request)

    assert result.duration_seconds > 0
    assert result.sample_rate_hz > 0
