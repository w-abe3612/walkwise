"""script/schemas/chapter_spec.py — 公開契約: ChapterSpec.validate().

Contract: docs/test-cases/TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md
Spec: docs/specifications/04-chapter-generation-schema.md
"""

from __future__ import annotations

from dataclasses import dataclass, field

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class RequiredTopicRef:
    """chapter-spec.yamlのrequired_topics[]の1件。"""

    topic_id: str
    title: str = ""
    requirements: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.topic_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_id is required")


@dataclass(frozen=True)
class ChapterSpec:
    """chapters/<chapter_id>/chapter-spec.yaml相当。

    known_topic_ids/known_source_ids は「承認済みproject内で実在するID一覧」を
    呼び出し側が渡す前提(04-chapter-generation-schema.md 8節の参照整合検証)。
    """

    project_id: str
    chapter_id: str
    order: int
    title: str
    purpose: str
    learning_outcomes: tuple[str, ...]
    required_topics: tuple[RequiredTopicRef, ...]
    explanation_order: tuple[str, ...]
    source_ids: tuple[str, ...]
    known_topic_ids: frozenset[str]
    known_source_ids: frozenset[str]
    ai_execution_policy: dict[str, str] = field(default_factory=dict)
    target_character_count: int | None = None

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if self.order < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "order must be 1 or greater")
        if not self.title:
            raise AppError(ErrorCode.VALIDATION_ERROR, "title is required")
        if not self.required_topics:
            raise AppError(ErrorCode.VALIDATION_ERROR, "required_topics must not be empty")
        if self.target_character_count is not None and self.target_character_count <= 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "target_character_count must be a positive integer")

    def validate(self) -> tuple[str, ...]:
        """topic/source参照と目標値を検証し、非致命的warningsを返す。

        04-chapter-generation-schema.md 8節:
        - 未知のchapter_id/topic参照、重複topic_id、source未知参照はError(AppErrorを送出)。
        - learning_outcomesが空はWarning(処理は継続、呼び出し側へ通知するだけ)。
        """
        topic_ids_in_spec = tuple(ref.topic_id for ref in self.required_topics)
        if len(set(topic_ids_in_spec)) != len(topic_ids_in_spec):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"duplicate required_topics topic_id in chapter {self.chapter_id}",
            )

        for topic_id in topic_ids_in_spec:
            if topic_id not in self.known_topic_ids:
                raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown topic_id referenced: {topic_id}")

        for topic_id in self.explanation_order:
            if topic_id not in topic_ids_in_spec:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"explanation_order references unknown topic_id: {topic_id}",
                )

        for source_id in self.source_ids:
            if source_id not in self.known_source_ids:
                raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown source_id referenced: {source_id}")

        warnings: list[str] = []
        if not self.learning_outcomes:
            warnings.append("learning_outcomes is empty")
        return tuple(warnings)
