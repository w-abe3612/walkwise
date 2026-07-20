"""STEP4 test implementation for TASK-PIPELINE-001: RegenerationPlanner / RegenerationPlan.

Contract: docs/test-cases/TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode
from script.pipelines.impact import Change, ChangeType, DependencyGraph, ImpactAnalyzer, TargetCategory
from script.pipelines.regeneration import CacheState, RegenerationPlanner

pytestmark = pytest.mark.mvp


def _graph() -> DependencyGraph:
    return DependencyGraph(
        project_id="proj-1",
        chapter_ids=frozenset({"ch01"}),
        segment_ids_by_chapter={"ch01": frozenset({"ch01-seg001", "ch01-seg002"})},
    )


def _all_approved() -> CacheState:
    return CacheState(
        approvals={
            "materials_curriculum": "approved",
            "planning": "approved",
            "verified_script": "approved",
            "preview_audio": "approved",
        }
    )


@pytest.mark.unit
def test_tc_pipeline_001_02() -> None:
    """TC-PIPELINE-001-02 — voice profile変更: 影響する音声だけ対象で原稿は対象外。"""
    change = Change(change_type=ChangeType.VOICE_PROFILE, project_id="proj-1", chapter_id="ch01")
    impact_set = ImpactAnalyzer().analyze(change, _graph())

    plan = RegenerationPlanner().plan(impact_set, _all_approved())

    targets = {step.target for step in plan.steps}
    assert targets == {TargetCategory.SEGMENT_AUDIO, TargetCategory.CHAPTER_MP3, TargetCategory.AUDIO_MANIFEST}
    assert TargetCategory.DRAFT_SCRIPT not in targets
    assert TargetCategory.NARRATION not in targets
    plan.validate_no_unrelated_targets()


@pytest.mark.unit
def test_tc_pipeline_001_04() -> None:
    """TC-PIPELINE-001-04 — 依存graph: 未知のchapter/segmentはNOT_FOUND、既知なら解決できる。"""
    graph = _graph()

    with pytest.raises(AppError) as excinfo_chapter:
        ImpactAnalyzer().analyze(
            Change(change_type=ChangeType.CHAPTER_SPEC, project_id="proj-1", chapter_id="unknown-chapter"),
            graph,
        )
    assert excinfo_chapter.value.code is ErrorCode.NOT_FOUND

    with pytest.raises(AppError) as excinfo_segment:
        ImpactAnalyzer().analyze(
            Change(
                change_type=ChangeType.TEXT,
                project_id="proj-1",
                chapter_id="ch01",
                segment_id="unknown-segment",
            ),
            graph,
        )
    assert excinfo_segment.value.code is ErrorCode.NOT_FOUND

    resolved = ImpactAnalyzer().analyze(
        Change(change_type=ChangeType.TEXT, project_id="proj-1", chapter_id="ch01", segment_id="ch01-seg001"),
        graph,
    )
    assert resolved.segment_id == "ch01-seg001"


@pytest.mark.unit
def test_tc_pipeline_001_06() -> None:
    """TC-PIPELINE-001-06 — 承認無効化: 未承認・invalidated・changes_requestedでは安定errorで停止する。"""
    change = Change(
        change_type=ChangeType.TEXT,
        project_id="proj-1",
        chapter_id="ch01",
        segment_id="ch01-seg001",
    )
    impact_set = ImpactAnalyzer().analyze(change, _graph())

    for blocking_status in ("draft", "invalidated", "changes_requested", "rejected", "review_pending"):
        cache_state = CacheState(approvals={"preview_audio": blocking_status})
        with pytest.raises(AppError) as excinfo:
            RegenerationPlanner().plan(impact_set, cache_state)
        assert excinfo.value.code is ErrorCode.PERMISSION_DENIED

    approved_cache_state = CacheState(approvals={"preview_audio": "approved"})
    plan = RegenerationPlanner().plan(impact_set, approved_cache_state)
    assert plan.steps


@pytest.mark.unit
def test_tc_pipeline_001_08() -> None:
    """TC-PIPELINE-001-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    change = Change(change_type=ChangeType.MP3_TAG, project_id="proj-1", chapter_id="ch01")
    impact_set = ImpactAnalyzer().analyze(change, _graph())

    with pytest.raises(AppError) as excinfo:
        RegenerationPlanner().plan(None, _all_approved())  # type: ignore[arg-type]
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        RegenerationPlanner().plan(impact_set, None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        CacheState(approvals=None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        Change(change_type=ChangeType.MP3_TAG, project_id="")


@pytest.mark.unit
def test_tc_pipeline_001_10() -> None:
    """TC-PIPELINE-001-10 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    change = Change(change_type=ChangeType.MP3_TAG, project_id="proj-1", chapter_id="ch01")
    impact_set = ImpactAnalyzer().analyze(change, _graph())
    cache_state = _all_approved()

    plan = RegenerationPlanner().plan(impact_set, cache_state)
    before = (impact_set.targets, dict(cache_state.approvals))

    blocked_change = Change(
        change_type=ChangeType.TEXT, project_id="proj-1", chapter_id="ch01", segment_id="ch01-seg001"
    )
    blocked_impact_set = ImpactAnalyzer().analyze(blocked_change, _graph())
    blocked_cache_state = CacheState(approvals={"preview_audio": "invalidated"})
    with pytest.raises(AppError):
        RegenerationPlanner().plan(blocked_impact_set, blocked_cache_state)

    assert (impact_set.targets, dict(cache_state.approvals)) == before
    assert plan.steps
