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

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-02 is not implemented")
def test_tc_db_002_02() -> None:
    """TC-DB-002-02 — Artifact追記専用
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: unit
    Given: 既存Artifactをupdateしようとする
    When: Repository APIを呼ぶ
    Then: 操作を拒否し既存行を変更しない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-04 is not implemented")
def test_tc_db_002_04() -> None:
    """TC-DB-002-04 — insert/find/list/updateの許可範囲
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「insert/find/list/updateの許可範囲」を実行する
    Then: 必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-06 is not implemented")
def test_tc_db_002_06() -> None:
    """TC-DB-002-06 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-DB-002-08 is not implemented")
def test_tc_db_002_08() -> None:
    """TC-DB-002-08 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-DB-002-08")
