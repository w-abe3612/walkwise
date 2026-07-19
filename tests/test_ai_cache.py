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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-02 is not implemented")
def test_tc_ai_002_02() -> None:
    """TC-AI-002-02 — cache hit
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: 同一task/model/prompt/input hash
    When: 2回実行
    Then: 2回目はclientを呼ばない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-05 is not implemented")
def test_tc_ai_002_05() -> None:
    """TC-AI-002-05 — token/usage記録
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「token/usage記録」を実行する
    Then: 「token/usage記録」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-002-08 is not implemented")
def test_tc_ai_002_08() -> None:
    """TC-AI-002-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-002-08")
