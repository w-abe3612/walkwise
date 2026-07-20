"""script/audio/synthesis.py — 公開契約:
SegmentSynthesizer.synthesize(script, profile) -> list[SegmentAudio].

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Spec: docs/specifications/05-script-segment-schema.md(11節: TTS内部分割)
"""

from __future__ import annotations

import contextlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from script.audio.cache import AudioCache, CachedAudio
from script.core.errors import AppError, ErrorCode
from script.schemas.profiles import VoiceProfile
from script.schemas.script import ScriptDocument
from script.tts_clients.base import TTSClient
from script.tts_clients.models import SynthesisRequest

_DEFAULT_MAX_TEXT_LENGTH = 300
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？!?.])\s*")


def _split_into_parts(text: str, *, max_length: int) -> list[str]:
    """05-script-segment-schema.md 11節: 300文字超のsegmentを内部partへ分割する(句読点優先)。"""
    if len(text) <= max_length:
        return [text]

    sentences = [sentence for sentence in _SENTENCE_SPLIT_RE.split(text) if sentence.strip()] or [text]

    parts: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = current + sentence
        if len(candidate) <= max_length:
            current = candidate
            continue

        if current:
            parts.append(current)
            current = ""

        if len(sentence) > max_length:
            for start in range(0, len(sentence), max_length):
                parts.append(sentence[start : start + max_length])
        else:
            current = sentence

    if current:
        parts.append(current)
    return parts


def _atomic_write(path: Path, data: bytes) -> None:
    """一時ファイルへ書き、検査後にatomic renameする(02-process-input-output.md 13節)。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            tmp_file.write(data)
        os.replace(tmp_name, str(path))
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.remove(tmp_name)
        raise


@dataclass(frozen=True)
class SegmentAudioPart:
    """300文字超segmentの内部part(manifestだけに記録し原稿YAMLへは恒久追加しない)。"""

    part_id: str
    output_path: str
    duration_seconds: float


@dataclass(frozen=True)
class SegmentAudio:
    """SegmentSynthesizer.synthesize()の1segment分の戻り値。"""

    segment_id: str
    audio_id: str
    output_path: str
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    parts: tuple[SegmentAudioPart, ...] = ()
    cache_hit: bool = False

    def __post_init__(self) -> None:
        if not self.segment_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "segment_id is required")
        if not self.audio_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "audio_id is required")
        if self.duration_seconds < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "duration_seconds must not be negative")
        if self.sample_rate_hz <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "sample_rate_hz must be greater than 0")


class SegmentSynthesizer:
    """承認済み(verified)scriptから、tts_text優先・cache・atomic出力でsegment WAVを生成する。"""

    def __init__(
        self,
        *,
        tts_client: TTSClient,
        cache: AudioCache | None = None,
        max_text_length: int = _DEFAULT_MAX_TEXT_LENGTH,
        output_dir: Path | None = None,
    ) -> None:
        if tts_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "tts_client is required")
        self._client = tts_client
        self._cache = cache if cache is not None else AudioCache()
        self._max_text_length = max_text_length
        self._output_dir = output_dir

    def synthesize(self, script: ScriptDocument, profile: VoiceProfile) -> list[SegmentAudio]:
        """TTS clientを通じてsegment/part WAVを生成する。"""
        if script is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script is required")
        if profile is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "profile is required")
        if not script.segments:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script.segments must not be empty")
        if script.stage != "verified":
            # 未承認script本番禁止: verified stage以外からの本番TTSを拒否する。
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"production TTS requires a verified script, got stage={script.stage!r}",
            )

        voice_content_hash = profile.content_hash()
        results: list[SegmentAudio] = []
        for segment in script.segments:
            results.append(self._synthesize_segment(segment, profile, voice_content_hash))
        return results

    def _synthesize_segment(self, segment, profile: VoiceProfile, voice_content_hash: str) -> SegmentAudio:
        # tts_text優先: tts_textがあればそれを、なければtextを使う。
        text_for_tts = segment.tts_text if segment.tts_text else segment.text

        cache_key = self._cache.key(
            text=segment.text,
            tts_text=segment.tts_text,
            voice_profile_id=profile.voice_profile_id,
            voice_content_hash=voice_content_hash,
            engine_version=profile.engine_identity.engine_version,
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return SegmentAudio(
                segment_id=segment.segment_id,
                audio_id=cache_key.value,
                output_path=cached.output_path,
                duration_seconds=cached.duration_seconds,
                sample_rate_hz=cached.sample_rate_hz,
                channels=cached.channels,
                cache_hit=True,
            )

        part_texts = _split_into_parts(text_for_tts, max_length=self._max_text_length)
        parts: list[SegmentAudioPart] = []
        total_duration = 0.0
        sample_rate_hz = 0
        channels = 1

        for index, part_text in enumerate(part_texts, start=1):
            part_id = f"{segment.segment_id}-part{index:03d}"
            request = SynthesisRequest(
                request_id=part_id,
                engine=profile.engine,
                text=part_text,
                speaker_id=profile.speaker.id,
                output_path=f"audio/cache/wav/segments/{part_id}.wav",
            )
            result = self._client.synthesize(request)

            if self._output_dir is not None and result.audio_bytes is not None:
                _atomic_write(self._output_dir / f"{part_id}.wav", result.audio_bytes)

            parts.append(
                SegmentAudioPart(part_id=part_id, output_path=result.output_path, duration_seconds=result.duration_seconds)
            )
            total_duration += result.duration_seconds
            sample_rate_hz = result.sample_rate_hz
            channels = result.channels

        output_path = f"audio/cache/wav/segments/{segment.segment_id}.wav"
        segment_audio = SegmentAudio(
            segment_id=segment.segment_id,
            audio_id=cache_key.value,
            output_path=output_path,
            duration_seconds=round(total_duration, 3),
            sample_rate_hz=sample_rate_hz,
            channels=channels,
            parts=tuple(parts),
            cache_hit=False,
        )
        self._cache.put(
            cache_key,
            CachedAudio(
                key=cache_key,
                output_path=segment_audio.output_path,
                duration_seconds=segment_audio.duration_seconds,
                sample_rate_hz=segment_audio.sample_rate_hz,
                channels=segment_audio.channels,
            ),
        )
        return segment_audio
