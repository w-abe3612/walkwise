"""STEP4 test implementation for TASK-PIPELINE-001: ImpactAnalyzer.

Contract: docs/test-cases/TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.pipelines.impact import Change, ChangeType, DependencyGraph, ImpactAnalyzer, TargetCategory

pytestmark = pytest.mark.mvp


def _graph() -> DependencyGraph:
    return DependencyGraph(
        project_id="proj-1",
        chapter_ids=frozenset({"ch01"}),
        segment_ids_by_chapter={"ch01": frozenset({"ch01-seg001", "ch01-seg002"})},
    )


@pytest.mark.unit
def test_tc_pipeline_001_01() -> None:
    """TC-PIPELINE-001-01 — tts_text変更: 対象segment audioと章MP3/manifestだけ対象。"""
    change = Change(
        change_type=ChangeType.TTS_TEXT,
        project_id="proj-1",
        chapter_id="ch01",
        segment_id="ch01-seg002",
    )
    impact_set = ImpactAnalyzer().analyze(change, _graph())

    assert set(impact_set.targets) == {
        TargetCategory.SEGMENT_AUDIO,
        TargetCategory.CHAPTER_MP3,
        TargetCategory.AUDIO_MANIFEST,
    }
    assert impact_set.segment_id == "ch01-seg002"
    assert TargetCategory.DRAFT_SCRIPT not in impact_set.targets


@pytest.mark.unit
def test_tc_pipeline_001_03() -> None:
    """TC-PIPELINE-001-03 — MP3 tag変更: MP3 packagingだけ対象。"""
    change = Change(change_type=ChangeType.MP3_TAG, project_id="proj-1", chapter_id="ch01")
    impact_set = ImpactAnalyzer().analyze(change, _graph())

    assert impact_set.targets == (TargetCategory.MP3_PACKAGING,)


@pytest.mark.unit
def test_tc_pipeline_001_05() -> None:
    """TC-PIPELINE-001-05 — hash差分: 同一入力で同一hash、内容差分でhashが変化する。"""
    change_1 = Change(change_type=ChangeType.MP3_TAG, project_id="proj-1", chapter_id="ch01", detail="artist tag")
    change_2 = Change(change_type=ChangeType.MP3_TAG, project_id="proj-1", chapter_id="ch01", detail="artist tag")
    change_different = Change(
        change_type=ChangeType.MP3_TAG, project_id="proj-1", chapter_id="ch01", detail="album tag"
    )

    result_1 = ImpactAnalyzer().analyze(change_1, _graph())
    result_2 = ImpactAnalyzer().analyze(change_2, _graph())
    result_different = ImpactAnalyzer().analyze(change_different, _graph())

    assert result_1.content_hash == result_2.content_hash
    assert result_1.content_hash != result_different.content_hash


@pytest.mark.unit
def test_tc_pipeline_001_07() -> None:
    """TC-PIPELINE-001-07 — 既存正常成果物保持: analyzeは入力(change/graph)を変更しない。"""
    change = Change(
        change_type=ChangeType.TEXT,
        project_id="proj-1",
        chapter_id="ch01",
        segment_id="ch01-seg001",
    )
    graph = _graph()
    before_graph = (graph.project_id, graph.chapter_ids, dict(graph.segment_ids_by_chapter))
    before_change = (change.change_type, change.project_id, change.chapter_id, change.segment_id)

    ImpactAnalyzer().analyze(change, graph)

    after_graph = (graph.project_id, graph.chapter_ids, dict(graph.segment_ids_by_chapter))
    after_change = (change.change_type, change.project_id, change.chapter_id, change.segment_id)
    assert before_graph == after_graph
    assert before_change == after_change


@pytest.mark.unit
def test_tc_pipeline_001_09() -> None:
    """TC-PIPELINE-001-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    change = Change(
        change_type=ChangeType.VOICE_PROFILE,
        project_id="proj-1",
        chapter_id="ch01",
    )
    graph = _graph()

    result_1 = ImpactAnalyzer().analyze(change, graph)
    result_2 = ImpactAnalyzer().analyze(change, graph)

    assert result_1 == result_2
