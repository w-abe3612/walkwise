"""script/worker/handlers.py — 公開契約: HandlerRegistry.register/dispatch.

Contract: docs/test-cases/TASK-WORKER-001-python-worker-request-and-event-protocol.md
Spec: docs/specifications/21-electron-python-worker-interface.md
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest

Handler = Callable[[WorkerRequest, Callable[[str], None]], Iterator[WorkerEvent]]


class HandlerRegistry:
    """command名(job_type)でhandlerを選択し未知commandを拒否する。"""

    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, job_type: str, handler: Handler) -> None:
        """job_typeに対応するhandlerを登録する。"""
        if not job_type:
            raise WorkerError("invalid_request", "job_type is required for registration")
        if handler is None:
            raise WorkerError("invalid_request", "handler is required for registration")
        self._handlers[job_type] = handler

    def dispatch(self, request: WorkerRequest, *, log: Callable[[str], None]) -> Iterator[WorkerEvent]:
        """job_typeでhandlerを選択し、started/progress/artifact/completedのeventを順に出す。

        未登録job_typeはerror eventを返しprocessを継続する(例外を送出しない)。
        """
        handler = self._handlers.get(request.job_type)
        if handler is None:
            yield WorkerEvent(
                event="error",
                job_id=request.job_id,
                code="unknown_job_type",
                message=f"unknown job_type: {request.job_type}",
            )
            return

        yield WorkerEvent(event="started", job_id=request.job_id)

        last_progress: int | None = None
        try:
            for event in handler(request, log):
                if event.data.get("event") == "progress":
                    current = event.data.get("current")
                    if last_progress is not None and current is not None and current < last_progress:
                        # progressは単調でなければならず、完了後に逆行させない。
                        raise WorkerError(
                            "general_error",
                            f"progress must not regress: {current} < {last_progress}",
                        )
                    if current is not None:
                        last_progress = current
                yield event
        except WorkerError as exc:
            yield WorkerEvent(event="error", job_id=request.job_id, code=exc.code, message=exc.message)
            return
        except Exception as exc:  # handler内の予期しない失敗もerror eventへ変換する
            yield WorkerEvent(event="error", job_id=request.job_id, code="general_error", message=str(exc))
            return

        yield WorkerEvent(event="completed", job_id=request.job_id)
