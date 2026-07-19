"""STEP3 test scaffold for TASK-SCRIPT-001: 原稿segment・章初稿生成.

Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
Release scope: MVP
Planned production files:
- script/pipelines/draft_generation.py
- script/schemas/script.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-02 is not implemented")
def test_tc_script_001_02() -> None:
    """TC-SCRIPT-001-02 — 指定外資料
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P0
    Layer: integration_mock
    Given: AI結果がsource_ids外の事実を含む
    When: 生成結果を検査
    Then: pending claimとして記録し黙って承認しない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-04 is not implemented")
def test_tc_script_001_04() -> None:
    """TC-SCRIPT-001-04 — standard generation
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ScriptDocument/ScriptSegment/SpeakerRef`を通じて「standard generation」を実行する
    Then: 「standard generation」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-06 is not implemented")
def test_tc_script_001_06() -> None:
    """TC-SCRIPT-001-06 — 入力不変
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ScriptDocument/ScriptSegment/SpeakerRef`を通じて「入力不変」を実行する
    Then: 処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-SCRIPT-001-08 is not implemented")
def test_tc_script_001_08() -> None:
    """TC-SCRIPT-001-08 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ScriptDocument/ScriptSegment/SpeakerRef`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-SCRIPT-001-08")
