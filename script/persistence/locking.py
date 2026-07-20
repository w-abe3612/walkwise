"""script/persistence/locking.py — 公開契約: ProjectLock.acquire(project_root) -> ContextManager[ProjectLock].

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Spec: docs/specifications/17-local-data-persistence-policy.md
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from script.core.errors import AppError, ErrorCode

_LOCK_FILE_NAME = ".project.lock"


class ProjectLock:
    """Project単位排他lock。"""

    def __init__(self, project_root: Path, lock_path: Path) -> None:
        self.project_root = project_root
        self._lock_path = lock_path

    def release(self) -> None:
        try:
            self._lock_path.unlink()
        except FileNotFoundError:
            pass

    @classmethod
    @contextmanager
    def acquire(cls, project_root: Path) -> Iterator["ProjectLock"]:
        """Project単位排他lockを取得・解放する。"""
        root = Path(project_root)
        root.mkdir(parents=True, exist_ok=True)
        lock_path = root / _LOCK_FILE_NAME

        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise AppError(ErrorCode.CONFLICT, f"project is already locked: {root}") from exc

        try:
            os.write(fd, str(os.getpid()).encode("utf-8"))
        finally:
            os.close(fd)

        lock = cls(root, lock_path)
        try:
            yield lock
        finally:
            lock.release()
