"""STEP3 test scaffold for TASK-INGEST-001: 資料入力orchestrator・テキスト入力.

Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
Release scope: MVP
Planned production files:
- script/source_processing/orchestrator.py
- script/source_processing/text_ingestion.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-INGEST-001-02 is not implemented")
def test_tc_ingest_001_02() -> None:
    """TC-INGEST-001-02 — 未知media
    
    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P0
    Layer: unit
    Given: epubまたはvideo
    When: processする
    Then: MVPではunsupported_media_typeで停止する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-INGEST-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-INGEST-001-04 is not implemented")
def test_tc_ingest_001_04() -> None:
    """TC-INGEST-001-04 — original/extracted/normalized/structured handoff
    
    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「original/extracted/normalized/structured handoff」を実行する
    Then: 「original/extracted/normalized/structured handoff」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-INGEST-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-INGEST-001-06 is not implemented")
def test_tc_ingest_001_06() -> None:
    """TC-INGEST-001-06 — Job進捗hook
    
    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「Job進捗hook」を実行する
    Then: current/totalとmessageを単調・順序どおりに通知し、完了後に進捗を逆行させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-INGEST-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-INGEST-001-08 is not implemented")
def test_tc_ingest_001_08() -> None:
    """TC-INGEST-001-08 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-INGEST-001-08")
