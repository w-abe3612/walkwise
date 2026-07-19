from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/asr/base.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-ASR-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-ASR-001', 'ASRClient Protocol: check_connectivity()/transcribe()', 'local runtime/model確認と文字起こしを分離する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-ASR-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'ASR単独fail禁止', 'given': '大きな差分report', 'when': 'verify', 'then': 'review_required候補に留め最終failにしない', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'segment fallback', 'given': 'segment alignment不能', 'when': 'verify', 'then': '章単位比較へfallbackし理由を記録', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '用語正規化', 'given': 'SQL/エスキューエル辞書', 'when': '比較', 'then': '辞書上同義として扱い原稿自体は変更しない', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'local adapter', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ASRClient Protocol: check_connectivity()/transcribe()`を通じて「local adapter」を実行する', 'then': '「local adapter」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'cloud off', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ASRClient Protocol: check_connectivity()/transcribe()`を通じて「cloud off」を実行する', 'then': '通常・実接続テストともcloud endpointへ送信せず、network clientが呼ばれていないことを確認する。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'terminology normalization', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ASRClient Protocol: check_connectivity()/transcribe()`を通じて「terminology normalization」を実行する', 'then': '「terminology normalization」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '差分report', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ASRClient Protocol: check_connectivity()/transcribe()`を通じて「差分report」を実行する', 'then': '「差分report」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ASRClient Protocol: check_connectivity()/transcribe()`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ASRClient Protocol: check_connectivity()/transcribe()`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-11', 'priority': 'P0', 'layer': 'integration_smoke', 'title': 'ローカルWhisper互換runtimeの疎通確認', 'given': '実接続テストが明示的に有効化され、必要な設定が存在する', 'when': 'runtime/modelの存在・読込可否・versionを確認し、まだ音声文字起こしは行わない。', 'then': 'ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。', 'test_file': '`tests/test_asr_verification.py`'},
    {'id': 'TC-ASR-001-12', 'priority': 'P1', 'layer': 'integration_live', 'title': 'ローカルWhisper互換runtimeの実機能テスト', 'given': '`asr_connectivity_gate`が成功済み', 'when': '疎通成功後、数秒の固定fixture WAVだけを文字起こしし、非空segmentとtimestamp順を確認する。', 'then': '最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。', 'test_file': '`tests/test_asr_verification.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/asr/base.py)")

class ASRClient(Protocol):
    """Protocol fixed by STEP2 for script/asr/base.py."""
    def check_connectivity(self) -> Any:
        """local runtime/model確認と文字起こしを分離する。 Contract: ASRClient Protocol: check_connectivity()/transcribe()"""
        ...
    def transcribe(self) -> Any:
        """local runtime/model確認と文字起こしを分離する。 Contract: ASRClient Protocol: check_connectivity()/transcribe()"""
        ...
