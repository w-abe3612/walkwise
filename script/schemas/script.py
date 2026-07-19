from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/schemas/script.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-SCRIPT-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-SCRIPT-001', 'ScriptDocument/ScriptSegment/SpeakerRef', 'segment ID、order、text/tts_text、claim refsを型付けする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-SCRIPT-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'segment一意', 'given': '8〜10segment初稿', 'when': 'validate', 'then': 'ID/order/textを検証し順序を保持', 'test_file': '`tests/test_script_schema.py`'},
    {'id': 'TC-SCRIPT-001-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': '指定外資料', 'given': 'AI結果がsource_ids外の事実を含む', 'when': '生成結果を検査', 'then': 'pending claimとして記録し黙って承認しない', 'test_file': '`tests/test_draft_generation.py`'},
    {'id': 'TC-SCRIPT-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '旧TXT', 'given': '同一TXTを2回変換', 'when': 'segment化', 'then': '同一ID/orderになり人間未承認', 'test_file': '`tests/test_script_schema.py`'},
    {'id': 'TC-SCRIPT-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'standard generation', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ScriptDocument/ScriptSegment/SpeakerRef`を通じて「standard generation」を実行する', 'then': '「standard generation」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_draft_generation.py`'},
    {'id': 'TC-SCRIPT-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'prompt/input provenance', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ScriptDocument/ScriptSegment/SpeakerRef`を通じて「prompt/input provenance」を実行する', 'then': '「prompt/input provenance」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_script_schema.py`'},
    {'id': 'TC-SCRIPT-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '入力不変', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ScriptDocument/ScriptSegment/SpeakerRef`を通じて「入力不変」を実行する', 'then': '処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。', 'test_file': '`tests/test_draft_generation.py`'},
    {'id': 'TC-SCRIPT-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ScriptDocument/ScriptSegment/SpeakerRef`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_script_schema.py`'},
    {'id': 'TC-SCRIPT-001-08', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ScriptDocument/ScriptSegment/SpeakerRef`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_draft_generation.py`'},
    {'id': 'TC-SCRIPT-001-09', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_script_schema.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/schemas/script.py)")

class ScriptDocument:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ScriptSegment:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SpeakerRef:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
