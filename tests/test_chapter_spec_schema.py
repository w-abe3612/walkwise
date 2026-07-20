"""STEP4 test implementation for TASK-CURRICULUM-001: ChapterSpec schema.

Contract: docs/test-cases/TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode
from script.schemas.chapter_spec import ChapterSpec, RequiredTopicRef

pytestmark = pytest.mark.mvp


def _make_spec(**overrides: object) -> ChapterSpec:
    fields: dict[str, object] = dict(
        project_id="proj-1",
        chapter_id="chapter-0001",
        order=1,
        title="Loops",
        purpose="Cover loops",
        learning_outcomes=("Explain loops",),
        required_topics=(RequiredTopicRef(topic_id="loops"),),
        explanation_order=("loops",),
        source_ids=("src-1",),
        known_topic_ids=frozenset({"loops", "functions"}),
        known_source_ids=frozenset({"src-1", "src-2"}),
    )
    fields.update(overrides)
    return ChapterSpec(**fields)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_curriculum_001_02() -> None:
    """TC-CURRICULUM-001-02 — 未知topic: chapter specが未定義topicを参照するとvalidateがerrorにする。"""
    spec = _make_spec(
        required_topics=(RequiredTopicRef(topic_id="unknown_topic"),),
        explanation_order=("unknown_topic",),
        known_topic_ids=frozenset({"loops", "functions"}),
    )

    with pytest.raises(AppError) as excinfo:
        spec.validate()
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR
    assert "unknown_topic" in excinfo.value.message


@pytest.mark.unit
def test_tc_curriculum_001_04() -> None:
    """TC-CURRICULUM-001-04 — learning outcomes: 空はWarningとして扱い、validateは例外にしない。"""
    empty_spec = _make_spec(learning_outcomes=())
    warnings = empty_spec.validate()
    assert any("learning_outcomes" in warning for warning in warnings)

    filled_spec = _make_spec(learning_outcomes=("Explain loops",))
    assert filled_spec.validate() == ()


@pytest.mark.unit
def test_tc_curriculum_001_06() -> None:
    """TC-CURRICULUM-001-06 — source_ids: 未知source_id参照はerrorにし、既知なら通す。"""
    bad_spec = _make_spec(source_ids=("unknown_source",))
    with pytest.raises(AppError) as excinfo:
        bad_spec.validate()
    assert "unknown_source" in excinfo.value.message

    good_spec = _make_spec(source_ids=("src-1", "src-2"))
    assert good_spec.validate() == ()


@pytest.mark.unit
def test_tc_curriculum_001_08() -> None:
    """TC-CURRICULUM-001-08 — 必須入力欠落: 主ID欠落は副作用前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as excinfo:
        _make_spec(chapter_id="")
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        _make_spec(required_topics=())

    with pytest.raises(AppError):
        _make_spec(project_id="")


@pytest.mark.unit
def test_tc_curriculum_001_10() -> None:
    """TC-CURRICULUM-001-10 — 入力・既存成果物の不変性: validateの成功/失敗でspecの値が変化しない。"""
    spec = _make_spec()
    before = (spec.chapter_id, spec.required_topics, spec.source_ids, spec.learning_outcomes)

    spec.validate()
    assert (spec.chapter_id, spec.required_topics, spec.source_ids, spec.learning_outcomes) == before

    bad_spec = _make_spec(source_ids=("unknown_source",))
    before_bad = (bad_spec.chapter_id, bad_spec.required_topics, bad_spec.source_ids, bad_spec.learning_outcomes)
    with pytest.raises(AppError):
        bad_spec.validate()
    assert (bad_spec.chapter_id, bad_spec.required_topics, bad_spec.source_ids, bad_spec.learning_outcomes) == before_bad
