"""script/tts_clients/models.py — 公開契約:
SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities.

Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
Spec: docs/specifications/10-tts-client-common-interface.md
"""

from __future__ import annotations

from dataclasses import dataclass, field

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class SynthesisParameters:
    """10-tts-client-common-interface.md 4節のparameters。"""

    speed_scale: float = 1.0
    pitch_scale: float = 0.0
    intonation_scale: float = 1.0
    volume_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.speed_scale <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speed_scale must be greater than 0")
        if self.volume_scale <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "volume_scale must be greater than 0")


@dataclass(frozen=True)
class SynthesisRequest:
    """TTSClient.synthesize()への共通入力。"""

    request_id: str
    engine: str
    text: str
    speaker_id: str
    parameters: SynthesisParameters = field(default_factory=SynthesisParameters)
    output_path: str | None = None
    project_id: str | None = None
    chapter_id: str | None = None
    segment_id: str | None = None

    def __post_init__(self) -> None:
        if not self.request_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request_id is required")
        if not self.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        if not self.text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")
        if not self.speaker_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speaker_id is required")


@dataclass(frozen=True)
class SynthesisResult:
    """TTSClient.synthesize()の共通出力。"""

    request_id: str
    engine: str
    speaker_id: str
    output_path: str
    duration_seconds: float
    sample_rate_hz: int
    channels: int = 1
    engine_version: str | None = None
    warnings: tuple[str, ...] = ()
    audio_bytes: bytes | None = None

    def __post_init__(self) -> None:
        if not self.request_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request_id is required")
        if not self.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        if not self.output_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "output_path is required")
        if self.duration_seconds < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "duration_seconds must not be negative")
        if self.sample_rate_hz <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "sample_rate_hz must be greater than 0")
        if self.channels <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "channels must be greater than 0")


@dataclass(frozen=True)
class SpeakerInfo:
    """TTSClient.list_speakers()の1件。表示名ではなくspeaker_id(engineの識別子)で解決する。"""

    speaker_id: str
    display_name: str
    engine: str
    style_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.speaker_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speaker_id is required")
        if not self.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")


@dataclass(frozen=True)
class EngineCapabilities:
    """10-tts-client-common-interface.md 6節のcapabilities。"""

    engine: str
    supports_speed_scale: bool = True
    supports_pitch_scale: bool = True
    supports_intonation_scale: bool = True
    supports_volume_scale: bool = True
    supports_speaker_listing: bool = True
    supports_accent_phrase_editing: bool = False
    supports_streaming: bool = False
    recommended_max_text_length: int = 300

    def __post_init__(self) -> None:
        if not self.engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        if self.recommended_max_text_length <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "recommended_max_text_length must be greater than 0")
