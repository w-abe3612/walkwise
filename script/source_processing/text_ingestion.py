from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/text_ingestion.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-INGEST-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-INGEST-001', 'TextIngestionAdapter.process(path, context) -> StructuredSource', 'UTF-8本文を共通資料構造へ変換する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-INGEST-001-01', 'priority': 'P0', 'layer': 'unit', 'title': 'dispatch', 'given': 'text/pdf/image Source', 'when': 'processする', 'then': '各adapterへ正確に1回dispatchする', 'test_file': '`tests/test_material_input_orchestrator.py`'},
    {'id': 'TC-INGEST-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '未知media', 'given': 'epubまたはvideo', 'when': 'processする', 'then': 'MVPではunsupported_media_typeで停止する', 'test_file': '`tests/test_text_ingestion.py`'},
    {'id': 'TC-INGEST-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'text encoding', 'given': 'UTF-8正常/不正bytes', 'when': 'text adapterを実行', 'then': '正常はstructured、異常はfailedで原本保持', 'test_file': '`tests/test_material_input_orchestrator.py`'},
    {'id': 'TC-INGEST-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'original/extracted/normalized/structured handoff', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「original/extracted/normalized/structured handoff」を実行する', 'then': '「original/extracted/normalized/structured handoff」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_text_ingestion.py`'},
    {'id': 'TC-INGEST-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'status更新', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「status更新」を実行する', 'then': '承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。', 'test_file': '`tests/test_material_input_orchestrator.py`'},
    {'id': 'TC-INGEST-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'Job進捗hook', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「Job進捗hook」を実行する', 'then': 'current/totalとmessageを単調・順序どおりに通知し、完了後に進捗を逆行させない。', 'test_file': '`tests/test_text_ingestion.py`'},
    {'id': 'TC-INGEST-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_material_input_orchestrator.py`'},
    {'id': 'TC-INGEST-001-08', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_text_ingestion.py`'},
    {'id': 'TC-INGEST-001-09', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_material_input_orchestrator.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/text_ingestion.py)")

class StructuredSource:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class TextIngestionAdapter:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def process(self, path: Any, context: Any) -> StructuredSource:
        """UTF-8本文を共通資料構造へ変換する。

        Public contract: ``TextIngestionAdapter.process(path, context) -> StructuredSource``.
        """
        _step4_unimplemented('TextIngestionAdapter.process')
