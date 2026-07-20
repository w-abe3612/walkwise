"""Implementation for TASK-FILE-001: ローカルファイル永続化・Project配置・atomic write.

Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
Production files exercised: script/persistence/paths.py, script/persistence/files.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.core.errors import AppError
from script.persistence.files import atomic_write_bytes
from script.persistence.paths import ProjectPaths

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_file_001_03(tmp_path: Path) -> None:
    """TC-FILE-001-03 — root escape拒否

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: `../outside`を含む相対候補
    When: Project pathを解決する
    Then: Project root外を拒否する
    """
    paths = ProjectPaths.for_root(tmp_path, "database-foundations")

    resolved = paths.resolve_relative("sources/manifests/database-book-image.yaml")
    assert resolved.is_relative_to(paths.project_root.resolve())

    with pytest.raises(AppError):
        paths.resolve_relative("../outside/secret.yaml")

    with pytest.raises(AppError):
        paths.resolve_relative("../../etc/passwd")


@pytest.mark.integration_mock
def test_tc_file_001_06(tmp_path: Path) -> None:
    """TC-FILE-001-06 — 絶対パスのDB保存禁止

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPaths.for_root(data_root: Path, project_id: str) -> ProjectPaths`を通じて「絶対パスのDB保存禁止」を実行する
    Then: 保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。
    """
    paths = ProjectPaths.for_root(tmp_path, "database-foundations")

    within_root = paths.project_root / "sources" / "manifests" / "book.yaml"
    stored_value = paths.to_relative_str(within_root)
    assert stored_value == "sources/manifests/book.yaml"
    assert not Path(stored_value).is_absolute()

    outside_root = tmp_path / "outside" / "book.yaml"
    with pytest.raises(AppError):
        paths.to_relative_str(outside_root)


@pytest.mark.unit
def test_tc_file_001_09(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-FILE-001-09 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    target = tmp_path / "approvals.yaml"
    atomic_write_bytes(target, b"approved-state")
    digest_before = target.read_bytes()

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated failure")

    monkeypatch.setattr("script.persistence.files.os.replace", _boom)
    with pytest.raises(AppError):
        atomic_write_bytes(target, b"attempted-change", backup=False)
    monkeypatch.undo()

    assert target.read_bytes() == digest_before

    atomic_write_bytes(target, b"new-approved-state", backup=True)
    assert target.read_bytes() == b"new-approved-state"
    backup_path = target.with_name(target.name + ".bak")
    assert backup_path.read_bytes() == digest_before
