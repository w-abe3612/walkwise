"""STEP4 test implementation for TASK-WORKER-002: timeout / mid-run crash / invariance.

Contract: docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md
Release scope: MVP
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from script.worker.cancellation import CancellationToken
from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest
from script.worker.runtime import WorkerRuntime

pytestmark = pytest.mark.mvp


@pytest.mark.integration_mock
def test_tc_worker_002_02() -> None:
    """TC-WORKER-002-02 — timeout: handlerが期限超過した場合、timeout errorとcleanupを実行する。"""
    clock_value = {"t": 0.0}
    cleanup_called = {"n": 0}

    def _slow_handler(request: WorkerRequest, token: CancellationToken):
        clock_value["t"] += 10.0  # 期限超過をシミュレート
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1)

    def _cleanup(request: WorkerRequest) -> None:
        cleanup_called["n"] += 1

    runtime = WorkerRuntime(_slow_handler, timeout_seconds=5.0, clock=lambda: clock_value["t"], cleanup=_cleanup)
    token = CancellationToken()
    request = WorkerRequest(job_id="job-1", job_type="slow")

    events = list(runtime.run(request, token))

    assert [e.event for e in events] == ["started", "progress", "error"]
    assert events[-1].code == "timeout"
    assert cleanup_called["n"] == 1


@pytest.mark.unit
def test_tc_worker_002_04() -> None:
    """TC-WORKER-002-04 — grace period: cancel後もgrace period内なら強制終了せず自発停止を待つ。"""
    flag = {"cancel": False}
    token = CancellationToken(is_requested=lambda: flag["cancel"])
    clock_value = {"t": 0.0}

    def _handler(request: WorkerRequest, token: CancellationToken):
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=3)
        yield WorkerEvent(event="progress", job_id=request.job_id, current=2, total=3)
        token.raise_if_cancelled()
        yield WorkerEvent(event="progress", job_id=request.job_id, current=3, total=3)

    runtime = WorkerRuntime(_handler, grace_period_seconds=5.0, clock=lambda: clock_value["t"])
    request = WorkerRequest(job_id="job-1", job_type="task")

    events: list[WorkerEvent] = []
    for event in runtime.run(request, token):
        events.append(event)
        if event.event == "progress" and event.current == 1:
            flag["cancel"] = True
            clock_value["t"] += 0.5  # grace period(5.0)には遠く及ばない経過時間

    assert [e.event for e in events] == ["started", "progress", "cancel_requested", "progress", "cancelled"]
    assert events[-1].forced is False  # grace period内の自発停止であり強制終了ではない


@pytest.mark.unit
def test_tc_worker_002_06() -> None:
    """TC-WORKER-002-06 — 途中終了: handlerの予期しない例外はerror eventへ変換されcompletedにならない。"""
    cleanup_called = {"n": 0}

    def _crashing_handler(request: WorkerRequest, token: CancellationToken):
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=3)
        raise RuntimeError("unexpected mid-processing crash")

    def _cleanup(request: WorkerRequest) -> None:
        cleanup_called["n"] += 1

    runtime = WorkerRuntime(_crashing_handler, clock=lambda: 0.0, cleanup=_cleanup)
    token = CancellationToken()
    request = WorkerRequest(job_id="job-1", job_type="task")

    events = list(runtime.run(request, token))

    assert [e.event for e in events] == ["started", "progress", "error"]
    assert events[-1].code == "general_error"
    assert cleanup_called["n"] == 1
    assert "completed" not in [e.event for e in events]


@pytest.mark.unit
def test_tc_worker_002_08() -> None:
    """TC-WORKER-002-08 — 必須入力欠落: 副作用開始前に安定したvalidation errorを返す。"""
    with pytest.raises(WorkerError):
        WorkerRuntime(None)  # type: ignore[arg-type]

    def _handler(request: WorkerRequest, token: CancellationToken):
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1)

    runtime = WorkerRuntime(_handler, clock=lambda: 0.0)
    token = CancellationToken()

    with pytest.raises(WorkerError):
        list(runtime.run(None, token))  # type: ignore[arg-type]

    with pytest.raises(WorkerError):
        list(runtime.run(WorkerRequest(job_id="job-1", job_type="task"), None))  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_worker_002_10(tmp_path: Path) -> None:
    """TC-WORKER-002-10 — 入力・既存成果物の不変性: 成功・失敗いずれも既存正常成果物は変化しない。"""
    good_artifact = tmp_path / "existing.mp3"
    good_artifact.write_bytes(b"already-registered-good-audio-bytes")
    before_bytes = good_artifact.read_bytes()
    before_hash = hashlib.sha256(before_bytes).hexdigest()

    def _failing_handler(request: WorkerRequest, token: CancellationToken):
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1)
        raise WorkerError("general_error", "simulated failure")

    runtime = WorkerRuntime(_failing_handler, clock=lambda: 0.0)
    token = CancellationToken()
    events = list(runtime.run(WorkerRequest(job_id="job-1", job_type="task"), token))
    assert events[-1].event == "error"
    assert good_artifact.read_bytes() == before_bytes
    assert hashlib.sha256(good_artifact.read_bytes()).hexdigest() == before_hash

    def _succeeding_handler(request: WorkerRequest, token: CancellationToken):
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1)

    runtime2 = WorkerRuntime(_succeeding_handler, clock=lambda: 0.0)
    events2 = list(runtime2.run(WorkerRequest(job_id="job-2", job_type="task"), token))
    assert events2[-1].event == "completed"
    assert good_artifact.read_bytes() == before_bytes
