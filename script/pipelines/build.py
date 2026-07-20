"""script/pipelines/build.py — 公開契約: BuildPipeline.run(build_request_id) -> BuildResult.

Contract: docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md
Spec: docs/specifications/02-process-input-output.md, docs/db/05-artifacts-table.md
"""

from __future__ import annotations

import contextlib
import sqlite3
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from script.audio.packaging import ChapterArtifact, ChapterMetadata, ChapterPackager
from script.core.errors import AppError, ErrorCode
from script.domain.enums import ArtifactType
from script.domain.models import Artifact, BuildRequest
from script.persistence.repositories import BuildRequestRepository
from script.schemas.production_manifest import ManifestOutput, ProductionManifest
from script.services.artifacts import ArtifactService, RegisterArtifact

_MP3_FORMAT = "mp3"
_TEXT_FORMAT = "text"


@dataclass(frozen=True)
class ChapterBuildContent:
    """1章分の、初稿検証・TTS工程から得られる素材(実際のAI/TTS実行は本タスクの対象外、呼び出し側が注入する)。"""

    chapter_id: str
    wavs: tuple[object, ...]
    metadata: ChapterMetadata
    verified_text: str

    def __post_init__(self) -> None:
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if not self.verified_text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "verified_text is required")


@dataclass(frozen=True)
class BuildResult:
    """BuildPipeline.run()の戻り値。"""

    build_request_id: str
    project_id: str
    artifacts: tuple[Artifact, ...]
    manifest: ProductionManifest


class BuildPipeline:
    """承認gateから複数形式(mp3/text)のArtifact登録・manifest生成までを順序制御する。"""

    def __init__(
        self,
        *,
        connection: sqlite3.Connection,
        data_root: Path,
        job_id: str,
        chapter_packager: ChapterPackager,
        chapter_content_provider: Callable[[BuildRequest], ChapterBuildContent],
        approval_gate_check: Callable[[str], bool] | None = None,
    ) -> None:
        if connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
        if not data_root:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root is required")
        if not job_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id is required")
        if chapter_packager is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_packager is required")
        if chapter_content_provider is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_content_provider is required")

        self._connection = connection
        self._data_root = Path(data_root)
        self._job_id = job_id
        self._chapter_packager = chapter_packager
        self._chapter_content_provider = chapter_content_provider
        self._approval_gate_check = approval_gate_check or (lambda build_request_id: True)
        self._artifact_service = ArtifactService(self._data_root, connection)

    def run(self, build_request_id: str) -> BuildResult:
        """承認gateから複数形式Artifact登録までを順序制御する。"""
        if not build_request_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "build_request_id is required")

        build_request = BuildRequestRepository(self._connection).find(build_request_id)
        if build_request is None:
            raise AppError(ErrorCode.NOT_FOUND, f"build request not found: {build_request_id}")

        if not self._approval_gate_check(build_request_id):
            # 承認gate: verified_script/preview_audio未承認ならTTS/packagingを一切開始しない。
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"required approvals (verified_script, preview_audio) are not satisfied: {build_request_id}",
            )

        content = self._chapter_content_provider(build_request)

        artifacts: list[Artifact] = []
        outputs: list[ManifestOutput] = []

        if _MP3_FORMAT in build_request.output_formats:
            chapter_artifact = self._chapter_packager.package(content.wavs, content.metadata)
            artifact = self._register_bytes(
                build_request_id=build_request_id,
                project_id=build_request.project_id,
                chapter_id=content.chapter_id,
                artifact_type=ArtifactType.MP3_CHAPTER,
                data=chapter_artifact.mp3_bytes,
                path_prefix="audio/chapters",
                extension="mp3",
            )
            artifacts.append(artifact)
            outputs.append(self._mp3_output(artifact, chapter_artifact))

        if _TEXT_FORMAT in build_request.output_formats:
            text_bytes = content.verified_text.encode("utf-8")
            artifact = self._register_bytes(
                build_request_id=build_request_id,
                project_id=build_request.project_id,
                chapter_id=content.chapter_id,
                artifact_type=ArtifactType.TEXT_VERIFIED_SCRIPT,
                data=text_bytes,
                path_prefix="text/verified",
                extension="txt",
            )
            artifacts.append(artifact)
            outputs.append(
                ManifestOutput(
                    audio_id=artifact.artifact_id,
                    output_type="text_verified_script",
                    chapter_id=content.chapter_id,
                    path=artifact.file_path,
                    content_hash=artifact.content_hash,
                )
            )

        manifest = ProductionManifest(project_id=build_request.project_id, outputs=tuple(outputs))
        manifest.validate()

        return BuildResult(
            build_request_id=build_request_id,
            project_id=build_request.project_id,
            artifacts=tuple(artifacts),
            manifest=manifest,
        )

    @staticmethod
    def _mp3_output(artifact: Artifact, chapter_artifact: ChapterArtifact) -> ManifestOutput:
        return ManifestOutput(
            audio_id=artifact.artifact_id,
            output_type="chapter_mp3",
            chapter_id=chapter_artifact.chapter_id,
            path=artifact.file_path,
            duration_seconds=chapter_artifact.duration_seconds,
            source_segments=chapter_artifact.source_segments,
            content_hash=artifact.content_hash,
        )

    def _register_bytes(
        self,
        *,
        build_request_id: str,
        project_id: str,
        chapter_id: str,
        artifact_type: ArtifactType,
        data: bytes,
        path_prefix: str,
        extension: str,
    ) -> Artifact:
        existing_versions = self._artifact_service.list_versions(project_id, artifact_type)
        next_version = (existing_versions[0].version_number + 1) if existing_versions else 1

        artifact_id = f"{build_request_id}-{artifact_type.value}-v{next_version:04d}"
        destination_relative = f"{path_prefix}/{chapter_id}-v{next_version:04d}.{extension}"

        fd, tmp_name = tempfile.mkstemp(prefix="build-pipeline-", suffix=f".{extension}")
        tmp_path = Path(tmp_name)
        try:
            with open(fd, "wb") as tmp_file:
                tmp_file.write(data)
            return self._artifact_service.register(
                RegisterArtifact(
                    artifact_id=artifact_id,
                    job_id=self._job_id,
                    project_id=project_id,
                    artifact_type=artifact_type,
                    source_path=tmp_path,
                    destination_relative=destination_relative,
                )
            )
        finally:
            with contextlib.suppress(FileNotFoundError):
                tmp_path.unlink()
