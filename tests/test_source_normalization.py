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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-01 is not implemented")
def test_tc_source_002_01() -> None:
    """TC-SOURCE-002-01 — 低リスク正規化
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: 改行・Unicode・反復headerがある
    When: normalizeする
    Then: 決定的修正とbefore/after hash/diffを返す
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-04 is not implemented")
def test_tc_source_002_04() -> None:
    """TC-SOURCE-002-04 — Unicode/改行/空白の決定的正規化
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「Unicode/改行/空白の決定的正規化」を実行する
    Then: 「Unicode/改行/空白の決定的正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-07 is not implemented")
def test_tc_source_002_07() -> None:
    """TC-SOURCE-002-07 — structured Markdown/YAML/JSON
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「structured Markdown/YAML/JSON」を実行する
    Then: 「structured Markdown/YAML/JSON」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-10 is not implemented")
def test_tc_source_002_10() -> None:
    """TC-SOURCE-002-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-10")
