from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Iterator, Mapping, MutableMapping, Protocol, Sequence

"""STEP4 typed source scaffold for script/services/artifacts.py.

This file is the implementation contract for the related STEP2 task(s).
Public bodies intentionally raise ``NotImplementedError`` until Claude Code implements them.
Tasks: TASK-ARTIFACT-001
"""

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-ARTIFACT-001', 'ArtifactService.register(command: RegisterArtifact) -> Artifact', 'ファイル存在・hash・Job/Project整合を確認し次versionで追記する。'),
    ('TASK-ARTIFACT-001', 'ArtifactService.list_latest(project_id) -> list[Artifact]', 'artifact typeごとの最新versionを返す。'),
    ('TASK-ARTIFACT-001', 'ArtifactService.list_versions(project_id, artifact_type) -> list[Artifact]', '全versionを降順で返す。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-ARTIFACT-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': '形式別version', 'given': 'mp3 v1とtext v1がある', 'when': '双方を再登録', 'then': 'mp3 v2とtext v2として独立採番する', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'file不在', 'given': '存在しないpath', 'when': 'registerする', 'then': 'DBへ行を追加しない', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '上書き禁止', 'given': '既存Artifact fileを出力先に指定', 'when': 'registerする', 'then': '既存内容を変更せず新version/pathを要求する', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'mp3_chapter/text_verified_script', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ArtifactService.register(command: RegisterArtifact) -> Artifact`を通じて「mp3_chapter/text_verified_script」を実行する', 'then': '有効なmedia header・形式・順序を確認し、破損または形式不一致を成功扱いにしない。', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'ファイル存在/hash確認', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ArtifactService.register(command: RegisterArtifact) -> Artifact`を通じて「ファイル存在/hash確認」を実行する', 'then': '同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'Project/Job整合', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`ArtifactService.register(command: RegisterArtifact) -> Artifact`を通じて「Project/Job整合」を実行する', 'then': '「Project/Job整合」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-07', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`ArtifactService.register(command: RegisterArtifact) -> Artifact`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-08', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`ArtifactService.register(command: RegisterArtifact) -> Artifact`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_artifact_service.py`'},
    {'id': 'TC-ARTIFACT-001-09', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_artifact_service.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/services/artifacts.py)")

class Artifact:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class RegisterArtifact:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ArtifactService:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def register(self, command: RegisterArtifact) -> Artifact:
        """ファイル存在・hash・Job/Project整合を確認し次versionで追記する。

        Public contract: ``ArtifactService.register(command: RegisterArtifact) -> Artifact``.
        """
        _step4_unimplemented('ArtifactService.register')
    def list_latest(self, project_id: Any) -> list[Artifact]:
        """artifact typeごとの最新versionを返す。

        Public contract: ``ArtifactService.list_latest(project_id) -> list[Artifact]``.
        """
        _step4_unimplemented('ArtifactService.list_latest')
    def list_versions(self, project_id: Any, artifact_type: Any) -> list[Artifact]:
        """全versionを降順で返す。

        Public contract: ``ArtifactService.list_versions(project_id, artifact_type) -> list[Artifact]``.
        """
        _step4_unimplemented('ArtifactService.list_versions')
