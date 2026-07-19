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

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-01 is not implemented")
def test_tc_ocr_001_01() -> None:
    """TC-OCR-001-01 — runtimeなし
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: integration_mock
    Given: Tesseractが見つからない
    When: OCRを開始
    Then: 疎通確認で停止しSourceをfailed/reviewableにする
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-01")

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-03 is not implemented")
def test_tc_ocr_001_03() -> None:
    """TC-OCR-001-03 — ページ失敗分離
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: integration_mock
    Given: 複数page中1件だけsubprocess失敗
    When: 処理
    Then: 他page結果を保持しmanifestに失敗を記録
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-05 is not implemented")
def test_tc_ocr_001_05() -> None:
    """TC-OCR-001-05 — 言語設定
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「言語設定」を実行する
    Then: 「言語設定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-07 is not implemented")
def test_tc_ocr_001_07() -> None:
    """TC-OCR-001-07 — table/code/math/figure flag
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「table/code/math/figure flag」を実行する
    Then: 「table/code/math/figure flag」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-09 is not implemented")
def test_tc_ocr_001_09() -> None:
    """TC-OCR-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `OcrClient.check_runtime() -> RuntimeHealth`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-09")

@pytest.mark.integration_smoke
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-OCR-001-11 is not implemented")
def test_tc_ocr_001_11() -> None:
    """TC-OCR-001-11 — Tesseract runtimeの疎通確認
    
    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: `tesseract --version`と必要言語一覧を確認し、画像処理を行わない。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-OCR-001-11")
