"""script/persistence/paths.py — 公開契約: ProjectPaths.for_root(data_root, project_id) -> ProjectPaths.

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Spec: docs/specifications/17-local-data-persistence-policy.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from script.core.errors import AppError, ErrorCode
from script.core.identifiers import validate_identifier


@dataclass(frozen=True)
class ProjectPaths:
    """Project配下の相対・決定的な保存先。"""

    data_root: Path
    project_id: str

    @property
    def project_root(self) -> Path:
        return self.data_root / "library" / self.project_id

    @property
    def sources_dir(self) -> Path:
        return self.project_root / "sources"

    @property
    def chapters_dir(self) -> Path:
        return self.project_root / "chapters"

    @property
    def manifests_dir(self) -> Path:
        return self.project_root / "manifests"

    def resolve_relative(self, relative: str) -> Path:
        """Project root配下の相対pathを解決し、root外escapeを拒否する。"""
        root = self.project_root.resolve()
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"path escapes project root: {relative!r}") from exc
        return candidate

    def to_relative_str(self, path: Path) -> str:
        """DB保存用の、Project root基準の相対path文字列を返す(絶対path・root外は拒否)。"""
        root = self.project_root.resolve()
        resolved = Path(path).resolve()
        try:
            relative = resolved.relative_to(root)
        except ValueError as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"path outside project root: {path}") from exc
        return PurePosixPath(relative).as_posix()

    @classmethod
    def for_root(cls, data_root: Path, project_id: str) -> "ProjectPaths":
        if not data_root or not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root and project_id are required")
        validate_identifier(project_id)
        return cls(data_root=Path(data_root), project_id=project_id)
