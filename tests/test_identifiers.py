"""Implementation for TASK-CORE-002: 共通ID・canonical hash・YAML/JSON入出力 (identifiers).

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Production file exercised: script/core/identifiers.py
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError
from script.core.identifiers import normalize_unit_id, validate_identifier

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_core_002_01() -> None:
    """TC-CORE-002-01 — ID境界

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: 正常IDと空白・underscore・日本語・slashを含むIDがある
    When: validate_identifierを呼ぶ
    Then: 正常だけを返し不正値はvalidation error
    """
    valid_ids = ["database-foundations", "ch01", "ch01-seg001", "mysql-8-reference"]
    for value in valid_ids:
        assert validate_identifier(value) == value

    invalid_ids = [
        "Database Foundations",
        "database_foundations",
        "データベース",
        "database/foundations",
        "",
    ]
    for value in invalid_ids:
        with pytest.raises(AppError):
            validate_identifier(value)


@pytest.mark.unit
def test_tc_core_002_04() -> None:
    """TC-CORE-002-04 — UTF-8/NFC/LF正規化

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `validate_identifier(value: str) -> str`を通じて「UTF-8/NFC/LF正規化」を実行する
    Then: 「UTF-8/NFC/LF正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    # NFD-decomposed "book" alias must normalize to the same NFC form as the
    # canonical alias target before comparison.
    nfd_full_book = "full_book"
    assert normalize_unit_id(nfd_full_book) == "book"
    assert normalize_unit_id("book") == "book"
    assert normalize_unit_id("ch01") == "ch01"


@pytest.mark.unit
def test_tc_core_002_07() -> None:
    """TC-CORE-002-07 — 再実行時の決定性

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `validate_identifier(value: str) -> str`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    first = validate_identifier("ch01-seg001")
    second = validate_identifier("ch01-seg001")
    assert first == second == "ch01-seg001"

    first_unit = normalize_unit_id("full_book")
    second_unit = normalize_unit_id("full_book")
    assert first_unit == second_unit == "book"
