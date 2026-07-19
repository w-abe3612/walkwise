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

@pytest.mark.integration_mock
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-02 is not implemented")
def test_tc_audio_001_02() -> None:
    """TC-AUDIO-001-02 — 部分再生成
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
    Priority: P0
    Layer: integration_mock
    Given: 1segmentだけ変更
    When: synthesize
    Then: 対象segmentだけclientを呼ぶ
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-05 is not implemented")
def test_tc_audio_001_05() -> None:
    """TC-AUDIO-001-05 — 300文字超internal part
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SegmentSynthesizer.synthesize(script, profile) -> list[SegmentAudio]`を通じて「300文字超internal part」を実行する
    Then: 「300文字超internal part」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-05")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-AUDIO-001-08 is not implemented")
def test_tc_audio_001_08() -> None:
    """TC-AUDIO-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `SegmentSynthesizer.synthesize(script, profile) -> list[SegmentAudio]`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-AUDIO-001-08")
