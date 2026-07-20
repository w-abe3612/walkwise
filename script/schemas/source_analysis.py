"""script/schemas/source_analysis.py — 公開契約: SourceSummary/TopicIndex/CoverageMap/SourceRequirement.

Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from script.core.errors import AppError, ErrorCode


class CoverageStatus(str, Enum):
    """source-storage-and-common-schema.md 5.7節の状態列挙値。"""

    COVERED = "covered"
    PARTIALLY_COVERED = "partially_covered"
    CONFLICT = "conflict"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class SourceSummary:
    """資料ごとの目的・範囲・役割(source-summary.yaml相当)。"""

    source_id: str
    summary: str
    scope_notes: str = ""
    roles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")
        if not self.summary:
            raise AppError(ErrorCode.VALIDATION_ERROR, "summary is required")


@dataclass(frozen=True)
class TopicIndexEntry:
    """1 topicに対応するchunk参照(topic-index.yaml相当)。"""

    topic_id: str
    chunk_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.topic_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_id is required")
        if not self.chunk_refs:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chunk_refs must not be empty")


@dataclass(frozen=True)
class TopicIndex:
    """topic -> source chunkの対応一覧。"""

    entries: tuple[TopicIndexEntry, ...]

    def chunk_refs_for(self, topic_id: str) -> tuple[str, ...]:
        for entry in self.entries:
            if entry.topic_id == topic_id:
                return entry.chunk_refs
        return ()


@dataclass(frozen=True)
class CoverageEntry:
    """1 topicの充足状態(coverage-map.yaml相当)。"""

    topic_id: str
    status: CoverageStatus
    source_refs: tuple[str, ...] = ()
    next_action: str | None = None

    def __post_init__(self) -> None:
        if not self.topic_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_id is required")
        if self.status is CoverageStatus.CONFLICT and not self.next_action:
            # source-storage-and-common-schema.md 10節:
            # coverageがconflictなのにnext_actionがない状態はError(黙った解決の禁止)。
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "conflict coverage entries require a next_action (must not silently resolve)",
            )


@dataclass(frozen=True)
class CoverageMap:
    """project全体のcoverage状態。"""

    project_id: str
    entries: tuple[CoverageEntry, ...]

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")


@dataclass(frozen=True)
class SourceRequirement:
    """coverage不足から生成される追加資料要件(source-requirements.yaml相当)。"""

    topic_id: str
    reason: str
    required_source_roles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.topic_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_id is required")
        if not self.reason:
            raise AppError(ErrorCode.VALIDATION_ERROR, "reason is required")
