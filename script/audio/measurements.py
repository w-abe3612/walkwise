"""script/audio/measurements.py — 公開契約:
AudioMeasurementAdapter.check_runtime()/measure(path).

Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
Spec: docs/specifications/13-audio-validation.md(4節: 初期必須検査)
"""

from __future__ import annotations

import math
import struct
import subprocess
import wave
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from script.core.errors import AppError, ErrorCode

_SAMPLE_FORMAT_BY_WIDTH = {1: "b", 2: "h", 4: "i"}
_MAX_VALUE_BY_WIDTH = {1: 127, 2: 32767, 4: 2147483647}
_SILENCE_AMPLITUDE_RATIO = 0.01


@dataclass(frozen=True)
class RuntimeCheckResult:
    """副作用のない疎通確認結果(ffmpeg/ffprobeの起動可否だけを確認する)。"""

    available: bool
    detail: str = ""
    ffmpeg_version: str | None = None
    ffprobe_version: str | None = None


@dataclass(frozen=True)
class AudioMeasurement:
    """1音声ファイルの測定結果。peak/silence_ratio/lufsは測定不能な場合Noneを許可する。"""

    duration_seconds: float
    sample_rate_hz: int
    channels: int
    peak_dbfs: float | None = None
    silence_ratio: float | None = None
    lufs: float | None = None


def _first_line(text: str | None) -> str | None:
    if not text:
        return None
    return text.splitlines()[0].strip() or None


def _measure_samples(raw_frames: bytes, sample_width: int) -> tuple[float | None, float | None]:
    """peak(dBFS)とsilence_ratioを生PCMから決定的に計算する(ffmpegなしで動作)。"""
    fmt = _SAMPLE_FORMAT_BY_WIDTH.get(sample_width)
    if fmt is None or not raw_frames:
        return None, None

    sample_count = len(raw_frames) // sample_width
    if sample_count == 0:
        return None, None

    samples = struct.unpack(f"<{sample_count}{fmt}", raw_frames[: sample_count * sample_width])
    max_value = _MAX_VALUE_BY_WIDTH[sample_width]
    peak = max(abs(sample) for sample in samples)
    peak_dbfs = 20 * math.log10(peak / max_value) if peak > 0 else -math.inf

    silence_threshold = max_value * _SILENCE_AMPLITUDE_RATIO
    silent_count = sum(1 for sample in samples if abs(sample) < silence_threshold)
    silence_ratio = silent_count / len(samples)

    return peak_dbfs, silence_ratio


class AudioMeasurementAdapter:
    """ffprobe/ffmpeg利用可能性確認(疎通)と、WAVの構造的測定を分離する。"""

    def __init__(
        self,
        *,
        ffmpeg_cmd: str = "ffmpeg",
        ffprobe_cmd: str = "ffprobe",
        runner: Callable[..., subprocess.CompletedProcess] | None = None,
    ) -> None:
        self._ffmpeg_cmd = ffmpeg_cmd
        self._ffprobe_cmd = ffprobe_cmd
        self._runner = runner or subprocess.run

    def check_runtime(self) -> RuntimeCheckResult:
        """`ffmpeg -version`/`ffprobe -version`を実行し、実行可能・version取得可能か確認する。"""
        try:
            ffmpeg_result = self._run_version_command(self._ffmpeg_cmd)
            ffprobe_result = self._run_version_command(self._ffprobe_cmd)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return RuntimeCheckResult(available=False, detail=str(exc))

        if ffmpeg_result.returncode != 0 or ffprobe_result.returncode != 0:
            return RuntimeCheckResult(available=False, detail="ffmpeg/ffprobe -version returned a non-zero exit code")

        return RuntimeCheckResult(
            available=True,
            ffmpeg_version=_first_line(ffmpeg_result.stdout),
            ffprobe_version=_first_line(ffprobe_result.stdout),
        )

    def _run_version_command(self, command: str) -> subprocess.CompletedProcess:
        return self._runner([command, "-version"], capture_output=True, text=True, timeout=10)

    def measure(self, path: Path | str) -> AudioMeasurement:
        """WAVファイルの構造(duration/sample_rate/channels)とpeak/silenceを測定する。"""
        if path is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")

        resolved_path = Path(path)
        if not resolved_path.exists() or resolved_path.stat().st_size == 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"audio file is missing or empty: {resolved_path}")

        try:
            with wave.open(str(resolved_path), "rb") as wav_file:
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                raw_frames = wav_file.readframes(n_frames)
        except (wave.Error, EOFError) as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"audio file is not a valid WAV: {exc}") from exc

        duration_seconds = (n_frames / framerate) if framerate else 0.0
        peak_dbfs, silence_ratio = _measure_samples(raw_frames, sample_width)

        return AudioMeasurement(
            duration_seconds=round(duration_seconds, 3),
            sample_rate_hz=framerate,
            channels=channels,
            peak_dbfs=peak_dbfs,
            silence_ratio=silence_ratio,
        )
