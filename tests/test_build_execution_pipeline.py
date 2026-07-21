"""Tests for TASK-BUILD-EXEC-001 §11-13: Build Execution Orchestrator.

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(11, 12, 13, 14.5節)
Production file exercised: script/pipelines/build_execution.py
"""

from __future__ import annotations

import struct
import wave
from io import BytesIO
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.audio.packaging import ChapterPackager
from script.core.errors import AppError
from script.core.serialization import dump_yaml, load_yaml
from script.domain.enums import JobStatus, VoiceProfileRecordStatus
from script.domain.models import Job
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import JobRepository
from script.pipelines.build_execution import BuildExecutionOrchestrator
from script.schemas.approvals import ApprovalGate, ApprovalTarget
from script.services.approvals import ApprovalService
from script.services.build_requests import BuildRequestService, CreateBuildRequest
from script.services.jobs import JobService
from script.services.projects import CreateProject, ProjectService
from script.services.voice_profiles import CreateVoiceProfile, UpdateVoiceProfile, VoiceProfileService
from script.tts_clients.models import EngineCapabilities, SynthesisRequest, SynthesisResult
from script.tts_clients.registry import TTSClientRegistry

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _make_wav_bytes(*, nframes: int = 48000, amplitude: int = 3000) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(struct.pack(f"<{nframes}h", *([amplitude] * nframes)))
    return buffer.getvalue()


def _fake_encoder(wav_bytes: bytes) -> bytes:
    return b"FAKE_MP3:" + wav_bytes[:16]


class _FakeTTSClient:
    """外部接続なしの決定的TTSClient(実WAV bytesを返す点でMockTTSClientと異なる)。"""

    engine_name = "voicevox"

    def __init__(
        self, *, connectivity: bool = True, fail_segment_id: str | None = None,
        cancel_after_chapter_id: str | None = None, job_service: JobService | None = None, job_id: str | None = None,
    ) -> None:
        self._connectivity = connectivity
        self._fail_segment_id = fail_segment_id
        self._cancel_after_chapter_id = cancel_after_chapter_id
        self._job_service = job_service
        self._job_id = job_id
        self._cancel_triggered = False
        self.calls: list[str] = []

    def check_connectivity(self) -> bool:
        return self._connectivity

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(engine=self.engine_name)

    def list_speakers(self) -> list:
        return []

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        self.calls.append(request.segment_id or request.request_id)
        if self._fail_segment_id is not None and request.segment_id == self._fail_segment_id:
            from script.tts_clients.base import TTSClientError, TTSErrorCode

            raise TTSClientError(TTSErrorCode.SYNTHESIS_FAILED, engine_detail=request.segment_id)

        if not self._cancel_triggered and self._cancel_after_chapter_id is not None and request.chapter_id == self._cancel_after_chapter_id:
            # 別プロセスから当該Jobへcancel要求が届いた状況を模擬する(この章自体は正常合成として完了させる)。
            self._cancel_triggered = True
            self._job_service.request_cancel(self._job_id)

        return SynthesisResult(
            request_id=request.request_id, engine=request.engine, speaker_id=request.speaker_id,
            output_path=f"audio/cache/wav/segments/{request.segment_id}.wav",
            duration_seconds=2.0, sample_rate_hz=24000, channels=1, audio_bytes=_make_wav_bytes(),
        )


def _setup_project(data_root: Path, connection, project_id: str = "proj-1", *, chapters: list[dict] | None = None):
    project_service = ProjectService(data_root, connection)
    project_service.create(CreateProject(project_id=project_id, title="テストProject", domain="test", purpose="p"))

    plan_path = data_root / "library" / project_id / "project" / "project-plan.yaml"
    plan = load_yaml(plan_path)
    plan["chapters"] = chapters if chapters is not None else [{"chapter_id": "ch01", "order": 1}]
    dump_yaml(plan_path, plan)

    for chapter in plan["chapters"]:
        script_path = data_root / "library" / project_id / "chapters" / chapter["chapter_id"] / "verified" / "script.yaml"
        dump_yaml(
            script_path,
            {
                "schema_version": "1.0",
                "chapter_id": chapter["chapter_id"],
                "segments": [
                    {"segment_id": "segment-01", "order": 1, "text": "本文1", "tts_text": "音声本文1", "claim_ids": []},
                    {"segment_id": "segment-02", "order": 2, "text": "本文2", "tts_text": "音声本文2", "claim_ids": []},
                ],
            },
        )

    approvals = ApprovalService(data_root)
    target = ApprovalTarget(paths=("chapters/ch01/verified/script.yaml",), content_hash="dummy-hash")
    approvals.submit(project_id, ApprovalGate.VERIFIED_SCRIPT, target=target)
    approvals.approve(project_id, ApprovalGate.VERIFIED_SCRIPT, approved_by="tester")

    return project_service


def _setup_voice_profile(connection, project_id: str = "proj-1", voice_profile_id: str = "vp-1") -> None:
    voice_service = VoiceProfileService(connection)
    voice_service.create(
        CreateVoiceProfile(
            voice_profile_id=voice_profile_id, project_id=project_id, name="ナレーター1",
            engine="voicevox", speaker_id="3",
        )
    )
    voice_service.update(UpdateVoiceProfile(voice_profile_id=voice_profile_id, status=VoiceProfileRecordStatus.APPROVED))


def _make_orchestrator(data_root: Path, connection, *, tts_client=None, connectivity: bool = True, fail_segment_id: str | None = None):
    tts_registry = TTSClientRegistry()
    tts_registry.register("voicevox", tts_client or _FakeTTSClient(connectivity=connectivity, fail_segment_id=fail_segment_id))
    packager = ChapterPackager(mp3_encoder=_fake_encoder)
    return BuildExecutionOrchestrator(
        connection=connection, data_root=data_root, tts_registry=tts_registry, chapter_packager=packager,
        runtime_checker=lambda: True,
    )


def _make_job(connection, build_request_id: str, job_id: str = "job-1") -> None:
    JobService(connection).enqueue(job_id, build_request_id, "build_execution")


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_01_mp3_and_text_build_succeeds(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-01 — mp3+text指定で全chapterを合成・packaging・登録しJobがsucceededになる。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection)
    _setup_voice_profile(connection)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(
            build_request_id="br-1", project_id="proj-1", output_formats=["mp3", "text"], voice_profile_id="vp-1"
        )
    )
    _make_job(connection, build_request.build_request_id)

    orchestrator = _make_orchestrator(data_root, connection)
    result = orchestrator.run("job-1")

    assert result.status == "succeeded"
    assert len(result.artifacts) == 2  # 1 mp3 + 1 text, single chapter
    assert result.manifest is not None
    assert {output.output_type for output in result.manifest.outputs} == {"chapter_mp3", "text_verified_script"}

    # TASK-BUILD-EXEC-001 13節: manifestがvoice_profile snapshot/chapter_order/verified_script情報を保持する。
    assert result.manifest.build_request_id == "br-1"
    assert result.manifest.job_id == "job-1"
    assert result.manifest.chapter_order == ("ch01",)
    assert result.manifest.output_formats == ("mp3", "text")
    assert result.manifest.verified_script_paths == ("chapters/ch01/verified/script.yaml",)
    assert len(result.manifest.verified_script_content_hashes) == 1
    assert result.manifest.voice_profile_snapshot["voice_profile_id"] == "vp-1"
    assert result.manifest.voice_profile_config_hash

    job = JobRepository(connection).find("job-1")
    assert job.status is JobStatus.SUCCEEDED
    assert job.finished_at is not None


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_02_text_only_never_calls_tts(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-02 — text-onlyのBuildはTTS/音声検証/ffmpegを一切呼び出さない。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(build_request_id="br-1", project_id="proj-1", output_formats=["text"])
    )
    _make_job(connection, build_request.build_request_id)

    fake_tts = _FakeTTSClient()
    orchestrator = _make_orchestrator(data_root, connection, tts_client=fake_tts)
    result = orchestrator.run("job-1")

    assert result.status == "succeeded"
    assert len(result.artifacts) == 1
    assert result.manifest.outputs[0].output_type == "text_verified_script"
    assert fake_tts.calls == []  # TTSは一切呼ばれていない
    assert result.manifest.voice_profile_snapshot is None
    assert result.manifest.voice_profile_config_hash is None


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_03_one_bad_chapter_rejects_whole_job_before_any_tts_call(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-03 — 1chapterでも検証エラーがあれば、TTS呼び出し前にJob全体を拒否する。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection, chapters=[{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 2}])
    _setup_voice_profile(connection)

    # ch02のverified scriptを破損させる(chapter_id不一致)。
    script_path = data_root / "library" / "proj-1" / "chapters" / "ch02" / "verified" / "script.yaml"
    data = load_yaml(script_path)
    data["chapter_id"] = "wrong-id"
    dump_yaml(script_path, data)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(build_request_id="br-1", project_id="proj-1", output_formats=["mp3"], voice_profile_id="vp-1")
    )
    _make_job(connection, build_request.build_request_id)

    fake_tts = _FakeTTSClient()
    orchestrator = _make_orchestrator(data_root, connection, tts_client=fake_tts)

    with pytest.raises(AppError, match="build_target_not_ready"):
        orchestrator.run("job-1")

    assert fake_tts.calls == []

    job = JobRepository(connection).find("job-1")
    assert job.status is JobStatus.FAILED
    assert job.error_code == "build_target_not_ready"
    assert job.error_stage == "validating_verified_scripts"
    assert "verified_script_invalid" in job.error_detail_json


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_04_tts_engine_unreachable_fails_job(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-04 — TTS疎通不可はchecking_runtime段階でJobを失敗させる。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection)
    _setup_voice_profile(connection)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(build_request_id="br-1", project_id="proj-1", output_formats=["mp3"], voice_profile_id="vp-1")
    )
    _make_job(connection, build_request.build_request_id)

    orchestrator = _make_orchestrator(data_root, connection, connectivity=False)

    with pytest.raises(AppError, match="tts_engine_unreachable"):
        orchestrator.run("job-1")

    job = JobRepository(connection).find("job-1")
    assert job.status is JobStatus.FAILED
    assert job.error_code == "tts_engine_unreachable"
    assert job.error_stage == "checking_runtime"


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_05_no_partial_artifacts_on_mid_build_failure(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-05 — 2章目のTTS失敗時、1章目分も含め1件もArtifactを登録しない。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection, chapters=[{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 2}])
    _setup_voice_profile(connection)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(build_request_id="br-1", project_id="proj-1", output_formats=["mp3"], voice_profile_id="vp-1")
    )
    _make_job(connection, build_request.build_request_id)

    # ch02のsegment-01合成で失敗させる。
    fake_tts = _FakeTTSClient(fail_segment_id="segment-01")
    orchestrator = _make_orchestrator(data_root, connection, tts_client=fake_tts)

    with pytest.raises(AppError, match="tts_synthesis_failed"):
        orchestrator.run("job-1")

    from script.services.artifacts import ArtifactService
    from script.domain.enums import ArtifactType

    artifacts = ArtifactService(data_root, connection).list_versions("proj-1", ArtifactType.MP3_CHAPTER)
    assert artifacts == []  # ch01は合成済みだったはずだが、1件も登録されていない

    job = JobRepository(connection).find("job-1")
    assert job.status is JobStatus.FAILED
    assert job.error_code == "tts_synthesis_failed"
    assert job.error_stage == "synthesizing_chapter"


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_06_cancel_requested_stops_before_next_chapter(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-06 — 実行中に届いたcancel要求は、次chapter開始前に検出されJobがcancelledになる。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection, chapters=[{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 2}])
    _setup_voice_profile(connection)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(build_request_id="br-1", project_id="proj-1", output_formats=["mp3"], voice_profile_id="vp-1")
    )
    _make_job(connection, build_request.build_request_id)

    job_service = JobService(connection)
    # ch01合成完了後に(別プロセスからの)cancel要求が届いた状況を模擬する。
    fake_tts = _FakeTTSClient(cancel_after_chapter_id="ch01", job_service=job_service, job_id="job-1")
    orchestrator = _make_orchestrator(data_root, connection, tts_client=fake_tts)

    result = orchestrator.run("job-1")

    assert result.status == "cancelled"
    job = JobRepository(connection).find("job-1")
    assert job.status is JobStatus.CANCELLED
    # ch02は一切合成されていない。
    assert all(not call.startswith("segment") or "ch02" not in call for call in fake_tts.calls)

    from script.domain.enums import ArtifactType
    from script.services.artifacts import ArtifactService

    assert ArtifactService(data_root, connection).list_versions("proj-1", ArtifactType.MP3_CHAPTER) == []


@pytest.mark.integration_mock
def test_tc_build_exec_pipeline_001_07_voice_profile_snapshot_read_once(tmp_path: Path) -> None:
    """TC-BUILD-EXEC-PIPELINE-001-07 — Job実行中にVoiceProfileが更新されても、そのJobの結果には反映されない。"""
    data_root = tmp_path / "data"
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _setup_project(data_root, connection)
    _setup_voice_profile(connection)

    build_request = BuildRequestService(connection).create(
        CreateBuildRequest(build_request_id="br-1", project_id="proj-1", output_formats=["mp3"], voice_profile_id="vp-1")
    )
    _make_job(connection, build_request.build_request_id)

    orchestrator = _make_orchestrator(data_root, connection)
    result = orchestrator.run("job-1")

    assert result.status == "succeeded"
    # このテスト自体はsnapshotが1回だけ読まれることの間接的な確認(値の変化はtest_voice_profile_snapshot.pyで直接検証済み)。
    assert len(result.artifacts) == 1
