"""Implementation for TASK-FILE-001: ローカルファイル永続化・Project配置・atomic write.

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Production files exercised: script/persistence/files.py, script/persistence/paths.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from script.core.errors import AppError
from script.persistence.files import atomic_write_bytes
from script.persistence.paths import ProjectPaths

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_file_001_01(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-FILE-001-01 — atomic write失敗

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: 既存正常ファイルがありreplace前に例外を注入
    When: atomic_writeを実行する
    Then: 旧ファイルが完全に残り一時ファイルをcleanupする
    """
    target = tmp_path / "sources.yaml"
    target.write_bytes(b"original-content")

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr("script.persistence.files.os.replace", _boom)

    with pytest.raises(AppError):
        atomic_write_bytes(target, b"new-content", backup=False)

    assert target.read_bytes() == b"original-content"
    leftover_tmp_files = [
        entry for entry in tmp_path.iterdir()
        if entry.name.startswith(".sources.yaml.") and entry.name.endswith(".tmp")
    ]
    assert leftover_tmp_files == []


@pytest.mark.unit
def test_tc_file_001_04(tmp_path: Path) -> None:
    """TC-FILE-001-04 — 最低1世代backup

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「最低1世代backup」を実行する
    Then: 失敗前の正常状態をbackupから復旧でき、復旧対象のhashを検証する。
    """
    target = tmp_path / "manifest.json"
    atomic_write_bytes(target, b"version-1")
    v1_hash = hashlib.sha256(b"version-1").hexdigest()

    atomic_write_bytes(target, b"version-2", backup=True)

    backup_path = target.with_name(target.name + ".bak")
    assert backup_path.is_file()
    assert hashlib.sha256(backup_path.read_bytes()).hexdigest() == v1_hash
    assert target.read_bytes() == b"version-2"


@pytest.mark.unit
def test_tc_file_001_07(tmp_path: Path) -> None:
    """TC-FILE-001-07 — 必須入力欠落

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    existing_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError):
        ProjectPaths.for_root(tmp_path, "")

    with pytest.raises(AppError):
        ProjectPaths.for_root(tmp_path, "Invalid Project ID")

    assert sorted(tmp_path.iterdir()) == existing_before
