from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/integration/mvp_flow.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-DESKTOP-003
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-DESKTOP-003', 'run_mvp_flow(dependencies) -> MvpFlowResult', 'Project作成からArtifactまでの縦切りをmock依存で実行する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-DESKTOP-003-01', 'priority': 'P0', 'layer': 'e2e', 'title': '最短導線', 'given': 'mock AI/TTSと空data', 'when': 'E2Eを実行', 'then': 'Project→text Source→承認→text Artifactまで完了', 'test_file': '`tests/integration/test_mvp_flow.py`'},
    {'id': 'TC-DESKTOP-003-02', 'priority': 'P0', 'layer': 'e2e', 'title': 'mp3導線', 'given': 'mock VOICEVOX', 'when': 'E2E', 'then': 'preview承認後に章MP3を一覧表示', 'test_file': '`electron/tests/e2e/mvp-flow.test.ts`'},
    {'id': 'TC-DESKTOP-003-03', 'priority': 'P0', 'layer': 'e2e', 'title': '再起動保持', 'given': 'Project作成後アプリ再起動', 'when': '一覧', 'then': '同じProject/Job/Artifactを表示', 'test_file': '`tests/integration/test_mvp_flow.py`'},
    {'id': 'TC-DESKTOP-003-04', 'priority': 'P1', 'layer': 'integration_mock', 'title': '実IPC/DB/file/worker統合', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「実IPC/DB/file/worker統合」を実行する', 'then': '「実IPC/DB/file/worker統合」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`electron/tests/e2e/mvp-flow.test.ts`'},
    {'id': 'TC-DESKTOP-003-05', 'priority': 'P1', 'layer': 'unit', 'title': '正常導線', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「正常導線」を実行する', 'then': '「正常導線」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/integration/test_mvp_flow.py`'},
    {'id': 'TC-DESKTOP-003-06', 'priority': 'P1', 'layer': 'unit', 'title': 'worker失敗/retry', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「worker失敗/retry」を実行する', 'then': '再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。', 'test_file': '`electron/tests/e2e/mvp-flow.test.ts`'},
    {'id': 'TC-DESKTOP-003-07', 'priority': 'P1', 'layer': 'unit', 'title': '再起動後永続化', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「再起動後永続化」を実行する', 'then': '「再起動後永続化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/integration/test_mvp_flow.py`'},
    {'id': 'TC-DESKTOP-003-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`run_mvp_flow(dependencies) -> MvpFlowResult`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`electron/tests/e2e/mvp-flow.test.ts`'},
    {'id': 'TC-DESKTOP-003-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`run_mvp_flow(dependencies) -> MvpFlowResult`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/integration/test_mvp_flow.py`'},
    {'id': 'TC-DESKTOP-003-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`electron/tests/e2e/mvp-flow.test.ts`'},
    {'id': 'TC-DESKTOP-003-11', 'priority': 'P0', 'layer': 'integration_smoke', 'title': 'Desktop統合runtimeの疎通確認', 'given': '実接続テストが明示的に有効化され、必要な設定が存在する', 'when': 'アプリ起動、preload API公開、DB/worker healthまでを確認し、作品生成は行わない。', 'then': 'ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。', 'test_file': '`tests/integration/test_mvp_flow.py`'},
    {'id': 'TC-DESKTOP-003-12', 'priority': 'P1', 'layer': 'e2e', 'title': 'Desktop統合runtimeの実機能テスト', 'given': '`desktop_connectivity_gate`が成功済み', 'when': '疎通成功後、mock AI/TTSで最短MVP導線を最後まで実行する。', 'then': '最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。', 'test_file': '`electron/tests/e2e/mvp-flow.test.ts`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/integration/mvp_flow.py)")

class MvpFlowResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

def run_mvp_flow(dependencies: Any) -> MvpFlowResult:
    """Project作成からArtifactまでの縦切りをmock依存で実行する。

    Public contract: ``run_mvp_flow(dependencies) -> MvpFlowResult``.
    """
    _step4_unimplemented('run_mvp_flow')
