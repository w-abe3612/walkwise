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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-02 is not implemented")
def test_tc_source_002_02() -> None:
    """TC-SOURCE-002-02 — soft chunk
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: 2000文字付近の段落
    When: chunkする
    Then: 意味境界を優先しlocatorを失わない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-05 is not implemented")
def test_tc_source_002_05() -> None:
    """TC-SOURCE-002-05 — 繰返しheader/footer除去
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `normalize_text(text, rules) -> NormalizationResult`を通じて「繰返しheader/footer除去」を実行する
    Then: 「繰返しheader/footer除去」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-002-08 is not implemented")
def test_tc_source_002_08() -> None:
    """TC-SOURCE-002-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `normalize_text(text, rules) -> NormalizationResult`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-002-08")
