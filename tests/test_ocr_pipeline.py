"""STEP3 test scaffold for TASK-OCR-001: OCR・スキャンPDF処理.

Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
Release scope: MVP
Planned production files:
- script/source_processing/ocr/client.py
- script/source_processing/ocr/pipeline.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-02 is not implemented")
def test_tc_ocr_001_02() -> None:
    """TC-OCR-001-02 — 高リスク要素
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: unit
    Given: table/code/math/figure候補page
    When: pipeline処理
    Then: review_required flagを付け自動確定しない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-02")

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-04 is not implemented")
def test_tc_ocr_001_04() -> None:
    """TC-OCR-001-04 — Tesseract subprocess/adapter境界
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「Tesseract subprocess/adapter境界」を実行する
    Then: 「Tesseract subprocess/adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-06 is not implemented")
def test_tc_ocr_001_06() -> None:
    """TC-OCR-001-06 — confidence
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「confidence」を実行する
    Then: 「confidence」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-08 is not implemented")
def test_tc_ocr_001_08() -> None:
    """TC-OCR-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `OcrClient.check_runtime() -> RuntimeHealth`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-10 is not implemented")
def test_tc_ocr_001_10() -> None:
    """TC-OCR-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-10")

@pytest.mark.integration_live
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-12 is not implemented")
def test_tc_ocr_001_12(tesseract_connectivity_gate: object) -> None:
    """TC-OCR-001-12 — Tesseract runtimeの実機能テスト
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: integration_live
    Given: `tesseract_connectivity_gate`が成功済み
    When: 疎通成功後、1行だけの固定fixture画像をOCRし、期待語を含むpage resultを確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    
    Connectivity prerequisite: tesseract_connectivity_gate
    The live test must not run unless the preceding smoke check succeeds.
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-12")
