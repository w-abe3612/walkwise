"""STEP3 test scaffold for TASK-JOB-001: Job状態遷移・FIFO・再試行・stale復旧.

Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
Release scope: MVP
Planned production files:
- script/services/jobs.py
- script/domain/job_state.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-03 is not implemented")
def test_tc_job_001_03() -> None:
    """TC-JOB-001-03 — stale復旧
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: integration_mock
    Given: 起動前からrunningのJob
    When: recover_staleする
    Then: failedと異常終了messageへ更新する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-06 is not implemented")
def test_tc_job_001_06() -> None:
    """TC-JOB-001-06 — approval gate hook
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「approval gate hook」を実行する
    Then: 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-09 is not implemented")
def test_tc_job_001_09() -> None:
    """TC-JOB-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-09")
