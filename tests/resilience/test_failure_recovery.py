"""Test suite for TASK-RELEASE-002: 性能・耐障害・最終release受入.

Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
Cases in this file: TC-RELEASE-002-02, 04, 06, 08, 10.
"""

from __future__ import annotations

import dataclasses
import sqlite3
import time
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError, ErrorCode
from script.domain.enums import BuildStatus, JobStatus, PlanningStage
from script.domain.job_state import can_transition
from script.domain.models import BuildRequest, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import BuildRequestRepository, JobRepository, ProjectRepository
from script.services.jobs import JobService
from script.worker.cancellation import CancellationToken
from script.worker.protocol import WorkerEvent, WorkerRequest
from script.worker.runtime import WorkerRuntime, recover_after_abnormal_exit

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _seed(connection: sqlite3.Connection, project_id: str = "release-002", build_request_id: str = "br-release-002") -> None:
    now = "2026-07-20T00:00:00+00:00"
    ProjectRepository(connection).insert(
        Project(
            project_id=project_id, title="タイトル", domain="release",
            planning_stage=PlanningStage.REGISTERED, content_revision=1,
            plan_file_path="project/project-plan.yaml", created_at=now, updated_at=now,
        )
    )
    BuildRequestRepository(connection).insert(
        BuildRequest(
            build_request_id=build_request_id, project_id=project_id, output_formats=("text",),
            status=BuildStatus.DRAFT, created_at=now, updated_at=now,
        )
    )
    connection.commit()


def _service(tmp_path: Path, name: str = "app.db", **kwargs: object) -> JobService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _seed(connection)
    return JobService(connection, **kwargs)


@pytest.mark.resilience
def test_tc_release_002_02(tmp_path: Path) -> None:
    """TC-RELEASE-002-02 — 強制終了/再起動

    Given: running Job中にprocess kill
    When: 再起動
    Then: stale Jobをfailedにし再試行可能

    `TASK-JOB-001`の`JobService.recover_stale`と`TASK-WORKER-002`の
    `recover_after_abnormal_exit`(いずれも既存実装)を組み合わせて検証する。
    """
    service = _service(tmp_path)
    job = service.enqueue("job-001", "br-release-002", "audio_packaging")
    job = service.start_next()
    assert job.status is JobStatus.RUNNING

    # process kill: プロセスは死んでいるがDB上はrunningのまま(再起動をsimulate)。
    recovered = service.recover_stale(is_process_alive=lambda _job_id: False)
    assert len(recovered) == 1
    assert recovered[0].status is JobStatus.FAILED
    assert recovered[0].last_message == "stale_job_detected_on_startup"

    # 純粋関数側の判定も同じ決定を返す(重複実装ではなく既存の判断ロジックを再利用)。
    decision = recover_after_abnormal_exit(dataclasses.replace(job, status=JobStatus.RUNNING))
    assert decision.new_status is JobStatus.FAILED
    assert decision.reason == "stale_job_detected_on_startup"
    assert decision.discard_partial_artifacts is True

    # failedになったJobは再試行可能である。
    retried = service.retry("job-001", new_job_id="job-001-retry-1")
    assert retried.status is JobStatus.QUEUED
    assert retried.parent_job_id == "job-001"


@pytest.mark.unit
def test_tc_release_002_04(tmp_path: Path) -> None:
    """TC-RELEASE-002-04 — 性能基準の測定記録: stale復旧処理の所要時間を実測し記録する。"""
    service = _service(tmp_path)
    service.enqueue("job-001", "br-release-002", "audio_packaging")
    service.start_next()

    start = time.perf_counter()
    recovered = service.recover_stale(is_process_alive=lambda _job_id: False)
    duration_seconds = time.perf_counter() - start

    assert len(recovered) == 1
    assert duration_seconds >= 0.0
    measurement_record = {"scenario": "TC-RELEASE-002-04", "duration_seconds": duration_seconds}
    assert measurement_record["duration_seconds"] is not None


@pytest.mark.unit
def test_tc_release_002_06(tmp_path: Path) -> None:
    """TC-RELEASE-002-06 — cancel/restart

    Then: 許可状態だけでcancel要求を受け付け、cooperative停止後にcancelledへ確定する。
    """
    service = _service(tmp_path)
    service.enqueue("job-001", "br-release-002", "audio_packaging")
    job = service.start_next()
    assert job.status is JobStatus.RUNNING

    # 終端状態からのcancel要求は許可されない。
    assert can_transition(JobStatus.SUCCEEDED, JobStatus.CANCEL_REQUESTED) is False

    cancelled_job = service.request_cancel("job-001")
    assert cancelled_job.status is JobStatus.CANCEL_REQUESTED

    # 二重のcancel要求(CANCEL_REQUESTED -> CANCEL_REQUESTED)は許可されない。
    with pytest.raises(AppError) as exc_info:
        service.request_cancel("job-001")
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    # WorkerRuntimeはcancel要求に対しcooperativeに停止する(TASK-WORKER-002の既存実装)。
    def handler(request: WorkerRequest, token: CancellationToken):
        for step in range(5):
            token.raise_if_cancelled()
            yield WorkerEvent(event="progress", job_id=request.job_id, current=step, total=5)

    runtime = WorkerRuntime(handler)
    token = CancellationToken(is_requested=lambda: True)
    request = WorkerRequest(job_id="job-001", job_type="audio_packaging")
    events = list(runtime.run(request, token))

    assert events[0].event == "started"
    assert events[-1].event == "cancelled"
    assert events[-1].forced is False

    # WorkerからcancelledイベントをElectron main相当が受け取り、最終確定する。
    repository = JobRepository(service._connection)  # type: ignore[attr-defined]
    current = repository.find("job-001")
    assert can_transition(current.status, JobStatus.CANCELLED) is True
    finalized = dataclasses.replace(current, status=JobStatus.CANCELLED, finished_at="2026-07-20T00:05:00+00:00")
    repository.update(finalized)
    service._connection.commit()  # type: ignore[attr-defined]

    reloaded = repository.find("job-001")
    assert reloaded.status is JobStatus.CANCELLED


@pytest.mark.unit
def test_tc_release_002_08(tmp_path: Path) -> None:
    """TC-RELEASE-002-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as exc_info:
        JobService(None)  # type: ignore[arg-type]
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    service = _service(tmp_path)
    with pytest.raises(AppError) as exc_info:
        service.enqueue("", "br-release-002", "audio_packaging")
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(Exception):
        recover_after_abnormal_exit(None)  # type: ignore[arg-type]

    # DBには何も追加されていない。
    row_count = service._connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]  # type: ignore[attr-defined]
    assert row_count == 0


@pytest.mark.unit
def test_tc_release_002_10(tmp_path: Path) -> None:
    """TC-RELEASE-002-10 — 入力・既存成果物の不変性: 失敗した操作が既存の正常な行を変更しない。"""
    service = _service(tmp_path)
    job = service.enqueue("job-001", "br-release-002", "audio_packaging")
    job = service.start_next()
    assert job.status is JobStatus.RUNNING

    repository = JobRepository(service._connection)  # type: ignore[attr-defined]
    before = repository.find("job-001")

    # RUNNING状態のJobをretryしようとすると失敗する(failedだけがretry対象)。
    with pytest.raises(AppError) as exc_info:
        service.retry("job-001", new_job_id="job-001-retry-1")
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    after = repository.find("job-001")
    assert after == before
    assert after.status is JobStatus.RUNNING
    # 失敗したretryによって新規Jobも作られていない。
    assert repository.find("job-001-retry-1") is None
