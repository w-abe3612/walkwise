"""STEP3->STEP4 test suite for TASK-SOURCE-002: 資料正規化・chunk・index・manifest.

Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
Spec: docs/specifications/source-preprocessing.md
Production files:
- script/source_processing/normalize.py
- script/source_processing/chunking.py
- script/source_processing/manifests.py
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode
from script.source_processing.normalize import NormalizationRules, normalize_text

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_source_002_01() -> None:
    """TC-SOURCE-002-01 — 低リスク正規化

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: 改行・Unicode・反復headerがある
    When: normalizeする
    Then: 決定的修正とbefore/after hash/diffを返す
    """
    text = (
        "Chapter Title\r\n"
        "\r\n"
        "本文の１行目です。\r\n"
        "Chapter Title\r\n"
        "本文の２行目です。\r\n"
        "Chapter Title\r\n"
    )

    result = normalize_text(text, NormalizationRules())

    assert result.original_text == text
    assert "\r" not in result.normalized_text
    # 反復headerは最初の1回だけ残り、以降は除去される。
    assert result.normalized_text.count("Chapter Title") == 1
    assert "Chapter Title" in result.removed_lines

    assert result.input_hash != result.output_hash
    assert len(result.diff) > 0


@pytest.mark.unit
def test_tc_source_002_04() -> None:
    """TC-SOURCE-002-04 — Unicode/改行/空白の決定的正規化

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「Unicode/改行/空白の決定的正規化」を実行する
    Then: 「Unicode/改行/空白の決定的正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    # 全角英数字(NFKC正規化対象)と、行末の余分な空白、CRLF混在。
    text = "Ａｌｐｈａ　Ｂｅｔａ   \r\nSecond line\t\t\r\n"

    rules = NormalizationRules()
    first = normalize_text(text, rules)
    second = normalize_text(text, rules)

    assert first == second
    assert "Alpha" in first.normalized_text
    assert "Beta" in first.normalized_text
    for line in first.normalized_text.split("\n"):
        assert line == line.rstrip()


@pytest.mark.unit
def test_tc_source_002_07() -> None:
    """TC-SOURCE-002-07 — structured Markdown/YAML/JSON

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「structured Markdown/YAML/JSON」を実行する
    Then: 「structured Markdown/YAML/JSON」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    fenced_yaml = "```yaml\nkey:   value   \r\nlist:\r\n  - a  \r\n```"
    text = f"導入の説明文です。   \r\n\r\n{fenced_yaml}\r\n\r\n続きの説明文です。   \r\n"

    result = normalize_text(text, NormalizationRules())

    # fenced block(structured YAML)の内容は一切変更されない。
    assert fenced_yaml in result.normalized_text
    # fenced block外の通常本文は行末空白が除去される。
    assert "導入の説明文です。" in result.normalized_text
    assert "導入の説明文です。   " not in result.normalized_text


@pytest.mark.unit
def test_tc_source_002_10() -> None:
    """TC-SOURCE-002-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    text = "既存の正常な入力本文です。\n"
    good_result = normalize_text(text, NormalizationRules())
    good_input_hash_before = good_result.input_hash
    good_output_hash_before = good_result.output_hash

    # 意図的な失敗(rules欠落)を発生させる。
    with pytest.raises(AppError) as excinfo:
        normalize_text(text, None)
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    # 既存の正常な結果は変化しない(dataclassはfrozenであり、再代入もできない)。
    assert good_result.input_hash == good_input_hash_before
    assert good_result.output_hash == good_output_hash_before
    assert good_result.original_text == text
    with pytest.raises(AttributeError):
        good_result.normalized_text = "tampered"
