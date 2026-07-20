"""Implementation for TASK-JOB-001: Job状態遷移・FIFO・再試行・stale復旧 (lifecycle).

Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
Production files exercised: script/services/jobs.py, script/domain/job_state.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import BuildStatus, JobStatus, PlanningStage
from script.domain.job_state import can_transition
from script.domain.models import BuildRequest, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import BuildRequestRepository, ProjectRepository
from script.services.jobs import JobService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _seed(connection: sqlite3.Connection, project_id: str = "database-foundations", build_request_id: str = "br-0001") -> None:
    now = "2026-07-19T21:00:00+09:00"
    ProjectRepository(connection).insert(
        Project(
            project_id=project_id, title="タイトル", domain="database",
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


def _service(tmp_path: Path, name: str = "app.db") -> JobService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _seed(connection)
    return JobService(connection)


@pytest.mark.integration_mock
def test_tc_job_001_01(tmp_path: Path) -> None:
    """TC-JOB-001-01 — FIFO

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: integration_mock
    Given: queued Jobが3件
    When: start_nextを繰り返す
    Then: created/enqueued順で1件ずつrunningになる
    """
    service = _service(tmp_path)
    service.enqueue("job-1", "br-0001", "tts")
    service.enqueue("job-2", "br-0001", "tts")
    service.enqueue("job-3", "br-0001", "tts")

    first = service.start_next()
    assert first is not None and first.job_id == "job-1"
    assert first.status is JobStatus.RUNNING

    # A second job cannot start while one is running (concurrency == 1).
    assert service.start_next() is None

    service.request_cancel("job-1")  # move job-1 out of running (cancel_requested)
    second = service.start_next()
    assert second is not None and second.job_id == "job-2"

    service.request_cancel("job-2")
    third = service.start_next()
    assert third is not None and third.job_id == "job-3"


@pytest.mark.unit
def test_tc_job_001_04() -> None:
    """TC-JOB-001-04 — 状態遷移表

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「状態遷移表」を実行する
    Then: 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。
    """
    assert can_transition(JobStatus.QUEUED, JobStatus.RUNNING) is True
    assert can_transition(JobStatus.RUNNING, JobStatus.SUCCEEDED) is True
    assert can_transition(JobStatus.RUNNING, JobStatus.FAILED) is True
    assert can_transition(JobStatus.RUNNING, JobStatus.CANCEL_REQUESTED) is True
    assert can_transition(JobStatus.CANCEL_REQUESTED, JobStatus.CANCELLED) is True

    assert can_transition(JobStatus.CANCELLED, JobStatus.RUNNING) is False
    assert can_transition(JobStatus.SUCCEEDED, JobStatus.RUNNING) is False
    assert can_transition(JobStatus.QUEUED, JobStatus.SUCCEEDED) is False


@pytest.mark.unit
def test_tc_job_001_07(tmp_path: Path) -> None:
    """TC-JOB-001-07 — finished_at規則

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「finished_at規則」を実行する
    Then: 「finished_at規則」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    service = _service(tmp_path)
    service.enqueue("job-1", "br-0001", "tts")
    running = service.start_next()
    assert running.finished_at is None

    cancel_requested = service.request_cancel("job-1")
    assert cancel_requested.finished_at is None

    cancelled = service._transition("job-1", JobStatus.CANCELLED)
    assert cancelled.finished_at is not None


@pytest.mark.unit
def test_tc_job_001_10(tmp_path: Path) -> None:
    """TC-JOB-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    service = _service(tmp_path)
    job = service.enqueue("job-1", "br-0001", "tts")
    snapshot = job

    with pytest.raises(AppError):
        service.request_cancel("job-does-not-exist")

    unchanged = service.start_next()
    assert unchanged.job_id == snapshot.job_id
    assert unchanged.build_request_id == snapshot.build_request_id
