"""STEP4 test implementation for TASK-AUDIO-003: ProductionManifest / ChapterPackager ordering & determinism.

Contract: docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md
Release scope: MVP
"""

from __future__ import annotations

import struct
import wave
from io import BytesIO

import pytest

from script.audio.packaging import ChapterAudioInput, ChapterMetadata, ChapterPackager
from script.core.errors import AppError
from script.schemas.production_manifest import ManifestOutput, ProductionManifest

pytestmark = pytest.mark.mvp


def _make_wav_bytes(*, framerate: int = 24000, nframes: int = 2400, amplitude: int = 3000) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        wav_file.writeframes(struct.pack(f"<{nframes}h", *([amplitude] * nframes)))
    return buffer.getvalue()


def _fake_encoder(wav_bytes: bytes) -> bytes:
    return b"FAKE_MP3:" + wav_bytes[:16]


def _metadata() -> ChapterMetadata:
    return ChapterMetadata(project_id="proj-1", chapter_id="ch01", title="Chapter 1", album="Database Basics")


@pytest.mark.unit
def test_tc_audio_003_03() -> None:
    """TC-AUDIO-003-03 — manifest順序: 複数segment/partでmanifest順と章音声順が一致する。"""
    # 意図的に入力順序をorderと不一致にする(order=2を先、order=1を後)。
    wavs = (
        ChapterAudioInput(segment_id="ch01-seg002", order=2, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
        ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
        ChapterAudioInput(segment_id="ch01-seg003", order=3, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
    )
    packager = ChapterPackager(mp3_encoder=_fake_encoder)

    chapter_artifact = packager.package(wavs, _metadata())

    assert chapter_artifact.source_segments == ("ch01-seg001", "ch01-seg002", "ch01-seg003")

    manifest_output = ManifestOutput(
        audio_id="ch01-r0001",
        output_type="chapter_mp3",
        chapter_id="ch01",
        path="audio/chapters/ch01-v0001.mp3",
        content_hash=chapter_artifact.content_hash,
        source_segments=chapter_artifact.source_segments,
    )
    assert manifest_output.source_segments == chapter_artifact.source_segments


@pytest.mark.unit
def test_tc_audio_003_06() -> None:
    """TC-AUDIO-003-06 — 複数形式同時生成: mp3とtextの両方をmanifestが別出力として保持する。"""
    mp3_output = ManifestOutput(
        audio_id="ch01-mp3-v0001",
        output_type="chapter_mp3",
        chapter_id="ch01",
        path="audio/chapters/ch01-v0001.mp3",
        content_hash="hash-mp3",
        duration_seconds=120.0,
        source_segments=("ch01-seg001", "ch01-seg002"),
    )
    text_output = ManifestOutput(
        audio_id="ch01-text-v0001",
        output_type="text_verified_script",
        chapter_id="ch01",
        path="text/verified/ch01-v0001.txt",
        content_hash="hash-text",
    )

    manifest = ProductionManifest(project_id="proj-1", outputs=(mp3_output, text_output))
    manifest.validate()

    mapping = manifest.to_mapping()
    output_types = {entry["type"] for entry in mapping["outputs"]}
    assert output_types == {"chapter_mp3", "text_verified_script"}
    paths = {entry["path"] for entry in mapping["outputs"]}
    assert paths == {"audio/chapters/ch01-v0001.mp3", "text/verified/ch01-v0001.txt"}


@pytest.mark.unit
def test_tc_audio_003_09() -> None:
    """TC-AUDIO-003-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    wavs = (
        ChapterAudioInput(segment_id="ch01-seg001", order=1, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
        ChapterAudioInput(segment_id="ch01-seg002", order=2, wav_bytes=_make_wav_bytes(), voice_content_hash="hash-1"),
    )
    packager = ChapterPackager(mp3_encoder=_fake_encoder)

    result_1 = packager.package(wavs, _metadata())
    result_2 = packager.package(wavs, _metadata())

    assert result_1 == result_2


@pytest.mark.unit
def test_tc_build_exec_001_manifest_01_new_fields_are_optional_and_backward_compatible() -> None:
    """TC-BUILD-EXEC-001-MANIFEST-01 — TASK-BUILD-EXEC-001 13節の新filedは省略可能で、既存出力形状を壊さない。"""
    output = ManifestOutput(
        audio_id="ch01-mp3-v0001", output_type="chapter_mp3", chapter_id="ch01",
        path="audio/chapters/ch01-v0001.mp3", content_hash="hash-mp3",
    )
    manifest = ProductionManifest(project_id="proj-1", outputs=(output,))
    mapping = manifest.to_mapping()

    assert mapping["build_request_id"] is None
    assert mapping["job_id"] is None
    assert mapping["chapter_order"] == []
    assert mapping["output_formats"] == []
    assert mapping["verified_script_paths"] == []
    assert mapping["verified_script_content_hashes"] == []
    assert mapping["voice_profile_snapshot"] is None
    assert mapping["voice_profile_config_hash"] is None
    assert {entry["path"] for entry in mapping["outputs"]} == {"audio/chapters/ch01-v0001.mp3"}


@pytest.mark.unit
def test_tc_build_exec_001_manifest_02_carries_voice_profile_snapshot_and_chapter_order() -> None:
    """TC-BUILD-EXEC-001-MANIFEST-02 — voice_profile_snapshot/config_hash/chapter_orderを保持する。"""
    output = ManifestOutput(
        audio_id="ch01-mp3-v0001", output_type="chapter_mp3", chapter_id="ch01",
        path="audio/chapters/ch01-v0001.mp3", content_hash="hash-mp3",
    )
    snapshot = {"voice_profile_id": "vp-1", "engine": "voicevox", "speaker_id": "3"}
    manifest = ProductionManifest(
        project_id="proj-1", outputs=(output,),
        build_request_id="br-1", job_id="job-1", created_at="2026-07-22T00:00:00+09:00",
        chapter_order=("ch01", "ch02"), output_formats=("mp3", "text"),
        verified_script_paths=("chapters/ch01/verified/script.yaml",),
        verified_script_content_hashes=("hash-script-1",),
        voice_profile_snapshot=snapshot, voice_profile_config_hash="hash-config-1",
    )

    mapping = manifest.to_mapping()
    assert mapping["build_request_id"] == "br-1"
    assert mapping["job_id"] == "job-1"
    assert mapping["chapter_order"] == ["ch01", "ch02"]
    assert mapping["output_formats"] == ["mp3", "text"]
    assert mapping["voice_profile_snapshot"] == snapshot
    assert mapping["voice_profile_config_hash"] == "hash-config-1"


@pytest.mark.unit
def test_tc_build_exec_001_manifest_03_rejects_mismatched_verified_script_lengths() -> None:
    """TC-BUILD-EXEC-001-MANIFEST-03 — verified_script_pathsとcontent_hashesの件数不一致は拒否する。"""
    output = ManifestOutput(
        audio_id="ch01-mp3-v0001", output_type="chapter_mp3", chapter_id="ch01",
        path="audio/chapters/ch01-v0001.mp3", content_hash="hash-mp3",
    )
    with pytest.raises(AppError):
        ProductionManifest(
            project_id="proj-1", outputs=(output,),
            verified_script_paths=("chapters/ch01/verified/script.yaml", "chapters/ch02/verified/script.yaml"),
            verified_script_content_hashes=("hash-1",),
        )
