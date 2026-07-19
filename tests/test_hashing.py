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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-02 is not implemented")
def test_tc_core_002_02() -> None:
    """TC-CORE-002-02 — canonical hash
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: mapping key順・CRLF/NFDだけが異なる同値data
    When: canonical_sha256を計算する
    Then: 同じhashになる。配列順差は別hashになる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-05 is not implemented")
def test_tc_core_002_05() -> None:
    """TC-CORE-002-05 — 安全なYAML/JSON load/dump
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `validate_identifier(value: str) -> str`を通じて「安全なYAML/JSON load/dump」を実行する
    Then: 「安全なYAML/JSON load/dump」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-08 is not implemented")
def test_tc_core_002_08() -> None:
    """TC-CORE-002-08 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-08")
