"""Implementation for TASK-JOB-001: Job状態遷移・FIFO・再試行・stale復旧 (recovery/approval gate).

Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
Production file exercised: script/services/jobs.py
"""

from __future__ import annotations

import dataclasses
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


def _service(tmp_path: Path, name: str = "app.db", **kwargs) -> JobService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _seed(connection)
    return JobService(connection, **kwargs)


@pytest.mark.integration_mock
def test_tc_job_001_03(tmp_path: Path) -> None:
    """TC-JOB-001-03 — stale復旧

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: integration_mock
    Given: 起動前からrunningのJob
    When: recover_staleする
    Then: failedと異常終了messageへ更新する
    """
    service = _service(tmp_path)
    service.enqueue("job-1", "br-0001", "tts")
    service.enqueue("job-2", "br-0001", "tts")
    service.start_next()  # job-1 becomes running
    # Simulate a second stale running row directly (as if left over from a crash).
    stale_row = JobRepository(service._connection).find("job-2")
    JobRepository(service._connection).update(dataclasses.replace(stale_row, status=JobStatus.RUNNING))
    service._connection.commit()

    recovered = service.recover_stale(is_process_alive=lambda job_id: False)

    recovered_ids = {job.job_id for job in recovered}
    assert recovered_ids == {"job-1", "job-2"}
    for job in recovered:
        assert job.status is JobStatus.FAILED
        assert job.last_message == "stale_job_detected_on_startup"
        assert job.finished_at is not None


@pytest.mark.unit
def test_tc_job_001_06(tmp_path: Path) -> None:
    """TC-JOB-001-06 — approval gate hook

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「approval gate hook」を実行する
    Then: 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。
    """
    blocked_service = _service(tmp_path, name="blocked.db", approval_gate_check=lambda build_request_id: False)
    with pytest.raises(AppError):
        blocked_service.enqueue("job-blocked", "br-0001", "tts")
    assert blocked_service._connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0

    allowed_service = _service(tmp_path, name="allowed.db", approval_gate_check=lambda build_request_id: True)
    job = allowed_service.enqueue("job-allowed", "br-0001", "tts")
    assert job.status is JobStatus.QUEUED


@pytest.mark.unit
def test_tc_job_001_09(tmp_path: Path) -> None:
    """TC-JOB-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    service = _service(tmp_path)
    service.enqueue("job-1", "br-0001", "tts")

    first = service.recover_stale(is_process_alive=lambda job_id: True)
    second = service.recover_stale(is_process_alive=lambda job_id: True)
    assert first == second == []
