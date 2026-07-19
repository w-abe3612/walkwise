"""STEP3 test scaffold for TASK-CLAIM-001: 技術的主張・出典対応・fact check.

Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
Release scope: MVP
Planned production files:
- script/pipelines/claims.py
- script/schemas/claims.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-02 is not implemented")
def test_tc_claim_001_02() -> None:
    """TC-CLAIM-001-02 — verified条件
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P0
    Layer: unit
    Given: source locatorあり・人間承認あり
    When: verify
    Then: verified可能。AI出力のみでは不可
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-04 is not implemented")
def test_tc_claim_001_04() -> None:
    """TC-CLAIM-001-04 — economy抽出はpending
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `Claim/SourceEvidence/FactCheckReport`を通じて「economy抽出はpending」を実行する
    Then: 「economy抽出はpending」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-06 is not implemented")
def test_tc_claim_001_06() -> None:
    """TC-CLAIM-001-06 — source locator
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `Claim/SourceEvidence/FactCheckReport`を通じて「source locator」を実行する
    Then: 「source locator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-08 is not implemented")
def test_tc_claim_001_08() -> None:
    """TC-CLAIM-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `Claim/SourceEvidence/FactCheckReport`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-10 is not implemented")
def test_tc_claim_001_10() -> None:
    """TC-CLAIM-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-10")
