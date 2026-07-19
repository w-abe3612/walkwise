from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/ocr/pipeline.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-OCR-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-OCR-001', 'OcrPipeline.process_pages(pages, context) -> OcrManifest', 'ページ単位結果・confidence・review flagを集約し失敗を分離する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-OCR-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'runtimeなし', 'given': 'Tesseractが見つからない', 'when': 'OCRを開始', 'then': '疎通確認で停止しSourceをfailed/reviewableにする', 'test_file': '`tests/test_ocr_client.py`'},
    {'id': 'TC-OCR-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '高リスク要素', 'given': 'table/code/math/figure候補page', 'when': 'pipeline処理', 'then': 'review_required flagを付け自動確定しない', 'test_file': '`tests/test_ocr_pipeline.py`'},
    {'id': 'TC-OCR-001-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'ページ失敗分離', 'given': '複数page中1件だけsubprocess失敗', 'when': '処理', 'then': '他page結果を保持しmanifestに失敗を記録', 'test_file': '`tests/test_ocr_client.py`'},
    {'id': 'TC-OCR-001-04', 'priority': 'P1', 'layer': 'integration_mock', 'title': 'Tesseract subprocess/adapter境界', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`OcrClient.check_runtime() -> RuntimeHealth`を通じて「Tesseract subprocess/adapter境界」を実行する', 'then': '「Tesseract subprocess/adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ocr_pipeline.py`'},
    {'id': 'TC-OCR-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '言語設定', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`OcrClient.check_runtime() -> RuntimeHealth`を通じて「言語設定」を実行する', 'then': '「言語設定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ocr_client.py`'},
    {'id': 'TC-OCR-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'confidence', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`OcrClient.check_runtime() -> RuntimeHealth`を通じて「confidence」を実行する', 'then': '「confidence」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ocr_pipeline.py`'},
    {'id': 'TC-OCR-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'table/code/math/figure flag', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`OcrClient.check_runtime() -> RuntimeHealth`を通じて「table/code/math/figure flag」を実行する', 'then': '「table/code/math/figure flag」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ocr_client.py`'},
    {'id': 'TC-OCR-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`OcrClient.check_runtime() -> RuntimeHealth`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_ocr_pipeline.py`'},
    {'id': 'TC-OCR-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`OcrClient.check_runtime() -> RuntimeHealth`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_ocr_client.py`'},
    {'id': 'TC-OCR-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_ocr_pipeline.py`'},
    {'id': 'TC-OCR-001-11', 'priority': 'P0', 'layer': 'integration_smoke', 'title': 'Tesseract runtimeの疎通確認', 'given': '実接続テストが明示的に有効化され、必要な設定が存在する', 'when': '`tesseract --version`と必要言語一覧を確認し、画像処理を行わない。', 'then': 'ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。', 'test_file': '`tests/test_ocr_client.py`'},
    {'id': 'TC-OCR-001-12', 'priority': 'P1', 'layer': 'integration_live', 'title': 'Tesseract runtimeの実機能テスト', 'given': '`tesseract_connectivity_gate`が成功済み', 'when': '疎通成功後、1行だけの固定fixture画像をOCRし、期待語を含むpage resultを確認する。', 'then': '最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。', 'test_file': '`tests/test_ocr_pipeline.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/ocr/pipeline.py)")

class OcrManifest:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class OcrPipeline:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def process_pages(self, pages: Any, context: Any) -> OcrManifest:
        """ページ単位結果・confidence・review flagを集約し失敗を分離する。

        Public contract: ``OcrPipeline.process_pages(pages, context) -> OcrManifest``.
        """
        _step4_unimplemented('OcrPipeline.process_pages')
