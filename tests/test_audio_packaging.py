"""STEP4 test implementation for TASK-AUDIO-003: ChapterPackager / multi-format BuildPipeline.run().

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
from script.core.errors import AppError
from script.domain.enums import BuildStatus, JobStatus, PlanningStage
from script.domain.models import BuildRequest, Job, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import BuildRequestRepository, JobRepository, ProjectRepository
from script.pipelines.build import BuildPipeline, ChapterBuildContent

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _make_wav_bytes(*, framerate: int = 24000, nchannels: int = 1, nframes: int = 2400, amplitude: int = 3000) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(nchannels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        wav_file.writeframes(struct.pack(f"<{nframes}h", *([amplitude] * nframes)))
    return buffer.getvalue()


def _fake_encoder(wav_bytes: bytes) -> bytes:
    return b"FAKE_MP3:" + wav_bytes[:16]


def _metadata(chapter_id: str = "ch01") -> ChapterMetadata:
    return ChapterMetadata(project_id="proj-1", chapter_id=chapter_id, title="Chapter 1", album="Database Basics")


def _seed(connection: sqlite3.Connection, *, output_formats: tuple[str, ...] = ("mp3", "text")) -> tuple[str, str]:
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
            build_request_id=build_request_id, project_id=project_id, output_formats=output_formats,
            status=BuildStatus.DRAFT, created_at=now, updated_at=now, voice_profile_id="sample-voicevox-profile",
        )
    )
    JobRepository(connection).insert(
        Job(job_id=job_id, build_request_id=build_request_id, job_type="audio_packaging", status=JobStatus.RUNNING)
    )
    connection.commit()
    return build_request_id, job_id


def _build_pipeline(tmp_path: Path, connection: sqlite3.Connection, job_id: str) -> BuildPipeline:
    def _content_provider(build_request: BuildRequest) -> ChapterBuildContent:
        wavs = (
            ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
            ChapterAudioInput(segment_id="ch01-seg002", order=2, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
        )
        return ChapterBuildContent(
            chapter_id="ch01", wavs=wavs, metadata=_metadata(), verified_text="検証済みの原稿本文です。"
        )

    return BuildPipeline(
        connection=connection,
        data_root=tmp_path,
        job_id=job_id,
        chapter_packager=ChapterPackager(mp3_encoder=_fake_encoder),
        chapter_content_provider=_content_provider,
    )


@pytest.mark.integration_mock
def test_tc_audio_003_01(tmp_path: Path) -> None:
    """TC-AUDIO-003-01 — 複数形式: mp3+textを別file/Artifactとして両方生成し上書きしない。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    build_request_id, job_id = _seed(connection, output_formats=("mp3", "text"))

    pipeline = _build_pipeline(tmp_path, connection, job_id)
    result = pipeline.run(build_request_id)

    assert len(result.artifacts) == 2
    file_paths = {artifact.file_path for artifact in result.artifacts}
    assert len(file_paths) == 2  # 別fileとして生成(上書きなし)
    artifact_types = {artifact.artifact_type.value for artifact in result.artifacts}
    assert artifact_types == {"mp3_chapter", "text_verified_script"}
    for file_path in file_paths:
        assert (tmp_path / "library" / "proj-1" / file_path).is_file()


@pytest.mark.unit
def test_tc_audio_003_04() -> None:
    """TC-AUDIO-003-04 — 章単位MP3: 破損・形式不一致は成功扱いにしない。"""
    packager = ChapterPackager(mp3_encoder=_fake_encoder)

    corrupted_wavs = (
        ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=b"not a real wav", voice_content_hash="hash-1"),
    )
    with pytest.raises(AppError):
        packager.package(corrupted_wavs, _metadata())

    mismatched_wavs = (
        ChapterAudioInput(
            segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(framerate=24000), voice_content_hash="hash-1"
        ),
        ChapterAudioInput(
            segment_id="ch01-seg002", order=2, wav_bytes=_make_wav_bytes(framerate=48000), voice_content_hash="hash-1"
        ),
    )
    with pytest.raises(AppError):
        packager.package(mismatched_wavs, _metadata())


@pytest.mark.unit
def test_tc_audio_003_07() -> None:
    """TC-AUDIO-003-07 — 形式ごとversion: 異なるvoice_content_hashを黙って互換扱いしない。"""
    packager = ChapterPackager(mp3_encoder=_fake_encoder)

    inconsistent_wavs = (
        ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-old"),
        ChapterAudioInput(segment_id="ch01-seg002", order=2, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-new"),
    )
    with pytest.raises(AppError):
        packager.package(inconsistent_wavs, _metadata())

    consistent_wavs = (
        ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
        ChapterAudioInput(segment_id="ch01-seg002", order=2, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
    )
    result = packager.package(consistent_wavs, _metadata())
    assert result.voice_content_hash == "hash-1"
    assert result.content_revision == 1


@pytest.mark.unit
def test_tc_audio_003_10(tmp_path: Path) -> None:
    """TC-AUDIO-003-10 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    build_request_id, job_id = _seed(connection, output_formats=("mp3",))

    pipeline = _build_pipeline(tmp_path, connection, job_id)
    result = pipeline.run(build_request_id)
    good_file_path = tmp_path / "library" / "proj-1" / result.artifacts[0].file_path
    before_bytes = good_file_path.read_bytes()

    with pytest.raises(AppError):
        ChapterPackager(mp3_encoder=_fake_encoder).package(
            (ChapterAudioInput(segment_id="bad-seg", order=1, wav_bytes=b"corrupted", voice_content_hash="hash-1"),),
            _metadata(),
        )

    assert good_file_path.read_bytes() == before_bytes
