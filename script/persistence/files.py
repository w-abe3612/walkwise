"""script/persistence/files.py — 公開契約: atomic_write_bytes, copy_immutable.

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Spec: docs/specifications/17-local-data-persistence-policy.md
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class FileDigest:
    """入力・成果物のhash表現。"""

    algorithm: str
    value: str


def _write_via_temp_then_replace(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(destination.parent), prefix=f".{destination.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, destination)
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        raise AppError(
            ErrorCode.INTERNAL_ERROR,
            f"atomic write failed for {destination}",
            technical_detail=str(exc),
        ) from exc


def atomic_write_bytes(path: Path, data: bytes, *, backup: bool = True) -> None:
    """同一volumeの一時ファイルから置換し、失敗時に旧正常ファイルを保持する。"""
    path = Path(path)
    if backup and path.exists():
        backup_path = path.with_name(path.name + ".bak")
        shutil.copy2(path, backup_path)
    _write_via_temp_then_replace(path, data)


def copy_immutable(source: Path, destination: Path) -> FileDigest:
    """入力を変更せずコピーしSHA-256を返す。"""
    source = Path(source)
    destination = Path(destination)
    if not source.is_file():
        raise AppError(ErrorCode.NOT_FOUND, f"source file does not exist: {source}")
    data = source.read_bytes()
    _write_via_temp_then_replace(destination, data)
    digest = hashlib.sha256(data).hexdigest()
    return FileDigest(algorithm="sha256", value=digest)
