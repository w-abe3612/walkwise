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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-03 is not implemented")
def test_tc_core_002_03() -> None:
    """TC-CORE-002-03 — 未知schema version
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: 未知majorと未知minorを読む
    When: structured fileをloadする
    Then: 未知majorはerror、読める未知minorはwarning
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-002-06 is not implemented")
def test_tc_core_002_06() -> None:
    """TC-CORE-002-06 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `validate_identifier(value: str) -> str`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-002-06")
