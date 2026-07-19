"""STEP3 test scaffold for TASK-DB-001: SQLite接続・migration runner・初期schema.

Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
Release scope: MVP
Planned production files:
- script/persistence/database.py
- script/persistence/migrations.py
- script/persistence/sql/0001_initial.sql

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-02 is not implemented")
def test_tc_db_001_02() -> None:
    """TC-DB-001-02 — 冪等適用
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: integration_mock
    Given: 適用済みDB
    When: apply_allを再実行する
    Then: 新規適用0件でschemaと履歴が変わらない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-05 is not implemented")
def test_tc_db_001_05() -> None:
    """TC-DB-001-05 — PRAGMA foreign_keys
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「PRAGMA foreign_keys」を実行する
    Then: 「PRAGMA foreign_keys」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-08 is not implemented")
def test_tc_db_001_08() -> None:
    """TC-DB-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `connect_database(path: Path) -> sqlite3.Connection`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-08")
