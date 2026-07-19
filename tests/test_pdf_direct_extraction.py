"""STEP3 test scaffold for TASK-PDF-001: PDF直接テキスト抽出.

Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
Release scope: MVP
Planned production files:
- script/source_processing/pdf/extract.py
- script/source_processing/pdf/models.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PDF-001-01 is not implemented")
def test_tc_pdf_001_01() -> None:
    """TC-PDF-001-01 — password拒否
    
    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: integration_mock
    Given: password protected PDF
    When: extractする
    Then: 解除を試みずunsupported_password_protected_pdf
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PDF-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PDF-001-03 is not implemented")
def test_tc_pdf_001_03() -> None:
    """TC-PDF-001-03 — OCR fallback
    
    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P0
    Layer: unit
    Given: 空または極少文字pageを含むPDF
    When: fallback判定
    Then: 該当pageだけOCR候補となる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PDF-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PDF-001-05 is not implemented")
def test_tc_pdf_001_05() -> None:
    """TC-PDF-001-05 — pypdf secondary adapter境界
    
    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PdfPage/PdfExtractionReport`を通じて「pypdf secondary adapter境界」を実行する
    Then: 「pypdf secondary adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PDF-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PDF-001-07 is not implemented")
def test_tc_pdf_001_07() -> None:
    """TC-PDF-001-07 — 空/極少文字ページflag
    
    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PdfPage/PdfExtractionReport`を通じて「空/極少文字ページflag」を実行する
    Then: 「空/極少文字ページflag」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PDF-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PDF-001-09 is not implemented")
def test_tc_pdf_001_09() -> None:
    """TC-PDF-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `PdfPage/PdfExtractionReport`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PDF-001-09")
