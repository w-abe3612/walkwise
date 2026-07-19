"""STEP3 test scaffold for TASK-PROFILE-001: Character・Voice profile読込と選択.

Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
Release scope: MVP
Planned production files:
- script/profiles/characters.py
- script/profiles/voices.py
- script/schemas/profiles.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROFILE-001-02 is not implemented")
def test_tc_profile_001_02() -> None:
    """TC-PROFILE-001-02 — MVP engine filter
    
    Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
    Priority: P0
    Layer: unit
    Given: VOICEVOXとCOEIROINK profile
    When: list_available
    Then: MVPでは承認済みVOICEVOXだけ表示
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROFILE-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROFILE-001-04 is not implemented")
def test_tc_profile_001_04() -> None:
    """TC-PROFILE-001-04 — revision/hash
    
    Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `CharacterProfile/VoiceProfile/EngineIdentity`を通じて「revision/hash」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROFILE-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROFILE-001-06 is not implemented")
def test_tc_profile_001_06() -> None:
    """TC-PROFILE-001-06 — 作品別既定
    
    Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `CharacterProfile/VoiceProfile/EngineIdentity`を通じて「作品別既定」を実行する
    Then: 「作品別既定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROFILE-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-PROFILE-001-08 is not implemented")
def test_tc_profile_001_08() -> None:
    """TC-PROFILE-001-08 — 再実行時の決定性
    
    Contract: docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `CharacterProfile/VoiceProfile/EngineIdentity`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-PROFILE-001-08")
