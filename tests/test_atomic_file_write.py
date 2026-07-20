"""Implementation for TASK-FILE-001: ローカルファイル永続化・Project配置・atomic write.

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Production files exercised: script/persistence/locking.py, script/persistence/files.py,
script/persistence/paths.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from script.core.errors import AppError
from script.persistence.files import copy_immutable
from script.persistence.locking import ProjectLock
from script.persistence.paths import ProjectPaths

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_file_001_02(tmp_path: Path) -> None:
    """TC-FILE-001-02 — lock競合

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: 同じProject lockを保持中
    When: 2つ目のlockを取得する
    Then: 競合errorとなり既存lockを壊さない
    """
    project_root = tmp_path / "project-a"
    with ProjectLock.acquire(project_root):
        lock_file = project_root / ".project.lock"
        assert lock_file.is_file()
        content_before = lock_file.read_bytes()

        with pytest.raises(AppError):
            with ProjectLock.acquire(project_root):
                pass

        assert lock_file.is_file()
        assert lock_file.read_bytes() == content_before


@pytest.mark.unit
def test_tc_file_001_05(tmp_path: Path) -> None:
    """TC-FILE-001-05 — 入力原本のimmutable保存

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「入力原本のimmutable保存」を実行する
    Then: 処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。
    """
    source = tmp_path / "original.jpg"
    source.write_bytes(b"raw-image-bytes")
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    destination = tmp_path / "preserved" / "original-000001.jpg"
    digest = copy_immutable(source, destination)

    assert source.read_bytes() == b"raw-image-bytes"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
    assert destination.is_file()
    assert digest.algorithm == "sha256"
    assert digest.value == original_hash


@pytest.mark.unit
def test_tc_file_001_08(tmp_path: Path) -> None:
    """TC-FILE-001-08 — 再実行時の決定性

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    first = ProjectPaths.for_root(tmp_path, "database-foundations")
    second = ProjectPaths.for_root(tmp_path, "database-foundations")
    assert first == second
    assert first.project_root == second.project_root
