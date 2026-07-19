from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/migration/report.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-MIGRATION-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-MIGRATION-001', 'MigrationReport', '変換、warning、provenance、未移行項目を記録する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-MIGRATION-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '新形式優先', 'given': '新旧両形式がある', 'when': 'read/migrate', 'then': '新形式を採用し旧形式を上書きしない', 'test_file': '`tests/test_legacy_migration.py`'},
    {'id': 'TC-MIGRATION-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'full_book正規化', 'given': '旧unit_id=full_book', 'when': 'migrate', 'then': 'bookへ変換しprovenanceを記録', 'test_file': '`tests/test_legacy_input_priority.py`'},
    {'id': 'TC-MIGRATION-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '不明項目', 'given': '変換不能field', 'when': 'migrate', 'then': '推測せずwarning/reportへ残す', 'test_file': '`tests/test_legacy_migration.py`'},
    {'id': 'TC-MIGRATION-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'bookId/project_id', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`LegacyBook/LegacySection/LegacyAudioInput`を通じて「bookId/project_id」を実行する', 'then': '「bookId/project_id」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_legacy_input_priority.py`'},
    {'id': 'TC-MIGRATION-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'sectionId/chapter_id', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`LegacyBook/LegacySection/LegacyAudioInput`を通じて「sectionId/chapter_id」を実行する', 'then': '「sectionId/chapter_id」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_legacy_migration.py`'},
    {'id': 'TC-MIGRATION-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'approval.yaml/approvals.yaml', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`LegacyBook/LegacySection/LegacyAudioInput`を通じて「approval.yaml/approvals.yaml」を実行する', 'then': '必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。', 'test_file': '`tests/test_legacy_input_priority.py`'},
    {'id': 'TC-MIGRATION-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'legacy text priority', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`LegacyBook/LegacySection/LegacyAudioInput`を通じて「legacy text priority」を実行する', 'then': '「legacy text priority」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_legacy_migration.py`'},
    {'id': 'TC-MIGRATION-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`LegacyBook/LegacySection/LegacyAudioInput`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_legacy_input_priority.py`'},
    {'id': 'TC-MIGRATION-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`LegacyBook/LegacySection/LegacyAudioInput`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_legacy_migration.py`'},
    {'id': 'TC-MIGRATION-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_legacy_input_priority.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/migration/report.py)")

class MigrationReport:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
