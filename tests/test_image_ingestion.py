"""STEP3 test scaffold for TASK-IMAGE-001: 画像群登録・順序・manifest.

Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
Release scope: MVP
Planned production files:
- script/source_processing/images/ingestion.py
- script/source_processing/images/manifest.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-01 is not implemented")
def test_tc_image_001_01() -> None:
    """TC-IMAGE-001-01 — 自然順
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: page1,page2,page10のファイル
    When: ingestする
    Then: natural orderで1,2,10となる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-03 is not implemented")
def test_tc_image_001_03() -> None:
    """TC-IMAGE-001-03 — EXIF privacy
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: 位置情報付きJPEG
    When: manifest/exportを作る
    Then: 内部warningは保持しても公開成果物に位置情報を含めない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-05 is not implemented")
def test_tc_image_001_05() -> None:
    """TC-IMAGE-001-05 — 壊れた画像検出
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「壊れた画像検出」を実行する
    Then: 「壊れた画像検出」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-07 is not implemented")
def test_tc_image_001_07() -> None:
    """TC-IMAGE-001-07 — hash
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「hash」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-09 is not implemented")
def test_tc_image_001_09() -> None:
    """TC-IMAGE-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-09")
