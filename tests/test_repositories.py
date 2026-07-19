"""STEP3 test scaffold for TASK-DB-002: Repository・transaction境界.

Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
Release scope: MVP
Planned production files:
- script/persistence/repositories.py
- script/persistence/unit_of_work.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-01 is not implemented")
def test_tc_db_002_01() -> None:
    """TC-DB-002-01 — transaction rollback
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: integration_mock
    Given: 2つ目の書込みでconstraint errorを発生
    When: UnitOfWorkを終了する
    Then: 1つ目を含め全変更がrollbackされる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-03 is not implemented")
def test_tc_db_002_03() -> None:
    """TC-DB-002-03 — Project/Source/BuildRequest/Job/Artifact repository契約
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「Project/Source/BuildRequest/Job/Artifact repository契約」を実行する
    Then: 「Project/Source/BuildRequest/Job/Artifact repository契約」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-05 is not implemented")
def test_tc_db_002_05() -> None:
    """TC-DB-002-05 — FK/constraint例外変換
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「FK/constraint例外変換」を実行する
    Then: 「FK/constraint例外変換」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-07 is not implemented")
def test_tc_db_002_07() -> None:
    """TC-DB-002-07 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-07")
