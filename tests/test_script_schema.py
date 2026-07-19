"""STEP3 test scaffold for TASK-SCRIPT-001: 原稿segment・章初稿生成.

Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
Release scope: MVP
Planned production files:
- script/pipelines/draft_generation.py
- script/schemas/script.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-01 is not implemented")
def test_tc_script_001_01() -> None:
    """TC-SCRIPT-001-01 — segment一意
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P0
    Layer: unit
    Given: 8〜10segment初稿
    When: validate
    Then: ID/order/textを検証し順序を保持
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-03 is not implemented")
def test_tc_script_001_03() -> None:
    """TC-SCRIPT-001-03 — 旧TXT
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P0
    Layer: unit
    Given: 同一TXTを2回変換
    When: segment化
    Then: 同一ID/orderになり人間未承認
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-05 is not implemented")
def test_tc_script_001_05() -> None:
    """TC-SCRIPT-001-05 — prompt/input provenance
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ScriptDocument/ScriptSegment/SpeakerRef`を通じて「prompt/input provenance」を実行する
    Then: 「prompt/input provenance」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-07 is not implemented")
def test_tc_script_001_07() -> None:
    """TC-SCRIPT-001-07 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ScriptDocument/ScriptSegment/SpeakerRef`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-09 is not implemented")
def test_tc_script_001_09() -> None:
    """TC-SCRIPT-001-09 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-09")
