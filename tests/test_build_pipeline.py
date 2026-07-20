"""STEP4 test implementation for TASK-AUDIO-003: BuildPipeline approval gate / tag metadata / required inputs.

Contract: docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md
Release scope: MVP
"""

from __future__ import annotations

import sqlite3
import struct
import wave
from io import BytesIO
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.audio.packaging import ChapterAudioInput, ChapterMetadata, ChapterPackager
from script.core.errors import AppError, ErrorCode
from script.domain.enums import BuildStatus, JobStatus, PlanningStage
from script.domain.models import BuildRequest, Job, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import BuildRequestRepository, JobRepository, ProjectRepository
from script.pipelines.build import BuildPipeline, ChapterBuildContent

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _make_wav_bytes(*, nframes: int = 2400, amplitude: int = 3000) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(struct.pack(f"<{nframes}h", *([amplitude] * nframes)))
    return buffer.getvalue()


def _fake_encoder(wav_bytes: bytes) -> bytes:
    return b"FAKE_MP3:" + wav_bytes[:16]


def _seed(connection: sqlite3.Connection) -> tuple[str, str]:
    now = "2026-07-19T21:00:00+09:00"
    project_id = "proj-1"
    build_request_id = "br-0001"
    job_id = "job-0001"

    ProjectRepository(connection).insert(
        Project(
            project_id=project_id, title="タイトル", domain="database",
            planning_stage=PlanningStage.REGISTERED, content_revision=1,
            plan_file_path="project/project-plan.yaml", created_at=now, updated_at=now,
        )
    )
    BuildRequestRepository(connection).insert(
        BuildRequest(
            build_request_id=build_request_id, project_id=project_id, output_formats=("mp3",),
            status=BuildStatus.DRAFT, created_at=now, updated_at=now, voice_profile_id="sample-voicevox-profile",
        )
    )
    JobRepository(connection).insert(
        Job(job_id=job_id, build_request_id=build_request_id, job_type="audio_packaging", status=JobStatus.RUNNING)
    )
    connection.commit()
    return build_request_id, job_id


def _content_provider(build_request: BuildRequest) -> ChapterBuildContent:
    wavs = (
        ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
    )
    metadata = ChapterMetadata(
        project_id=build_request.project_id, chapter_id="ch01", title="データベース入門", album="Database Basics",
        content_revision=2, track_number=1,
    )
    return ChapterBuildContent(chapter_id="ch01", wavs=wavs, metadata=metadata, verified_text="text")


@pytest.mark.integration_mock
def test_tc_audio_003_02(tmp_path: Path) -> None:
    """TC-AUDIO-003-02 — 承認gate: verified_scriptまたはpreview_audio未承認ならTTS/packagingを開始しない。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    build_request_id, job_id = _seed(connection)

    call_count = {"n": 0}

    def _tracking_content_provider(build_request: BuildRequest) -> ChapterBuildContent:
        call_count["n"] += 1
        return _content_provider(build_request)

    pipeline = BuildPipeline(
        connection=connection,
        data_root=tmp_path,
        job_id=job_id,
        chapter_packager=ChapterPackager(mp3_encoder=_fake_encoder),
        chapter_content_provider=_tracking_content_provider,
        approval_gate_check=lambda build_request_id: False,  # 未承認を模擬
    )

    with pytest.raises(AppError) as excinfo:
        pipeline.run(build_request_id)

    assert excinfo.value.code is ErrorCode.PERMISSION_DENIED
    assert call_count["n"] == 0  # 承認gateで停止し、TTS/packaging(content provider)を一切呼ばない


@pytest.mark.unit
def test_tc_audio_003_05(tmp_path: Path) -> None:
    """TC-AUDIO-003-05 — tag metadata: 章のtag metadataがpackagerとmanifestへ正しく伝わる。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    build_request_id, job_id = _seed(connection)

    captured_metadata: list[ChapterMetadata] = []
    real_packager = ChapterPackager(mp3_encoder=_fake_encoder)

    class _CapturingPackager:
        def package(self, wavs: object, metadata: ChapterMetadata) -> object:
            captured_metadata.append(metadata)
            return real_packager.package(wavs, metadata)

    pipeline = BuildPipeline(
        connection=connection,
        data_root=tmp_path,
        job_id=job_id,
        chapter_packager=_CapturingPackager(),
        chapter_content_provider=_content_provider,
    )

    result = pipeline.run(build_request_id)

    assert captured_metadata[0].chapter_id == "ch01"
    assert captured_metadata[0].title == "データベース入門"
    assert captured_metadata[0].content_revision == 2
    assert result.manifest.outputs[0].chapter_id == "ch01"


@pytest.mark.unit
def test_tc_audio_003_08(tmp_path: Path) -> None:
    """TC-AUDIO-003-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    build_request_id, job_id = _seed(connection)

    with pytest.raises(AppError):
        BuildPipeline(
            connection=None,  # type: ignore[arg-type]
            data_root=tmp_path,
            job_id=job_id,
            chapter_packager=ChapterPackager(mp3_encoder=_fake_encoder),
            chapter_content_provider=_content_provider,
        )

    pipeline = BuildPipeline(
        connection=connection,
        data_root=tmp_path,
        job_id=job_id,
        chapter_packager=ChapterPackager(mp3_encoder=_fake_encoder),
        chapter_content_provider=_content_provider,
    )

    with pytest.raises(AppError):
        pipeline.run("")

    with pytest.raises(AppError) as excinfo:
        pipeline.run("unknown-build-request-id")
    assert excinfo.value.code is ErrorCode.NOT_FOUND
