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
    AIClientError,
    AIRequest,
    AIResult,
    make_json_response_validator,
)
from script.ai_clients.gemini.client import GeminiClient
from script.core.errors import ErrorCode

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


def _fixed_gemini_response(text: str, *, usage: dict[str, int] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "candidates": [{"content": {"parts": [{"text": text}]}}],
    }
    if usage is not None:
        data["usageMetadata"] = usage
    return data


@pytest.mark.integration_mock
def test_tc_ai_001_01() -> None:
    """TC-AI-001-01 — mock生成

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: integration_mock
    Given: 固定Gemini HTTP response
    When: generateする
    Then: AIResult text/provider/model/usageへ変換する
    """
    fixed_data = _fixed_gemini_response(
        "hello from gemini",
        usage={"promptTokenCount": 10, "candidatesTokenCount": 5, "totalTokenCount": 15},
    )

    def fake_post(url, headers, json, timeout):
        return _FakeResponse(200, fixed_data)

    client = GeminiClient(api_key="test-key", session_post=fake_post)
    result = client.generate(AIRequest(user_text="say hello"))

    assert isinstance(result, AIResult)
    assert result.text == "hello from gemini"
    assert result.provider == "gemini"
    assert result.model
    assert result.usage.input_tokens == 10
    assert result.usage.output_tokens == 5
    assert result.usage.total_tokens == 15


@pytest.mark.unit
def test_tc_ai_001_03() -> None:
    """TC-AI-001-03 — structured response

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: 不正JSONと正常JSON
    When: validation hook付き生成
    Then: 正常だけ受理し不正はschema error
    """
    valid_json_data = _fixed_gemini_response('{"key": "value"}')
    invalid_json_data = _fixed_gemini_response("not valid json {{{")

    def make_post(data):
        def fake_post(url, headers, json, timeout):
            return _FakeResponse(200, data)
        return fake_post

    validator = make_json_response_validator()

    good_client = GeminiClient(api_key="test-key", session_post=make_post(valid_json_data))
    result = good_client.generate(
        AIRequest(user_text="give json", response_mime_type="application/json", validate_response=validator)
    )
    assert result.text == '{"key": "value"}'

    bad_client = GeminiClient(api_key="test-key", session_post=make_post(invalid_json_data))
    with pytest.raises(AIClientError) as excinfo:
        bad_client.generate(
            AIRequest(user_text="give json", response_mime_type="application/json", validate_response=validator)
        )
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR
    assert excinfo.value.retryable is False


@pytest.mark.unit
def test_tc_ai_001_05() -> None:
    """TC-AI-001-05 — prompt template

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「prompt template」を実行する
    Then: 「prompt template」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    captured: dict[str, Any] = {}

    def fake_post(url, headers, json, timeout):
        captured["json"] = json
        captured["url"] = url
        return _FakeResponse(200, _fixed_gemini_response("ok"))

    client = GeminiClient(api_key="test-key", api_version="v1beta", model="gemini-test-model", session_post=fake_post)
    client.generate(AIRequest(user_text="the user prompt", system_instruction="the system prompt"))

    assert captured["json"]["contents"][0]["parts"][0]["text"] == "the user prompt"
    assert captured["json"]["system_instruction"]["parts"][0]["text"] == "the system prompt"
    assert "gemini-test-model" in captured["url"]


@pytest.mark.unit
def test_tc_ai_001_07() -> None:
    """TC-AI-001-07 — timeout

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「timeout」を実行する
    Then: timeoutを安定した共通errorへ変換し、半端な最終ファイルや成功状態を残さない。
    """
    import requests

    calls = {"count": 0}

    def timeout_post(url, headers, json, timeout):
        calls["count"] += 1
        raise requests.Timeout("simulated timeout")

    client = GeminiClient(api_key="test-key", session_post=timeout_post, sleep=lambda _seconds: None)
    with pytest.raises(AIClientError) as excinfo:
        client.generate(AIRequest(user_text="prompt"))

    assert excinfo.value.code is ErrorCode.EXTERNAL_UNAVAILABLE
    assert excinfo.value.retryable is False
    # timeoutは再試行せず即座に停止する。
    assert calls["count"] == 1


@pytest.mark.unit
def test_tc_ai_001_09() -> None:
    """TC-AI-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    fixed_data = _fixed_gemini_response("stable text", usage={"promptTokenCount": 1, "candidatesTokenCount": 1, "totalTokenCount": 2})

    def fake_post(url, headers, json, timeout):
        return _FakeResponse(200, fixed_data)

    client_a = GeminiClient(api_key="test-key", session_post=fake_post)
    client_b = GeminiClient(api_key="test-key", session_post=fake_post)

    result_a = client_a.generate(AIRequest(user_text="prompt"))
    result_b = client_b.generate(AIRequest(user_text="prompt"))

    assert result_a == result_b


@pytest.mark.integration_smoke
def test_tc_ai_001_11(gemini_connectivity_gate) -> None:
    """TC-AI-001-11 — Gemini APIの疎通確認

    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: 認証付きの軽量なmodel metadata/list操作を1回だけ実行し、DNS/TLS/HTTP/認証/応答schemaを確認する。生成本文は要求しない。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert gemini_connectivity_gate.available is True
    assert gemini_connectivity_gate.provider == "gemini"
