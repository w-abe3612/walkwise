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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-03 is not implemented")
def test_tc_db_001_03() -> None:
    """TC-DB-001-03 — checksum改変
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P0
    Layer: integration_mock
    Given: 適用済みmigration fileの内容を変更
    When: checksum検証する
    Then: 起動停止相当errorとなる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-03")

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-06 is not implemented")
def test_tc_db_001_06() -> None:
    """TC-DB-001-06 — migration discovery/order
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `connect_database(path: Path) -> sqlite3.Connection`を通じて「migration discovery/order」を実行する
    Then: 入力の論理順を維持し、再実行しても同じ順序になる。順序重複・欠落は検出する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-001-09 is not implemented")
def test_tc_db_001_09() -> None:
    """TC-DB-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `connect_database(path: Path) -> sqlite3.Connection`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-001-09")
