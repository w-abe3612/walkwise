"""STEP3 test scaffold for TASK-RELEASE-002: 性能・耐障害・最終release受入.

Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
Release scope: MVP
Planned production files:
- tests/performance/test_large_sources.py
- tests/resilience/test_failure_recovery.py
- release/checklist.md

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.resilience
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-RELEASE-002-01 is not implemented")
def test_tc_release_002_01() -> None:
    """TC-RELEASE-002-01 — disk full
    
    Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
    Priority: P0
    Layer: resilience
    Given: 成果物書込途中でENOSPC
    When: pipeline
    Then: 旧正常成果物とDB整合を保持
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-RELEASE-002-01")

@pytest.mark.performance
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-RELEASE-002-03 is not implemented")
def test_tc_release_002_03() -> None:
    """TC-RELEASE-002-03 — 大規模入力
    
    Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
    Priority: P0
    Layer: performance
    Given: 規定fixture size
    When: 性能測定
    Then: 時間/memory実測を記録し根拠なしのpassをしない
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-RELEASE-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-RELEASE-002-05 is not implemented")
def test_tc_release_002_05() -> None:
    """TC-RELEASE-002-05 — メモリ/処理時間
    
    Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `performance scenarios`を通じて「メモリ/処理時間」を実行する
    Then: 「メモリ/処理時間」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-RELEASE-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-RELEASE-002-07 is not implemented")
def test_tc_release_002_07() -> None:
    """TC-RELEASE-002-07 — 既存成果物保持
    
    Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `performance scenarios`を通じて「既存成果物保持」を実行する
    Then: 「既存成果物保持」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-RELEASE-002-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-RELEASE-002-09 is not implemented")
def test_tc_release_002_09() -> None:
    """TC-RELEASE-002-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `performance scenarios`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-RELEASE-002-09")


# ---------------------------------------------------------------------------
# STEP4 typed contract additions. Existing working implementation above is
# preserved. New public APIs remain intentionally unimplemented.
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-RELEASE-002', 'performance scenarios', '大規模資料の時間・memoryを測定し根拠を記録する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-RELEASE-002-01', 'priority': 'P0', 'layer': 'resilience', 'title': 'disk full', 'given': '成果物書込途中でENOSPC', 'when': 'pipeline', 'then': '旧正常成果物とDB整合を保持', 'test_file': '`tests/performance/test_large_sources.py`'},
    {'id': 'TC-RELEASE-002-02', 'priority': 'P0', 'layer': 'resilience', 'title': '強制終了/再起動', 'given': 'running Job中にprocess kill', 'when': '再起動', 'then': 'stale Jobをfailedにし再試行可能', 'test_file': '`tests/resilience/test_failure_recovery.py`'},
    {'id': 'TC-RELEASE-002-03', 'priority': 'P0', 'layer': 'performance', 'title': '大規模入力', 'given': '規定fixture size', 'when': '性能測定', 'then': '時間/memory実測を記録し根拠なしのpassをしない', 'test_file': '`tests/performance/test_large_sources.py`'},
    {'id': 'TC-RELEASE-002-04', 'priority': 'P1', 'layer': 'unit', 'title': '性能基準の測定記録', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`performance scenarios`を通じて「性能基準の測定記録」を実行する', 'then': '「性能基準の測定記録」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/resilience/test_failure_recovery.py`'},
    {'id': 'TC-RELEASE-002-05', 'priority': 'P1', 'layer': 'unit', 'title': 'メモリ/処理時間', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`performance scenarios`を通じて「メモリ/処理時間」を実行する', 'then': '「メモリ/処理時間」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/performance/test_large_sources.py`'},
    {'id': 'TC-RELEASE-002-06', 'priority': 'P1', 'layer': 'unit', 'title': 'cancel/restart', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`performance scenarios`を通じて「cancel/restart」を実行する', 'then': '許可状態だけでcancel要求を受け付け、cooperative停止後にcancelledへ確定する。', 'test_file': '`tests/resilience/test_failure_recovery.py`'},
    {'id': 'TC-RELEASE-002-07', 'priority': 'P1', 'layer': 'unit', 'title': '既存成果物保持', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`performance scenarios`を通じて「既存成果物保持」を実行する', 'then': '「既存成果物保持」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/performance/test_large_sources.py`'},
    {'id': 'TC-RELEASE-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`performance scenarios`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/resilience/test_failure_recovery.py`'},
    {'id': 'TC-RELEASE-002-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`performance scenarios`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/performance/test_large_sources.py`'},
    {'id': 'TC-RELEASE-002-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/resilience/test_failure_recovery.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (tests/performance/test_large_sources.py)")
