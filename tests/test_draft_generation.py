"""STEP4 test implementation for TASK-SCRIPT-001: DraftGenerationPipeline.

Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
Release scope: MVP
"""

from __future__ import annotations

import copy

import pytest

from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.pipelines.draft_generation import DraftChunkInput, DraftGenerationPipeline
from script.schemas.chapter_spec import ChapterSpec, RequiredTopicRef

pytestmark = pytest.mark.mvp


def _chapter_spec(**overrides: object) -> ChapterSpec:
    fields: dict[str, object] = dict(
        project_id="proj-1",
        chapter_id="ch01",
        order=1,
        title="Loops",
        purpose="Cover loops",
        learning_outcomes=("Explain loops",),
        required_topics=(RequiredTopicRef(topic_id="loops"),),
        explanation_order=("loops",),
        source_ids=("src-1", "src-2"),
        known_topic_ids=frozenset({"loops"}),
        known_source_ids=frozenset({"src-1", "src-2"}),
    )
    fields.update(overrides)
    return ChapterSpec(**fields)  # type: ignore[arg-type]


class _ScriptedAIClient:
    """chunk_idごとに固定の応答を返すfake AIClient。"""

    def __init__(self, responses: dict[str, str]) -> None:
        self._responses = responses
        self.calls: list[AIRequest] = []

    def check_connectivity(self) -> object:
        return object()

    def generate(self, request: AIRequest) -> AIResult:
        self.calls.append(request)
        for marker, response_text in self._responses.items():
            if marker in request.user_text:
                return AIResult(text=response_text, provider="fake", model=request.model or "fake-model", usage=AIUsage())
        raise AssertionError(f"no scripted response for request: {request.user_text!r}")


@pytest.mark.integration_mock
def test_tc_script_001_02() -> None:
    """TC-SCRIPT-001-02 — 指定外資料: source_ids外の事実はpending claimとして記録し黙って承認しない。"""
    chapter_spec = _chapter_spec(source_ids=("src-1",), known_source_ids=frozenset({"src-1"}))
    chunks = (DraftChunkInput(chunk_id="c1", source_id="src-1", text="loops material"),)

    fake_client = _ScriptedAIClient(
        {"loops material": "SOURCE_REFS: src-1, src-unlisted\nTEXT: loops explained with an extra claim"}
    )
    pipeline = DraftGenerationPipeline(ai_client=fake_client)

    document = pipeline.generate(chapter_spec, chunks)

    assert document.pending_claims == ("ch01-seg001",)
    segment = document.segments[0]
    assert "src-unlisted" in segment.source_refs
    assert segment.review_status != "approved"


@pytest.mark.unit
def test_tc_script_001_04() -> None:
    """TC-SCRIPT-001-04 — standard generation: 呼び出しは指定modelのまま、勝手に別tierへ変更しない。"""
    chapter_spec = _chapter_spec()
    chunks = (
        DraftChunkInput(chunk_id="c1", source_id="src-1", text="loops material"),
        DraftChunkInput(chunk_id="c2", source_id="src-2", text="loops material 2"),
    )
    fake_client = _ScriptedAIClient(
        {
            "loops material": "SOURCE_REFS: src-1\nTEXT: first segment",
            "loops material 2": "SOURCE_REFS: src-2\nTEXT: second segment",
        }
    )
    pipeline = DraftGenerationPipeline(ai_client=fake_client, model="gemini-2.5-flash")

    pipeline.generate(chapter_spec, chunks)

    assert len(fake_client.calls) == 2
    assert all(call.model == "gemini-2.5-flash" for call in fake_client.calls)


@pytest.mark.unit
def test_tc_script_001_06() -> None:
    """TC-SCRIPT-001-06 — 入力不変: 処理前後で入力chunk/chapter_specが変化しない。"""
    chapter_spec = _chapter_spec()
    chunks = (DraftChunkInput(chunk_id="c1", source_id="src-1", text="loops material"),)
    chunks_before = copy.deepcopy(chunks)
    chapter_spec_before = copy.deepcopy(chapter_spec)

    fake_client = _ScriptedAIClient({"loops material": "SOURCE_REFS: src-1\nTEXT: first segment"})
    pipeline = DraftGenerationPipeline(ai_client=fake_client)

    pipeline.generate(chapter_spec, chunks)

    assert chunks == chunks_before
    assert chapter_spec == chapter_spec_before


@pytest.mark.unit
def test_tc_script_001_08() -> None:
    """TC-SCRIPT-001-08 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    chapter_spec = _chapter_spec()
    chunks = (DraftChunkInput(chunk_id="c1", source_id="src-1", text="loops material"),)

    fake_client = _ScriptedAIClient({"loops material": "SOURCE_REFS: src-1\nTEXT: first segment"})
    pipeline = DraftGenerationPipeline(ai_client=fake_client)

    document_1 = pipeline.generate(chapter_spec, chunks)
    document_2 = pipeline.generate(chapter_spec, chunks)

    assert document_1 == document_2
    assert len(fake_client.calls) == 2
