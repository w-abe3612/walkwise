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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-01 is not implemented")
def test_tc_project_001_01() -> None:
    """TC-PROJECT-001-01 — Project作成atomicity
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: integration_mock
    Given: 有効入力
    When: createする
    Then: plan fileとDB行が同じproject_id/revisionで作成される
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-03 is not implemented")
def test_tc_project_001_03() -> None:
    """TC-PROJECT-001-03 — archive除外
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: unit
    Given: activeとarchived Projectがある
    When: list_activeする
    Then: activeだけを返す
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-05 is not implemented")
def test_tc_project_001_05() -> None:
    """TC-PROJECT-001-05 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ProjectPlan.from_mapping()/to_mapping()/validate()`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROJECT-001-07 is not implemented")
def test_tc_project_001_07() -> None:
    """TC-PROJECT-001-07 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-PROJECT-001-07")
