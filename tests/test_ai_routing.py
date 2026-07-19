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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-01 is not implemented")
def test_tc_ai_002_01() -> None:
    """TC-AI-002-01 — 高保証未設定
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: high_assurance taskでmodel未設定
    When: routeする
    Then: standardへ降格せずblocked/human review
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-04 is not implemented")
def test_tc_ai_002_04() -> None:
    """TC-AI-002-04 — model policy load
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「model policy load」を実行する
    Then: 「model policy load」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-07 is not implemented")
def test_tc_ai_002_07() -> None:
    """TC-AI-002-07 — 予算上限
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「予算上限」を実行する
    Then: 予算不足を外部API呼出し前に検出し、usageを実測値と推測値で混同しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-10 is not implemented")
def test_tc_ai_002_10() -> None:
    """TC-AI-002-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-10")
