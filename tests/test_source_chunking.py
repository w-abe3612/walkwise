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
from script.source_processing.chunking import ChunkLocator, StructuredSourceInput, chunk_structured_source
from script.source_processing.normalize import NormalizationRules, normalize_text

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_source_002_02() -> None:
    """TC-SOURCE-002-02 — soft chunk

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: 2000文字付近の段落
    When: chunkする
    Then: 意味境界を優先しlocatorを失わない
    """
    paragraph_a = "あ" * 1200
    paragraph_b = "い" * 1200
    paragraph_c = "う" * 500
    text = f"{paragraph_a}\n\n{paragraph_b}\n\n{paragraph_c}"

    locator = ChunkLocator(chapter="3", section="3.2")
    source = StructuredSourceInput(source_id="sample-source", text=text, locator=locator)

    chunks = chunk_structured_source(source, soft_limit=2000)

    # paragraph_a単独で1200文字、+paragraph_b(1200)は2000を超えるため、
    # 意味境界(段落境界)でchunkが分かれる。paragraph_bとparagraph_c(500)は
    # 合計1700文字で2000以下のため同じchunkにまとめてよい。
    assert len(chunks) == 2
    assert chunks[0].text == paragraph_a
    assert chunks[1].text == f"{paragraph_b}\n\n{paragraph_c}"

    # 各段落は途中で分割されず、どこかのchunkに丸ごと含まれる。
    combined = "\n\n".join(chunk.text for chunk in chunks)
    assert paragraph_a in combined
    assert paragraph_b in combined
    assert paragraph_c in combined

    for chunk in chunks:
        assert chunk.locator == locator
        assert chunk.chunk_id.startswith("sample-source-chunk-")


@pytest.mark.unit
def test_tc_source_002_05() -> None:
    """TC-SOURCE-002-05 — 繰返しheader/footer除去

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「繰返しheader/footer除去」を実行する
    Then: 「繰返しheader/footer除去」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    text = (
        "MySQL 8.0 Reference Manual\n"
        "13.1 Data Definition Statements\n"
        "MySQL 8.0 Reference Manual\n"
        "13.1.20 CREATE TABLE\n"
        "MySQL 8.0 Reference Manual\n"
    )

    result = normalize_text(text, NormalizationRules(remove_repeated_headers_footers=True))
    assert result.normalized_text.count("MySQL 8.0 Reference Manual") == 1
    assert result.removed_lines.count("MySQL 8.0 Reference Manual") == 2

    # 無効化した場合は除去しない。
    result_disabled = normalize_text(text, NormalizationRules(remove_repeated_headers_footers=False))
    assert result_disabled.normalized_text.count("MySQL 8.0 Reference Manual") == 3


@pytest.mark.unit
def test_tc_source_002_08() -> None:
    """TC-SOURCE-002-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `normalize_text(text, rules) -> NormalizationResult`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_source:
        chunk_structured_source(None)
    assert excinfo_source.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_source_id:
        chunk_structured_source(StructuredSourceInput(source_id="", text="本文"))
    assert excinfo_source_id.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_text:
        chunk_structured_source(StructuredSourceInput(source_id="src-1", text=""))
    assert excinfo_text.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_limit:
        chunk_structured_source(StructuredSourceInput(source_id="src-1", text="本文"), soft_limit=0)
    assert excinfo_limit.value.code is ErrorCode.VALIDATION_ERROR
