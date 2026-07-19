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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-02 is not implemented")
def test_tc_file_001_02() -> None:
    """TC-FILE-001-02 — lock競合
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: 同じProject lockを保持中
    When: 2つ目のlockを取得する
    Then: 競合errorとなり既存lockを壊さない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-05 is not implemented")
def test_tc_file_001_05() -> None:
    """TC-FILE-001-05 — 入力原本のimmutable保存
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「入力原本のimmutable保存」を実行する
    Then: 処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-FILE-001-08 is not implemented")
def test_tc_file_001_08() -> None:
    """TC-FILE-001-08 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-FILE-001-08")
