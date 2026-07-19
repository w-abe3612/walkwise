"""STEP3 test scaffold for TASK-SOURCE-002: 資料正規化・chunk・index・manifest.

Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
Release scope: MVP
Planned production files:
- script/source_processing/normalize.py
- script/source_processing/chunking.py
- script/source_processing/manifests.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-03 is not implemented")
def test_tc_source_002_03() -> None:
    """TC-SOURCE-002-03 — 参照整合
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: chunk manifestとtopic index
    When: validateする
    Then: 全chunk IDが存在し重複がない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-06 is not implemented")
def test_tc_source_002_06() -> None:
    """TC-SOURCE-002-06 — footnote分離
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「footnote分離」を実行する
    Then: 「footnote分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-09 is not implemented")
def test_tc_source_002_09() -> None:
    """TC-SOURCE-002-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `normalize_text(text, rules) -> NormalizationResult`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-09")
