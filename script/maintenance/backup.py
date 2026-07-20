"""script/maintenance/backup.py — 公開契約: create_backup/restore_backup/verify_backup.

Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
Spec: docs/specifications/17-local-data-persistence-policy.md(5.4節)
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from script.core.errors import AppError, ErrorCode
from script.core.serialization import dump_json, load_json
from script.persistence.files import copy_immutable


def _default_clock() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _iter_backup_source_files(data_root: Path) -> list[Path]:
    return sorted(path for path in data_root.rglob("*") if path.is_file())


class BackupManifest:
    """1世代分のbackup(SQLite+Projectディレクトリ一式)を型付けする(17節5.4節)。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class BackupVerificationResult:
    """`verify_backup`の戻り値。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class BackupRestoreResult:
    """`restore_backup`の戻り値。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def create_backup(data_root: Any, destination: Any, *, clock: Callable[[], str] | None = None) -> BackupManifest:
    """SQLiteファイルとProjectディレクトリ一式を1世代のbackupとして作成する(17節5.4節)。

    Public contract: ``create_backup/restore_backup/verify_backup``.
    """
    if not data_root:
        raise AppError(ErrorCode.VALIDATION_ERROR, "data_root is required")
    if not destination:
        raise AppError(ErrorCode.VALIDATION_ERROR, "destination is required")

    data_root = Path(data_root)
    if not data_root.is_dir():
        raise AppError(ErrorCode.NOT_FOUND, f"data_root does not exist: {data_root}")

    source_files = _iter_backup_source_files(data_root)
    if not source_files:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"data_root contains no files to back up: {data_root}")

    resolve_clock = clock or _default_clock
    created_at = resolve_clock()
    generation_id = re.sub(r"[^0-9A-Za-z]", "", created_at)
    generation_dir = Path(destination) / generation_id

    file_hashes: dict[str, str] = {}
    for source_file in source_files:
        relative = source_file.relative_to(data_root).as_posix()
        backup_file_path = generation_dir / "files" / relative
        digest = copy_immutable(source_file, backup_file_path)
        file_hashes[relative] = digest.value

    manifest_payload = {
        "schema_version": "1.0",
        "generation_id": generation_id,
        "created_at": created_at,
        "source_data_root": str(data_root),
        "file_hashes": file_hashes,
    }
    dump_json(generation_dir / "manifest.json", manifest_payload)

    return BackupManifest(**manifest_payload)


def verify_backup(backup_dir: Any) -> BackupVerificationResult:
    """backup済みfileのhashを再計算し、manifestと照合する(17節5.4節)。

    Public contract: ``create_backup/restore_backup/verify_backup``.
    """
    if not backup_dir:
        raise AppError(ErrorCode.VALIDATION_ERROR, "backup_dir is required")

    backup_dir = Path(backup_dir)
    manifest_path = backup_dir / "manifest.json"
    if not manifest_path.is_file():
        raise AppError(ErrorCode.NOT_FOUND, f"backup manifest not found: {manifest_path}")

    manifest = load_json(manifest_path)
    file_hashes = manifest.get("file_hashes", {})

    valid_files: list[str] = []
    corrupted_files: list[str] = []
    missing_files: list[str] = []
    for relative, expected_hash in file_hashes.items():
        backed_up_path = backup_dir / "files" / relative
        if not backed_up_path.is_file():
            missing_files.append(relative)
            continue
        actual_hash = _sha256_bytes(backed_up_path.read_bytes())
        if actual_hash == expected_hash:
            valid_files.append(relative)
        else:
            corrupted_files.append(relative)

    return BackupVerificationResult(
        generation_id=manifest.get("generation_id"),
        valid_files=tuple(sorted(valid_files)),
        corrupted_files=tuple(sorted(corrupted_files)),
        missing_files=tuple(sorted(missing_files)),
        all_valid=not corrupted_files and not missing_files,
    )


def restore_backup(backup_dir: Any, destination_data_root: Any) -> BackupRestoreResult:
    """検証に成功したbackup fileだけをdestinationへ復旧する(17節5.4節)。

    破損・欠落したfileは復旧対象から除外し、`corrupted_files`/`missing_files`へ
    明示的に報告する(黙って破損内容を復旧しない)。

    Public contract: ``create_backup/restore_backup/verify_backup``.
    """
    if not backup_dir:
        raise AppError(ErrorCode.VALIDATION_ERROR, "backup_dir is required")
    if not destination_data_root:
        raise AppError(ErrorCode.VALIDATION_ERROR, "destination_data_root is required")

    backup_dir = Path(backup_dir)
    destination_data_root = Path(destination_data_root)

    verification = verify_backup(backup_dir)

    restored_files: list[str] = []
    for relative in verification.valid_files:
        source_file = backup_dir / "files" / relative
        destination_file = destination_data_root / relative
        copy_immutable(source_file, destination_file)
        restored_files.append(relative)

    return BackupRestoreResult(
        generation_id=verification.generation_id,
        restored_files=tuple(restored_files),
        corrupted_files=verification.corrupted_files,
        missing_files=verification.missing_files,
        fully_restored=verification.all_valid,
    )
