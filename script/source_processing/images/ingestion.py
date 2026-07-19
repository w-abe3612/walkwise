from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/images/ingestion.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-IMAGE-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-IMAGE-001', 'ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult', '画像を検証し決定的順序でimmutable登録する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-IMAGE-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '自然順', 'given': 'page1,page2,page10のファイル', 'when': 'ingestする', 'then': 'natural orderで1,2,10となる', 'test_file': '`tests/test_image_ingestion.py`'},
    {'id': 'TC-IMAGE-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '明示順', 'given': 'explicit orderを指定', 'when': 'ingestする', 'then': '指定順を採用し重複/欠落を拒否する', 'test_file': '`tests/test_image_manifest.py`'},
    {'id': 'TC-IMAGE-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'EXIF privacy', 'given': '位置情報付きJPEG', 'when': 'manifest/exportを作る', 'then': '内部warningは保持しても公開成果物に位置情報を含めない', 'test_file': '`tests/test_image_ingestion.py`'},
    {'id': 'TC-IMAGE-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '形式検証', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「形式検証」を実行する', 'then': '正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。', 'test_file': '`tests/test_image_manifest.py`'},
    {'id': 'TC-IMAGE-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '壊れた画像検出', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「壊れた画像検出」を実行する', 'then': '「壊れた画像検出」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_image_ingestion.py`'},
    {'id': 'TC-IMAGE-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '原画像immutable copy', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「原画像immutable copy」を実行する', 'then': '処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。', 'test_file': '`tests/test_image_manifest.py`'},
    {'id': 'TC-IMAGE-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'hash', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「hash」を実行する', 'then': '同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。', 'test_file': '`tests/test_image_ingestion.py`'},
    {'id': 'TC-IMAGE-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_image_manifest.py`'},
    {'id': 'TC-IMAGE-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_image_ingestion.py`'},
    {'id': 'TC-IMAGE-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_image_manifest.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/images/ingestion.py)")

class ImageIngestionResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ImageIngestionService:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def ingest(self, paths: Any, *, explicit_order: Any = None) -> ImageIngestionResult:
        """画像を検証し決定的順序でimmutable登録する。

        Public contract: ``ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult``.
        """
        _step4_unimplemented('ImageIngestionService.ingest')
