"""script/schemas/source_metadata.py — 公開契約: SourceMetadata.from_file(...).

Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
Spec: docs/db/02-sources-table.md, docs/specifications/source-storage-and-common-schema.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from script.core.errors import AppError, ErrorCode
from script.domain.enums import SourceStatus
from script.persistence.paths import ProjectPaths

_TEXT_EXTENSIONS = {".txt", ".md"}
_PDF_EXTENSIONS = {".pdf"}
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
_VALID_MEDIA_TYPES = {"text", "pdf", "image"}


def _infer_media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in _TEXT_EXTENSIONS:
        return "text"
    if suffix in _PDF_EXTENSIONS:
        return "pdf"
    if suffix in _IMAGE_EXTENSIONS:
        return "image"
    raise AppError(ErrorCode.VALIDATION_ERROR, f"unsupported source file extension: {suffix!r}")


@dataclass(frozen=True)
class SourceMetadata:
    """media type、Project相対path、hash、初期状態を保持する。"""

    media_type: str
    relative_path: str
    content_hash: str
    status: SourceStatus

    @classmethod
    def from_file(
        cls,
        source_path: Path,
        *,
        project_paths: ProjectPaths,
        destination_relative: str,
        media_type: str | None = None,
    ) -> "SourceMetadata":
        if not source_path or project_paths is None or not destination_relative:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "source_path, project_paths and destination_relative are required",
            )

        source_path = Path(source_path)
        if source_path.is_symlink():
            # TASK-REVIEW-001 2.6節: symlink経由でproject外のfileを読み出すことを防ぐ。
            raise AppError(ErrorCode.VALIDATION_ERROR, f"symbolic links are not allowed as source files: {source_path}")
        if not source_path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"source file does not exist: {source_path}")

        # Raises AppError on absolute path or project-root escape.
        project_paths.resolve_relative(destination_relative)

        resolved_media_type = media_type or _infer_media_type(source_path)
        if resolved_media_type not in _VALID_MEDIA_TYPES:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unsupported media_type: {resolved_media_type!r}")

        content_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        status = SourceStatus.READY if resolved_media_type == "text" else SourceStatus.REGISTERED

        return cls(
            media_type=resolved_media_type,
            relative_path=destination_relative,
            content_hash=content_hash,
            status=status,
        )
