"""script/worker/protocol.py — 公開契約: WorkerRequest/WorkerEvent/WorkerError.

Contract: docs/test-cases/TASK-WORKER-001-python-worker-request-and-event-protocol.md
Spec: docs/specifications/21-electron-python-worker-interface.md(5.2, 5.3, 5.7節)
"""

from __future__ import annotations

import json
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

_VALID_EVENT_TYPES = frozenset(
    {"started", "progress", "artifact", "warning", "error", "completed", "cancel_requested", "cancelled"}
)


class WorkerError(RuntimeError):
    """JSON Linesプロトコル上の安定したエラー(code/message)。"""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _is_absolute_path(path_value: str) -> bool:
    return PurePosixPath(path_value).is_absolute() or PureWindowsPath(path_value).is_absolute()


class WorkerEvent:
    """21-electron-python-worker-interface.md 5.3節のJSON Linesイベント1件。"""

    def __init__(self, **data: Any) -> None:
        event_type = data.get("event")
        if not event_type:
            raise WorkerError("invalid_request", "event is required")
        if event_type not in _VALID_EVENT_TYPES:
            raise WorkerError("invalid_request", f"unknown event type: {event_type}")
        if event_type == "artifact":
            path_value = data.get("path")
            if not path_value:
                raise WorkerError("invalid_request", "artifact event requires path")
            if _is_absolute_path(str(path_value)):
                # 5.7節: artifactのpathはProject rootからの相対pathのみ許可する。
                raise WorkerError("invalid_request", f"artifact path must be relative: {path_value}")
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def to_json_line(self) -> str:
        """1行1JSON(改行を含まない)としてシリアライズする。"""
        return json.dumps(self.data, ensure_ascii=False, sort_keys=True)


class WorkerRequest:
    """21-electron-python-worker-interface.md 5.2節のrequest。"""

    def __init__(self, **data: Any) -> None:
        if not data.get("job_id"):
            raise WorkerError("invalid_request", "job_id is required")
        if not data.get("job_type"):
            raise WorkerError("invalid_request", "job_type is required")
        self.data = dict(data)
        self.data.setdefault("parameters", {})

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @classmethod
    def from_json_line(cls, line: str) -> "WorkerRequest":
        """stdinの1行をrequestとしてparseし検証する。"""
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise WorkerError("invalid_request", f"malformed request JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise WorkerError("invalid_request", "request must be a JSON object")
        return cls(**payload)
