"""STEP4 test implementation for TASK-TTS-001: TTSClient Protocol / TTSClientError contract.

Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.tts_clients.base import MockTTSClient, TTSClient, TTSClientError, TTSErrorCode
from script.tts_clients.models import SpeakerInfo, SynthesisRequest
from script.tts_clients.registry import TTSClientRegistry

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_tts_001_01() -> None:
    """TC-TTS-001-01 — registry: voicevox client登録 → get → 同一instance/contractを返す。"""
    client = MockTTSClient()
    registry = TTSClientRegistry()
    registry.register("voicevox", client)

    resolved = registry.get("voicevox")

    assert resolved is client
    assert isinstance(resolved, TTSClient)


@pytest.mark.unit
def test_tc_tts_001_03() -> None:
    """TC-TTS-001-03 — 共通error: engine固有timeoutを上位へTTSClientError(code=timeout)として変換する。"""

    class _TimeoutProneClient:
        engine_name = "flaky"

        def check_connectivity(self) -> bool:
            return True

        def get_capabilities(self):  # noqa: ANN201 - test double
            raise NotImplementedError

        def list_speakers(self) -> list[SpeakerInfo]:
            return [SpeakerInfo(speaker_id="s1", display_name="Speaker", engine=self.engine_name)]

        def synthesize(self, request: SynthesisRequest):
            try:
                raise TimeoutError("engine socket timed out after 30s")
            except TimeoutError as exc:
                raise TTSClientError(TTSErrorCode.TIMEOUT, engine_detail=str(exc)) from exc

    client = _TimeoutProneClient()
    request = SynthesisRequest(request_id="r1", engine="flaky", text="hello", speaker_id="s1")

    with pytest.raises(TTSClientError) as excinfo:
        client.synthesize(request)

    assert excinfo.value.code is TTSErrorCode.TIMEOUT
    assert "timed out" in excinfo.value.engine_detail


@pytest.mark.unit
def test_tc_tts_001_05() -> None:
    """TC-TTS-001-05 — health_check: 疎通確認は副作用なくbool/失敗codeを返す。"""
    healthy_client = MockTTSClient()
    assert healthy_client.check_connectivity() is True

    class _UnhealthyClient:
        engine_name = "down"

        def check_connectivity(self) -> bool:
            raise TTSClientError(TTSErrorCode.HEALTH_CHECK_FAILED, engine_detail="connection refused")

        def get_capabilities(self):  # noqa: ANN201 - test double
            raise NotImplementedError

        def list_speakers(self) -> list[SpeakerInfo]:
            return []

        def synthesize(self, request: SynthesisRequest):
            raise NotImplementedError

    with pytest.raises(TTSClientError) as excinfo:
        _UnhealthyClient().check_connectivity()
    assert excinfo.value.code is TTSErrorCode.HEALTH_CHECK_FAILED


@pytest.mark.unit
def test_tc_tts_001_07() -> None:
    """TC-TTS-001-07 — synthesize: 正常なrequestからSynthesisResultを生成する。"""
    client = MockTTSClient()
    request = SynthesisRequest(
        request_id="synth-ch01-seg001-r0001", engine="mock", text="hello world", speaker_id="mock-speaker-1"
    )

    result = client.synthesize(request)

    assert result.request_id == request.request_id
    assert result.engine == "mock"
    assert result.speaker_id == "mock-speaker-1"
    assert result.duration_seconds > 0
    assert result.sample_rate_hz == 24000


@pytest.mark.unit
def test_tc_tts_001_09() -> None:
    """TC-TTS-001-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    client = MockTTSClient()
    request = SynthesisRequest(request_id="r1", engine="mock", text="deterministic text", speaker_id="mock-speaker-1")

    result_1 = client.synthesize(request)
    result_2 = client.synthesize(request)

    assert result_1 == result_2
