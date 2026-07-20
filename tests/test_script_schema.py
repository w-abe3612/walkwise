"""STEP4 test implementation for TASK-SCRIPT-001: ScriptDocument/ScriptSegment/SpeakerRef schema.

Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.core.errors import AppError, ErrorCode
from script.pipelines.draft_generation import DraftChunkInput, DraftGenerationPipeline, segment_legacy_text
from script.schemas.chapter_spec import ChapterSpec, RequiredTopicRef
from script.schemas.script import ScriptDocument, ScriptSegment, SpeakerRef

pytestmark = pytest.mark.mvp


def _speaker() -> SpeakerRef:
    return SpeakerRef(character_id="neutral-explainer", role="explainer")


def _segment(segment_id: str, order: int, text: str = "some narration text") -> ScriptSegment:
    return ScriptSegment(
        segment_id=segment_id,
        order=order,
        speaker=_speaker(),
        segment_type="explanation",
        text=text,
    )


@pytest.mark.unit
def test_tc_script_001_01() -> None:
    """TC-SCRIPT-001-01 — segment一意: ID/order/textを検証し順序を保持。"""
    segments = tuple(_segment(f"ch01-seg{i:03d}", i, f"text {i}") for i in range(1, 9))
    document = ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=segments)

    assert [segment.order for segment in document.ordered_segments()] == list(range(1, 9))
    assert [segment.text for segment in document.ordered_segments()] == [f"text {i}" for i in range(1, 9)]

    with pytest.raises(AppError):
        ScriptDocument(
            project_id="proj-1",
            chapter_id="ch01",
            stage="draft",
            segments=segments + (_segment("ch01-seg001", 9),),  # 重複segment_id
        )

    with pytest.raises(AppError):
        ScriptDocument(
            project_id="proj-1",
            chapter_id="ch01",
            stage="draft",
            segments=segments[:-1] + (_segment("ch01-seg999", 1),),  # 重複order
        )


@pytest.mark.unit
def test_tc_script_001_03() -> None:
    """TC-SCRIPT-001-03 — 旧TXT: 同一TXTを2回変換すると同一ID/orderになり人間未承認。"""
    legacy_text = "第一段落の説明文です。\n\n第二段落の説明文です。\n\n第三段落の説明文です。"

    document_1 = segment_legacy_text(legacy_text, chapter_id="ch01")
    document_2 = segment_legacy_text(legacy_text, chapter_id="ch01")

    assert document_1 == document_2
    assert [segment.segment_id for segment in document_1.segments] == [
        "ch01-seg001",
        "ch01-seg002",
        "ch01-seg003",
    ]
    for segment in document_1.segments:
        assert segment.review_status == "pending_review"
        assert segment.review_status != "approved"
    assert document_1.provenance is not None
    assert document_1.provenance.legacy_input is True


@pytest.mark.unit
def test_tc_script_001_05() -> None:
    """TC-SCRIPT-001-05 — prompt/input provenance: 生成物が入力chunk/modelの由来を保持する。"""

    class _FakeAIClient:
        def check_connectivity(self) -> object:
            return object()

        def generate(self, request: AIRequest) -> AIResult:
            return AIResult(
                text="SOURCE_REFS: src-1\nTEXT: generated narration",
                provider="fake",
                model=request.model or "fake-model",
                usage=AIUsage(),
            )

    chapter_spec = ChapterSpec(
        project_id="proj-1",
        chapter_id="ch01",
        order=1,
        title="Loops",
        purpose="Cover loops",
        learning_outcomes=("Explain loops",),
        required_topics=(RequiredTopicRef(topic_id="loops"),),
        explanation_order=("loops",),
        source_ids=("src-1",),
        known_topic_ids=frozenset({"loops"}),
        known_source_ids=frozenset({"src-1"}),
    )
    chunks = (DraftChunkInput(chunk_id="c1", source_id="src-1", text="loops explained"),)

    pipeline = DraftGenerationPipeline(ai_client=_FakeAIClient(), model="gemini-2.5-flash")
    document = pipeline.generate(chapter_spec, chunks)

    assert document.provenance is not None
    assert document.provenance.source_chunk_ids == ("c1",)
    assert document.provenance.model == "gemini-2.5-flash"
    assert document.provenance.legacy_input is False


@pytest.mark.unit
def test_tc_script_001_07() -> None:
    """TC-SCRIPT-001-07 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as excinfo:
        ScriptDocument(project_id="", chapter_id="ch01", stage="draft", segments=(_segment("s1", 1),))
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=())

    with pytest.raises(AppError):
        ScriptSegment(segment_id="", order=1, speaker=_speaker(), segment_type="explanation", text="x")

    with pytest.raises(AppError):
        ScriptSegment(segment_id="s1", order=1, speaker=_speaker(), segment_type="explanation", text="")


@pytest.mark.unit
def test_tc_script_001_09() -> None:
    """TC-SCRIPT-001-09 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    segments = (_segment("ch01-seg001", 1), _segment("ch01-seg002", 2))
    document = ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=segments)
    before = (document.project_id, document.chapter_id, document.segments)

    with pytest.raises(AppError):
        ScriptDocument(
            project_id="proj-1",
            chapter_id="ch01",
            stage="draft",
            segments=segments + (_segment("ch01-seg001", 3),),
        )

    assert (document.project_id, document.chapter_id, document.segments) == before
