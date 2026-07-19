"""STEP3 test scaffold for TASK-AI-002: AIモデルrouting・cache・費用・予算停止.

Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
Release scope: MVP
Planned production files:
- script/ai/routing.py
- script/ai/cache.py
- script/ai/budget.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-03 is not implemented")
def test_tc_ai_002_03() -> None:
    """TC-AI-002-03 — 予算停止
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: 残予算0
    When: AI実行を要求
    Then: API呼出し前にbudget_exceeded
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-06 is not implemented")
def test_tc_ai_002_06() -> None:
    """TC-AI-002-06 — 推測値と実測値の区別
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「推測値と実測値の区別」を実行する
    Then: 「推測値と実測値の区別」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-09 is not implemented")
def test_tc_ai_002_09() -> None:
    """TC-AI-002-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-09")
