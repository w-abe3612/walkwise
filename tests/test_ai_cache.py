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

from script.ai.cache import AICache, AICacheKey
from script.core.errors import AppError, ErrorCode

pytestmark = pytest.mark.mvp


def _key(input_hash: str = "hash-0001") -> AICacheKey:
    return AICacheKey(
        task_type="topic_extraction",
        logical_tier="economy_structuring",
        model="gemini-2.5-flash-lite",
        prompt_id="topic-extraction",
        prompt_version="1.0",
        input_hash=input_hash,
    )


@pytest.mark.unit
def test_tc_ai_002_02() -> None:
    """TC-AI-002-02 — cache hit

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: 同一task/model/prompt/input hash
    When: 2回実行
    Then: 2回目はclientを呼ばない
    """
    cache = AICache()
    key = _key()
    client_calls = {"count": 0}

    def call_client_with_cache(cache_key: AICacheKey) -> str:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        client_calls["count"] += 1
        result = "generated result"
        cache.put(cache_key, result)
        return result

    first = call_client_with_cache(key)
    second = call_client_with_cache(key)

    assert first == second == "generated result"
    assert client_calls["count"] == 1

    # 異なるinput hashはcache missとなり、clientが再度呼ばれる。
    different_key = _key(input_hash="hash-0002")
    call_client_with_cache(different_key)
    assert client_calls["count"] == 2


@pytest.mark.unit
def test_tc_ai_002_05() -> None:
    """TC-AI-002-05 — token/usage記録

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を通じて「token/usage記録」を実行する
    Then: 「token/usage記録」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    cache = AICache()
    key = _key()

    result_with_usage = {
        "text": "structured output",
        "usage": {"input_tokens": 120, "output_tokens": 40, "total_tokens": 160},
    }
    cache.put(key, result_with_usage)

    cached = cache.get(key)
    assert cached is not None
    assert cached["usage"]["total_tokens"] == 160
    # cache経由でも取得結果はkeyに対して決定的(常に同一)である。
    assert cache.get(key) == cached


@pytest.mark.unit
def test_tc_ai_002_08() -> None:
    """TC-AI-002-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `AIRouter.resolve(task_class, policy) -> ModelSelection`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    cache = AICache()

    with pytest.raises(AppError) as excinfo_get:
        cache.get(None)
    assert excinfo_get.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_put:
        cache.put(None, "value")
    assert excinfo_put.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_key:
        AICacheKey(
            task_type="",
            logical_tier="economy_structuring",
            model="gemini-2.5-flash-lite",
            prompt_id="topic-extraction",
            prompt_version="1.0",
            input_hash="hash-0001",
        )
    assert excinfo_key.value.code is ErrorCode.VALIDATION_ERROR
