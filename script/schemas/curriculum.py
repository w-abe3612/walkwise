from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/schemas/curriculum.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-CURRICULUM-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-CURRICULUM-001', 'TopicMap/Curriculum', 'topic、章順、learning outcomeを型付けする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-CURRICULUM-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': '章参照整合', 'given': 'valid analysis/project plan', 'when': '生成', 'then': 'topic/source参照が存在し章orderが一意', 'test_file': '`tests/test_curriculum_pipeline.py`'},
    {'id': 'TC-CURRICULUM-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '未知topic', 'given': 'chapter specが未定義topicを参照', 'when': 'validate', 'then': 'errorにする', 'test_file': '`tests/test_chapter_spec_schema.py`'},
    {'id': 'TC-CURRICULUM-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '承認前状態', 'given': 'AI生成直後', 'when': 'resultを保存', 'then': 'approvedではなくreview_pending/draft', 'test_file': '`tests/test_curriculum_pipeline.py`'},
    {'id': 'TC-CURRICULUM-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'learning outcomes', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`TopicMap/Curriculum`を通じて「learning outcomes」を実行する', 'then': '「learning outcomes」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_chapter_spec_schema.py`'},
    {'id': 'TC-CURRICULUM-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'coverage反映', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`TopicMap/Curriculum`を通じて「coverage反映」を実行する', 'then': '「coverage反映」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_curriculum_pipeline.py`'},
    {'id': 'TC-CURRICULUM-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'source_ids', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`TopicMap/Curriculum`を通じて「source_ids」を実行する', 'then': '「source_ids」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_chapter_spec_schema.py`'},
    {'id': 'TC-CURRICULUM-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'AI tier指定', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`TopicMap/Curriculum`を通じて「AI tier指定」を実行する', 'then': '「AI tier指定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_curriculum_pipeline.py`'},
    {'id': 'TC-CURRICULUM-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`TopicMap/Curriculum`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_chapter_spec_schema.py`'},
    {'id': 'TC-CURRICULUM-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`TopicMap/Curriculum`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_curriculum_pipeline.py`'},
    {'id': 'TC-CURRICULUM-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_chapter_spec_schema.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/schemas/curriculum.py)")

class Curriculum:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class TopicMap:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
