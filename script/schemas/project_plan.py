from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/schemas/project_plan.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-PROJECT-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-PROJECT-001', 'ProjectPlan.from_mapping()/to_mapping()/validate()', '企画書YAMLの必須項目とplanning stage規則を検証する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-PROJECT-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'Project作成atomicity', 'given': '有効入力', 'when': 'createする', 'then': 'plan fileとDB行が同じproject_id/revisionで作成される', 'test_file': '`tests/test_project_service.py`'},
    {'id': 'TC-PROJECT-001-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'DB失敗cleanup', 'given': 'file作成後のDB insertを失敗させる', 'when': 'createする', 'then': '不完全Projectを一覧へ出さずcleanup/rollbackする', 'test_file': '`tests/test_project_plan_schema.py`'},
    {'id': 'TC-PROJECT-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'archive除外', 'given': 'activeとarchived Projectがある', 'when': 'list_activeする', 'then': 'activeだけを返す', 'test_file': '`tests/test_project_service.py`'},
    {'id': 'TC-PROJECT-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '入力validation', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ProjectPlan.from_mapping()/to_mapping()/validate()`を通じて「入力validation」を実行する', 'then': '正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。', 'test_file': '`tests/test_project_plan_schema.py`'},
    {'id': 'TC-PROJECT-001-05', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ProjectPlan.from_mapping()/to_mapping()/validate()`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_project_service.py`'},
    {'id': 'TC-PROJECT-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ProjectPlan.from_mapping()/to_mapping()/validate()`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_project_plan_schema.py`'},
    {'id': 'TC-PROJECT-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_project_service.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/schemas/project_plan.py)")

class ProjectPlan:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def from_mapping(self) -> Any:
        """企画書YAMLの必須項目とplanning stage規則を検証する。

        Public contract: ``ProjectPlan.from_mapping()/to_mapping()/validate()``.
        """
        _step4_unimplemented('ProjectPlan.from_mapping')
    def to_mapping(self) -> Any:
        """企画書YAMLの必須項目とplanning stage規則を検証する。

        Public contract: ``ProjectPlan.from_mapping()/to_mapping()/validate()``.
        """
        _step4_unimplemented('ProjectPlan.to_mapping')
    def validate(self) -> Any:
        """企画書YAMLの必須項目とplanning stage規則を検証する。

        Public contract: ``ProjectPlan.from_mapping()/to_mapping()/validate()``.
        """
        _step4_unimplemented('ProjectPlan.validate')
