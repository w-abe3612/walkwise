"""STEP4 test implementation for TASK-WORKER-002: cooperative cancel / abnormal-exit recovery.

Contract: docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md
Release scope: MVP
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.domain.enums import JobStatus
from script.domain.models import Job
from script.worker.cancellation import CancellationToken
from script.worker.protocol import WorkerEvent, WorkerRequest
from script.worker.runtime import WorkerRuntime, recover_after_abnormal_exit

pytestmark = pytest.mark.mvp


@pytest.mark.integration_mock
def test_tc_worker_002_01() -> None:
    """TC-WORKER-002-01 — cooperative cancel: 長処理中にcancelしcancel_requested→cancelledで停止する。"""
    flag = {"cancel": False}
    token = CancellationToken(is_requested=lambda: flag["cancel"])

    def _handler(request: WorkerRequest, token: CancellationToken):
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=5)
        token.raise_if_cancelled()
        yield WorkerEvent(event="progress", job_id=request.job_id, current=2, total=5)

    runtime = WorkerRuntime(_handler, clock=lambda: 0.0)
    request = WorkerRequest(job_id="job-1", job_type="long_task")

    collected: list[str] = []
    for event in runtime.run(request, token):
        collected.append(event.event)
        if event.event == "progress" and event.current == 1:
            flag["cancel"] = True

    assert collected == ["started", "progress", "cancel_requested", "cancelled"]


@pytest.mark.integration_mock
def test_tc_worker_002_03(tmp_path: Path) -> None:
    """TC-WORKER-002-03 — 異常終了: killされたJobを復旧し正式成果物へ登録せず既存成果物を保持する。"""
    existing_artifact = tmp_path / "chapter01.mp3"
    existing_artifact.write_bytes(b"already-registered-good-audio-bytes")
    before_bytes = existing_artifact.read_bytes()

    partial_output = tmp_path / "chapter01.partial.mp3"
    partial_output.write_bytes(b"partial-bytes-from-killed-process")

    job = Job(job_id="job-1", build_request_id="br-1", job_type="audio_packaging", status=JobStatus.RUNNING)
    decision = recover_after_abnormal_exit(job)

    assert decision.job_id == "job-1"
    assert decision.new_status == JobStatus.FAILED
    assert decision.reason == "stale_job_detected_on_startup"
    assert decision.discard_partial_artifacts is True
    # 復旧判断自体はfilesystemへ触れない純粋な決定関数であり、
    # 既存正常成果物のbyteは変化しない。
    assert existing_artifact.read_bytes() == before_bytes


@pytest.mark.unit
def test_tc_worker_002_05() -> None:
    """TC-WORKER-002-05 — force terminate契約: grace period超過でhandlerを強制終了する。"""
    flag = {"cancel": False}
    token = CancellationToken(is_requested=lambda: flag["cancel"])
    clock_value = {"t": 0.0}
    finally_called = {"n": 0}

    def _stubborn_handler(request: WorkerRequest, token: CancellationToken):
        try:
            current = 0
            while True:
                current += 1
                yield WorkerEvent(event="progress", job_id=request.job_id, current=current, total=None)
        finally:
            finally_called["n"] += 1

    runtime = WorkerRuntime(_stubborn_handler, grace_period_seconds=2.0, clock=lambda: clock_value["t"])
    request = WorkerRequest(job_id="job-1", job_type="stubborn")

    events: list[WorkerEvent] = []
    for event in runtime.run(request, token):
        events.append(event)
        if event.event == "progress" and event.current == 1:
            flag["cancel"] = True
        if event.event == "cancel_requested":
            clock_value["t"] += 3.0  # grace period(2.0)を超過させる

    assert events[-1].event == "cancelled"
    assert events[-1].forced is True
    assert finally_called["n"] == 1  # generator.close()によりhandlerのfinally節が実行された


@pytest.mark.unit
def test_tc_worker_002_07(tmp_path: Path) -> None:
    """TC-WORKER-002-07 — 既存正常成果物保持: cancel時のcleanupは一時物のみ対象とする。"""
    good_artifact = tmp_path / "good.mp3"
    good_artifact.write_bytes(b"existing-good-audio-bytes")
    before_bytes = good_artifact.read_bytes()

    partial_path = tmp_path / "partial.mp3"

    flag = {"cancel": False}
    token = CancellationToken(is_requested=lambda: flag["cancel"])

    def _handler(request: WorkerRequest, token: CancellationToken):
        partial_path.write_bytes(b"partial-in-progress-bytes")
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=2)
        token.raise_if_cancelled()
        yield WorkerEvent(event="progress", job_id=request.job_id, current=2, total=2)

    def _cleanup(request: WorkerRequest) -> None:
        if partial_path.exists():
            partial_path.unlink()

    runtime = WorkerRuntime(_handler, clock=lambda: 0.0, cleanup=_cleanup)
    request = WorkerRequest(job_id="job-1", job_type="task")

    for event in runtime.run(request, token):
        if event.event == "progress" and event.current == 1:
            flag["cancel"] = True

    assert good_artifact.read_bytes() == before_bytes
    assert not partial_path.exists()


@pytest.mark.unit
def test_tc_worker_002_09() -> None:
    """TC-WORKER-002-09 — 再実行時の決定性: 同じ入力で2回実行しても同じ論理結果になる。"""
    call_count = {"n": 0}

    def _handler(request: WorkerRequest, token: CancellationToken):
        call_count["n"] += 1
        yield WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1)

    def _run() -> list[str]:
        runtime = WorkerRuntime(_handler, clock=lambda: 0.0)
        token = CancellationToken()
        request = WorkerRequest(job_id="job-1", job_type="task")
        return [event.event for event in runtime.run(request, token)]

    first = _run()
    second = _run()

    assert first == second == ["started", "progress", "completed"]
    assert call_count["n"] == 2  # 実行ごとに1回ずつ(重複外部呼出しなし)
