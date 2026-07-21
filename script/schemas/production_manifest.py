"""script/schemas/production_manifest.py — 公開契約:
ProductionManifest.validate()/to_mapping().

Contract: docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md
Spec: docs/specifications/14-audio-packaging.md(10節: manifest), docs/db/06-voice-profiles-table.md

TASK-BUILD-EXEC-001(13節): voice_profile_snapshot/voice_profile_config_hash/
chapter_order/verified_script_paths/verified_script_content_hashes/output_formats/
build_request_id/job_id/created_atは既存consumer/testsとの後方互換を保つため
全てoptionalとし、未指定時は従来通りの出力になる(schemas層はservices層に
依存しないため、voice_profile_snapshotはVoiceProfileSnapshot dataclassではなく
呼び出し側が変換したMapping[str, object]として受け取る)。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class ManifestOutput:
    """14-audio-packaging.md 10節のoutputs[]の1件。"""

    audio_id: str
    output_type: str
    chapter_id: str
    path: str
    content_hash: str
    duration_seconds: float | None = None
    source_segments: tuple[str, ...] = ()
    threshold_status: str | None = None

    def __post_init__(self) -> None:
        if not self.audio_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "audio_id is required")
        if not self.output_type:
            raise AppError(ErrorCode.VALIDATION_ERROR, "output_type is required")
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if not self.path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")
        if not self.content_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_hash is required")
        if len(self.source_segments) != len(set(self.source_segments)):
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate source_segments in output {self.audio_id}")


@dataclass(frozen=True)
class ProductionManifest:
    """入力revision、音声順、hash、閾値状態を記録する(14-audio-packaging.md 10節)。"""

    project_id: str
    outputs: tuple[ManifestOutput, ...]
    schema_version: str = "1.0"
    content_revision: int = 1
    voice_profile_revision: int = 1
    build_request_id: str | None = None
    job_id: str | None = None
    created_at: str | None = None
    chapter_order: tuple[str, ...] = ()
    output_formats: tuple[str, ...] = ()
    verified_script_paths: tuple[str, ...] = ()
    verified_script_content_hashes: tuple[str, ...] = ()
    voice_profile_snapshot: Mapping[str, Any] | None = None
    voice_profile_config_hash: str | None = None

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.outputs:
            raise AppError(ErrorCode.VALIDATION_ERROR, "outputs must not be empty")

        audio_ids = [output.audio_id for output in self.outputs]
        if len(audio_ids) != len(set(audio_ids)):
            raise AppError(ErrorCode.VALIDATION_ERROR, "duplicate audio_id among production manifest outputs")

        if len(self.verified_script_paths) != len(self.verified_script_content_hashes):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "verified_script_paths and verified_script_content_hashes must have the same length",
            )

    def validate(self) -> None:
        """入力revision、音声順、hash、閾値状態の整合を検証する。"""
        for output in self.outputs:
            if not output.source_segments:
                continue
            if len(output.source_segments) != len(set(output.source_segments)):
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"duplicate source_segments in manifest output: {output.audio_id}",
                )

    def to_mapping(self) -> dict[str, object]:
        """14-audio-packaging.md 10節のJSON schemaへ変換する(TASK-BUILD-EXEC-001 13節の追加fieldを含む)。"""
        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "content_revision": self.content_revision,
            "voice_profile_revision": self.voice_profile_revision,
            "build_request_id": self.build_request_id,
            "job_id": self.job_id,
            "created_at": self.created_at,
            "chapter_order": list(self.chapter_order),
            "output_formats": list(self.output_formats),
            "verified_script_paths": list(self.verified_script_paths),
            "verified_script_content_hashes": list(self.verified_script_content_hashes),
            "voice_profile_snapshot": dict(self.voice_profile_snapshot) if self.voice_profile_snapshot is not None else None,
            "voice_profile_config_hash": self.voice_profile_config_hash,
            "outputs": [
                {
                    "audio_id": output.audio_id,
                    "type": output.output_type,
                    "chapter_id": output.chapter_id,
                    "path": output.path,
                    "duration_seconds": output.duration_seconds,
                    "source_segments": list(output.source_segments),
                    "content_hash": output.content_hash,
                    **({"threshold_status": output.threshold_status} if output.threshold_status else {}),
                }
                for output in self.outputs
            ],
        }
