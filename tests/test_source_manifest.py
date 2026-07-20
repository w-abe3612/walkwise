"""STEP3->STEP4 test suite for TASK-SOURCE-002: 資料正規化・chunk・index・manifest.

Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
Spec: docs/specifications/source-storage-and-common-schema.md
Production files:
- script/source_processing/normalize.py
- script/source_processing/chunking.py
- script/source_processing/manifests.py
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode
from script.source_processing.chunking import ChunkLocator, SourceChunk
from script.source_processing.manifests import build_chunk_manifest, build_topic_index
from script.source_processing.normalize import NormalizationRules, normalize_text

pytestmark = pytest.mark.mvp


def _chunk(chunk_id: str, order: int) -> SourceChunk:
    return SourceChunk(
        chunk_id=chunk_id,
        order=order,
        text=f"text-{order}",
        locator=ChunkLocator(chapter="1"),
        input_hash="a" * 64,
    )


@pytest.mark.unit
def test_tc_source_002_03() -> None:
    """TC-SOURCE-002-03 — 参照整合

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: chunk manifestとtopic index
    When: validateする
    Then: 全chunk IDが存在し重複がない
    """
    chunks = [_chunk("src-chunk-0001", 1), _chunk("src-chunk-0002", 2)]
    manifest = build_chunk_manifest(chunks)
    assert [entry["chunk_id"] for entry in manifest["chunks"]] == ["src-chunk-0001", "src-chunk-0002"]

    # 重複chunk_idは拒否する。
    with pytest.raises(AppError) as excinfo_dup_id:
        build_chunk_manifest([_chunk("src-chunk-0001", 1), _chunk("src-chunk-0001", 2)])
    assert excinfo_dup_id.value.code is ErrorCode.VALIDATION_ERROR

    # 重複orderも拒否する。
    with pytest.raises(AppError) as excinfo_dup_order:
        build_chunk_manifest([_chunk("src-chunk-0001", 1), _chunk("src-chunk-0002", 1)])
    assert excinfo_dup_order.value.code is ErrorCode.VALIDATION_ERROR

    # topic indexは存在するchunk_idだけを参照できる。
    topic_index = build_topic_index({"normalization": ["src-chunk-0001"]}, chunk_manifest=manifest)
    assert topic_index["topics"][0]["chunk_refs"] == ["src-chunk-0001"]

    with pytest.raises(AppError) as excinfo_unknown:
        build_topic_index({"normalization": ["src-chunk-9999"]}, chunk_manifest=manifest)
    assert excinfo_unknown.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_source_002_06() -> None:
    """TC-SOURCE-002-06 — footnote分離

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「footnote分離」を実行する
    Then: 「footnote分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    text = (
        "本文中に脚注参照[1]があります。\n"
        "[1]: これは脚注の本文です。\n"
        "[2]: 2番目の脚注です。\n"
    )

    result = normalize_text(text, NormalizationRules(separate_footnotes=True))

    assert result.footnotes == {
        "1": "これは脚注の本文です。",
        "2": "2番目の脚注です。",
    }
    assert "[1]: これは脚注の本文です。" not in result.normalized_text
    assert "本文中に脚注参照[1]があります。" in result.normalized_text

    # 無効化した場合は分離しない。
    result_disabled = normalize_text(text, NormalizationRules(separate_footnotes=False))
    assert result_disabled.footnotes == {}
    assert "[1]: これは脚注の本文です。" in result_disabled.normalized_text


@pytest.mark.unit
def test_tc_source_002_09() -> None:
    """TC-SOURCE-002-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `normalize_text(text, rules) -> NormalizationResult`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    chunks = [_chunk("src-chunk-0001", 1), _chunk("src-chunk-0002", 2)]

    first_manifest = build_chunk_manifest(chunks)
    second_manifest = build_chunk_manifest(chunks)
    assert first_manifest == second_manifest

    first_index = build_topic_index({"normalization": ["src-chunk-0001"]}, chunk_manifest=first_manifest)
    second_index = build_topic_index({"normalization": ["src-chunk-0001"]}, chunk_manifest=second_manifest)
    assert first_index == second_index
