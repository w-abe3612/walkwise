from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/domain/enums.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-DOMAIN-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-DOMAIN-001', 'PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType', '承認済み列挙値だけを定義する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-DOMAIN-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '複数出力canonical', 'given': '`text, mp3`の入力', 'when': 'BuildRequestを生成する', 'then': 'formatsはmp3,text順で保持される', 'test_file': '`tests/test_domain_models.py`'},
    {'id': 'TC-DOMAIN-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'voice条件', 'given': 'text-onlyとmp3を含む入力', 'when': 'validationを行う', 'then': 'text-onlyはvoice null可、mp3はnull拒否', 'test_file': '`tests/test_domain_validation.py`'},
    {'id': 'TC-DOMAIN-001-03', 'priority': 'P1', 'layer': 'unit', 'title': 'dataclass/enum', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「dataclass/enum」を実行する', 'then': '「dataclass/enum」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_domain_models.py`'},
    {'id': 'TC-DOMAIN-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '必須項目', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「必須項目」を実行する', 'then': '「必須項目」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_domain_validation.py`'},
    {'id': 'TC-DOMAIN-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '状態列挙', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「状態列挙」を実行する', 'then': '承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。', 'test_file': '`tests/test_domain_models.py`'},
    {'id': 'TC-DOMAIN-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '相対path value object', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「相対path value object」を実行する', 'then': '保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。', 'test_file': '`tests/test_domain_validation.py`'},
    {'id': 'TC-DOMAIN-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_domain_models.py`'},
    {'id': 'TC-DOMAIN-001-08', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_domain_validation.py`'},
    {'id': 'TC-DOMAIN-001-09', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_domain_models.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/domain/enums.py)")

class ArtifactType:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class BuildStatus:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class JobStatus:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class PlanningStage:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SourceStatus:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
