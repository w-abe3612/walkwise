"""STEP3->STEP4 test suite for TASK-AI-001: AI共通契約・Gemini adapter.

Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
Production files:
- script/ai_clients/base.py
- script/ai_clients/gemini/client.py
- script/ai_clients/registry.py
"""

from __future__ import annotations

from typing import Any

import pytest

from script.ai_clients.base import (
    AIClient,
    AIClientError,
    AIRequest,
    make_yaml_response_validator,
)
from script.ai_clients.gemini.client import ConnectivityResult, GeminiClient
from script.ai_clients.registry import AIClientRegistry
from script.core.errors import AppError, ErrorCode

pytestmark = pytest.mark.mvp


class _FakeResponse:
    def __init__(self, status_code: int, json_data: dict[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
        self.reason = "OK" if status_code < 400 else "ERROR"
        self.headers: dict[str, str] = {}

    def json(self) -> dict[str, Any]:
        return self._json_data


def _fixed_gemini_response(text: str) -> dict[str, Any]:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


@pytest.mark.unit
def test_tc_ai_001_02() -> None:
    """TC-AI-001-02 — retry区分

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: 429/5xxと400を返すmock
    When: generateする
    Then: 前者だけ上限内再試行し400は即時error
    """
    # 429を2回返し3回目で成功する。
    calls = {"count": 0}

    def flaky_post(url, headers, json, timeout):
        calls["count"] += 1
        if calls["count"] < 3:
            return _FakeResponse(429, text="rate limited")
        return _FakeResponse(200, _fixed_gemini_response("recovered"))

    client = GeminiClient(api_key="test-key", session_post=flaky_post, sleep=lambda _seconds: None)
    result = client.generate(AIRequest(user_text="prompt"))
    assert result.text == "recovered"
    assert calls["count"] == 3

    # 400は即時error(再試行しない)。
    bad_calls = {"count": 0}

    def bad_request_post(url, headers, json, timeout):
        bad_calls["count"] += 1
        return _FakeResponse(400, text="bad request")

    client_400 = GeminiClient(api_key="test-key", session_post=bad_request_post, sleep=lambda _seconds: None)
    with pytest.raises(AIClientError) as excinfo:
        client_400.generate(AIRequest(user_text="prompt"))
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR
    assert excinfo.value.retryable is False
    assert bad_calls["count"] == 1


@pytest.mark.unit
def test_tc_ai_001_04() -> None:
    """TC-AI-001-04 — AIClient Protocol

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「AIClient Protocol」を実行する
    Then: 「AIClient Protocol」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    client = GeminiClient(api_key="test-key")
    assert isinstance(client, AIClient)

    registry = AIClientRegistry()
    registry.register("gemini", client)
    assert registry.get("gemini") is client

    with pytest.raises(AppError) as excinfo:
        registry.get("unknown-provider")
    assert excinfo.value.code is ErrorCode.NOT_FOUND


@pytest.mark.unit
def test_tc_ai_001_06() -> None:
    """TC-AI-001-06 — JSON/YAML response validation hook

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「JSON/YAML response validation hook」を実行する
    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    """
    validator = make_yaml_response_validator()

    def make_post(text):
        def fake_post(url, headers, json, timeout):
            return _FakeResponse(200, _fixed_gemini_response(text))
        return fake_post

    good_client = GeminiClient(api_key="test-key", session_post=make_post("key: value\nlist:\n  - a\n  - b\n"))
    result = good_client.generate(AIRequest(user_text="prompt", validate_response=validator))
    assert "key: value" in result.text

    bad_client = GeminiClient(api_key="test-key", session_post=make_post(": : : not yaml : : :\n\t bad indent"))
    with pytest.raises(AIClientError) as excinfo:
        bad_client.generate(AIRequest(user_text="prompt", validate_response=validator))
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_ai_001_08() -> None:
    """TC-AI-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_user_text:
        AIRequest(user_text="")
    assert excinfo_user_text.value.code is ErrorCode.VALIDATION_ERROR

    def unreachable_post(url, headers, json, timeout):
        raise AssertionError("must not be called before validation")

    client_no_key = GeminiClient(api_key="", session_post=unreachable_post)
    with pytest.raises(AppError) as excinfo_no_key_generate:
        client_no_key.generate(AIRequest(user_text="prompt"))
    assert excinfo_no_key_generate.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_no_key_connectivity:
        client_no_key.check_connectivity()
    assert excinfo_no_key_connectivity.value.code is ErrorCode.VALIDATION_ERROR

    registry = AIClientRegistry()
    with pytest.raises(AppError) as excinfo_registry:
        registry.get("gemini")
    assert excinfo_registry.value.code is ErrorCode.NOT_FOUND


@pytest.mark.unit
def test_tc_ai_001_10() -> None:
    """TC-AI-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    def fake_post(url, headers, json, timeout):
        return _FakeResponse(200, _fixed_gemini_response("good result"))

    client = GeminiClient(api_key="test-key", session_post=fake_post)
    good_request = AIRequest(user_text="prompt")
    good_result = client.generate(good_request)
    assert good_result.text == "good result"

    # requestはfrozenであり、生成後に書き換えられない。
    with pytest.raises(AttributeError):
        good_request.user_text = "tampered"

    # 意図的な失敗(別clientで400)を発生させても、既存の正常結果は変化しない。
    def bad_post(url, headers, json, timeout):
        return _FakeResponse(400, text="bad request")

    failing_client = GeminiClient(api_key="test-key", session_post=bad_post, sleep=lambda _seconds: None)
    with pytest.raises(AIClientError):
        failing_client.generate(AIRequest(user_text="prompt"))

    assert good_result.text == "good result"
    assert good_request.user_text == "prompt"


@pytest.mark.integration_live
def test_tc_ai_001_12(gemini_connectivity_gate) -> None:
    """TC-AI-001-12 — Gemini APIの実機能テスト

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: integration_live
    Given: `gemini_connectivity_gate`が成功済み
    When: 疎通成功後、極短い固定promptを1回生成し、非空text・provider/model・usageまたはusage unavailable warningを確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    assert gemini_connectivity_gate.available is True

    client = GeminiClient()
    result = client.generate(AIRequest(user_text="Reply with exactly one word: OK"))

    assert result.text.strip()
    assert result.provider == "gemini"
    assert result.model
    has_usage = result.usage.total_tokens is not None
    assert has_usage or "usage_unavailable" in result.warnings
