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
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-02 is not implemented")
def test_tc_tts_001_02() -> None:
    """TC-TTS-001-02 — 未知engine
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P0
    Layer: unit
    Given: 未登録名
    When: get
    Then: unsupported_engine
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-04 is not implemented")
def test_tc_tts_001_04() -> None:
    """TC-TTS-001-04 — request/result型
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「request/result型」を実行する
    Then: 「request/result型」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-06 is not implemented")
def test_tc_tts_001_06() -> None:
    """TC-TTS-001-06 — list_speakers
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「list_speakers」を実行する
    Then: 表示名へ依存せずengineの識別子から解決し、不在時はspeaker_not_foundまたは局所disableになる。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-08 is not implemented")
def test_tc_tts_001_08() -> None:
    """TC-TTS-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-TTS-001-10 is not implemented")
def test_tc_tts_001_10() -> None:
    """TC-TTS-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-TTS-001-10")
