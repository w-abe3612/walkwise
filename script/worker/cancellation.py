"""script/worker/cancellation.py — 公開契約: CancellationToken.requested()/raise_if_cancelled().

Contract: docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md
Spec: docs/specifications/21-electron-python-worker-interface.md(5.6節)
"""

from __future__ import annotations

from collections.abc import Callable

from script.worker.protocol import WorkerError


class CancellationToken:
    """外部から注入されたcancel要求の有無を読み取るcooperative cancel token。"""

    def __init__(self, is_requested: Callable[[], bool] | None = None) -> None:
        self._is_requested = is_requested if is_requested is not None else (lambda: False)

    def requested(self) -> bool:
        """cancelが要求されているかを返す。"""
        return bool(self._is_requested())

    def raise_if_cancelled(self) -> None:
        """cancelが要求されていれば`WorkerError(code="cancelled")`を送出する。"""
        if self.requested():
            raise WorkerError("cancelled", "cancellation requested")
