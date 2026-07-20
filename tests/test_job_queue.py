"""Implementation for TASK-JOB-001: Job状態遷移・FIFO・再試行・stale復旧 (queue/retry).

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
from script.domain.models import BuildRequest, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import BuildRequestRepository, JobRepository, ProjectRepository
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


@pytest.mark.unit
def test_tc_job_001_02(tmp_path: Path) -> None:
    """TC-JOB-001-02 — 不正遷移

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: unit
    Given: cancelled Job
    When: runningへ遷移
    Then: 拒否し状態を維持する
    """
    service = _service(tmp_path)
    service.enqueue("job-1", "br-0001", "tts")
    service.request_cancel("job-1")
    cancelled = service._transition("job-1", JobStatus.CANCELLED)
    assert cancelled.status is JobStatus.CANCELLED

    with pytest.raises(AppError):
        service._transition("job-1", JobStatus.RUNNING)

    unchanged = JobRepository(service._connection).find("job-1")
    assert unchanged.status is JobStatus.CANCELLED


@pytest.mark.unit
def test_tc_job_001_05(tmp_path: Path) -> None:
    """TC-JOB-001-05 — parent_job_id再試行

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「parent_job_id再試行」を実行する
    Then: 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。
    """
    service = _service(tmp_path)
    service.enqueue("job-1", "br-0001", "tts")
    service.start_next()
    service._transition("job-1", JobStatus.FAILED)

    retried = service.retry("job-1", new_job_id="job-1-retry-1")
    assert retried.parent_job_id == "job-1"
    assert retried.status is JobStatus.QUEUED

    with pytest.raises(AppError):
        service.retry("job-2-does-not-exist", new_job_id="job-x")

    with pytest.raises(AppError):
        service.retry("job-1", new_job_id="job-1-retry-1")  # duplicate new_job_id -> unique violation


@pytest.mark.unit
def test_tc_job_001_08(tmp_path: Path) -> None:
    """TC-JOB-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.enqueue("", "br-0001", "tts")

    with pytest.raises(AppError):
        JobService(None)  # type: ignore[arg-type]

    assert service._connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
