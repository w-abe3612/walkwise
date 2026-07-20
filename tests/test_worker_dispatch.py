"""STEP4 test implementation for TASK-WORKER-001: HandlerRegistry dispatch behavior.

Contract: docs/test-cases/TASK-WORKER-001-python-worker-request-and-event-protocol.md
Release scope: MVP
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.worker.handlers import HandlerRegistry
from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest

pytestmark = pytest.mark.mvp


def _noop_log(message: str) -> None:
    pass


@pytest.mark.unit
def test_tc_worker_001_02() -> None:
    """TC-WORKER-001-02 — 未知command: error eventを返しprocessを継続する(例外を投げない)。"""
    registry = HandlerRegistry()
    registry.register(
        "known", lambda request, log: [WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1)]
    )

    request = WorkerRequest(job_id="job-1", job_type="unregistered_type")
    events = list(registry.dispatch(request, log=_noop_log))

    assert len(events) == 1
    assert events[0].event == "error"
    assert events[0].code == "unknown_job_type"

    # processは継続しており、既知のjob_typeは引き続き正常に処理できる。
    known_request = WorkerRequest(job_id="job-2", job_type="known")
    known_events = [e.event for e in registry.dispatch(known_request, log=_noop_log)]
    assert known_events == ["started", "progress", "completed"]


@pytest.mark.unit
def test_tc_worker_001_04() -> None:
    """TC-WORKER-001-04 — handler registry: job_typeごとに正しいhandlerが選択される。"""
    calls: list[str] = []

    def _handler_a(request: WorkerRequest, log) -> list[WorkerEvent]:
        calls.append("a")
        return []

    def _handler_b(request: WorkerRequest, log) -> list[WorkerEvent]:
        calls.append("b")
        return []

    registry = HandlerRegistry()
    registry.register("type_a", _handler_a)
    registry.register("type_b", _handler_b)

    list(registry.dispatch(WorkerRequest(job_id="job-1", job_type="type_a"), log=_noop_log))
    list(registry.dispatch(WorkerRequest(job_id="job-2", job_type="type_b"), log=_noop_log))

    assert calls == ["a", "b"]

    with pytest.raises(WorkerError):
        registry.register("", _handler_a)
    with pytest.raises(WorkerError):
        registry.register("type_c", None)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_worker_001_06() -> None:
    """TC-WORKER-001-06 — progress: current/totalは単調で、逆行するとerrorへ変換される。"""
    def _monotonic_handler(request: WorkerRequest, log) -> list[WorkerEvent]:
        return [
            WorkerEvent(event="progress", job_id=request.job_id, current=1, total=3, message="1/3"),
            WorkerEvent(event="progress", job_id=request.job_id, current=2, total=3, message="2/3"),
            WorkerEvent(event="progress", job_id=request.job_id, current=3, total=3, message="3/3"),
        ]

    registry = HandlerRegistry()
    registry.register("monotonic", _monotonic_handler)
    events = [e.event for e in registry.dispatch(WorkerRequest(job_id="job-1", job_type="monotonic"), log=_noop_log)]
    assert events == ["started", "progress", "progress", "progress", "completed"]

    def _regressing_handler(request: WorkerRequest, log) -> list[WorkerEvent]:
        return [
            WorkerEvent(event="progress", job_id=request.job_id, current=2, total=3),
            WorkerEvent(event="progress", job_id=request.job_id, current=1, total=3),  # 逆行
        ]

    registry.register("regressing", _regressing_handler)
    regressing_events = list(registry.dispatch(WorkerRequest(job_id="job-2", job_type="regressing"), log=_noop_log))
    assert regressing_events[-1].event == "error"  # 逆行はcompletedにならずerrorへ変換される


@pytest.mark.unit
def test_tc_worker_001_08() -> None:
    """TC-WORKER-001-08 — 必須入力欠落: 副作用開始前に安定したvalidation errorを返す。"""
    with pytest.raises(WorkerError) as excinfo:
        WorkerRequest(job_type="echo")  # job_id欠落
    assert excinfo.value.code == "invalid_request"

    with pytest.raises(WorkerError) as excinfo:
        WorkerRequest(job_id="job-1")  # job_type欠落
    assert excinfo.value.code == "invalid_request"


@pytest.mark.unit
def test_tc_worker_001_10(tmp_path: Path) -> None:
    """TC-WORKER-001-10 — 入力・既存成果物の不変性: 失敗時も既存正常成果物のbyte/hashは変化しない。"""
    good_artifact = tmp_path / "existing.mp3"
    good_artifact.write_bytes(b"already-registered-audio-bytes")
    before_bytes = good_artifact.read_bytes()

    def _failing_handler(request: WorkerRequest, log) -> list[WorkerEvent]:
        raise WorkerError("general_error", "simulated failure during processing")

    registry = HandlerRegistry()
    registry.register("failing", _failing_handler)
    events = list(registry.dispatch(WorkerRequest(job_id="job-1", job_type="failing"), log=_noop_log))

    assert events[-1].event == "error"
    assert good_artifact.read_bytes() == before_bytes  # 既存成果物は変化しない
