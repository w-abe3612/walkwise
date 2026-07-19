from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/tts_clients/models.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-TTS-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-TTS-001', 'SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities', 'TTS共通入出力を型付けする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-TTS-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'registry', 'given': 'voicevox client登録', 'when': 'get', 'then': '同一instance/contractを返す', 'test_file': '`tests/test_tts_client_contract.py`'},
    {'id': 'TC-TTS-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '未知engine', 'given': '未登録名', 'when': 'get', 'then': 'unsupported_engine', 'test_file': '`tests/test_tts_registry.py`'},
    {'id': 'TC-TTS-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '共通error', 'given': 'engine固有timeout', 'when': '上位へ変換', 'then': 'TTSClientError code=timeoutとdetail保持', 'test_file': '`tests/test_tts_client_contract.py`'},
    {'id': 'TC-TTS-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'request/result型', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「request/result型」を実行する', 'then': '「request/result型」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_tts_registry.py`'},
    {'id': 'TC-TTS-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'health_check', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「health_check」を実行する', 'then': '「health_check」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_tts_client_contract.py`'},
    {'id': 'TC-TTS-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'list_speakers', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「list_speakers」を実行する', 'then': '表示名へ依存せずengineの識別子から解決し、不在時はspeaker_not_foundまたは局所disableになる。', 'test_file': '`tests/test_tts_registry.py`'},
    {'id': 'TC-TTS-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'synthesize', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を通じて「synthesize」を実行する', 'then': '「synthesize」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_tts_client_contract.py`'},
    {'id': 'TC-TTS-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_tts_registry.py`'},
    {'id': 'TC-TTS-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`SynthesisRequest/SynthesisResult/SpeakerInfo/EngineCapabilities`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_tts_client_contract.py`'},
    {'id': 'TC-TTS-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_tts_registry.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/tts_clients/models.py)")

class EngineCapabilities:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SpeakerInfo:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SynthesisRequest:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SynthesisResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
