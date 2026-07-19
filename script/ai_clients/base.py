from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/ai_clients/base.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-AI-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-AI-001', 'AIClient Protocol: check_connectivity(), generate(request) -> AIResult', 'health確認と生成を分離した共通契約。'),
    ('TASK-AI-001', 'AIRequest/AIResult/AIUsage/AIClientError', 'prompt、model、usage、retryable errorを型付けする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-AI-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'mock生成', 'given': '固定Gemini HTTP response', 'when': 'generateする', 'then': 'AIResult text/provider/model/usageへ変換する', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'retry区分', 'given': '429/5xxと400を返すmock', 'when': 'generateする', 'then': '前者だけ上限内再試行し400は即時error', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'structured response', 'given': '不正JSONと正常JSON', 'when': 'validation hook付き生成', 'then': '正常だけ受理し不正はschema error', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'AIClient Protocol', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「AIClient Protocol」を実行する', 'then': '「AIClient Protocol」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'prompt template', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「prompt template」を実行する', 'then': '「prompt template」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'JSON/YAML response validation hook', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「JSON/YAML response validation hook」を実行する', 'then': '正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'timeout', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「timeout」を実行する', 'then': 'timeoutを安定した共通errorへ変換し、半端な最終ファイルや成功状態を残さない。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-11', 'priority': 'P0', 'layer': 'integration_smoke', 'title': 'Gemini APIの疎通確認', 'given': '実接続テストが明示的に有効化され、必要な設定が存在する', 'when': '認証付きの軽量なmodel metadata/list操作を1回だけ実行し、DNS/TLS/HTTP/認証/応答schemaを確認する。生成本文は要求しない。', 'then': 'ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-12', 'priority': 'P1', 'layer': 'integration_live', 'title': 'Gemini APIの実機能テスト', 'given': '`gemini_connectivity_gate`が成功済み', 'when': '疎通成功後、極短い固定promptを1回生成し、非空text・provider/model・usageまたはusage unavailable warningを確認する。', 'then': '最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。', 'test_file': '`tests/test_gemini_client.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/ai_clients/base.py)")

class AIClientError(RuntimeError):
    """Public error placeholder declared by the STEP2 contract."""

class AIRequest:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class AIResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class AIUsage:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class AIClient(Protocol):
    """Protocol fixed by STEP2 for script/ai_clients/base.py."""
    def check_connectivity(self, _: Any, generate_request: Any) -> AIResult:
        """health確認と生成を分離した共通契約。 Contract: AIClient Protocol: check_connectivity(), generate(request) -> AIResult"""
        ...
