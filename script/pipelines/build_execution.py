"""script/pipelines/build_execution.py — 公開契約: BuildExecutionOrchestrator.run(job_id) -> BuildExecutionResult.

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(11, 12, 13節)
Spec: docs/specifications/02-process-input-output.md, docs/db/05-artifacts-table.md

既存のscript/pipelines/build.py::BuildPipeline(単一chapter・呼び出し側が用意した
content前提)を破壊的に置き換えず、Projectの全chapterに対して実際にchapter順序解決・
verified script検証・(mp3を含む場合のみ)TTS合成・音声検証・chapter packaging・
manifest生成・Artifact登録までを順序制御する、新しいorchestration層として追加する。

- text-onlyのBuildRequestはTTS/VOICEVOX/音声検証/ffmpegを一切呼び出さない。
- 1chapterでも検証エラーがあれば、TTS呼び出しを一切開始せずJob全体を拒否する
  (script/services/build_target_resolution.pyのis_ready判定)。
- Artifactは全chapterの合成・packaging・検証が成功した後にまとめて登録する
  (途中で失敗した場合、1件もArtifactを登録しない)。
- VoiceProfileはJob開始時に1度だけ読み込みJob全体で不変のsnapshotとして扱う
  (script/services/voice_profile_snapshot.py)。

scope note: 05-script-segment-schema.md 11節が定める300文字超segmentの内部分割は
本orchestratorの対象外とする(既存のscript/audio/synthesis.py::SegmentSynthesizerは
分割後の複数part WAVを1segment分の単一ファイルへ結合しないため、そのまま流用すると
章内のsegment順序整合性を壊しかねない)。今回のverified script実データ(05-script-
segment-schema.md想定のtts_text)は300文字を超えない前提とし、TTSClient.synthesize()
を1segmentにつき1回呼び出す。300文字超のtext_for_ttsは、engine側の
TEXT_TOO_LONG(TTSClientError)としてそのまま失敗させる(サイレント切り詰め・
無断分割は行わない)。
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import os
import sqlite3
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from script.audio.measurements import AudioMeasurementAdapter
from script.audio.packaging import ChapterAudioInput, ChapterMetadata, ChapterPackager
from script.audio.thresholds import AudioThresholds, AudioThresholdSet
from script.audio.validation import AudioValidator, ValidationStatus
from script.core.errors import AppError, ErrorCode
from script.core.serialization import load_yaml
from script.domain.enums import ArtifactType, JobStatus
from script.domain.models import Artifact, BuildRequest, Project
from script.persistence.paths import ProjectPaths
from script.persistence.repositories import BuildRequestRepository, JobRepository, ProjectRepository
from script.schemas.production_manifest import ManifestOutput, ProductionManifest
from script.services.artifacts import ArtifactService, RegisterArtifact
from script.services.build_target_resolution import ChapterTarget, resolve_build_target
from script.services.jobs import JobService
from script.services.voice_profile_snapshot import VoiceProfileSnapshot, capture_voice_profile_snapshot
from script.tts_clients.base import TTSClient, TTSClientError
from script.tts_clients.models import SynthesisParameters, SynthesisRequest
from script.tts_clients.registry import TTSClientRegistry

_MP3_FORMAT = "mp3"
_TEXT_FORMAT = "text"


@dataclass(frozen=True)
class BuildExecutionResult:
    """BuildExecutionOrchestrator.run()の戻り値。"""

    job_id: str
    build_request_id: str
    project_id: str
    status: str  # "succeeded" | "cancelled"
    artifacts: tuple[Artifact, ...] = ()
    manifest: ProductionManifest | None = None


@dataclass(frozen=True)
class _PendingChapterOutput:
    """全chapter分の合成・packaging・検証が成功するまでArtifact登録を保留するための一時保持。"""

    chapter_id: str
    artifact_type: ArtifactType
    data: bytes
    path_prefix: str
    extension: str
    output_type: str
    track_number: int
    duration_seconds: float | None = None
    source_segments: tuple[str, ...] = ()


def _extract_error_code(message: str) -> str:
    code, _, _ = message.partition(":")
    return code.strip() or "internal_error"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BuildExecutionOrchestrator:
    """chapter順序解決からArtifact登録・Job完了までを実際に順序制御する。"""

    def __init__(
        self,
        *,
        connection: sqlite3.Connection,
        data_root: Path,
        tts_registry: TTSClientRegistry,
        chapter_packager: ChapterPackager,
        audio_validator: AudioValidator | None = None,
        audio_thresholds: AudioThresholdSet | None = None,
        runtime_checker: Callable[[], bool] | None = None,
    ) -> None:
        if connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
        if not data_root:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root is required")
        if tts_registry is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "tts_registry is required")
        if chapter_packager is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_packager is required")

        self._connection = connection
        self._data_root = Path(data_root)
        self._tts_registry = tts_registry
        self._chapter_packager = chapter_packager
        self._audio_validator = audio_validator if audio_validator is not None else AudioValidator()
        self._audio_thresholds = audio_thresholds if audio_thresholds is not None else AudioThresholds().load()
        self._runtime_checker = runtime_checker or (lambda: AudioMeasurementAdapter().check_runtime().available)
        self._job_service = JobService(connection)
        self._artifact_service = ArtifactService(self._data_root, connection)
        self._current_stage = "resolving_build_target"

    def run(self, job_id: str) -> BuildExecutionResult:
        """queued状態のJobをrunningへ進め、成功/失敗/取消いずれかの終端状態まで実行する。"""
        if not job_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id is required")

        job = JobRepository(self._connection).find(job_id)
        if job is None:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {job_id}")
        build_request = BuildRequestRepository(self._connection).find(job.build_request_id)
        if build_request is None:
            raise AppError(ErrorCode.NOT_FOUND, f"build request not found: {job.build_request_id}")
        project = ProjectRepository(self._connection).find(build_request.project_id)
        if project is None:
            raise AppError(ErrorCode.NOT_FOUND, f"project not found: {build_request.project_id}")

        # 呼び出し側(Worker `job.start`)がJobService.start_next()で既にrunningへ
        # 進めている場合はそのまま継続し、queuedのまま渡された場合(単体テスト等)は
        # ここでrunningへ進める。運用時の同時実行1件制約はstart_next()側が担保する。
        if job.status is JobStatus.QUEUED:
            self._job_service.mark_running(job_id)
        elif job.status is not JobStatus.RUNNING:
            raise AppError(
                ErrorCode.VALIDATION_ERROR, f"job is not queued or running: {job.status.value}"
            )

        try:
            return self._run_locked(job_id, build_request, project)
        except AppError as exc:
            detail = json.loads(exc.technical_detail) if exc.technical_detail else {"message": exc.message}
            self._job_service.fail(
                job_id,
                error_code=_extract_error_code(exc.message),
                error_stage=self._current_stage,
                error_detail_json=json.dumps(detail, ensure_ascii=False),
            )
            raise

    def _run_locked(self, job_id: str, build_request: BuildRequest, project: Project) -> BuildExecutionResult:
        needs_mp3 = _MP3_FORMAT in build_request.output_formats
        needs_text = _TEXT_FORMAT in build_request.output_formats

        self._current_stage = "resolving_build_target"
        self._job_service.report_progress(job_id, stage=self._current_stage)
        resolution = resolve_build_target(self._data_root, self._connection, build_request.project_id)

        self._current_stage = "validating_verified_scripts"
        if not resolution.is_ready:
            detail = {
                "chapters": [
                    {"chapter_id": error.chapter_id, "error_code": error.error_code}
                    for error in resolution.errors
                ]
            }
            raise AppError(
                ErrorCode.VALIDATION_ERROR, "build_target_not_ready", technical_detail=json.dumps(detail)
            )

        voice_snapshot: VoiceProfileSnapshot | None = None
        tts_client: TTSClient | None = None
        if needs_mp3:
            self._current_stage = "loading_voice_profile"
            self._job_service.report_progress(job_id, stage=self._current_stage)
            voice_snapshot = capture_voice_profile_snapshot(
                self._connection, build_request.project_id, build_request.voice_profile_id
            )

            self._current_stage = "checking_runtime"
            self._job_service.report_progress(job_id, stage=self._current_stage)
            tts_client = self._tts_registry.get(voice_snapshot.engine)
            if not tts_client.check_connectivity():
                raise AppError(ErrorCode.EXTERNAL_UNAVAILABLE, "tts_engine_unreachable")
            if not self._runtime_checker():
                raise AppError(ErrorCode.EXTERNAL_UNAVAILABLE, "audio_runtime_unavailable")

        paths = ProjectPaths.for_root(self._data_root, build_request.project_id)
        total_chapters = len(resolution.chapters)
        pending: list[_PendingChapterOutput] = []

        with tempfile.TemporaryDirectory(prefix="build-execution-") as scratch_dir:
            for index, chapter in enumerate(resolution.chapters, start=1):
                if self._is_cancel_requested(job_id):
                    self._job_service.mark_cancelled(job_id)
                    return BuildExecutionResult(
                        job_id=job_id, build_request_id=build_request.build_request_id,
                        project_id=build_request.project_id, status="cancelled",
                    )

                raw_data = load_yaml(paths.project_root / chapter.script_relative_path)
                raw_segments = sorted(raw_data["segments"], key=lambda segment: segment["order"])

                if needs_mp3:
                    self._current_stage = "synthesizing_chapter"
                    self._job_service.report_progress(
                        job_id, stage=f"synthesizing_chapter:{chapter.chapter_id}",
                        progress_current=index, progress_total=total_chapters,
                    )
                    wavs = self._synthesize_chapter(
                        tts_client, voice_snapshot, build_request.project_id, chapter, raw_segments, Path(scratch_dir)
                    )

                    self._current_stage = "packaging_chapter"
                    self._job_service.report_progress(
                        job_id, stage=f"packaging_chapter:{chapter.chapter_id}",
                        progress_current=index, progress_total=total_chapters,
                    )
                    metadata = ChapterMetadata(
                        project_id=build_request.project_id, chapter_id=chapter.chapter_id,
                        title=chapter.chapter_id, album=project.title, track_number=chapter.order,
                    )
                    chapter_artifact = self._chapter_packager.package(wavs, metadata)
                    pending.append(
                        _PendingChapterOutput(
                            chapter_id=chapter.chapter_id, artifact_type=ArtifactType.MP3_CHAPTER,
                            data=chapter_artifact.mp3_bytes, path_prefix="audio/chapters", extension="mp3",
                            output_type="chapter_mp3", track_number=chapter.order,
                            duration_seconds=chapter_artifact.duration_seconds,
                            source_segments=chapter_artifact.source_segments,
                        )
                    )

                if needs_text:
                    self._current_stage = "writing_text"
                    self._job_service.report_progress(
                        job_id, stage=f"writing_text:{chapter.chapter_id}",
                        progress_current=index, progress_total=total_chapters,
                    )
                    verified_text = "\n".join(segment.get("tts_text") or segment["text"] for segment in raw_segments)
                    pending.append(
                        _PendingChapterOutput(
                            chapter_id=chapter.chapter_id, artifact_type=ArtifactType.TEXT_VERIFIED_SCRIPT,
                            data=verified_text.encode("utf-8"), path_prefix="text/verified", extension="txt",
                            output_type="text_verified_script", track_number=chapter.order,
                        )
                    )

        self._current_stage = "writing_manifest"
        self._job_service.report_progress(job_id, stage=self._current_stage)

        self._current_stage = "registering_artifacts"
        self._job_service.report_progress(job_id, stage=self._current_stage)
        artifacts: list[Artifact] = []
        outputs: list[ManifestOutput] = []
        for item in pending:
            artifact = self._register_bytes(
                build_request_id=build_request.build_request_id, project_id=build_request.project_id,
                job_id=job_id, chapter_id=item.chapter_id, artifact_type=item.artifact_type,
                data=item.data, path_prefix=item.path_prefix, extension=item.extension,
            )
            artifacts.append(artifact)
            outputs.append(
                ManifestOutput(
                    audio_id=artifact.artifact_id, output_type=item.output_type, chapter_id=item.chapter_id,
                    path=artifact.file_path, content_hash=artifact.content_hash,
                    duration_seconds=item.duration_seconds, source_segments=item.source_segments,
                )
            )

        manifest = ProductionManifest(
            project_id=build_request.project_id,
            outputs=tuple(outputs),
            build_request_id=build_request.build_request_id,
            job_id=job_id,
            created_at=_now_iso(),
            chapter_order=tuple(chapter.chapter_id for chapter in resolution.chapters),
            output_formats=build_request.output_formats,
            verified_script_paths=tuple(chapter.script_relative_path for chapter in resolution.chapters),
            verified_script_content_hashes=tuple(chapter.content_hash for chapter in resolution.chapters),
            voice_profile_snapshot=dataclasses.asdict(voice_snapshot) if voice_snapshot is not None else None,
            voice_profile_config_hash=voice_snapshot.voice_profile_config_hash if voice_snapshot is not None else None,
        )
        manifest.validate()

        self._current_stage = "completed"
        self._job_service.succeed(job_id, message="completed")

        return BuildExecutionResult(
            job_id=job_id, build_request_id=build_request.build_request_id, project_id=build_request.project_id,
            status="succeeded", artifacts=tuple(artifacts), manifest=manifest,
        )

    def _is_cancel_requested(self, job_id: str) -> bool:
        current = JobRepository(self._connection).find(job_id)
        return current is not None and current.status is JobStatus.CANCEL_REQUESTED

    def _synthesize_chapter(
        self,
        tts_client: TTSClient,
        voice_snapshot: VoiceProfileSnapshot,
        project_id: str,
        chapter: ChapterTarget,
        raw_segments: list[dict],
        scratch_dir: Path,
    ) -> list[ChapterAudioInput]:
        wavs: list[ChapterAudioInput] = []
        parameters = SynthesisParameters(
            speed_scale=voice_snapshot.speed_scale, pitch_scale=voice_snapshot.pitch_scale,
            intonation_scale=voice_snapshot.intonation_scale, volume_scale=voice_snapshot.volume_scale,
        )
        for order, segment in enumerate(raw_segments, start=1):
            segment_id = segment["segment_id"]
            text_for_tts = segment.get("tts_text") or segment["text"]
            request = SynthesisRequest(
                request_id=f"{chapter.chapter_id}-{segment_id}", engine=voice_snapshot.engine, text=text_for_tts,
                speaker_id=voice_snapshot.speaker_id, parameters=parameters,
                project_id=project_id, chapter_id=chapter.chapter_id, segment_id=segment_id,
            )
            try:
                result = tts_client.synthesize(request)
            except TTSClientError as exc:
                raise AppError(
                    ErrorCode.EXTERNAL_UNAVAILABLE, f"tts_synthesis_failed: {exc.code.value}"
                ) from exc

            if result.audio_bytes is None:
                raise AppError(
                    ErrorCode.EXTERNAL_UNAVAILABLE, f"tts_synthesis_failed: no audio_bytes for segment {segment_id}"
                )

            self._current_stage = "validating_audio"
            wav_path = scratch_dir / f"{chapter.chapter_id}-{segment_id}.wav"
            wav_path.write_bytes(result.audio_bytes)
            report = self._audio_validator.validate(wav_path, text_for_tts, self._audio_thresholds)
            if report.status is ValidationStatus.FAIL:
                issue_codes = [issue.code for issue in report.issues]
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"audio_validation_failed: chapter={chapter.chapter_id} segment={segment_id} issues={issue_codes}",
                )

            wavs.append(
                ChapterAudioInput(
                    segment_id=segment_id, order=order, wav_bytes=result.audio_bytes,
                    voice_content_hash=voice_snapshot.voice_profile_config_hash,
                )
            )
        return wavs

    def _register_bytes(
        self, *, build_request_id: str, project_id: str, job_id: str, chapter_id: str,
        artifact_type: ArtifactType, data: bytes, path_prefix: str, extension: str,
    ) -> Artifact:
        existing_versions = self._artifact_service.list_versions(project_id, artifact_type)
        next_version = (existing_versions[0].version_number + 1) if existing_versions else 1

        artifact_id = f"{build_request_id}-{artifact_type.value}-{chapter_id}-v{next_version:04d}"
        destination_relative = f"{path_prefix}/{chapter_id}-v{next_version:04d}.{extension}"

        fd, tmp_name = tempfile.mkstemp(prefix="build-execution-", suffix=f".{extension}")
        tmp_path = Path(tmp_name)
        try:
            with os.fdopen(fd, "wb") as tmp_file:
                tmp_file.write(data)
            return self._artifact_service.register(
                RegisterArtifact(
                    artifact_id=artifact_id, job_id=job_id, project_id=project_id, artifact_type=artifact_type,
                    source_path=tmp_path, destination_relative=destination_relative,
                )
            )
        finally:
            with contextlib.suppress(FileNotFoundError):
                tmp_path.unlink()
