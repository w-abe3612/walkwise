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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-01 is not implemented")
def test_tc_file_001_01() -> None:
    """TC-FILE-001-01 — atomic write失敗
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: 既存正常ファイルがありreplace前に例外を注入
    When: atomic_writeを実行する
    Then: 旧ファイルが完全に残り一時ファイルをcleanupする
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-04 is not implemented")
def test_tc_file_001_04() -> None:
    """TC-FILE-001-04 — 最低1世代backup
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「最低1世代backup」を実行する
    Then: 失敗前の正常状態をbackupから復旧でき、復旧対象のhashを検証する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-07 is not implemented")
def test_tc_file_001_07() -> None:
    """TC-FILE-001-07 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-07")
