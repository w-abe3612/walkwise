"""STEP3 test scaffold for TASK-PROJECT-001: Project作成・一覧・取得サービス.

Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
Release scope: MVP
Planned production files:
- script/services/projects.py
- script/schemas/project_plan.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-02 is not implemented")
def test_tc_project_001_02() -> None:
    """TC-PROJECT-001-02 — DB失敗cleanup
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: integration_mock
    Given: file作成後のDB insertを失敗させる
    When: createする
    Then: 不完全Projectを一覧へ出さずcleanup/rollbackする
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-04 is not implemented")
def test_tc_project_001_04() -> None:
    """TC-PROJECT-001-04 — 入力validation
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPlan.from_mapping()/to_mapping()/validate()`を通じて「入力validation」を実行する
    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-06 is not implemented")
def test_tc_project_001_06() -> None:
    """TC-PROJECT-001-06 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ProjectPlan.from_mapping()/to_mapping()/validate()`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-06")
