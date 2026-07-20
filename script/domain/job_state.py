"""script/domain/job_state.py — 公開契約: can_transition(current, target) -> bool.

Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
Spec: docs/specifications/22-job-lifecycle-and-recovery.md (5.2節)
"""

from __future__ import annotations

from script.core.errors import AppError, ErrorCode
from script.domain.enums import JobStatus

# 5.2節の状態遷移図に加え、queued状態からの取消要求(request_cancel)を許可する。
# 図はrunning->cancel_requestedのみ示すが、開始前のqueued Jobを取消できないと
# 「取消」機能自体が使えなくなるため、この1点のみ拡張している。
_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.RUNNING, JobStatus.CANCEL_REQUESTED}),
    JobStatus.RUNNING: frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCEL_REQUESTED}),
    JobStatus.CANCEL_REQUESTED: frozenset({JobStatus.CANCELLED}),
    JobStatus.SUCCEEDED: frozenset(),
    JobStatus.FAILED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}


def can_transition(current: JobStatus, target: JobStatus) -> bool:
    """状態遷移表を純粋関数で判定する。"""
    if current is None or target is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "current and target are required")
    return target in _TRANSITIONS.get(current, frozenset())
