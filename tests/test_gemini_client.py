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

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-02 is not implemented")
def test_tc_ai_001_02() -> None:
    """TC-AI-001-02 — retry区分
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: 429/5xxと400を返すmock
    When: generateする
    Then: 前者だけ上限内再試行し400は即時error
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-04 is not implemented")
def test_tc_ai_001_04() -> None:
    """TC-AI-001-04 — AIClient Protocol
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「AIClient Protocol」を実行する
    Then: 「AIClient Protocol」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-06 is not implemented")
def test_tc_ai_001_06() -> None:
    """TC-AI-001-06 — JSON/YAML response validation hook
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「JSON/YAML response validation hook」を実行する
    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-08 is not implemented")
def test_tc_ai_001_08() -> None:
    """TC-AI-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-10 is not implemented")
def test_tc_ai_001_10() -> None:
    """TC-AI-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-10")

@pytest.mark.integration_live
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AI-001-12 is not implemented")
def test_tc_ai_001_12(gemini_connectivity_gate: object) -> None:
    """TC-AI-001-12 — Gemini APIの実機能テスト
    
    Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
    Priority: P1
    Layer: integration_live
    Given: `gemini_connectivity_gate`が成功済み
    When: 疎通成功後、極短い固定promptを1回生成し、非空text・provider/model・usageまたはusage unavailable warningを確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    
    Connectivity prerequisite: gemini_connectivity_gate
    The live test must not run unless the preceding smoke check succeeds.
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AI-001-12")
