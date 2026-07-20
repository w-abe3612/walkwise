"""script/schemas/curriculum.py — 公開契約: TopicMap/Curriculum.

Contract: docs/test-cases/TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md
Spec: docs/specifications/03-project-plan-schema.md
"""

from __future__ import annotations

from dataclasses import dataclass

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class TopicMapEntry:
    """1 topicのtitleと関連source。"""

    topic_id: str
    title: str
    source_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.topic_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_id is required")
        if not self.title:
            raise AppError(ErrorCode.VALIDATION_ERROR, "title is required")


@dataclass(frozen=True)
class TopicMap:
    """カリキュラム全体のtopic一覧。"""

    entries: tuple[TopicMapEntry, ...]

    def topic_ids(self) -> frozenset[str]:
        return frozenset(entry.topic_id for entry in self.entries)


@dataclass(frozen=True)
class CurriculumChapter:
    """1章分の最小情報(章ID・順序・扱うtopic)。"""

    chapter_id: str
    order: int
    title: str
    topic_ids: tuple[str, ...]
    learning_outcomes: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if self.order < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "order must be 1 or greater")
        if not self.topic_ids:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_ids must not be empty")


@dataclass(frozen=True)
class Curriculum:
    """章順・topic対応の全体構造。生成直後はdraftであり、承認済みで作成できない。"""

    project_id: str
    chapters: tuple[CurriculumChapter, ...]
    status: str = "draft"

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.chapters:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapters must not be empty")

        orders = [chapter.order for chapter in self.chapters]
        if len(orders) != len(set(orders)):
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter order must be unique")

        if self.status == "approved":
            # 07-approval-workflow.mdと連動: AI生成物は人間承認前にapprovedになれない。
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "Curriculum must not be constructed in approved status (human approval required)",
            )
