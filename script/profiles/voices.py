from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/profiles/voices.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-PROFILE-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-PROFILE-001', 'VoiceProfileRepository.load/select/list_available', 'MVPではVOICEVOXだけを利用可能一覧へ出す。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-PROFILE-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'ID分離', 'given': '同名characterとengine speaker', 'when': 'load', 'then': 'character_id/voice_profile_id/engine IDsを別保持', 'test_file': '`tests/test_character_profiles.py`'},
    {'id': 'TC-PROFILE-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'MVP engine filter', 'given': 'VOICEVOXとCOEIROINK profile', 'when': 'list_available', 'then': 'MVPでは承認済みVOICEVOXだけ表示', 'test_file': '`tests/test_voice_profiles.py`'},
    {'id': 'TC-PROFILE-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '未承認選択', 'given': 'candidate/rejected profile', 'when': 'select', 'then': '拒否する', 'test_file': '`tests/test_character_profiles.py`'},
    {'id': 'TC-PROFILE-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'revision/hash', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CharacterProfile/VoiceProfile/EngineIdentity`を通じて「revision/hash」を実行する', 'then': '同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。', 'test_file': '`tests/test_voice_profiles.py`'},
    {'id': 'TC-PROFILE-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'provisional/selected', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CharacterProfile/VoiceProfile/EngineIdentity`を通じて「provisional/selected」を実行する', 'then': '「provisional/selected」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_character_profiles.py`'},
    {'id': 'TC-PROFILE-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '作品別既定', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`CharacterProfile/VoiceProfile/EngineIdentity`を通じて「作品別既定」を実行する', 'then': '「作品別既定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_voice_profiles.py`'},
    {'id': 'TC-PROFILE-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`CharacterProfile/VoiceProfile/EngineIdentity`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_character_profiles.py`'},
    {'id': 'TC-PROFILE-001-08', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`CharacterProfile/VoiceProfile/EngineIdentity`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_voice_profiles.py`'},
    {'id': 'TC-PROFILE-001-09', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_character_profiles.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/profiles/voices.py)")

class VoiceProfileRepository:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def load(self) -> Any:
        """MVPではVOICEVOXだけを利用可能一覧へ出す。

        Public contract: ``VoiceProfileRepository.load/select/list_available``.
        """
        _step4_unimplemented('VoiceProfileRepository.load')
    def select(self) -> Any:
        """MVPではVOICEVOXだけを利用可能一覧へ出す。

        Public contract: ``VoiceProfileRepository.load/select/list_available``.
        """
        _step4_unimplemented('VoiceProfileRepository.select')
    def list_available(self) -> Any:
        """MVPではVOICEVOXだけを利用可能一覧へ出す。

        Public contract: ``VoiceProfileRepository.load/select/list_available``.
        """
        _step4_unimplemented('VoiceProfileRepository.list_available')
