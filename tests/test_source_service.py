"""STEP3 test scaffold for TASK-SOURCE-001: Source登録・状態管理サービス.

Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
Release scope: MVP
Planned production files:
- script/services/sources.py
- script/schemas/source_metadata.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-001-01 is not implemented")
def test_tc_source_001_01() -> None:
    """TC-SOURCE-001-01 — text即ready
    
    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: integration_mock
    Given: UTF-8 textを登録
    When: registerする
    Then: immutable原本、hash、status readyが作成される
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-001-01")

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-001-03 is not implemented")
def test_tc_source_001_03() -> None:
    """TC-SOURCE-001-03 — 重複hash warning
    
    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: integration_mock
    Given: 同一bytesを2回登録
    When: registerする
    Then: 2件を追跡可能に保存しwarningを返す
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-001-05 is not implemented")
def test_tc_source_001_05() -> None:
    """TC-SOURCE-001-05 — Project相対path
    
    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceMetadata.from_file(...) -> SourceMetadata`を通じて「Project相対path」を実行する
    Then: 保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SOURCE-001-07 is not implemented")
def test_tc_source_001_07() -> None:
    """TC-SOURCE-001-07 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `SourceMetadata.from_file(...) -> SourceMetadata`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SOURCE-001-07")
