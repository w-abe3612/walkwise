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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-01 is not implemented")
def test_tc_db_001_01() -> None:
    """TC-DB-001-01 — 初期schema
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: integration_mock
    Given: 空SQLite DB
    When: 全migrationを適用する
    Then: 6テーブル・FK・index・checkが作成される
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-04 is not implemented")
def test_tc_db_001_04() -> None:
    """TC-DB-001-04 — SQLite接続factory
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「SQLite接続factory」を実行する
    Then: 「SQLite接続factory」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-07 is not implemented")
def test_tc_db_001_07() -> None:
    """TC-DB-001-07 — 0001 initial schema
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「0001 initial schema」を実行する
    Then: 「0001 initial schema」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-10 is not implemented")
def test_tc_db_001_10() -> None:
    """TC-DB-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-10")
