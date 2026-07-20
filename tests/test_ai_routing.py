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
from script.ai.routing import AIRouter, ModelPolicy, ModelSelection
from script.core.errors import AppError, ErrorCode

pytestmark = pytest.mark.mvp

_POLICY_MAPPING = {
    "provider": "google",
    "tiers": {
        "economy_structuring": {"model": "gemini-2.5-flash-lite", "env_override": "GEMINI_MODEL_ECONOMY"},
        "standard_generation": {"model": "gemini-2.5-flash", "env_override": "GEMINI_MODEL_STANDARD"},
        "high_assurance_review": {
            "model": None,
            "env_override": "GEMINI_MODEL_HIGH_ASSURANCE",
            "required_when_invoked": True,
        },
    },
}


@pytest.mark.unit
def test_tc_ai_002_01() -> None:
    """TC-AI-002-01 — 高保証未設定

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: high_assurance taskでmodel未設定
    When: routeする
    Then: standardへ降格せずblocked/human review
    """
    policy = ModelPolicy.from_mapping(_POLICY_MAPPING)
    router = AIRouter(env={})

    with pytest.raises(AppError) as excinfo:
        router.resolve("high_assurance_review", policy)

    assert excinfo.value.code is ErrorCode.EXTERNAL_UNAVAILABLE
    # resolve()が例外を送出しているため、standardへの黙った降格
    # (ModelSelectionがstandardモデルで返る事態)は発生し得ない。


@pytest.mark.unit
def test_tc_ai_002_04() -> None:
    """TC-AI-002-04 — model policy load

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「model policy load」を実行する
    Then: 「model policy load」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    policy = ModelPolicy.from_mapping(_POLICY_MAPPING)
    assert policy.provider == "google"
    assert set(policy.tiers) == {"economy_structuring", "standard_generation", "high_assurance_review"}

    router = AIRouter(env={})
    selection = router.resolve("economy_structuring", policy)
    assert isinstance(selection, ModelSelection)
    assert selection.model == "gemini-2.5-flash-lite"
    assert selection.logical_tier == "economy_structuring"

    # env_overrideが設定されていれば、policyの既定値より優先される。
    router_with_override = AIRouter(env={"GEMINI_MODEL_ECONOMY": "gemini-override-model"})
    overridden = router_with_override.resolve("economy_structuring", policy)
    assert overridden.model == "gemini-override-model"

    with pytest.raises(AppError) as excinfo:
        ModelPolicy.from_mapping({"provider": "google"})
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_ai_002_07() -> None:
    """TC-AI-002-07 — 予算上限

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「予算上限」を実行する
    Then: 予算不足を外部API呼出し前に検出し、usageを実測値と推測値で混同しない。
    """
    guard = BudgetGuard(stop_usd=1.0)
    api_calls = {"count": 0}

    def simulated_api_call() -> None:
        api_calls["count"] += 1

    # 見積り(推測値)がstop_usdを超える場合、API呼出し前にbudget_exceededとする。
    with pytest.raises(AppError) as excinfo:
        guard.reserve(UsageEstimate(cost_usd=5.0, is_measured=False))
        simulated_api_call()
    assert excinfo.value.code is ErrorCode.PERMISSION_DENIED
    assert api_calls["count"] == 0

    # reserve(推測値)はspent_usdを変更しない(実測値と混同しない)。
    assert guard.spent_usd == 0.0
    assert guard.records == ()

    # 実際の呼出し後、実測値だけをrecordする。
    guard.reserve(UsageEstimate(cost_usd=0.5, is_measured=False))
    simulated_api_call()
    guard.record(UsageEstimate(cost_usd=0.5, tokens=100, is_measured=True))
    assert api_calls["count"] == 1
    assert guard.spent_usd == 0.5
    assert guard.records[-1].is_measured is True


@pytest.mark.unit
def test_tc_ai_002_10() -> None:
    """TC-AI-002-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    policy = ModelPolicy.from_mapping(_POLICY_MAPPING)
    router = AIRouter(env={})

    good_selection = router.resolve("standard_generation", policy)
    assert good_selection.model == "gemini-2.5-flash"

    # ModelPolicy/ModelSelectionはfrozenであり、書き換えられない。
    with pytest.raises(AttributeError):
        good_selection.model = "tampered"
    with pytest.raises(AttributeError):
        policy.provider = "tampered"

    # 意図的な失敗(未知のtier)を発生させても、既存の正常な戻り値は変化しない。
    with pytest.raises(AppError):
        router.resolve("not_a_real_tier", policy)

    assert good_selection.model == "gemini-2.5-flash"
    assert policy.provider == "google"
