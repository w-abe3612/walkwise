from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/pipelines/claims.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-CLAIM-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-CLAIM-001', 'ClaimPipeline.extract(script) -> list[Claim]', '抽出結果はpendingで生成する。'),
    ('TASK-CLAIM-001', 'ClaimPipeline.verify(claims, sources) -> FactCheckReport', 'evidenceと人間承認なしにverifiedへしない。'),
    ('TASK-CLAIM-001', 'assert_script_claims_publishable(script, claims) -> None', 'unsupported/conflictを本番工程から遮断する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-CLAIM-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '抽出初期状態', 'given': '技術文を含むscript', 'when': 'extract', 'then': '全claimはpending', 'test_file': '`tests/test_claims_pipeline.py`'},
    {'id': 'TC-CLAIM-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'verified条件', 'given': 'source locatorあり・人間承認あり', 'when': 'verify', 'then': 'verified可能。AI出力のみでは不可', 'test_file': '`tests/test_claim_validation.py`'},
    {'id': 'TC-CLAIM-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'conflict gate', 'given': 'conflict claimを含むscript', 'when': 'publishable確認', 'then': '本番TTS前に停止する', 'test_file': '`tests/test_claims_pipeline.py`'},
    {'id': 'TC-CLAIM-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'economy抽出はpending', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`Claim/SourceEvidence/FactCheckReport`を通じて「economy抽出はpending」を実行する', 'then': '「economy抽出はpending」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_claim_validation.py`'},
    {'id': 'TC-CLAIM-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'evidence mapping', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`Claim/SourceEvidence/FactCheckReport`を通じて「evidence mapping」を実行する', 'then': '「evidence mapping」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_claims_pipeline.py`'},
    {'id': 'TC-CLAIM-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'source locator', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`Claim/SourceEvidence/FactCheckReport`を通じて「source locator」を実行する', 'then': '「source locator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_claim_validation.py`'},
    {'id': 'TC-CLAIM-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'unsupported block', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`Claim/SourceEvidence/FactCheckReport`を通じて「unsupported block」を実行する', 'then': '「unsupported block」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_claims_pipeline.py`'},
    {'id': 'TC-CLAIM-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`Claim/SourceEvidence/FactCheckReport`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_claim_validation.py`'},
    {'id': 'TC-CLAIM-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`Claim/SourceEvidence/FactCheckReport`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_claims_pipeline.py`'},
    {'id': 'TC-CLAIM-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_claim_validation.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/pipelines/claims.py)")

class Claim:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class FactCheckReport:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ClaimPipeline:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def extract(self, script: Any) -> list[Claim]:
        """抽出結果はpendingで生成する。

        Public contract: ``ClaimPipeline.extract(script) -> list[Claim]``.
        """
        _step4_unimplemented('ClaimPipeline.extract')
    def verify(self, claims: Any, sources: Any) -> FactCheckReport:
        """evidenceと人間承認なしにverifiedへしない。

        Public contract: ``ClaimPipeline.verify(claims, sources) -> FactCheckReport``.
        """
        _step4_unimplemented('ClaimPipeline.verify')

def assert_script_claims_publishable(script: Any, claims: Any) -> None:
    """unsupported/conflictを本番工程から遮断する。

    Public contract: ``assert_script_claims_publishable(script, claims) -> None``.
    """
    _step4_unimplemented('assert_script_claims_publishable')
