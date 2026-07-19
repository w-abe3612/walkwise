"""STEP3 test scaffold for TASK-IMAGE-002: 画像前処理・品質flag・見開き分割.

Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
Release scope: MVP
Planned production files:
- script/source_processing/images/preprocess.py
- script/source_processing/images/quality.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-002-01 is not implemented")
def test_tc_image_002_01() -> None:
    """TC-IMAGE-002-01 — 原画像不変
    
    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: 回転・contrast処理対象
    When: preprocessする
    Then: 原画像hash不変で派生PNGとparametersを保存
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-002-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-002-03 is not implemented")
def test_tc_image_002_03() -> None:
    """TC-IMAGE-002-03 — 見開きlocator
    
    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: 見開き画像
    When: splitする
    Then: 左右の元page座標対応を保持する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-002-05 is not implemented")
def test_tc_image_002_05() -> None:
    """TC-IMAGE-002-05 — before/after hash
    
    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「before/after hash」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-002-07 is not implemented")
def test_tc_image_002_07() -> None:
    """TC-IMAGE-002-07 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ImagePreprocessor.process(page, options) -> PreprocessedPage`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-002-07")
