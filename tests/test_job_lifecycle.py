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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-01 is not implemented")
def test_tc_job_001_01() -> None:
    """TC-JOB-001-01 — FIFO
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: integration_mock
    Given: queued Jobが3件
    When: start_nextを繰り返す
    Then: created/enqueued順で1件ずつrunningになる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-04 is not implemented")
def test_tc_job_001_04() -> None:
    """TC-JOB-001-04 — 状態遷移表
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「状態遷移表」を実行する
    Then: 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-07 is not implemented")
def test_tc_job_001_07() -> None:
    """TC-JOB-001-07 — finished_at規則
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「finished_at規則」を実行する
    Then: 「finished_at規則」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-10 is not implemented")
def test_tc_job_001_10() -> None:
    """TC-JOB-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-10")
