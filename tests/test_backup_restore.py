"""Test suite for TASK-RELEASE-001: Windows package・runtime同梱・license/privacy/backup.

Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
Cases in this file: TC-RELEASE-001-02, 05, 08, 11.
"""

from __future__ import annotations

import hashlib

import pytest

from script.core.errors import AppError, ErrorCode
from script.maintenance.backup import create_backup, restore_backup, verify_backup

pytestmark = pytest.mark.mvp


@pytest.mark.integration_mock
def test_tc_release_001_02(tmp_path) -> None:
    """TC-RELEASE-001-02 — backup restore: DB+filesをbackupし一部破損させても、hash整合した状態へ復旧する。"""
    data_root = tmp_path / "data_root"
    (data_root / "projects" / "sample-book").mkdir(parents=True)
    (data_root / "app.db").write_bytes(b"fake-sqlite-bytes")
    (data_root / "projects" / "sample-book" / "book.json").write_text('{"bookId": "book-1"}', encoding="utf-8")

    backup_destination = tmp_path / "backups"
    manifest = create_backup(data_root, backup_destination)
    backup_dir = backup_destination / manifest.generation_id

    # backup済みfileの1件だけを破損させる(復旧元の一部破損)。
    corrupted_file = backup_dir / "files" / "app.db"
    corrupted_file.write_bytes(b"CORRUPTED")

    verification = verify_backup(backup_dir)
    assert "app.db" in verification.corrupted_files
    assert "projects/sample-book/book.json" in verification.valid_files
    assert verification.all_valid is False

    restore_destination = tmp_path / "restored"
    result = restore_backup(backup_dir, restore_destination)

    assert "app.db" not in result.restored_files
    assert "projects/sample-book/book.json" in result.restored_files
    assert result.corrupted_files == ("app.db",)
    assert result.fully_restored is False

    restored_book_json = restore_destination / "projects" / "sample-book" / "book.json"
    assert restored_book_json.exists()
    original_hash = hashlib.sha256(
        (data_root / "projects" / "sample-book" / "book.json").read_bytes()
    ).hexdigest()
    restored_hash = hashlib.sha256(restored_book_json.read_bytes()).hexdigest()
    assert original_hash == restored_hash
    assert not (restore_destination / "app.db").exists()


@pytest.mark.unit
def test_tc_release_001_05(tmp_path) -> None:
    """TC-RELEASE-001-05 — Python worker bundling strategy: backupは指定data_root配下だけを対象にし、
    アプリのinstall先/bundled runtimeディレクトリ(利用者データ領域の外)には一切触れない
    (17-local-data-persistence-policy.md 5.7節: 利用者データはinstall先へ保存しない)。
    """
    install_dir = tmp_path / "install"
    (install_dir / "runtime" / "python").mkdir(parents=True)
    (install_dir / "runtime" / "python" / "python.exe").write_bytes(b"fake-bundled-python")
    (install_dir / "Walkwise.exe").write_bytes(b"fake-executable")

    data_root = tmp_path / "userdata"
    data_root.mkdir()
    (data_root / "app.db").write_bytes(b"fake-sqlite-bytes")

    backup_destination = tmp_path / "backups"
    manifest = create_backup(data_root, backup_destination)

    assert set(manifest.file_hashes.keys()) == {"app.db"}
    backup_dir = backup_destination / manifest.generation_id
    assert not (backup_dir / "files" / "runtime").exists()
    assert not (backup_dir / "files" / "Walkwise.exe").exists()
    # install先(bundled runtime)は元のまま残っている。
    assert (install_dir / "runtime" / "python" / "python.exe").exists()


@pytest.mark.unit
def test_tc_release_001_08(tmp_path) -> None:
    """TC-RELEASE-001-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as exc_info:
        create_backup(None, tmp_path / "backups")
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert not (tmp_path / "backups").exists()

    data_root = tmp_path / "data_root"
    data_root.mkdir()
    (data_root / "app.db").write_bytes(b"x")
    with pytest.raises(AppError) as exc_info:
        create_backup(data_root, None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        create_backup(tmp_path / "does-not-exist", tmp_path / "backups")
    assert exc_info.value.code is ErrorCode.NOT_FOUND
    assert not (tmp_path / "backups").exists()

    with pytest.raises(AppError) as exc_info:
        verify_backup(None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        restore_backup(tmp_path / "does-not-exist-backup", tmp_path / "restored")
    assert exc_info.value.code is ErrorCode.NOT_FOUND
    assert not (tmp_path / "restored").exists()


@pytest.mark.integration_smoke
def test_tc_release_001_11(release_runtime_connectivity_gate) -> None:
    """TC-RELEASE-001-11 — 配布runtime群の疎通確認

    Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: package内のPython、ffmpeg、ffprobe、Tesseractについてversion取得だけを順番に行う。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert release_runtime_connectivity_gate["available"] is True
    assert release_runtime_connectivity_gate["versions"]
