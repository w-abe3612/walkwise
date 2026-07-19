from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/source_processing/images/preprocess.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-IMAGE-002
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-IMAGE-002', 'ImagePreprocessor.process(page, options) -> PreprocessedPage', '原画像を変えずOCR用PNGと変換manifestを生成する。'),
    ('TASK-IMAGE-002', 'split_spread(page) -> tuple[PreprocessedPage, PreprocessedPage]', '左右locatorを保持して見開きを分割する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-IMAGE-002-01', 'priority': 'P0', 'layer': 'unit', 'title': '原画像不変', 'given': '回転・contrast処理対象', 'when': 'preprocessする', 'then': '原画像hash不変で派生PNGとparametersを保存', 'test_file': '`tests/test_image_preprocessing.py`'},
    {'id': 'TC-IMAGE-002-02', 'priority': 'P0', 'layer': 'unit', 'title': 'blank候補', 'given': 'ほぼ白紙の画像', 'when': 'quality評価する', 'then': '削除せずblank_candidate warningにする', 'test_file': '`tests/test_image_quality_flags.py`'},
    {'id': 'TC-IMAGE-002-03', 'priority': 'P0', 'layer': 'unit', 'title': '見開きlocator', 'given': '見開き画像', 'when': 'splitする', 'then': '左右の元page座標対応を保持する', 'test_file': '`tests/test_image_preprocessing.py`'},
    {'id': 'TC-IMAGE-002-04', 'priority': 'P1', 'layer': 'unit', 'title': '決定的な低リスク補正', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「決定的な低リスク補正」を実行する', 'then': '「決定的な低リスク補正」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_image_quality_flags.py`'},
    {'id': 'TC-IMAGE-002-05', 'priority': 'P1', 'layer': 'unit', 'title': 'before/after hash', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「before/after hash」を実行する', 'then': '同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。', 'test_file': '`tests/test_image_preprocessing.py`'},
    {'id': 'TC-IMAGE-002-06', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ImagePreprocessor.process(page, options) -> PreprocessedPage`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_image_quality_flags.py`'},
    {'id': 'TC-IMAGE-002-07', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ImagePreprocessor.process(page, options) -> PreprocessedPage`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_image_preprocessing.py`'},
    {'id': 'TC-IMAGE-002-08', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_image_quality_flags.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/source_processing/images/preprocess.py)")

class PreprocessedPage:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ImagePreprocessor:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def process(self, page: Any, options: Any) -> PreprocessedPage:
        """原画像を変えずOCR用PNGと変換manifestを生成する。

        Public contract: ``ImagePreprocessor.process(page, options) -> PreprocessedPage``.
        """
        _step4_unimplemented('ImagePreprocessor.process')

def split_spread(page: Any) -> tuple[PreprocessedPage, PreprocessedPage]:
    """左右locatorを保持して見開きを分割する。

    Public contract: ``split_spread(page) -> tuple[PreprocessedPage, PreprocessedPage]``.
    """
    _step4_unimplemented('split_spread')
