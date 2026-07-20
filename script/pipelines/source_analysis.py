"""script/pipelines/source_analysis.py — 公開契約: SourceAnalysisPipeline.run, analyze_gaps.

Contract: docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from script.ai_clients.base import AIClient, AIRequest
from script.core.errors import AppError, ErrorCode
from script.schemas.source_analysis import (
    CoverageEntry,
    CoverageMap,
    CoverageStatus,
    SourceRequirement,
    SourceSummary,
    TopicIndex,
    TopicIndexEntry,
)

_ECONOMY_MODEL_HINT = "gemini-2.5-flash-lite"


@dataclass(frozen=True)
class SourceChunkInput:
    """SourceAnalysisPipelineへの1 chunk分の入力。"""

    chunk_id: str
    source_id: str
    text: str
    topic_ids: tuple[str, ...] = ()
    conflicting: bool = False

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chunk_id is required")
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")
        if not self.text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")


@dataclass(frozen=True)
class RequiredTopic:
    """coverage判定で必須とみなすtopic(source-requirements.yaml相当の最小入力)。"""

    topic_id: str
    required_source_roles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.topic_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "topic_id is required")


@dataclass(frozen=True)
class SourceAnalysisBundle:
    """SourceAnalysisPipeline.run()の戻り値。"""

    project_id: str
    summaries: tuple[SourceSummary, ...]
    topic_index: TopicIndex
    coverage_map: CoverageMap


class SourceAnalysisPipeline:
    """必要chunkだけをAI(economy_structuring)へ渡しsummary/index/coverageを生成する。"""

    def __init__(self, *, ai_client: AIClient, model: str = _ECONOMY_MODEL_HINT) -> None:
        if ai_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "ai_client is required")
        if not model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")
        self._ai_client = ai_client
        self._model = model

    def run(
        self,
        project_id: str,
        chunks: Sequence[SourceChunkInput],
        *,
        required_topics: Sequence[RequiredTopic] = (),
    ) -> SourceAnalysisBundle:
        """必要chunkだけをAIへ渡しsummary/index/coverageを生成する。"""
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not chunks:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chunks must not be empty")

        summaries = tuple(self._build_summary(source_id, chunks) for source_id in self._distinct_source_ids(chunks))
        topic_index = self._build_topic_index(chunks)
        coverage_map = self._build_coverage_map(project_id, chunks, required_topics)

        return SourceAnalysisBundle(
            project_id=project_id,
            summaries=summaries,
            topic_index=topic_index,
            coverage_map=coverage_map,
        )

    @staticmethod
    def _distinct_source_ids(chunks: Sequence[SourceChunkInput]) -> list[str]:
        return sorted({chunk.source_id for chunk in chunks})

    def _build_summary(self, source_id: str, chunks: Sequence[SourceChunkInput]) -> SourceSummary:
        # 必要chunkだけをAIへ渡す: 対象source_idのchunkだけを本文に含める。
        own_chunks = [chunk for chunk in chunks if chunk.source_id == source_id]
        request = AIRequest(
            user_text="\n\n".join(chunk.text for chunk in own_chunks),
            system_instruction=f"Summarize the source '{source_id}' for a source-summary.yaml entry.",
            model=self._model,
        )
        result = self._ai_client.generate(request)
        return SourceSummary(source_id=source_id, summary=result.text)

    @staticmethod
    def _build_topic_index(chunks: Sequence[SourceChunkInput]) -> TopicIndex:
        topic_ids = sorted({topic_id for chunk in chunks for topic_id in chunk.topic_ids})
        entries = []
        for topic_id in topic_ids:
            # 必要chunkだけをAIへ渡す: 当該topicにhintされたchunkだけを参照する。
            relevant = [chunk.chunk_id for chunk in chunks if topic_id in chunk.topic_ids]
            entries.append(TopicIndexEntry(topic_id=topic_id, chunk_refs=tuple(relevant)))
        return TopicIndex(entries=tuple(entries))

    @staticmethod
    def _build_coverage_map(
        project_id: str,
        chunks: Sequence[SourceChunkInput],
        required_topics: Sequence[RequiredTopic],
    ) -> CoverageMap:
        entries: list[CoverageEntry] = []
        for required in required_topics:
            topic_chunks = [chunk for chunk in chunks if required.topic_id in chunk.topic_ids]
            source_refs = tuple(sorted({chunk.source_id for chunk in topic_chunks}))

            if not topic_chunks:
                entries.append(
                    CoverageEntry(
                        topic_id=required.topic_id,
                        status=CoverageStatus.MISSING,
                        source_refs=(),
                        next_action="propose_sources",
                    )
                )
                continue

            if any(chunk.conflicting for chunk in topic_chunks):
                # 矛盾を黙って解決しない: 常にhuman reviewへ送る。
                entries.append(
                    CoverageEntry(
                        topic_id=required.topic_id,
                        status=CoverageStatus.CONFLICT,
                        source_refs=source_refs,
                        next_action="human_review_required",
                    )
                )
                continue

            entries.append(
                CoverageEntry(topic_id=required.topic_id, status=CoverageStatus.COVERED, source_refs=source_refs)
            )

        return CoverageMap(project_id=project_id, entries=tuple(entries))


def analyze_gaps(bundle: SourceAnalysisBundle) -> list[SourceRequirement]:
    """missing/duplicate/conflictを決定的に抽出する。"""
    if bundle is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "bundle is required")

    requirements: list[SourceRequirement] = []
    for entry in sorted(bundle.coverage_map.entries, key=lambda item: item.topic_id):
        if entry.status is CoverageStatus.MISSING:
            requirements.append(SourceRequirement(topic_id=entry.topic_id, reason="missing"))
        elif entry.status is CoverageStatus.CONFLICT:
            requirements.append(SourceRequirement(topic_id=entry.topic_id, reason="conflict"))
        elif entry.status is CoverageStatus.PARTIALLY_COVERED:
            requirements.append(SourceRequirement(topic_id=entry.topic_id, reason="partially_covered"))

    # duplicate: 同一chunk_idが複数回入力された場合(データ不整合)を検出する。
    duplicate_topic_ids: set[str] = set()
    for entry in bundle.topic_index.entries:
        counts: dict[str, int] = {}
        for chunk_ref in entry.chunk_refs:
            counts[chunk_ref] = counts.get(chunk_ref, 0) + 1
        if any(count > 1 for count in counts.values()):
            duplicate_topic_ids.add(entry.topic_id)

    for topic_id in sorted(duplicate_topic_ids):
        requirements.append(SourceRequirement(topic_id=topic_id, reason="duplicate"))

    return requirements
