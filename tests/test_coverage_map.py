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
from script.core.errors import AppError, ErrorCode
from script.pipelines.source_analysis import (
    RequiredTopic,
    SourceAnalysisPipeline,
    SourceChunkInput,
    analyze_gaps,
)
from script.schemas.source_analysis import TopicIndex, TopicIndexEntry

pytestmark = pytest.mark.mvp


class _FakeAIClient:
    def __init__(self) -> None:
        self.requests: list[object] = []

    def check_connectivity(self):  # pragma: no cover
        return None

    def generate(self, request):
        self.requests.append(request)
        return AIResult(
            text=f"summary::{len(request.user_text)}chars",
            provider="gemini",
            model=request.model or "gemini-2.5-flash-lite",
            usage=AIUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        )


@pytest.mark.integration_mock
def test_tc_ai_003_02() -> None:
    """TC-AI-003-02 — coverage不足

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P0
    Layer: integration_mock
    Given: 必須topicが資料にない
    When: coverageを作る
    Then: missingと追加資料要件を出す
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("covered_topic",)),
    ]
    required_topics = [RequiredTopic(topic_id="covered_topic"), RequiredTopic(topic_id="uncovered_topic")]

    pipeline = SourceAnalysisPipeline(ai_client=client)
    bundle = pipeline.run("project-1", chunks, required_topics=required_topics)

    covered_entry = next(e for e in bundle.coverage_map.entries if e.topic_id == "covered_topic")
    assert covered_entry.status.value == "covered"

    missing_entry = next(e for e in bundle.coverage_map.entries if e.topic_id == "uncovered_topic")
    assert missing_entry.status.value == "missing"
    assert missing_entry.next_action == "propose_sources"

    requirements = analyze_gaps(bundle)
    assert any(req.topic_id == "uncovered_topic" and req.reason == "missing" for req in requirements)


@pytest.mark.unit
def test_tc_ai_003_04() -> None:
    """TC-AI-003-04 — economy structuring

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceSummary/TopicIndex/CoverageMap/SourceRequirement`を通じて「economy structuring」を実行する
    Then: 「economy structuring」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("t1",)),
    ]

    # 既定modelはeconomy_structuring層のヒント(gemini-2.5-flash-lite)を使う。
    pipeline = SourceAnalysisPipeline(ai_client=client)
    pipeline.run("project-1", chunks)

    assert len(client.requests) == 1
    assert client.requests[0].model == "gemini-2.5-flash-lite"

    # 明示的に別modelを指定した場合はそちらが使われる(強制固定ではない)。
    override_client = _FakeAIClient()
    override_pipeline = SourceAnalysisPipeline(ai_client=override_client, model="gemini-2.5-flash-lite-002")
    override_pipeline.run("project-1", chunks)
    assert override_client.requests[0].model == "gemini-2.5-flash-lite-002"


@pytest.mark.unit
def test_tc_ai_003_06() -> None:
    """TC-AI-003-06 — topic index

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceSummary/TopicIndex/CoverageMap/SourceRequirement`を通じて「topic index」を実行する
    Then: 「topic index」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    client = _FakeAIClient()
    chunks = [
        SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("t1", "t2")),
        SourceChunkInput(chunk_id="b-0001", source_id="source-b", text="content two", topic_ids=("t1",)),
    ]

    pipeline = SourceAnalysisPipeline(ai_client=client)
    bundle = pipeline.run("project-1", chunks)

    topic_index = bundle.topic_index
    assert isinstance(topic_index, TopicIndex)
    assert set(topic_index.chunk_refs_for("t1")) == {"a-0001", "b-0001"}
    assert topic_index.chunk_refs_for("t2") == ("a-0001",)
    assert topic_index.chunk_refs_for("no_such_topic") == ()

    with pytest.raises(AppError) as excinfo:
        TopicIndexEntry(topic_id="t1", chunk_refs=())
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_ai_003_08() -> None:
    """TC-AI-003-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `SourceSummary/TopicIndex/CoverageMap/SourceRequirement`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_client:
        SourceAnalysisPipeline(ai_client=None)
    assert excinfo_client.value.code is ErrorCode.VALIDATION_ERROR

    client = _FakeAIClient()
    pipeline = SourceAnalysisPipeline(ai_client=client)

    with pytest.raises(AppError) as excinfo_project:
        pipeline.run("", [SourceChunkInput(chunk_id="a", source_id="s", text="x")])
    assert excinfo_project.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_chunks:
        pipeline.run("project-1", [])
    assert excinfo_chunks.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_gaps:
        analyze_gaps(None)
    assert excinfo_gaps.value.code is ErrorCode.VALIDATION_ERROR

    # 検証失敗前に副作用(AI呼出し)が発生していない。
    assert client.requests == []


@pytest.mark.unit
def test_tc_ai_003_10() -> None:
    """TC-AI-003-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    client = _FakeAIClient()
    pipeline = SourceAnalysisPipeline(ai_client=client)

    good_chunks = [SourceChunkInput(chunk_id="a-0001", source_id="source-a", text="content one", topic_ids=("t1",))]
    good_bundle = pipeline.run("project-1", good_chunks)
    assert good_bundle.project_id == "project-1"

    # 意図的な失敗(空chunks)を発生させても、既存の正常な結果は変化しない。
    with pytest.raises(AppError):
        pipeline.run("project-1", [])

    assert good_bundle.project_id == "project-1"
    assert len(good_bundle.summaries) == 1
    assert good_chunks[0].text == "content one"
