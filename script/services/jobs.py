"""script/services/jobs.py — 公開契約:
JobService.enqueue/start_next/request_cancel/retry/recover_stale/
mark_running/report_progress/succeed/fail/mark_cancelled.

Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
Spec: docs/specifications/22-job-lifecycle-and-recovery.md

mark_running/report_progress/succeed/fail/mark_cancelledは、TASK-BUILD-EXEC-001
(11, 12節)のBuild Execution Orchestratorが、FIFO自動選択(start_next)を経由せず
特定のJobを直接進行させるために追加した(既存の状態遷移表・queue契約は変更しない)。
"""

from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Callable
from datetime import datetime, timezone

from script.core.errors import AppError, ErrorCode
from script.domain.enums import JobStatus
from script.domain.job_state import can_transition
from script.domain.models import Job
from script.persistence.repositories import JobRepository

_MAX_RETRIES = 3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobService:
    """同時実行1件のFIFO queue、状態遷移、cancel要求、再試行、stale復旧を提供する。"""

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        approval_gate_check: Callable[[str], bool] | None = None,
    ) -> None:
        if connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "connection is required")
        self._connection = connection
        self._approval_gate_check = approval_gate_check or (lambda build_request_id: True)

    def enqueue(self, job_id: str, build_request_id: str, job_type: str) -> Job:
        """approval gate確認後FIFO末尾へqueued Jobを追加する。"""
        if not job_id or not build_request_id or not job_type:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id, build_request_id and job_type are required")

        if not self._approval_gate_check(build_request_id):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "approval_gate_not_satisfied",
                technical_detail=f"build_request_id={build_request_id}",
            )

        job = Job(job_id=job_id, build_request_id=build_request_id, job_type=job_type, status=JobStatus.QUEUED)
        JobRepository(self._connection).insert(job)
        self._connection.commit()
        return job

    def start_next(self) -> Job | None:
        """runningがない場合だけ最古queuedをrunningへする。"""
        running_exists = self._connection.execute(
            "SELECT 1 FROM jobs WHERE status = ? LIMIT 1", (JobStatus.RUNNING.value,)
        ).fetchone()
        if running_exists is not None:
            return None

        row = self._connection.execute(
            "SELECT * FROM jobs WHERE status = ? ORDER BY rowid LIMIT 1", (JobStatus.QUEUED.value,)
        ).fetchone()
        if row is None:
            return None

        repository = JobRepository(self._connection)
        job = repository._to_model(row)
        updated = dataclasses.replace(job, status=JobStatus.RUNNING, started_at=_now_iso())
        repository.update(updated)
        self._connection.commit()
        return updated

    def _transition(self, job_id: str, target: JobStatus, *, message: str | None = None) -> Job:
        if not job_id or target is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id and target are required")

        repository = JobRepository(self._connection)
        current = repository.find(job_id)
        if current is None:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {job_id}")

        if not can_transition(current.status, target):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"illegal job status transition: {current.status.value} -> {target.value}",
            )

        is_terminal = target in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED)
        updated = dataclasses.replace(
            current,
            status=target,
            last_message=message if message is not None else current.last_message,
            finished_at=_now_iso() if is_terminal else current.finished_at,
        )
        repository.update(updated)
        self._connection.commit()
        return updated

    def request_cancel(self, job_id: str) -> Job:
        """取消要求を行う(実プロセス終了確認は対象外)。"""
        return self._transition(job_id, JobStatus.CANCEL_REQUESTED)

    def mark_running(self, job_id: str) -> Job:
        """FIFO自動選択(start_next)を経由せず、指定Jobをqueued→runningへ進める。"""
        return self._transition(job_id, JobStatus.RUNNING, message="running")

    def report_progress(
        self, job_id: str, *, stage: str, progress_current: int | None = None, progress_total: int | None = None
    ) -> Job:
        """statusを変えず、進捗段階(last_message)とchapter単位の件数だけを更新する。"""
        if not job_id or not stage:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id and stage are required")

        repository = JobRepository(self._connection)
        current = repository.find(job_id)
        if current is None:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {job_id}")

        updated = dataclasses.replace(
            current, last_message=stage, progress_current=progress_current, progress_total=progress_total
        )
        repository.update(updated)
        self._connection.commit()
        return updated

    def succeed(self, job_id: str, *, message: str = "completed") -> Job:
        """runningからsucceededへ完了させる。"""
        return self._transition(job_id, JobStatus.SUCCEEDED, message=message)

    def fail(self, job_id: str, *, error_code: str, error_stage: str, error_detail_json: str | None = None) -> Job:
        """安定したerror_code/error_stage/error_detail_jsonを記録しつつfailedへ遷移する。

        秘密値・原稿全文・絶対pathをerror_detail_jsonへ含めないこと。
        """
        if not error_code or not error_stage:
            raise AppError(ErrorCode.VALIDATION_ERROR, "error_code and error_stage are required")

        repository = JobRepository(self._connection)
        current = repository.find(job_id)
        if current is None:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {job_id}")
        if not can_transition(current.status, JobStatus.FAILED):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"illegal job status transition: {current.status.value} -> {JobStatus.FAILED.value}",
            )

        updated = dataclasses.replace(
            current,
            status=JobStatus.FAILED,
            last_message=f"failed:{error_stage}",
            finished_at=_now_iso(),
            error_code=error_code,
            error_stage=error_stage,
            error_detail_json=error_detail_json,
        )
        repository.update(updated)
        self._connection.commit()
        return updated

    def mark_cancelled(self, job_id: str) -> Job:
        """cancel_requestedからcancelledへ進める(Artifactは一切登録しない)。"""
        return self._transition(job_id, JobStatus.CANCELLED, message="cancelled")

    def retry(self, job_id: str, *, new_job_id: str) -> Job:
        """親参照付き再試行を、上限回数内でのみ許可する。"""
        if not job_id or not new_job_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id and new_job_id are required")

        repository = JobRepository(self._connection)
        original = repository.find(job_id)
        if original is None:
            raise AppError(ErrorCode.NOT_FOUND, f"job not found: {job_id}")
        if original.status is not JobStatus.FAILED:
            raise AppError(ErrorCode.VALIDATION_ERROR, "only failed jobs can be retried")

        depth = 0
        current = original
        while current.parent_job_id:
            depth += 1
            if depth >= _MAX_RETRIES:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"retry limit ({_MAX_RETRIES}) exceeded for job chain starting at {job_id}",
                )
            current = repository.find(current.parent_job_id)
            if current is None:
                break

        new_job = Job(
            job_id=new_job_id,
            build_request_id=original.build_request_id,
            job_type=original.job_type,
            status=JobStatus.QUEUED,
            parent_job_id=original.job_id,
        )
        repository.insert(new_job)
        self._connection.commit()
        return new_job

    def recover_stale(self, is_process_alive: Callable[[str], bool] | None = None) -> list[Job]:
        """起動時、runningのまま残ったJobのうち実プロセスがないものをfailedにする。"""
        is_process_alive = is_process_alive or (lambda job_id: False)

        repository = JobRepository(self._connection)
        rows = self._connection.execute(
            "SELECT * FROM jobs WHERE status = ?", (JobStatus.RUNNING.value,)
        ).fetchall()

        recovered: list[Job] = []
        for row in rows:
            job = repository._to_model(row)
            if is_process_alive(job.job_id):
                continue
            updated = dataclasses.replace(
                job,
                status=JobStatus.FAILED,
                last_message="stale_job_detected_on_startup",
                finished_at=_now_iso(),
            )
            repository.update(updated)
            recovered.append(updated)

        self._connection.commit()
        return recovered
