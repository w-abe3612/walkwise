"""STEP3 test scaffold for TASK-AUDIO-001: 試聴・segment TTS・WAV cache.

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Release scope: MVP
Planned production files:
- script/audio/synthesis.py
- script/audio/cache.py
- script/audio/preview.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-01 is not implemented")
def test_tc_audio_001_01() -> None:
    """TC-AUDIO-001-01 — cache key
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
    Priority: P0
    Layer: unit
    Given: text同一でvoice revision差
    When: key生成
    Then: 異なるkeyになる
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-01")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-04 is not implemented")
def test_tc_audio_001_04() -> None:
    """TC-AUDIO-001-04 — tts_text優先
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SegmentSynthesizer.synthesize(script, profile) -> list[SegmentAudio]`を通じて「tts_text優先」を実行する
    Then: 「tts_text優先」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-07 is not implemented")
def test_tc_audio_001_07() -> None:
    """TC-AUDIO-001-07 — atomic output
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SegmentSynthesizer.synthesize(script, profile) -> list[SegmentAudio]`を通じて「atomic output」を実行する
    Then: 「atomic output」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-07")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-10 is not implemented")
def test_tc_audio_001_10() -> None:
    """TC-AUDIO-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
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
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-10")
