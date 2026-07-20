"""script/tts_clients/voicevox/adapter.py — 公開契約:
VoicevoxAdapter.synthesize(request) -> SynthesisResult.

Contract: docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md
Spec: docs/specifications/11-voicevox-client.md
"""

from __future__ import annotations

import io
import wave

from script.core.errors import AppError, ErrorCode
from script.tts_clients.base import TTSClientError, TTSErrorCode
from script.tts_clients.models import SynthesisRequest, SynthesisResult
from script.tts_clients.voicevox.client import (
    DEFAULT_MAX_TEXT_LENGTH,
    VoicevoxHttpClient,
    apply_voice_settings,
    split_text_for_voicevox,
)


class VoicevoxAdapter:
    """TTS共通parameterをVOICEVOXのaudio_query/synthesisへ適合し、part分割・結合を行う。"""

    def __init__(self, *, client: VoicevoxHttpClient | None = None, max_text_length: int = DEFAULT_MAX_TEXT_LENGTH) -> None:
        self._client = client or VoicevoxHttpClient()
        self._max_text_length = max_text_length

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """共通parameter、分割、結合、manifest情報へ適合する。"""
        if request is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request is required")
        if request.engine != "voicevox":
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unsupported engine for VoicevoxAdapter: {request.engine}")

        try:
            speaker_id = int(request.speaker_id)
        except (TypeError, ValueError) as exc:
            raise TTSClientError(
                TTSErrorCode.INVALID_PARAMETER,
                engine_detail=f"speaker_id must be an integer-like string: {request.speaker_id!r}",
            ) from exc

        chunks = split_text_for_voicevox(request.text, max_length=self._max_text_length) or [request.text]

        wav_chunks: list[bytes] = []
        for chunk in chunks:
            audio_query = self._client.create_audio_query(text=chunk, speaker_id=speaker_id)
            audio_query = apply_voice_settings(
                audio_query,
                speed_scale=request.parameters.speed_scale,
                pitch_scale=request.parameters.pitch_scale,
                intonation_scale=request.parameters.intonation_scale,
                volume_scale=request.parameters.volume_scale,
            )
            wav_chunks.append(self._client.synthesize_wave(audio_query=audio_query, speaker_id=speaker_id))

        merged = self._client.merge_waves(wav_chunks)

        with wave.open(io.BytesIO(merged), "rb") as wav_reader:
            sample_rate_hz = wav_reader.getframerate()
            channels = wav_reader.getnchannels()
            frame_count = wav_reader.getnframes()
            duration_seconds = frame_count / sample_rate_hz if sample_rate_hz else 0.0

        output_path = request.output_path or f"audio/cache/wav/segments/{request.request_id}.wav"

        return SynthesisResult(
            request_id=request.request_id,
            engine="voicevox",
            speaker_id=request.speaker_id,
            output_path=output_path,
            duration_seconds=round(duration_seconds, 3),
            sample_rate_hz=sample_rate_hz,
            channels=channels,
            audio_bytes=merged,
        )
