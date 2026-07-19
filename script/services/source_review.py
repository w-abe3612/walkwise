from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/services/source_review.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-SOURCE-003
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-SOURCE-003', 'SourceReviewService.apply_correction(command) -> ReviewResult', 'rawを変えず修正版とdiffを新revisionへ保存する。'),
    ('TASK-SOURCE-003', 'SourceReviewService.mark_resolved/require_reprocessing', '問題解消または再処理要求を記録する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-SOURCE-003-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': '修正revision', 'given': 'review issueへ手動修正', 'when': 'apply_correction', 'then': 'raw不変で新revision・diff・provenanceを作る', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-02', 'priority': 'P0', 'layer': 'unit', 'title': '再処理', 'given': 'OCR設定変更を要求', 'when': 'require_reprocessing', 'then': '旧正常結果を残し新Job候補を作る', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-03', 'priority': 'P1', 'layer': 'unit', 'title': 'review item model', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「review item model」を実行する', 'then': '「review item model」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-04', 'priority': 'P1', 'layer': 'unit', 'title': '元ページlocator', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「元ページlocator」を実行する', 'then': '「元ページlocator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-05', 'priority': 'P1', 'layer': 'integration_mock', 'title': 'manual correction file', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「manual correction file」を実行する', 'then': '「manual correction file」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-06', 'priority': 'P1', 'layer': 'unit', 'title': '再OCR要求', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「再OCR要求」を実行する', 'then': '「再OCR要求」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-07', 'priority': 'P1', 'layer': 'unit', 'title': '問題なし承認', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「問題なし承認」を実行する', 'then': '必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`SourceReviewIssue/CorrectionPatch/ReviewDecision`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_source_review_service.py`'},
    {'id': 'TC-SOURCE-003-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_source_review_service.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/services/source_review.py)")

class ReviewResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SourceReviewService:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def apply_correction(self, command: Any) -> ReviewResult:
        """rawを変えず修正版とdiffを新revisionへ保存する。

        Public contract: ``SourceReviewService.apply_correction(command) -> ReviewResult``.
        """
        _step4_unimplemented('SourceReviewService.apply_correction')
    def mark_resolved(self) -> Any:
        """問題解消または再処理要求を記録する。

        Public contract: ``SourceReviewService.mark_resolved/require_reprocessing``.
        """
        _step4_unimplemented('SourceReviewService.mark_resolved')
    def require_reprocessing(self) -> Any:
        """問題解消または再処理要求を記録する。

        Public contract: ``SourceReviewService.mark_resolved/require_reprocessing``.
        """
        _step4_unimplemented('SourceReviewService.require_reprocessing')
