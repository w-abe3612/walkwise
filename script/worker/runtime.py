"""script/worker/runtime.py — 公開契約:
WorkerRuntime.run(request, token) -> Iterator[WorkerEvent],
recover_after_abnormal_exit(job) -> RecoveryDecision.

Contract: docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md
Spec: docs/specifications/21-electron-python-worker-interface.md(5.6, 5.8節),
      docs/specifications/22-job-lifecycle-and-recovery.md(5.6節)
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from typing import Any

from script.domain.enums import JobStatus
from script.domain.models import Job
from script.worker.cancellation import CancellationToken
from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest

Handler = Callable[[WorkerRequest, CancellationToken], Iterator[WorkerEvent]]


class RecoveryDecision:
    """recover_after_abnormal_exit()の戻り値。"""

    def __init__(self, **data: Any) -> None:
        if not data.get("job_id"):
            raise WorkerError("invalid_request", "job_id is required")
        if not data.get("new_status"):
            raise WorkerError("invalid_request", "new_status is required")
        if not data.get("reason"):
            raise WorkerError("invalid_request", "reason is required")
        self.data = dict(data)
        self.data.setdefault("discard_partial_artifacts", True)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class WorkerRuntime:
    """timeout、cancel、部分成果物cleanupを管理しつつhandlerを実行する。"""

    def __init__(
        self,
        handler: Handler,
        *,
        timeout_seconds: float | None = None,
        grace_period_seconds: float = 1.0,
        clock: Callable[[], float] | None = None,
        cleanup: Callable[[WorkerRequest], None] | None = None,
    ) -> None:
        if handler is None:
            raise WorkerError("invalid_request", "handler is required")
        if grace_period_seconds < 0:
            raise WorkerError("invalid_request", "grace_period_seconds must be 0 or greater")
        self._handler = handler
        self._timeout_seconds = timeout_seconds
        self._grace_period_seconds = grace_period_seconds
        self._clock = clock if clock is not None else time.monotonic
        self._cleanup = cleanup

    def run(self, request: WorkerRequest, token: CancellationToken) -> Iterator[WorkerEvent]:
        """timeout・cancelを監視しながらhandlerのeventを転送する。"""
        if request is None:
            raise WorkerError("invalid_request", "request is required")
        if token is None:
            raise WorkerError("invalid_request", "token is required")

        start = self._clock()
        yield WorkerEvent(event="started", job_id=request.job_id)

        generator = self._handler(request, token)
        cancel_deadline: float | None = None

        while True:
            if self._timeout_seconds is not None and (self._clock() - start) > self._timeout_seconds:
                generator.close()
                self._safe_cleanup(request)
                yield WorkerEvent(event="error", job_id=request.job_id, code="timeout",
                                   message="handler exceeded timeout")
                return

            if cancel_deadline is None and token.requested():
                cancel_deadline = self._clock() + self._grace_period_seconds
                yield WorkerEvent(event="cancel_requested", job_id=request.job_id)

            if cancel_deadline is not None and self._clock() >= cancel_deadline:
                # grace period内にhandlerが自発的に停止しなかった場合の強制終了。
                generator.close()
                self._safe_cleanup(request)
                yield WorkerEvent(event="cancelled", job_id=request.job_id, forced=True)
                return

            try:
                event = next(generator)
            except StopIteration:
                break
            except WorkerError as exc:
                self._safe_cleanup(request)
                if exc.code == "cancelled":
                    yield WorkerEvent(event="cancelled", job_id=request.job_id, forced=False)
                else:
                    yield WorkerEvent(event="error", job_id=request.job_id, code=exc.code, message=exc.message)
                return
            except Exception as exc:  # handler内の予期しない失敗
                self._safe_cleanup(request)
                yield WorkerEvent(event="error", job_id=request.job_id, code="general_error", message=str(exc))
                return

            yield event

        if cancel_deadline is not None:
            # cancel要求後、grace period内にhandlerが自発的に終了した(cooperative cancel)。
            self._safe_cleanup(request)
            yield WorkerEvent(event="cancelled", job_id=request.job_id, forced=False)
            return

        yield WorkerEvent(event="completed", job_id=request.job_id)

    def _safe_cleanup(self, request: WorkerRequest) -> None:
        if self._cleanup is not None:
            self._cleanup(request)


def recover_after_abnormal_exit(job: Job) -> RecoveryDecision:
    """22-job-lifecycle-and-recovery.md 5.6節: 異常終了で`running`のまま残ったJobを復旧判断する。

    中途半端な出力を正式成果物として登録せず、既存の正常な成果物はそのまま保持する
    (本関数はfilesystem/DBへの副作用を一切持たない、純粋な決定関数)。
    """
    if job is None:
        raise WorkerError("invalid_request", "job is required")
    if job.status != JobStatus.RUNNING:
        raise WorkerError(
            "invalid_request",
            f"job is not in a recoverable (running) state: {job.status}",
        )

    return RecoveryDecision(
        job_id=job.job_id,
        new_status=JobStatus.FAILED,
        reason="stale_job_detected_on_startup",
        discard_partial_artifacts=True,
    )
