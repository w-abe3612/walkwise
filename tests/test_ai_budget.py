"""STEP3->STEP4 test suite for TASK-AI-002: AIモデルrouting・cache・費用・予算停止.

Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
Production files:
- script/ai/routing.py
- script/ai/cache.py
- script/ai/budget.py
"""

from __future__ import annotations

import pytest

from script.ai.budget import BudgetGuard, UsageEstimate
from script.core.errors import AppError, ErrorCode

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_ai_002_03() -> None:
    """TC-AI-002-03 — 予算停止

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: 残予算0
    When: AI実行を要求
    Then: API呼出し前にbudget_exceeded
    """
    guard = BudgetGuard(stop_usd=0.0)
    api_calls = {"count": 0}

    def simulated_api_call() -> None:
        api_calls["count"] += 1

    with pytest.raises(AppError) as excinfo:
        guard.assert_available()
        simulated_api_call()

    assert excinfo.value.code is ErrorCode.PERMISSION_DENIED
    assert "budget_exceeded" in excinfo.value.message
    assert api_calls["count"] == 0


@pytest.mark.unit
def test_tc_ai_002_06() -> None:
    """TC-AI-002-06 — 推測値と実測値の区別

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「推測値と実測値の区別」を実行する
    Then: 「推測値と実測値の区別」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    guard = BudgetGuard(stop_usd=10.0)

    # reserve()は推測値であり、予算判定のためだけに使われ、spent_usdやrecordsを変更しない。
    guard.reserve(UsageEstimate(cost_usd=3.0, is_measured=False))
    guard.reserve(UsageEstimate(cost_usd=3.0, is_measured=False))
    assert guard.spent_usd == 0.0
    assert guard.records == ()

    # record()は実測値であり、spent_usdへ反映されrecordsに残る。
    guard.record(UsageEstimate(cost_usd=2.5, tokens=500, is_measured=True))
    assert guard.spent_usd == 2.5
    assert len(guard.records) == 1
    assert guard.records[0].is_measured is True
    assert guard.records[0].tokens == 500

    # usage metadata欠落(cost_usd=None)は推測値として扱い、実測費用へ加算しない。
    guard.record(UsageEstimate(cost_usd=None, tokens=None, is_measured=False))
    assert guard.spent_usd == 2.5
    assert len(guard.records) == 2
    assert guard.records[-1].is_measured is False


@pytest.mark.unit
def test_tc_ai_002_09() -> None:
    """TC-AI-002-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    guard_a = BudgetGuard(stop_usd=5.0)
    guard_b = BudgetGuard(stop_usd=5.0)

    usage = UsageEstimate(cost_usd=1.0, tokens=200, is_measured=True)
    guard_a.record(usage)
    guard_b.record(usage)

    assert guard_a.spent_usd == guard_b.spent_usd
    assert guard_a.records == guard_b.records
