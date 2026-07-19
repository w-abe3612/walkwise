"""STEP3 test scaffold for TASK-TTS-001: TTS共通Protocol・registry・エラー契約.

Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
Release scope: MVP
Planned production files:
- script/tts_clients/base.py
- script/tts_clients/registry.py
- script/tts_clients/models.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-01 is not implemented")
def test_tc_tts_001_01() -> None:
    """TC-TTS-001-01 — registry
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P0
    Layer: unit
    Given: voicevox client登録
    When: get
    Then: 同一instance/contractを返す
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-03 is not implemented")
def test_tc_tts_001_03() -> None:
    """TC-TTS-001-03 — 共通error
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P0
    Layer: unit
    Given: engine固有timeout
    When: 上位へ変換
    Then: TTSClientError code=timeoutとdetail保持
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-03")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-05 is not implemented")
def test_tc_tts_001_05() -> None:
    """TC-TTS-001-05 — health_check
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「health_check」を実行する
    Then: 「health_check」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-07 is not implemented")
def test_tc_tts_001_07() -> None:
    """TC-TTS-001-07 — synthesize
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「synthesize」を実行する
    Then: 「synthesize」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-09 is not implemented")
def test_tc_tts_001_09() -> None:
    """TC-TTS-001-09 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-09")
