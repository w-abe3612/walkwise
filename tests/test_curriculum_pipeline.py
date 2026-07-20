"""STEP4 test implementation for TASK-CURRICULUM-001: curriculum pipeline.

Contract: docs/test-cases/TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md
Release scope: MVP
"""

from __future__ import annotations

import copy

import pytest

from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.core.errors import AppError
from script.pipelines.curriculum import CurriculumPipeline, CurriculumResult
from script.pipelines.source_analysis import SourceAnalysisBundle
from script.schemas.source_analysis import (
    CoverageEntry,
    CoverageMap,
    CoverageStatus,
    SourceSummary,
    TopicIndex,
    TopicIndexEntry,
)

pytestmark = pytest.mark.mvp


class _FakeAIClient:
    def __init__(self) -> None:
        self.calls: list[AIRequest] = []

    def check_connectivity(self) -> object:
        return object()

    def generate(self, request: AIRequest) -> AIResult:
        self.calls.append(request)
        return AIResult(text="draft ordering rationale", provider="fake", model=request.model or "fake-model", usage=AIUsage())


def _bundle(*, include_missing: bool = False, include_conflict: bool = False) -> SourceAnalysisBundle:
    entries = [
        TopicIndexEntry(topic_id="loops", chunk_refs=("c1",)),
        TopicIndexEntry(topic_id="functions", chunk_refs=("c2",)),
    ]
    coverage_entries = [
        CoverageEntry(topic_id="loops", status=CoverageStatus.COVERED, source_refs=("src-1",)),
        CoverageEntry(topic_id="functions", status=CoverageStatus.COVERED, source_refs=("src-1", "src-2")),
    ]
    if include_missing:
        entries.append(TopicIndexEntry(topic_id="recursion", chunk_refs=("c3",)))
        coverage_entries.append(
            CoverageEntry(topic_id="recursion", status=CoverageStatus.MISSING, next_action="propose_sources")
        )
    if include_conflict:
        entries.append(TopicIndexEntry(topic_id="typing", chunk_refs=("c4",)))
        coverage_entries.append(
            CoverageEntry(
                topic_id="typing",
                status=CoverageStatus.CONFLICT,
                source_refs=("src-3",),
                next_action="human_review_required",
            )
        )

    return SourceAnalysisBundle(
        project_id="proj-1",
        summaries=(SourceSummary(source_id="src-1", summary="intro material"),),
        topic_index=TopicIndex(entries=tuple(entries)),
        coverage_map=CoverageMap(project_id="proj-1", entries=tuple(coverage_entries)),
    )


_PROJECT_PLAN = {"project_id": "proj-1", "planning_stage": "content_generation"}


@pytest.mark.integration_mock
def test_tc_curriculum_001_01() -> None:
    """TC-CURRICULUM-001-01 — 章参照整合: topic/source参照が存在し章orderが一意。"""
    pipeline = CurriculumPipeline(ai_client=_FakeAIClient())

    result = pipeline.generate(_bundle(), _PROJECT_PLAN)

    known_topic_ids = result.topic_map.topic_ids()
    orders = [chapter.order for chapter in result.curriculum.chapters]
    assert len(orders) == len(set(orders))

    for chapter_spec in result.chapter_specs:
        for ref in chapter_spec.required_topics:
            assert ref.topic_id in known_topic_ids
        for source_id in chapter_spec.source_ids:
            assert source_id in chapter_spec.known_source_ids
        # validate()が例外を出さないことで参照整合を再確認する。
        chapter_spec.validate()


@pytest.mark.unit
def test_tc_curriculum_001_03() -> None:
    """TC-CURRICULUM-001-03 — 承認前状態: AI生成直後はapprovedではなくreview_pending/draft。"""
    pipeline = CurriculumPipeline(ai_client=_FakeAIClient())

    result = pipeline.generate(_bundle(), _PROJECT_PLAN)

    assert result.status in ("review_pending", "draft")
    assert result.status != "approved"
    assert result.curriculum.status != "approved"

    with pytest.raises(AppError):
        # Curriculumはapproved状態で直接構築できない(人間承認が必須)。
        type(result.curriculum)(
            project_id="proj-1",
            chapters=result.curriculum.chapters,
            status="approved",
        )


@pytest.mark.unit
def test_tc_curriculum_001_05() -> None:
    """TC-CURRICULUM-001-05 — coverage反映: missing/conflictのtopicはcurriculumへ含めない。"""
    pipeline = CurriculumPipeline(ai_client=_FakeAIClient())

    result = pipeline.generate(_bundle(include_missing=True, include_conflict=True), _PROJECT_PLAN)

    included_topic_ids = {topic_id for chapter in result.curriculum.chapters for topic_id in chapter.topic_ids}
    assert "loops" in included_topic_ids
    assert "functions" in included_topic_ids
    assert "recursion" not in included_topic_ids
    assert "typing" not in included_topic_ids


@pytest.mark.unit
def test_tc_curriculum_001_07() -> None:
    """TC-CURRICULUM-001-07 — AI tier指定: 呼び出しは指定modelのまま、勝手に別tierへ変更しない。"""
    fake_client = _FakeAIClient()
    pipeline = CurriculumPipeline(ai_client=fake_client, model="gemini-2.5-flash")

    pipeline.generate(_bundle(), _PROJECT_PLAN)

    assert len(fake_client.calls) == 1
    assert fake_client.calls[0].model == "gemini-2.5-flash"


@pytest.mark.unit
def test_tc_curriculum_001_09() -> None:
    """TC-CURRICULUM-001-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    bundle = _bundle()
    fake_client = _FakeAIClient()
    pipeline = CurriculumPipeline(ai_client=fake_client)

    result_1 = pipeline.generate(bundle, _PROJECT_PLAN)
    result_2 = pipeline.generate(copy.deepcopy(bundle), _PROJECT_PLAN)

    assert result_1.topic_map == result_2.topic_map
    assert result_1.curriculum == result_2.curriculum
    assert result_1.chapter_specs == result_2.chapter_specs
    assert len(fake_client.calls) == 2
