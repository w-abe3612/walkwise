"""STEP3 test scaffold for TASK-AI-001: AI共通契約・Gemini adapter.

Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
Release scope: MVP
Planned production files:
- script/ai_clients/base.py
- script/ai_clients/gemini/client.py
- script/ai_clients/registry.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-01 is not implemented")
def test_tc_ai_001_01() -> None:
    """TC-AI-001-01 — mock生成
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: integration_mock
    Given: 固定Gemini HTTP response
    When: generateする
    Then: AIResult text/provider/model/usageへ変換する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-03 is not implemented")
def test_tc_ai_001_03() -> None:
    """TC-AI-001-03 — structured response
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: 不正JSONと正常JSON
    When: validation hook付き生成
    Then: 正常だけ受理し不正はschema error
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-05 is not implemented")
def test_tc_ai_001_05() -> None:
    """TC-AI-001-05 — prompt template
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「prompt template」を実行する
    Then: 「prompt template」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-07 is not implemented")
def test_tc_ai_001_07() -> None:
    """TC-AI-001-07 — timeout
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「timeout」を実行する
    Then: timeoutを安定した共通errorへ変換し、半端な最終ファイルや成功状態を残さない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-09 is not implemented")
def test_tc_ai_001_09() -> None:
    """TC-AI-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-09")

@pytest.mark.integration_smoke
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-11 is not implemented")
def test_tc_ai_001_11() -> None:
    """TC-AI-001-11 — Gemini APIの疎通確認
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: 認証付きの軽量なmodel metadata/list操作を1回だけ実行し、DNS/TLS/HTTP/認証/応答schemaを確認する。生成本文は要求しない。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-11")
