"""STEP3 test scaffold for TASK-BUILD-001: Build Request作成サービス.

Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
Release scope: MVP
Planned production files:
- script/services/build_requests.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-01 is not implemented")
def test_tc_build_001_01() -> None:
    """TC-BUILD-001-01 — text-only
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: formats=[text], voiceなし
    When: Build Requestを作成
    Then: draftとして成功する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-02 is not implemented")
def test_tc_build_001_02() -> None:
    """TC-BUILD-001-02 — mp3+text
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: formats=[text,mp3], voiceあり
    When: 作成する
    Then: JSONは["mp3","text"]になる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-03 is not implemented")
def test_tc_build_001_03() -> None:
    """TC-BUILD-001-03 — 空・未知・重複
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: 空、epub、mp3重複をそれぞれ渡す
    When: 作成する
    Then: 副作用前に拒否する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-04 is not implemented")
def test_tc_build_001_04() -> None:
    """TC-BUILD-001-04 — output_formatsの1件以上/許可値/重複禁止/order
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を通じて「output_formatsの1件以上/許可値/重複禁止/order」を実行する
    Then: 重複を検出し、仕様で許可されない重複は安定したvalidation errorとして副作用前に拒否する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-05 is not implemented")
def test_tc_build_001_05() -> None:
    """TC-BUILD-001-05 — Project存在確認
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を通じて「Project存在確認」を実行する
    Then: 「Project存在確認」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-06 is not implemented")
def test_tc_build_001_06() -> None:
    """TC-BUILD-001-06 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-07 is not implemented")
def test_tc_build_001_07() -> None:
    """TC-BUILD-001-07 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-BUILD-001-08 is not implemented")
def test_tc_build_001_08() -> None:
    """TC-BUILD-001-08 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-BUILD-001-08")
