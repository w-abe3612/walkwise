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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-01 is not implemented")
def test_tc_claim_001_01() -> None:
    """TC-CLAIM-001-01 — 抽出初期状態
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P0
    Layer: unit
    Given: 技術文を含むscript
    When: extract
    Then: 全claimはpending
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-03 is not implemented")
def test_tc_claim_001_03() -> None:
    """TC-CLAIM-001-03 — conflict gate
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P0
    Layer: unit
    Given: conflict claimを含むscript
    When: publishable確認
    Then: 本番TTS前に停止する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-05 is not implemented")
def test_tc_claim_001_05() -> None:
    """TC-CLAIM-001-05 — evidence mapping
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `Claim/SourceEvidence/FactCheckReport`を通じて「evidence mapping」を実行する
    Then: 「evidence mapping」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-07 is not implemented")
def test_tc_claim_001_07() -> None:
    """TC-CLAIM-001-07 — unsupported block
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `Claim/SourceEvidence/FactCheckReport`を通じて「unsupported block」を実行する
    Then: 「unsupported block」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-CLAIM-001-09 is not implemented")
def test_tc_claim_001_09() -> None:
    """TC-CLAIM-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `Claim/SourceEvidence/FactCheckReport`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-CLAIM-001-09")
