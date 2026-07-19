"""STEP3 test scaffold for TASK-AUDIO-002: 音声自動検査・provisional閾値.

Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
Release scope: MVP
Planned production files:
- script/audio/validation.py
- script/audio/measurements.py
- script/audio/thresholds.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-002-01 is not implemented")
def test_tc_audio_002_01() -> None:
    """TC-AUDIO-002-01 — 破損/0秒
    
    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P0
    Layer: unit
    Given: 破損WAVと0秒WAV
    When: validate
    Then: 常にfail
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-002-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-002-03 is not implemented")
def test_tc_audio_002_03() -> None:
    """TC-AUDIO-002-03 — approved禁止
    
    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P0
    Layer: unit
    Given: measured=falseまたは話者2未満
    When: threshold approve
    Then: 拒否する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-002-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-002-05 is not implemented")
def test_tc_audio_002_05() -> None:
    """TC-AUDIO-002-05 — 外部ffmpeg adapter境界
    
    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AudioThresholds.load()/validate_approval()`を通じて「外部ffmpeg adapter境界」を実行する
    Then: 「外部ffmpeg adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-002-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-002-07 is not implemented")
def test_tc_audio_002_07() -> None:
    """TC-AUDIO-002-07 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `AudioThresholds.load()/validate_approval()`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-002-07")

@pytest.mark.integration_smoke
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-002-09 is not implemented")
def test_tc_audio_002_09() -> None:
    """TC-AUDIO-002-09 — ffmpeg/ffprobe runtimeの疎通確認
    
    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: `ffmpeg -version`と`ffprobe -version`を実行し、実行可能・version取得可能であることだけを確認する。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-002-09")
