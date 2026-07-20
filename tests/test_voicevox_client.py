"""STEP4 test implementation for TASK-VOICEVOX-001: VoicevoxHttpClient.

Contract: docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md
Release scope: MVP
"""

from __future__ import annotations

import io
import wave

import pytest
import requests

from script.tts_clients.base import TTSClientError, TTSErrorCode
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


_SPEAKERS_RESPONSE = [
    {"speaker_uuid": "uuid-1", "name": "春日部つむぎ", "styles": [{"id": 8, "name": "ノーマル"}]},
    {
        "speaker_uuid": "uuid-2",
        "name": "四国めたん",
        "styles": [{"id": 2, "name": "ノーマル"}, {"id": 0, "name": "あまあま"}],
    },
]


@pytest.mark.integration_mock
def test_tc_voicevox_001_01() -> None:
    """TC-VOICEVOX-001-01 — speaker変換: UUID/name/style IDを保持し表示名分岐しない。"""

    def fake_get(url: str, timeout: object = None) -> _FakeResponse:
        assert url.endswith("/speakers")
        return _FakeResponse(json_data=_SPEAKERS_RESPONSE)

    client = VoicevoxHttpClient(session_get=fake_get)

    speakers = client.list_speakers()

    speaker_ids = {speaker.speaker_id for speaker in speakers}
    assert speaker_ids == {"8", "2", "0"}
    assert all(speaker.engine == "voicevox" for speaker in speakers)
    # 表示名で分岐しない: 同じ話者名でも異なるstyle_idごとに別レコードとして保持する。
    assert len(speakers) == len(speaker_ids)


@pytest.mark.unit
def test_tc_voicevox_001_03() -> None:
    """TC-VOICEVOX-001-03 — format不一致: 異なるsample rateの2WAVをmergeするとaudio_format_mismatch。"""
    client = VoicevoxHttpClient()
    wav_a = _make_wav_bytes(framerate=24000)
    wav_b = _make_wav_bytes(framerate=48000)

    with pytest.raises(TTSClientError) as excinfo:
        client.merge_waves([wav_a, wav_b])

    assert excinfo.value.code is TTSErrorCode.AUDIO_FORMAT_MISMATCH


@pytest.mark.unit
def test_tc_voicevox_001_05() -> None:
    """TC-VOICEVOX-001-05 — /audio_query: 破損・形式不一致の応答を成功扱いにしない。"""

    def fake_post_invalid_json(url: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(status_code=200, content=b"not json")

    with pytest.raises(TTSClientError) as excinfo_invalid_json:
        VoicevoxHttpClient(session_post=fake_post_invalid_json).create_audio_query(text="hello", speaker_id=1)
    assert excinfo_invalid_json.value.code is TTSErrorCode.QUERY_FAILED

    def fake_post_non_object(url: str, **kwargs: object) -> _FakeResponse:
        return _FakeResponse(status_code=200, json_data=["not", "an", "object"])

    with pytest.raises(TTSClientError) as excinfo_non_object:
        VoicevoxHttpClient(session_post=fake_post_non_object).create_audio_query(text="hello", speaker_id=1)
    assert excinfo_non_object.value.code is TTSErrorCode.QUERY_FAILED

    with pytest.raises(TTSClientError) as excinfo_empty_text:
        VoicevoxHttpClient().create_audio_query(text="   ", speaker_id=1)
    assert excinfo_empty_text.value.code is TTSErrorCode.TEXT_EMPTY


@pytest.mark.unit
def test_tc_voicevox_001_07() -> None:
    """TC-VOICEVOX-001-07 — timeout/error変換: timeoutを安定した共通errorへ変換し、半端な状態を残さない。"""

    def fake_get_timeout(url: str, timeout: object = None) -> _FakeResponse:
        raise requests.Timeout("read timed out after 10s")

    client = VoicevoxHttpClient(session_get=fake_get_timeout)

    with pytest.raises(TTSClientError) as excinfo:
        client.list_speakers()
    assert excinfo.value.code is TTSErrorCode.TIMEOUT

    # check_connectivity()はtimeoutを例外にせず、失敗を示すConnectivityResultへ変換する。
    result = client.check_connectivity()
    assert result.available is False
    assert "timeout" in result.detail.lower()


@pytest.mark.unit
def test_tc_voicevox_001_09() -> None:
    """TC-VOICEVOX-001-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    calls: list[str] = []

    def fake_get(url: str, timeout: object = None) -> _FakeResponse:
        calls.append(url)
        return _FakeResponse(json_data=_SPEAKERS_RESPONSE)

    client = VoicevoxHttpClient(session_get=fake_get)

    result_1 = client.check_connectivity()
    result_2 = client.check_connectivity()

    assert result_1 == result_2
    assert len(calls) == 2


@pytest.mark.integration_smoke
def test_tc_voicevox_001_11(voicevox_connectivity_gate) -> None:
    """TC-VOICEVOX-001-11 — VOICEVOX Engine APIの疎通確認

    Contract: docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: `GET /speakers`を1回実行し、HTTP成功、1件以上のspeaker、UUID・style IDを含むJSON配列を確認する。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert voicevox_connectivity_gate.available is True
    assert voicevox_connectivity_gate.speaker_count is not None
    assert voicevox_connectivity_gate.speaker_count >= 1
