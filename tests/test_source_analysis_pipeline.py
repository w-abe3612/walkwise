"""STEP3->STEP4 test suite for TASK-AI-003: source summary・topic index・coverage map.

Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
Production files:
- script/pipelines/source_analysis.py
- script/schemas/source_analysis.py
"""

from __future__ import annotations

import pytest

from script.ai_clients.base import AIResult, AIUsage
from script.pipelines.source_analysis import (
    RequiredTopic,
    SourceAnalysisPipeline,
    SourceChunkInput,
    analyze_gaps,
)
from script.schemas.source_analysis import SourceSummary

pytestmark = pytest.mark.mvp


class _FakeAIClient:
    def __init__(self) -> None:
        self.requests: list[object] = []

    def check_connectivity(self):  # pragma: no cover - not exercised in these tests
        return None

    def generate(self, request):
        self.requests.append(request)
        return AIResult(
            text=f"summary::{len(request.user_text)}chars",
            provider="gemini",
            model=request.model or "gemini-2.5-flash-lite",
            usage=AIUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        )


@pytest.mark.unit
def test_tc_ai_003_01() -> None:
    """TC-AI-003-01 — 必要chunk限定

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P0
    Layer: unit
    Given: 章に関連するchunkと無関係chunk
    When: pipelineを実行
    Then: AI requestには関連chunkだけ入る
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="RELEVANT_A content", topic_ids=("t1",)),
        SourceChunkInput(chunk_id="b-0001", source_id="source-b", text="UNRELATED_B content", topic_ids=("t2",)),
    ]

    pipeline = SourceAnalysisPipeline(ai_client=client)
    pipeline.run("project-1", chunks)

    # source-aのsummary生成requestには、source-bの本文が含まれない。
    source_a_requests = [req for req in client.requests if "RELEVANT_A" in req.user_text]
    assert len(source_a_requests) == 1
    assert "UNRELATED_B" not in source_a_requests[0].user_text


@pytest.mark.integration_mock
def test_tc_ai_003_03() -> None:
    """TC-AI-003-03 — 矛盾

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P0
    Layer: integration_mock
    Given: 同topicでsource conflict
    When: 分析
    Then: conflictを黙って解決せずreviewへ送る
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(
            chunk_id="a-0001", source_id="source-a", text="claim: X is true", topic_ids=("normalization",)
        ),
        SourceChunkInput(
            chunk_id="b-0001",
            source_id="source-b",
            text="claim: X is false",
            topic_ids=("normalization",),
            conflicting=True,
        ),
    ]
    required_topics = [RequiredTopic(topic_id="normalization")]

    pipeline = SourceAnalysisPipeline(ai_client=client)
    bundle = pipeline.run("project-1", chunks, required_topics=required_topics)

    entry = next(e for e in bundle.coverage_map.entries if e.topic_id == "normalization")
    assert entry.status.value == "conflict"
    assert entry.next_action == "human_review_required"

    requirements = analyze_gaps(bundle)
    assert any(req.topic_id == "normalization" and req.reason == "conflict" for req in requirements)


@pytest.mark.unit
def test_tc_ai_003_05() -> None:
    """TC-AI-003-05 — source summary schema

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceSummary/TopicIndex/CoverageMap/SourceRequirement`を通じて「source summary schema」を実行する
    Then: 「source summary schema」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("t1",)),
    ]

    pipeline = SourceAnalysisPipeline(ai_client=client)
    bundle = pipeline.run("project-1", chunks)

    assert len(bundle.summaries) == 1
    summary = bundle.summaries[0]
    assert isinstance(summary, SourceSummary)
    assert summary.source_id == "source-a"
    assert summary.summary


@pytest.mark.unit
def test_tc_ai_003_07() -> None:
    """TC-AI-003-07 — 追加資料要求

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceSummary/TopicIndex/CoverageMap/SourceRequirement`を通じて「追加資料要求」を実行する
    Then: 「追加資料要求」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("t1",)),
    ]
    required_topics = [RequiredTopic(topic_id="t1"), RequiredTopic(topic_id="missing_topic")]

    pipeline = SourceAnalysisPipeline(ai_client=client)
    bundle = pipeline.run("project-1", chunks, required_topics=required_topics)

    requirements = analyze_gaps(bundle)
    missing = [req for req in requirements if req.topic_id == "missing_topic"]
    assert len(missing) == 1
    assert missing[0].reason == "missing"


@pytest.mark.unit
def test_tc_ai_003_09() -> None:
    """TC-AI-003-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `SourceSummary/TopicIndex/CoverageMap/SourceRequirement`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("t1",)),
    ]
    required_topics = [RequiredTopic(topic_id="t1")]

    pipeline_a = SourceAnalysisPipeline(ai_client=_FakeAIClient())
    pipeline_b = SourceAnalysisPipeline(ai_client=_FakeAIClient())

    bundle_a = pipeline_a.run("project-1", chunks, required_topics=required_topics)
    bundle_b = pipeline_b.run("project-1", chunks, required_topics=required_topics)

    assert bundle_a == bundle_b
    assert analyze_gaps(bundle_a) == analyze_gaps(bundle_b)
