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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-02 is not implemented")
def test_tc_migration_001_02() -> None:
    """TC-MIGRATION-001-02 — full_book正規化
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P0
    Layer: unit
    Given: 旧unit_id=full_book
    When: migrate
    Then: bookへ変換しprovenanceを記録
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-04 is not implemented")
def test_tc_migration_001_04() -> None:
    """TC-MIGRATION-001-04 — bookId/project_id
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `LegacyBook/LegacySection/LegacyAudioInput`を通じて「bookId/project_id」を実行する
    Then: 「bookId/project_id」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-06 is not implemented")
def test_tc_migration_001_06() -> None:
    """TC-MIGRATION-001-06 — approval.yaml/approvals.yaml
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `LegacyBook/LegacySection/LegacyAudioInput`を通じて「approval.yaml/approvals.yaml」を実行する
    Then: 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-08 is not implemented")
def test_tc_migration_001_08() -> None:
    """TC-MIGRATION-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `LegacyBook/LegacySection/LegacyAudioInput`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-MIGRATION-001-10 is not implemented")
def test_tc_migration_001_10() -> None:
    """TC-MIGRATION-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-MIGRATION-001-10")
