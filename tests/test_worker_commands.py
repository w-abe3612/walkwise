"""Tests for TASK-REVIEW-001 P0 fix: Python Worker command registry.

Contract: docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md(2.2, 3.3, 4節)

Reproduces the audited defect first (TC-REVIEW-001-01): `python -m script.worker.cli`
starts with a completely empty `HandlerRegistry()` (built in TASK-WORKER-001), so even
a `health` request is rejected as `unknown_job_type`. `build_default_registry` wires the
registry to the existing, already-tested application services (TASK-PROJECT-001,
TASK-SOURCE-001, TASK-APPROVAL-001, TASK-BUILD-001, TASK-JOB-001, TASK-ARTIFACT-001)
so the worker subprocess can actually serve Electron main's IPC needs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.domain.enums import SourceStatus
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.schemas.approvals import ApprovalTarget
from script.services.approvals import ApprovalService
from script.services.sources import SourceService
from script.worker.commands import MIGRATIONS_DIR, build_default_registry
from script.worker.handlers import HandlerRegistry
from script.worker.protocol import WorkerRequest

pytestmark = pytest.mark.mvp


def _noop_log(message: str) -> None:
    pass


def _run(registry: HandlerRegistry, job_type: str, **parameters) -> list:
    request = WorkerRequest(job_id=f"job-{job_type}", job_type=job_type, parameters=parameters)
    return list(registry.dispatch(request, log=_noop_log))


@pytest.mark.unit
def test_tc_review_001_01_default_registry_is_empty_reproduces_defect() -> None:
    """TC-REVIEW-001-01 — 監査で確認された欠陥の再現: 素の`HandlerRegistry()`は`health`すら拒否する。"""
    registry = HandlerRegistry()
    events = _run(registry, "health")
    assert events[-1].event == "error"
    assert events[-1].code == "unknown_job_type"


@pytest.fixture
def migrated_connection(tmp_path: Path):
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, MIGRATIONS_DIR)
    yield connection
    connection.close()


@pytest.mark.integration_mock
def test_tc_review_001_02_health_and_migrate_via_default_registry(tmp_path: Path, migrated_connection) -> None:
    """TC-REVIEW-001-02 — `build_default_registry`は`health`/`db.migrate`を実処理する。"""
    registry = build_default_registry(tmp_path, migrated_connection)

    health_events = _run(registry, "health")
    assert [e.event for e in health_events] == ["started", "completed"]
    assert health_events[-1].result == {"status": "ok"}

    migrate_events = _run(registry, "db.migrate")
    assert migrate_events[-1].event == "completed"
    assert migrate_events[-1].result == {"applied": []}  # 再適用: 新規migrationなし


@pytest.mark.integration_mock
def test_tc_review_001_03_project_and_source_lifecycle(tmp_path: Path, migrated_connection) -> None:
    """TC-REVIEW-001-03 — project.create/list/get、source.register/listが既存serviceへ委譲される。"""
    registry = build_default_registry(tmp_path, migrated_connection)

    create_events = _run(
        registry,
        "project.create",
        project_id="proj-1",
        title="サンプル書籍",
        domain="science",
        purpose="学習用",
    )
    assert create_events[-1].event == "completed"
    assert create_events[-1].result["project"]["project_id"] == "proj-1"

    list_events = _run(registry, "project.list")
    projects = list_events[-1].result["projects"]
    assert [p["project_id"] for p in projects] == ["proj-1"]

    get_events = _run(registry, "project.get", project_id="proj-1")
    assert get_events[-1].result["project"]["title"] == "サンプル書籍"

    source_file = tmp_path / "chapter1.txt"
    source_file.write_text("本文サンプル", encoding="utf-8")
    register_events = _run(
        registry,
        "source.register",
        project_id="proj-1",
        source_path=str(source_file),
    )
    assert register_events[-1].event == "completed"
    source_id = register_events[-1].result["source"]["source_id"]
    assert register_events[-1].result["source"]["media_type"] == "text"

    source_list_events = _run(registry, "source.list", project_id="proj-1")
    assert [s["source_id"] for s in source_list_events[-1].result["sources"]] == [source_id]


@pytest.mark.integration_mock
def test_tc_review_001_04_job_start_is_fail_closed_until_approved(tmp_path: Path, migrated_connection) -> None:
    """TC-REVIEW-001-04 — approval gate未充足のbuild_requestはjob.startで拒否される(fail-closed)。"""
    registry = build_default_registry(tmp_path, migrated_connection)

    _run(registry, "project.create", project_id="proj-1", title="t", domain="d", purpose="p")
    build_events = _run(
        registry,
        "build_request.create",
        project_id="proj-1",
        output_formats=["text"],
    )
    build_request_id = build_events[-1].result["build_request"]["build_request_id"]

    gate_check_events = _run(registry, "build_request.approval_gate_satisfied", build_request_id=build_request_id)
    assert gate_check_events[-1].result == {"satisfied": False}

    denied_events = _run(registry, "job.start", build_request_id=build_request_id)
    assert denied_events[-1].event == "error"
    assert denied_events[-1].code == "validation_error"
    assert "approval_gate_not_satisfied" in denied_events[-1].message

    # 07-approval-workflow.md: draft -> review_pending -> approvedの順でのみ遷移できる。
    # submitはElectron IPCの対象範囲外(system側の自動遷移)のため、ここではApprovalServiceを
    # 直接使って前提状態(review_pending)を作る。
    approval_service = ApprovalService(tmp_path)
    for gate in ("verified_script", "preview_audio"):
        approval_service.submit(
            "proj-1", gate, target=ApprovalTarget(paths=("dummy.txt",), content_hash="deadbeef")
        )
        _run(
            registry,
            "approval.approve",
            project_id="proj-1",
            gate=gate,
            approved_by="reviewer",
        )

    satisfied_events = _run(registry, "build_request.approval_gate_satisfied", build_request_id=build_request_id)
    assert satisfied_events[-1].result == {"satisfied": True}

    # TASK-BUILD-EXEC-001: job.startはapproval gate通過後、実際に
    # BuildExecutionOrchestratorを同期実行する。このtestのProjectにはchapterを
    # 1件も定義していないため、gate自体は満たされていてもbuild_target_not_ready
    # (承認gateとは別の、build対象未整備によるfail-closed)でfailedになる。
    started_events = _run(registry, "job.start", build_request_id=build_request_id)
    assert started_events[-1].event == "completed"
    job = started_events[-1].result["job"]
    job_id = job["job_id"]
    assert job["status"] == "failed"
    assert job["error_code"] == "build_target_not_ready"

    get_events = _run(registry, "job.get", job_id=job_id)
    assert get_events[-1].result["job"]["job_id"] == job_id

    list_events = _run(registry, "job.list", project_id="proj-1")
    assert [j["job_id"] for j in list_events[-1].result["jobs"]] == [job_id]

    # 終端状態(failed)のJobはcancelできない(不正な状態遷移として拒否される)。
    cancel_events = _run(registry, "job.cancel", job_id=job_id)
    assert cancel_events[-1].event == "error"


@pytest.mark.integration_mock
def test_tc_review_001_05_approval_request_changes_and_artifact_list_empty(
    tmp_path: Path, migrated_connection
) -> None:
    """TC-REVIEW-001-05 — approval.request_changesと、成果物なしのartifact.listが安全に動く。"""
    registry = build_default_registry(tmp_path, migrated_connection)
    _run(registry, "project.create", project_id="proj-1", title="t", domain="d", purpose="p")

    # request_changesはreview_pending以外からは呼べない(現在draft) -> submitしていないためconflictになる。
    events = _run(registry, "approval.request_changes", project_id="proj-1", gate="planning", reason="修正が必要")
    assert events[-1].event == "error"
    assert events[-1].code == "conflict"

    artifact_events = _run(registry, "artifact.list", project_id="proj-1")
    assert artifact_events[-1].result["artifacts"] == []


@pytest.mark.unit
def test_tc_review_001_06_unknown_job_type_still_rejected(tmp_path: Path, migrated_connection) -> None:
    """TC-REVIEW-001-06 — 未登録job_typeは、登録済みregistryでも引き続きerrorで拒否される。"""
    registry = build_default_registry(tmp_path, migrated_connection)
    events = _run(registry, "totally_unknown_job_type")
    assert events[-1].event == "error"
    assert events[-1].code == "unknown_job_type"


@pytest.mark.integration_mock
def test_tc_review_001_07_source_retry_and_artifact_get(tmp_path: Path, migrated_connection) -> None:
    """TC-REVIEW-001-07 — source.retry(failed->registered)とartifact.getが既存serviceへ委譲される。"""
    registry = build_default_registry(tmp_path, migrated_connection)
    _run(registry, "project.create", project_id="proj-1", title="t", domain="d", purpose="p")

    source_file = tmp_path / "scan.jpg"
    source_file.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-bytes")
    register_events = _run(registry, "source.register", project_id="proj-1", source_path=str(source_file))
    source_id = register_events[-1].result["source"]["source_id"]

    # imageはregistered->processing->failedを経てからでないとretry(failed->registered)できない。
    service = SourceService(tmp_path, migrated_connection)
    service.transition(source_id, SourceStatus.PROCESSING)
    service.transition(source_id, SourceStatus.FAILED)

    retry_events = _run(registry, "source.retry", source_id=source_id)
    assert retry_events[-1].event == "completed"
    assert retry_events[-1].result["source"]["status"] == "registered"

    artifact_get_events = _run(registry, "artifact.get", artifact_id="does-not-exist")
    assert artifact_get_events[-1].event == "error"
    assert artifact_get_events[-1].code == "not_found"


@pytest.mark.unit
def test_tc_review_001_08_voice_list_engines_never_raises_regardless_of_engine_state(
    tmp_path: Path, migrated_connection
) -> None:
    """TC-REVIEW-001-08 — voice.list_enginesはVOICEVOXの起動有無に関わらずerror eventにしない
    (接続確認結果をhealth.availableとして報告するだけで、例外を送出しない)。
    """
    registry = build_default_registry(tmp_path, migrated_connection)
    events = _run(registry, "voice.list_engines")
    assert events[-1].event == "completed"
    assert events[-1].result["health"]["engine"] == "voicevox"
    assert isinstance(events[-1].result["health"]["available"], bool)
    assert isinstance(events[-1].result["speakers"], list)
    if not events[-1].result["health"]["available"]:
        assert events[-1].result["speakers"] == []


@pytest.mark.integration_mock
def test_tc_build_exec_001_worker_01_voice_profile_crud_lifecycle(tmp_path: Path, migrated_connection) -> None:
    """TC-BUILD-EXEC-001-WORKER-01 — voice_profile.create/list/get/update/archiveがVoiceProfileServiceへ委譲される。

    Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(14節)
    """
    registry = build_default_registry(tmp_path, migrated_connection)
    _run(registry, "project.create", project_id="proj-1", title="t", domain="d", purpose="p")

    create_events = _run(
        registry, "voice_profile.create", project_id="proj-1", name="ナレーター1", engine="voicevox", speaker_id="3",
    )
    assert create_events[-1].event == "completed"
    voice_profile = create_events[-1].result["voice_profile"]
    assert voice_profile["status"] == "draft"
    voice_profile_id = voice_profile["voice_profile_id"]

    list_events = _run(registry, "voice_profile.list", project_id="proj-1")
    assert [record["voice_profile_id"] for record in list_events[-1].result["voice_profiles"]] == [voice_profile_id]

    get_events = _run(registry, "voice_profile.get", voice_profile_id=voice_profile_id)
    assert get_events[-1].result["voice_profile"]["name"] == "ナレーター1"

    update_events = _run(registry, "voice_profile.update", voice_profile_id=voice_profile_id, status="approved")
    assert update_events[-1].result["voice_profile"]["status"] == "approved"

    archive_events = _run(registry, "voice_profile.archive", voice_profile_id=voice_profile_id)
    assert archive_events[-1].result["voice_profile"]["status"] == "archived"

    # archived後の更新は拒否される(物理削除はしないが、以後の変更はできない)。
    blocked_events = _run(registry, "voice_profile.update", voice_profile_id=voice_profile_id, name="renamed")
    assert blocked_events[-1].event == "error"


@pytest.mark.integration_mock
def test_tc_build_exec_001_worker_02_voice_profile_create_rejects_unknown_project(
    tmp_path: Path, migrated_connection
) -> None:
    """TC-BUILD-EXEC-001-WORKER-02 — 存在しないProjectを参照するvoice_profile.createは拒否される。"""
    registry = build_default_registry(tmp_path, migrated_connection)
    events = _run(
        registry, "voice_profile.create", project_id="does-not-exist", name="n", engine="voicevox", speaker_id="3",
    )
    assert events[-1].event == "error"


@pytest.mark.integration_mock
def test_tc_build_exec_001_worker_03_job_start_runs_text_only_build_end_to_end(
    tmp_path: Path, migrated_connection
) -> None:
    """TC-BUILD-EXEC-001-WORKER-03 — job.startは実際にBuildExecutionOrchestratorを実行し、
    text-onlyのbuildをTTS/ffmpegを一切必要とせず完了できる。

    Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(11, 14節)
    """
    from script.core.serialization import dump_yaml, load_yaml

    registry = build_default_registry(tmp_path, migrated_connection)
    _run(registry, "project.create", project_id="proj-1", title="t", domain="d", purpose="p")

    plan_path = tmp_path / "library" / "proj-1" / "project" / "project-plan.yaml"
    plan = load_yaml(plan_path)
    plan["chapters"] = [{"chapter_id": "ch01", "order": 1}]
    dump_yaml(plan_path, plan)

    script_path = tmp_path / "library" / "proj-1" / "chapters" / "ch01" / "verified" / "script.yaml"
    dump_yaml(
        script_path,
        {
            "schema_version": "1.0", "chapter_id": "ch01",
            "segments": [{"segment_id": "segment-01", "order": 1, "text": "本文1", "tts_text": "音声1", "claim_ids": []}],
        },
    )

    approval_service = ApprovalService(tmp_path)
    for gate in ("verified_script", "preview_audio"):
        approval_service.submit("proj-1", gate, target=ApprovalTarget(paths=("dummy.txt",), content_hash="deadbeef"))
        _run(registry, "approval.approve", project_id="proj-1", gate=gate, approved_by="reviewer")

    build_events = _run(registry, "build_request.create", project_id="proj-1", output_formats=["text"])
    build_request_id = build_events[-1].result["build_request"]["build_request_id"]

    started_events = _run(registry, "job.start", build_request_id=build_request_id)
    job = started_events[-1].result["job"]
    assert job["status"] == "succeeded"
    assert job["error_code"] is None

    artifact_events = _run(registry, "artifact.list", project_id="proj-1")
    assert len(artifact_events[-1].result["artifacts"]) == 1
    assert artifact_events[-1].result["artifacts"][0]["artifact_type"] == "text_verified_script"
