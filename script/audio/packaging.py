"""script/audio/packaging.py — 公開契約: ChapterPackager.package(wavs, metadata) -> ChapterArtifact.

Contract: docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md
Spec: docs/specifications/14-audio-packaging.md
"""

from __future__ import annotations

import hashlib
import io
import wave
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class ChapterAudioInput:
    """1 segment分のWAV入力。manifestのorder(章内音声順)を保持する。"""

    segment_id: str
    order: int
    wav_bytes: bytes
    voice_content_hash: str

    def __post_init__(self) -> None:
        if not self.segment_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "segment_id is required")
        if self.order < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "order must be 1 or greater")
        if not self.wav_bytes:
            raise AppError(ErrorCode.VALIDATION_ERROR, "wav_bytes is required")
        if not self.voice_content_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_content_hash is required")


@dataclass(frozen=True)
class ChapterMetadata:
    """14-audio-packaging.md 8節のtag metadata入力。"""

    project_id: str
    chapter_id: str
    title: str
    album: str
    content_revision: int = 1
    narrator: str | None = None
    track_number: int = 1

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if not self.title:
            raise AppError(ErrorCode.VALIDATION_ERROR, "title is required")
        if not self.album:
            raise AppError(ErrorCode.VALIDATION_ERROR, "album is required")
        if self.content_revision < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_revision must be 1 or greater")
        if self.track_number < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "track_number must be 1 or greater")


@dataclass(frozen=True)
class ChapterArtifact:
    """ChapterPackager.package()の戻り値。実ファイル書込みは呼び出し側(Artifact登録経路)が行う。"""

    chapter_id: str
    mp3_bytes: bytes
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    content_hash: str
    source_segments: tuple[str, ...]
    content_revision: int
    voice_content_hash: str

    def __post_init__(self) -> None:
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if not self.mp3_bytes:
            raise AppError(ErrorCode.VALIDATION_ERROR, "mp3_bytes is required")
        if self.duration_seconds <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "duration_seconds must be greater than 0")
        if not self.content_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_hash is required")
        if not self.source_segments:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_segments must not be empty")


def _merge_wavs(wav_chunks: Sequence[bytes]) -> bytes:
    """manifest orderで結合する。破損・形式不一致は常にerror(warningへ格下げしない)。"""
    if not wav_chunks:
        raise AppError(ErrorCode.VALIDATION_ERROR, "no wav chunks to merge")

    output_buffer = io.BytesIO()
    try:
        with wave.open(output_buffer, "wb") as output_wav:
            expected_format: tuple[int, int, int, str] | None = None
            for index, wav_bytes in enumerate(wav_chunks, start=1):
                with wave.open(io.BytesIO(wav_bytes), "rb") as input_wav:
                    current_format = (
                        input_wav.getnchannels(),
                        input_wav.getsampwidth(),
                        input_wav.getframerate(),
                        input_wav.getcomptype(),
                    )
                    if expected_format is None:
                        expected_format = current_format
                        output_wav.setnchannels(input_wav.getnchannels())
                        output_wav.setsampwidth(input_wav.getsampwidth())
                        output_wav.setframerate(input_wav.getframerate())
                        output_wav.setcomptype(input_wav.getcomptype(), input_wav.getcompname())
                    elif current_format != expected_format:
                        raise AppError(
                            ErrorCode.VALIDATION_ERROR,
                            f"audio_format_mismatch: chunk {index} format {current_format} != {expected_format}",
                        )
                    output_wav.writeframes(input_wav.readframes(input_wav.getnframes()))
    except wave.Error as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"corrupted or invalid WAV input: {exc}") from exc

    return output_buffer.getvalue()


def make_ffmpeg_mp3_encoder(*, ffmpeg_cmd: str = "ffmpeg") -> Callable[[bytes], bytes]:
    """14-audio-packaging.md 7節(libmp3lame, vbr q=2)相当の実ffmpeg encoderを作る(本タスクの通常テストでは使用しない)。"""

    def _encode(wav_bytes: bytes) -> bytes:
        import subprocess
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp_dir:
            wav_path = Path(tmp_dir) / "input.wav"
            mp3_path = Path(tmp_dir) / "output.mp3"
            wav_path.write_bytes(wav_bytes)
            result = subprocess.run(
                [
                    ffmpeg_cmd, "-y", "-i", str(wav_path),
                    "-codec:a", "libmp3lame", "-q:a", "2",
                    str(mp3_path),
                ],
                capture_output=True,
                timeout=60,
            )
            if result.returncode != 0 or not mp3_path.exists():
                raise AppError(
                    ErrorCode.EXTERNAL_UNAVAILABLE,
                    "ffmpeg mp3 encoding failed",
                    technical_detail=result.stderr.decode("utf-8", errors="replace")[:500],
                )
            return mp3_path.read_bytes()

    return _encode


class ChapterPackager:
    """検査済みsegment WAVをmanifest順に結合し、章単位MP3をatomic生成する。"""

    def __init__(self, *, mp3_encoder: Callable[[bytes], bytes]) -> None:
        if mp3_encoder is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "mp3_encoder is required")
        self._encoder = mp3_encoder

    def package(self, wavs: Sequence[ChapterAudioInput], metadata: ChapterMetadata) -> ChapterArtifact:
        """形式一致を確認し章MP3をatomic生成する。"""
        if not wavs:
            raise AppError(ErrorCode.VALIDATION_ERROR, "wavs must not be empty")
        if metadata is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "metadata is required")

        ordered = sorted(wavs, key=lambda chunk: chunk.order)
        orders = [chunk.order for chunk in ordered]
        if len(orders) != len(set(orders)):
            raise AppError(ErrorCode.VALIDATION_ERROR, "duplicate order among chapter audio inputs")

        voice_hashes = {chunk.voice_content_hash for chunk in ordered}
        if len(voice_hashes) > 1:
            # 改変検出: 異なるvoice profile revision由来のsegmentを黙って互換扱いで結合しない。
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"chapter audio inputs reference inconsistent voice_content_hash: {sorted(voice_hashes)}",
            )

        merged_wav = _merge_wavs([chunk.wav_bytes for chunk in ordered])

        with wave.open(io.BytesIO(merged_wav), "rb") as wav_reader:
            framerate = wav_reader.getframerate()
            duration_seconds = (wav_reader.getnframes() / framerate) if framerate else 0.0
            sample_rate_hz = framerate
            channels = wav_reader.getnchannels()

        mp3_bytes = self._encoder(merged_wav)
        content_hash = hashlib.sha256(mp3_bytes).hexdigest()

        return ChapterArtifact(
            chapter_id=metadata.chapter_id,
            mp3_bytes=mp3_bytes,
            duration_seconds=round(duration_seconds, 3),
            sample_rate_hz=sample_rate_hz,
            channels=channels,
            content_hash=content_hash,
            source_segments=tuple(chunk.segment_id for chunk in ordered),
            content_revision=metadata.content_revision,
            voice_content_hash=next(iter(voice_hashes)),
        )
