"""STEP3 test scaffold for TASK-FILE-001: ローカルファイル永続化・Project配置・atomic write.

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Release scope: MVP
Planned production files:
- script/persistence/paths.py
- script/persistence/files.py
- script/persistence/locking.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-03 is not implemented")
def test_tc_file_001_03() -> None:
    """TC-FILE-001-03 — root escape拒否
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: `../outside`を含む相対候補
    When: Project pathを解決する
    Then: Project root外を拒否する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-03")

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-06 is not implemented")
def test_tc_file_001_06() -> None:
    """TC-FILE-001-06 — 絶対パスのDB保存禁止
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「絶対パスのDB保存禁止」を実行する
    Then: 保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-09 is not implemented")
def test_tc_file_001_09() -> None:
    """TC-FILE-001-09 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-09")
