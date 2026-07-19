"""STEP3 test scaffold for TASK-EPUB-001: EPUBテキスト抽出.

Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
Release scope: post-MVP
Planned production files:
- script/source_processing/epub/extract.py
- script/source_processing/epub/models.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.post_mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-01 is not implemented")
def test_tc_epub_001_01() -> None:
    """TC-EPUB-001-01 — DRM拒否
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P0
    Layer: integration_mock
    Given: 暗号化EPUB
    When: extractする
    Then: 解除せずunsupported_drmで停止する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-01")

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-02 is not implemented")
def test_tc_epub_001_02() -> None:
    """TC-EPUB-001-02 — spine順
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P0
    Layer: integration_mock
    Given: manifest順とfile名順が異なるEPUB
    When: extractする
    Then: spine順を採用する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-03 is not implemented")
def test_tc_epub_001_03() -> None:
    """TC-EPUB-001-03 — footnote保持
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P0
    Layer: unit
    Given: annotation/footnoteを含むEPUB
    When: extractする
    Then: 別構造で保持し本文へ自動挿入しない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-04 is not implemented")
def test_tc_epub_001_04() -> None:
    """TC-EPUB-001-04 — EPUB2/3判定
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `EpubChapter/EpubExtractionReport`を通じて「EPUB2/3判定」を実行する
    Then: 「EPUB2/3判定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-05 is not implemented")
def test_tc_epub_001_05() -> None:
    """TC-EPUB-001-05 — container/OPF/spine解決
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `EpubChapter/EpubExtractionReport`を通じて「container/OPF/spine解決」を実行する
    Then: 入力の論理順を維持し、再実行しても同じ順序になる。順序重複・欠落は検出する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-06 is not implemented")
def test_tc_epub_001_06() -> None:
    """TC-EPUB-001-06 — 章/節locator
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `EpubChapter/EpubExtractionReport`を通じて「章/節locator」を実行する
    Then: 「章/節locator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-07 is not implemented")
def test_tc_epub_001_07() -> None:
    """TC-EPUB-001-07 — annotation分離
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `EpubChapter/EpubExtractionReport`を通じて「annotation分離」を実行する
    Then: 「annotation分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-08 is not implemented")
def test_tc_epub_001_08() -> None:
    """TC-EPUB-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `EpubChapter/EpubExtractionReport`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-09 is not implemented")
def test_tc_epub_001_09() -> None:
    """TC-EPUB-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `EpubChapter/EpubExtractionReport`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-09")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-EPUB-001-10 is not implemented")
def test_tc_epub_001_10() -> None:
    """TC-EPUB-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-EPUB-001-10")
