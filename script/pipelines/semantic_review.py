from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/pipelines/semantic_review.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-NARRATION-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-NARRATION-001', 'SemanticReview.compare(source, transformed) -> SemanticReviewResult', '意味差、条件削除、数値変化を検出する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-NARRATION-001-01', 'priority': 'P0', 'layer': 'unit', 'title': '段階不変', 'given': 'draft script', 'when': '3変換を実行', 'then': '各段階を別成果物にし元textを変更しない', 'test_file': '`tests/test_narration_transformations.py`'},
    {'id': 'TC-NARRATION-001-02', 'priority': 'P0', 'layer': 'unit', 'title': '意味差', 'given': '数値・否定・条件を変更した変換', 'when': 'semantic review', 'then': 'review_required/fail候補を返す', 'test_file': '`tests/test_verified_script_pipeline.py`'},
    {'id': 'TC-NARRATION-001-03', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'verified gate', 'given': 'fact checkまたはsemantic review未完', 'when': 'verified生成', 'then': '拒否する', 'test_file': '`tests/test_narration_transformations.py`'},
    {'id': 'TC-NARRATION-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'simplified/audio-adapted/character-styledの分離', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`NarrationPipeline.simplify/adapt_for_audio/apply_character`を通じて「simplified/audio-adapted/character-styledの分離」を実行する', 'then': '表示名へ依存せずengineの識別子から解決し、不在時はspeaker_not_foundまたは局所disableになる。', 'test_file': '`tests/test_verified_script_pipeline.py`'},
    {'id': 'TC-NARRATION-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'tts_textのみ発音調整', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`NarrationPipeline.simplify/adapt_for_audio/apply_character`を通じて「tts_textのみ発音調整」を実行する', 'then': '「tts_textのみ発音調整」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_narration_transformations.py`'},
    {'id': 'TC-NARRATION-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '未検証claim block', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`NarrationPipeline.simplify/adapt_for_audio/apply_character`を通じて「未検証claim block」を実行する', 'then': '正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。', 'test_file': '`tests/test_verified_script_pipeline.py`'},
    {'id': 'TC-NARRATION-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'high assurance final review', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`NarrationPipeline.simplify/adapt_for_audio/apply_character`を通じて「high assurance final review」を実行する', 'then': '「high assurance final review」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_narration_transformations.py`'},
    {'id': 'TC-NARRATION-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`NarrationPipeline.simplify/adapt_for_audio/apply_character`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_verified_script_pipeline.py`'},
    {'id': 'TC-NARRATION-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`NarrationPipeline.simplify/adapt_for_audio/apply_character`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_narration_transformations.py`'},
    {'id': 'TC-NARRATION-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_verified_script_pipeline.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/pipelines/semantic_review.py)")

class SemanticReviewResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SemanticReview:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def compare(self, source: Any, transformed: Any) -> SemanticReviewResult:
        """意味差、条件削除、数値変化を検出する。

        Public contract: ``SemanticReview.compare(source, transformed) -> SemanticReviewResult``.
        """
        _step4_unimplemented('SemanticReview.compare')
