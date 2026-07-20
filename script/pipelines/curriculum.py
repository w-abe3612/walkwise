"""script/pipelines/curriculum.py — 公開契約: CurriculumPipeline.generate(analysis, project_plan) -> CurriculumResult.

Contract: docs/test-cases/TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md
Spec: docs/specifications/04-chapter-generation-schema.md, docs/specifications/03-project-plan-schema.md
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from script.ai_clients.base import AIClient, AIRequest
from script.core.errors import AppError, ErrorCode
from script.pipelines.source_analysis import SourceAnalysisBundle
from script.schemas.chapter_spec import ChapterSpec, RequiredTopicRef
from script.schemas.curriculum import Curriculum, CurriculumChapter, TopicMap, TopicMapEntry
from script.schemas.source_analysis import CoverageStatus

_STANDARD_MODEL_HINT = "gemini-2.5-flash"

# 04-chapter-generation-schema.md ai_execution_policy: 章生成に使う論理層の既定値。
_DEFAULT_AI_EXECUTION_POLICY = {
    "draft_tier": "standard_generation",
    "claim_extraction_tier": "economy_structuring",
    "final_review_tier": "high_assurance_review",
}

_EXCLUDED_COVERAGE_STATUSES = (CoverageStatus.MISSING, CoverageStatus.CONFLICT)


@dataclass(frozen=True)
class CurriculumResult:
    """CurriculumPipeline.generate()の戻り値。承認前draftとして保存される。"""

    project_id: str
    status: str
    topic_map: TopicMap
    curriculum: Curriculum
    chapter_specs: tuple[ChapterSpec, ...]

    def __post_init__(self) -> None:
        if self.status not in ("review_pending", "draft"):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"CurriculumResult must be review_pending or draft, got: {self.status}",
            )


class CurriculumPipeline:
    """coverage反映済みのtopicから、承認前draftのtopic map・curriculum・章仕様を作る。"""

    def __init__(self, *, ai_client: AIClient, model: str = _STANDARD_MODEL_HINT) -> None:
        if ai_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "ai_client is required")
        if not model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")
        self._ai_client = ai_client
        self._model = model

    def generate(self, analysis: SourceAnalysisBundle, project_plan: Mapping[str, object]) -> CurriculumResult:
        """coverage反映済みのtopicだけをcurriculumへ含め、承認前draftを返す。"""
        if analysis is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "analysis is required")
        if not project_plan:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_plan is required")
        if not analysis.topic_index.entries:
            raise AppError(ErrorCode.VALIDATION_ERROR, "analysis.topic_index must not be empty")

        project_id = analysis.project_id
        coverage_by_topic = {entry.topic_id: entry for entry in analysis.coverage_map.entries}

        topic_entries: list[TopicMapEntry] = []
        for index_entry in sorted(analysis.topic_index.entries, key=lambda e: e.topic_id):
            coverage_entry = coverage_by_topic.get(index_entry.topic_id)
            if coverage_entry is not None and coverage_entry.status in _EXCLUDED_COVERAGE_STATUSES:
                # missing/conflictのtopicは解決されるまでcurriculumへ含めない(coverage反映)。
                continue
            source_refs = coverage_entry.source_refs if coverage_entry is not None else ()
            topic_entries.append(
                TopicMapEntry(
                    topic_id=index_entry.topic_id,
                    title=index_entry.topic_id.replace("_", " ").strip().title() or index_entry.topic_id,
                    source_ids=source_refs,
                )
            )

        if not topic_entries:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "no topics are eligible for curriculum generation (all missing/conflict)",
            )

        topic_map = TopicMap(entries=tuple(topic_entries))

        # AI tier指定: 章生成の下書きはstandard_generation層のmodelで実行する(黙った降格をしない)。
        request = AIRequest(
            user_text="\n".join(entry.title for entry in topic_map.entries),
            system_instruction="Draft a chapter ordering rationale for these topics.",
            model=self._model,
        )
        self._ai_client.generate(request)

        chapters = tuple(
            CurriculumChapter(
                chapter_id=f"chapter-{order:04d}",
                order=order,
                title=entry.title,
                topic_ids=(entry.topic_id,),
                source_ids=entry.source_ids,
            )
            for order, entry in enumerate(topic_map.entries, start=1)
        )
        curriculum = Curriculum(project_id=project_id, chapters=chapters, status="draft")

        known_topic_ids = topic_map.topic_ids()
        known_source_ids = frozenset(source_id for entry in topic_map.entries for source_id in entry.source_ids)

        chapter_specs = tuple(
            ChapterSpec(
                project_id=project_id,
                chapter_id=chapter.chapter_id,
                order=chapter.order,
                title=chapter.title,
                purpose=f"Cover the topic: {chapter.title}",
                learning_outcomes=(f"Explain {chapter.title}",),
                required_topics=tuple(RequiredTopicRef(topic_id=topic_id) for topic_id in chapter.topic_ids),
                explanation_order=chapter.topic_ids,
                source_ids=chapter.source_ids,
                known_topic_ids=known_topic_ids,
                known_source_ids=known_source_ids,
                ai_execution_policy=dict(_DEFAULT_AI_EXECUTION_POLICY),
            )
            for chapter in curriculum.chapters
        )
        for chapter_spec in chapter_specs:
            chapter_spec.validate()

        return CurriculumResult(
            project_id=project_id,
            status="review_pending",
            topic_map=topic_map,
            curriculum=curriculum,
            chapter_specs=chapter_specs,
        )
