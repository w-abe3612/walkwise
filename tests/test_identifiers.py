"""STEP3 test scaffold for TASK-CORE-002: 共通ID・canonical hash・YAML/JSON入出力.

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Release scope: MVP
Planned production files:
- script/core/identifiers.py
- script/core/hashing.py
- script/core/serialization.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-01 is not implemented")
def test_tc_core_002_01() -> None:
    """TC-CORE-002-01 — ID境界
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: 正常IDと空白・underscore・日本語・slashを含むIDがある
    When: validate_identifierを呼ぶ
    Then: 正常だけを返し不正値はvalidation error
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-04 is not implemented")
def test_tc_core_002_04() -> None:
    """TC-CORE-002-04 — UTF-8/NFC/LF正規化
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `validate_identifier(value: str) -> str`を通じて「UTF-8/NFC/LF正規化」を実行する
    Then: 「UTF-8/NFC/LF正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-07 is not implemented")
def test_tc_core_002_07() -> None:
    """TC-CORE-002-07 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `validate_identifier(value: str) -> str`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-07")
