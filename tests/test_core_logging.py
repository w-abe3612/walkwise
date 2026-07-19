"""STEP3 test scaffold for TASK-CORE-001: 設定・共通エラー・ログ契約.

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
Release scope: MVP
Planned production files:
- script/core/config.py
- script/core/errors.py
- script/core/logging.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-001-03 is not implemented")
def test_tc_core_001_03() -> None:
    """TC-CORE-001-03 — ログredaction
    
    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: API keyを含むcontextがある
    When: ログを出力する
    Then: keyを伏せ、timestampはtimezone付きISO 8601になる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CORE-001-06 is not implemented")
def test_tc_core_001_06() -> None:
    """TC-CORE-001-06 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `AppConfig.load(env: Mapping[str, str] | None = None) -> AppConfig`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CORE-001-06")
