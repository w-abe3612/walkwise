"""STEP4 test implementation for TASK-WORKER-001: JSON Lines protocol / stdout isolation.

Contract: docs/test-cases/TASK-WORKER-001-python-worker-request-and-event-protocol.md
Release scope: MVP
"""

from __future__ import annotations

import json
from io import StringIO

import pytest

from script.worker.cli import main
from script.worker.handlers import HandlerRegistry
from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest

pytestmark = pytest.mark.mvp


def _echo_handler(request: WorkerRequest, log) -> list[WorkerEvent]:
    return [
        WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1, message="done"),
        WorkerEvent(event="artifact", job_id=request.job_id, artifact_type="text", path="out/result.txt"),
    ]


def _logging_handler(request: WorkerRequest, log) -> list[WorkerEvent]:
    log("this is a technical log line, not JSON")
    return [WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1, message="ok")]


@pytest.mark.integration_mock
def test_tc_worker_001_01() -> None:
    """TC-WORKER-001-01 — JSON Lines: 2requestをstdinへ投入しrequestごとのeventを行単位・flush順で出す。"""
    registry = HandlerRegistry()
    registry.register("echo", _echo_handler)

    requests = [
        {"job_id": "job-1", "job_type": "echo", "parameters": {}},
        {"job_id": "job-2", "job_type": "echo", "parameters": {}},
    ]
    stdin = StringIO("\n".join(json.dumps(r) for r in requests) + "\n")
    stdout = StringIO()

    exit_code = main(stdin, stdout, registry=registry)

    assert exit_code == 0
    lines = [line for line in stdout.getvalue().splitlines() if line]
    parsed = [json.loads(line) for line in lines]
    # request1のevent列がすべてrequest2より先に出る(flush順・行単位)。
    job1_events = [e["event"] for e in parsed if e.get("job_id") == "job-1"]
    job2_events = [e["event"] for e in parsed if e.get("job_id") == "job-2"]
    assert job1_events == ["started", "progress", "artifact", "completed"]
    assert job2_events == ["started", "progress", "artifact", "completed"]
    first_job2_index = next(i for i, e in enumerate(parsed) if e.get("job_id") == "job-2")
    last_job1_index = max(i for i, e in enumerate(parsed) if e.get("job_id") == "job-1")
    assert last_job1_index < first_job2_index


@pytest.mark.integration_mock
def test_tc_worker_001_03() -> None:
    """TC-WORKER-001-03 — stdout汚染: handlerのlogはstdoutへ出さずstderrへ分離する。"""
    registry = HandlerRegistry()
    registry.register("logging_job", _logging_handler)

    stdin = StringIO(json.dumps({"job_id": "job-1", "job_type": "logging_job"}) + "\n")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(stdin, stdout, registry=registry, stderr=stderr)

    assert exit_code == 0
    for line in stdout.getvalue().splitlines():
        if not line:
            continue
        json.loads(line)  # 全行が有効なJSONであること(非JSON混入なし)
    assert "technical log line" in stderr.getvalue()
    assert "technical log line" not in stdout.getvalue()


@pytest.mark.unit
def test_tc_worker_001_05() -> None:
    """TC-WORKER-001-05 — 1行1JSON: WorkerEventのシリアライズは改行を含まない単一行JSONである。"""
    event = WorkerEvent(event="progress", job_id="job-1", current=1, total=2, message="複数行\nを含む文字列")
    line = event.to_json_line()

    assert "\n" not in line
    decoded = json.loads(line)
    assert decoded["event"] == "progress"
    assert decoded["message"] == "複数行\nを含む文字列"


@pytest.mark.unit
def test_tc_worker_001_07() -> None:
    """TC-WORKER-001-07 — artifact: pathはProject root相対のみ許可し絶対pathを拒否する。"""
    event = WorkerEvent(event="artifact", job_id="job-1", artifact_type="mp3", path="audio/chapters/ch01.mp3")
    assert event.path == "audio/chapters/ch01.mp3"

    with pytest.raises(WorkerError):
        WorkerEvent(event="artifact", job_id="job-1", artifact_type="mp3", path="/abs/ch01.mp3")

    with pytest.raises(WorkerError):
        WorkerEvent(event="artifact", job_id="job-1", artifact_type="mp3", path="C:\\abs\\ch01.mp3")


@pytest.mark.unit
def test_tc_worker_001_09() -> None:
    """TC-WORKER-001-09 — 再実行時の決定性: 同じ入力で2回実行しても同じ論理結果になる。"""
    call_count = {"n": 0}

    def _counting_handler(request: WorkerRequest, log) -> list[WorkerEvent]:
        call_count["n"] += 1
        return [WorkerEvent(event="progress", job_id=request.job_id, current=1, total=1, message="ok")]

    def _run() -> list[dict]:
        registry = HandlerRegistry()
        registry.register("job", _counting_handler)
        stdin = StringIO(json.dumps({"job_id": "job-1", "job_type": "job"}) + "\n")
        stdout = StringIO()
        main(stdin, stdout, registry=registry)
        return [json.loads(line) for line in stdout.getvalue().splitlines() if line]

    first = _run()
    second = _run()

    assert first == second
    assert call_count["n"] == 2  # それぞれの実行で1回ずつ(重複外部呼出しなし)
