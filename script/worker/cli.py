"""script/worker/cli.py — 公開契約: main(stdin, stdout) -> int.

Contract: docs/test-cases/TASK-WORKER-001-python-worker-request-and-event-protocol.md
Spec: docs/specifications/21-electron-python-worker-interface.md
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import TextIO

from script.worker.handlers import HandlerRegistry
from script.worker.protocol import WorkerError, WorkerEvent, WorkerRequest


def main(
    stdin: Iterable[str],
    stdout: TextIO,
    *,
    registry: HandlerRegistry | None = None,
    stderr: TextIO | None = None,
) -> int:
    """1行1requestを読み1行ずつeventをflushする。

    stdoutへは有効なJSON Linesイベントのみを出力し、handlerの技術ログは
    stderr(既定は`sys.stderr`)へ分離する。1requestの失敗は他のrequestの
    処理を止めない。
    """
    active_registry = registry if registry is not None else HandlerRegistry()
    error_stream = stderr if stderr is not None else sys.stderr

    def log(message: str) -> None:
        print(message, file=error_stream)

    had_error = False
    for raw_line in stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            request = WorkerRequest.from_json_line(line)
        except WorkerError as exc:
            had_error = True
            _emit(stdout, WorkerEvent(event="error", code=exc.code, message=exc.message))
            continue

        for event in active_registry.dispatch(request, log=log):
            if event.data.get("event") == "error":
                had_error = True
            _emit(stdout, event)

    return 1 if had_error else 0


def _emit(stdout: TextIO, event: WorkerEvent) -> None:
    stdout.write(event.to_json_line() + "\n")
    stdout.flush()


if __name__ == "__main__":  # pragma: no cover - exercised only by TASK-DESKTOP-002 smoke/live gates
    # Electron側(TASK-DESKTOP-002)がsubprocessとして起動するための実行可能entrypoint。
    # main(stdin, stdout)自体の契約(TASK-WORKER-001)は変更しない、純粋な追加。
    #
    # TASK-REVIEW-001: 実行可能entrypointは`WALKWISE_DB_PATH`(Electron mainが
    # bootstrap時に設定する)から実DBを開き、script/worker/commands.pyの
    # 実handler registryを使う。未設定時は空registry(旧来どおりunknown_job_typeで
    # 全requestを拒否する、後方互換の安全側既定)。
    import os

    db_path_env = os.environ.get("WALKWISE_DB_PATH")
    if db_path_env:
        from pathlib import Path

        from script.worker.commands import bootstrap_worker_registry

        active_registry = bootstrap_worker_registry(Path(db_path_env))
    else:
        active_registry = None

    sys.exit(main(sys.stdin, sys.stdout, registry=active_registry))
