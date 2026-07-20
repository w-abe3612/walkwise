"""script/audio/preview.py — 公開契約: PreviewService.generate(request) -> PreviewAudio.

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Spec: docs/specifications/07-approval-workflow.md(preview_audio承認地点)
"""

from __future__ import annotations

from dataclasses import dataclass

from script.audio.synthesis import SegmentAudio
from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class PreviewRequest:
    """PreviewService.generate()への入力。"""

    project_id: str
    chapter_id: str
    segment_audios: tuple[SegmentAudio, ...]

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if not self.segment_audios:
            raise AppError(ErrorCode.VALIDATION_ERROR, "segment_audios must not be empty")


@dataclass(frozen=True)
class PreviewAudio:
    """PreviewService.generate()の戻り値。試聴音声は常に新versionとして生成される。"""

    preview_id: str
    project_id: str
    chapter_id: str
    version: int
    output_path: str
    duration_seconds: float
    segment_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.preview_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "preview_id is required")
        if self.version < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "version must be 1 or greater")
        if self.duration_seconds <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "duration_seconds must be greater than 0")


class PreviewService:
    """検証済み原稿由来のsegment音声から、1〜3分程度の試聴音声を新versionで生成する。"""

    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], int] = {}

    def generate(self, request: PreviewRequest) -> PreviewAudio:
        """1〜3分の試聴とmetadataを新versionで生成する。"""
        if request is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request is required")

        for segment_audio in request.segment_audios:
            if segment_audio.duration_seconds <= 0:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"segment_audio {segment_audio.segment_id} has invalid duration_seconds",
                )
            if segment_audio.sample_rate_hz <= 0:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"segment_audio {segment_audio.segment_id} has invalid sample_rate_hz",
                )

        total_duration = sum(segment_audio.duration_seconds for segment_audio in request.segment_audios)

        version_key = (request.project_id, request.chapter_id)
        next_version = self._versions.get(version_key, 0) + 1
        self._versions[version_key] = next_version

        preview_id = f"{request.chapter_id}-preview-r{next_version:04d}"
        output_path = f"audio/preview/{request.chapter_id}/{preview_id}.wav"

        return PreviewAudio(
            preview_id=preview_id,
            project_id=request.project_id,
            chapter_id=request.chapter_id,
            version=next_version,
            output_path=output_path,
            duration_seconds=round(total_duration, 3),
            segment_ids=tuple(segment_audio.segment_id for segment_audio in request.segment_audios),
        )
