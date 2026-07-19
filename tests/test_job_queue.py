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

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-02 is not implemented")
def test_tc_job_001_02() -> None:
    """TC-JOB-001-02 — 不正遷移
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: unit
    Given: cancelled Job
    When: runningへ遷移
    Then: 拒否し状態を維持する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-05 is not implemented")
def test_tc_job_001_05() -> None:
    """TC-JOB-001-05 — parent_job_id再試行
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「parent_job_id再試行」を実行する
    Then: 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-JOB-001-08 is not implemented")
def test_tc_job_001_08() -> None:
    """TC-JOB-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `can_transition(current: JobStatus, target: JobStatus) -> bool`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-JOB-001-08")
