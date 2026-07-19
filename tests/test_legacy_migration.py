"""STEP3 test scaffold for TASK-MIGRATION-001: 旧形式・既存client互換adapter.

Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
Release scope: MVP
Planned production files:
- script/migration/legacy_models.py
- script/migration/adapters.py
- script/migration/report.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-01 is not implemented")
def test_tc_migration_001_01() -> None:
    """TC-MIGRATION-001-01 — 新形式優先
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P0
    Layer: unit
    Given: 新旧両形式がある
    When: read/migrate
    Then: 新形式を採用し旧形式を上書きしない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-03 is not implemented")
def test_tc_migration_001_03() -> None:
    """TC-MIGRATION-001-03 — 不明項目
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P0
    Layer: unit
    Given: 変換不能field
    When: migrate
    Then: 推測せずwarning/reportへ残す
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-05 is not implemented")
def test_tc_migration_001_05() -> None:
    """TC-MIGRATION-001-05 — sectionId/chapter_id
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `LegacyBook/LegacySection/LegacyAudioInput`を通じて「sectionId/chapter_id」を実行する
    Then: 「sectionId/chapter_id」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-07 is not implemented")
def test_tc_migration_001_07() -> None:
    """TC-MIGRATION-001-07 — legacy text priority
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `LegacyBook/LegacySection/LegacyAudioInput`を通じて「legacy text priority」を実行する
    Then: 「legacy text priority」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-09 is not implemented")
def test_tc_migration_001_09() -> None:
    """TC-MIGRATION-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `LegacyBook/LegacySection/LegacyAudioInput`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-09")
