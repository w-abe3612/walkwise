"""script/asr/base.py — 公開契約: ASRClient Protocol: check_connectivity()/transcribe().

Contract: docs/test-cases/TASK-ASR-001-asr-script-audio-verification.md
Spec: docs/specifications/asr-script-audio-verification.md(5.3, 5.6節)
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class ASRConnectivityResult:
    """疎通確認結果(local runtime/modelの存在・読込可否)。副作用なし。"""

    available: bool
    version: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class ASRSegment:
    """1文字起こしsegment。"""

    start_seconds: float
    end_seconds: float
    text: str


@dataclass(frozen=True)
class ASRTranscript:
    """`transcribe()`の戻り値。"""

    segments: tuple[ASRSegment, ...]
    provider: str
    provider_version: str | None = None


@runtime_checkable
class ASRClient(Protocol):
    """local runtime/model確認と文字起こしを分離する共通契約(cloud未使用)。"""

    def check_connectivity(self) -> ASRConnectivityResult:
        """認証を含まない軽量な疎通確認を副作用なく行う。"""
        ...

    def transcribe(self, audio_path: Path) -> ASRTranscript:
        """音声をローカルで文字起こしする(外部へは送信しない)。"""
        ...


def _first_line(text: str | None) -> str | None:
    if not text:
        return None
    lines = text.splitlines()
    return lines[0].strip() if lines else None


class LocalWhisperCompatibleClient:
    """ローカルWhisper互換CLIをsubprocess経由で呼び出すadapter(5.3節、クラウドは使用しない)。"""

    def __init__(
        self,
        *,
        command: str = "whisper",
        runner: Callable[..., subprocess.CompletedProcess] | None = None,
    ) -> None:
        self._command = command
        self._runner = runner or subprocess.run

    def check_connectivity(self) -> ASRConnectivityResult:
        """`<command> --version`相当を実行し、runtime/modelの読込可否を確認する。文字起こしは行わない。"""
        try:
            completed = self._runner([self._command, "--version"], capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return ASRConnectivityResult(available=False, error=str(exc))

        if completed.returncode != 0:
            return ASRConnectivityResult(available=False, error="ASR runtime --version returned a non-zero exit code")

        return ASRConnectivityResult(available=True, version=_first_line(completed.stdout))

    def transcribe(self, audio_path: Any) -> ASRTranscript:
        """ローカルCLIで音声を文字起こしする(既定で外部送信は一切行わない、5.6節)。"""
        if not audio_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "audio_path is required")
        resolved = Path(audio_path)
        if not resolved.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"audio file not found: {resolved}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            command = [self._command, str(resolved), "--output_format", "json", "--output_dir", tmp_dir]
            completed = self._runner(command, capture_output=True, text=True, timeout=120)
            if completed.returncode != 0:
                raise AppError(
                    ErrorCode.INTERNAL_ERROR,
                    "local ASR transcription failed",
                    technical_detail=(completed.stderr or "").strip() or None,
                )

            output_json = Path(tmp_dir) / f"{resolved.stem}.json"
            if not output_json.is_file():
                raise AppError(ErrorCode.INTERNAL_ERROR, f"expected ASR output file not found: {output_json}")
            payload = json.loads(output_json.read_text(encoding="utf-8"))

        segments = tuple(
            ASRSegment(
                start_seconds=float(segment["start"]),
                end_seconds=float(segment["end"]),
                text=str(segment["text"]).strip(),
            )
            for segment in payload.get("segments", [])
        )
        return ASRTranscript(segments=segments, provider="local_whisper_compatible")
