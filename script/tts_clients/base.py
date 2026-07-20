"""script/tts_clients/base.py — 公開契約:
TTSClient Protocol: check_connectivity/list_speakers/synthesize,
TTSClientError(code, engine_detail).

Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
Spec: docs/specifications/10-tts-client-common-interface.md
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Protocol, runtime_checkable

from script.core.errors import AppError, ErrorCode
from script.tts_clients.models import EngineCapabilities, SpeakerInfo, SynthesisRequest, SynthesisResult


class TTSErrorCode(str, Enum):
    """10-tts-client-common-interface.md 7節の共通エラー(+9節のunsupported_engine)。"""

    CONNECTION_ERROR = "connection_error"
    HEALTH_CHECK_FAILED = "health_check_failed"
    SPEAKER_NOT_FOUND = "speaker_not_found"
    UNSUPPORTED_PARAMETER = "unsupported_parameter"
    INVALID_PARAMETER = "invalid_parameter"
    TEXT_EMPTY = "text_empty"
    TEXT_TOO_LONG = "text_too_long"
    QUERY_FAILED = "query_failed"
    SYNTHESIS_FAILED = "synthesis_failed"
    INVALID_AUDIO_RESPONSE = "invalid_audio_response"
    AUDIO_FORMAT_MISMATCH = "audio_format_mismatch"
    TIMEOUT = "timeout"
    OUTPUT_WRITE_FAILED = "output_write_failed"
    UNSUPPORTED_ENGINE = "unsupported_engine"


class TTSClientError(RuntimeError):
    """engine固有例外を共通error codeへ変換する。"""

    def __init__(self, code: TTSErrorCode, engine_detail: str | None = None) -> None:
        message = f"TTS error: {code.value}"
        if engine_detail:
            message = f"{message} ({engine_detail})"
        super().__init__(message)
        self.code = code
        self.engine_detail = engine_detail


@runtime_checkable
class TTSClient(Protocol):
    """疎通、capabilities取得、話者一覧、合成を分離する共通契約。"""

    engine_name: str

    def check_connectivity(self) -> bool:
        """認証・起動確認を含む軽量な疎通確認を副作用なく行う。"""
        ...

    def get_capabilities(self) -> EngineCapabilities:
        """このengineが対応するparameter/機能を返す。"""
        ...

    def list_speakers(self) -> list[SpeakerInfo]:
        """利用可能なspeaker一覧をengineの識別子付きで返す。"""
        ...

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """promptを合成しSynthesisResultへ変換する。"""
        ...


class MockTTSClient:
    """外部接続なしの決定的TTSClient実装(smoke/dev/テスト用)。"""

    engine_name = "mock"

    def __init__(self, *, speakers: Sequence[SpeakerInfo] = ()) -> None:
        self._speakers = tuple(speakers) or (
            SpeakerInfo(speaker_id="mock-speaker-1", display_name="Mock Speaker", engine=self.engine_name),
        )

    def check_connectivity(self) -> bool:
        return True

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(engine=self.engine_name)

    def list_speakers(self) -> list[SpeakerInfo]:
        return list(self._speakers)

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        if request is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request is required")
        if not any(speaker.speaker_id == request.speaker_id for speaker in self._speakers):
            raise TTSClientError(TTSErrorCode.SPEAKER_NOT_FOUND, engine_detail=request.speaker_id)

        return SynthesisResult(
            request_id=request.request_id,
            engine=self.engine_name,
            speaker_id=request.speaker_id,
            output_path=request.output_path or f"mock/{request.request_id}.wav",
            duration_seconds=round(max(0.1, len(request.text) * 0.06), 3),
            sample_rate_hz=24000,
            channels=1,
        )
