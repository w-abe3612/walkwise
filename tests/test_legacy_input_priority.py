"""Test suite for TASK-MIGRATION-001: 旧形式・既存client互換adapter.

Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
Cases in this file: TC-MIGRATION-001-02, 04, 06, 08, 10.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from script.core.errors import AppError, ErrorCode
from script.migration.adapters import migrate_legacy_project
from script.migration.legacy_models import LegacyBook, LegacySection

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_migration_001_02(tmp_path) -> None:
    """TC-MIGRATION-001-02 — full_book正規化: 旧unit_id=full_bookをbookへ変換しprovenanceを記録する。"""
    source = tmp_path / "legacy_project"
    source.mkdir(parents=True)
    (source / "book.json").write_text(json.dumps({"bookId": "book-1", "title": "Book One"}), encoding="utf-8")
    destination = tmp_path / "dest"

    result = migrate_legacy_project(source, destination)

    assert len(result.chapters) == 1
    assert result.chapters[0]["chapter_id"] == "book"
    assert any("full_book" in note for note in result.report["conversions"])
    normalization_entries = [
        entry
        for entry in result.report["provenance"]
        if entry.get("legacy_unit_id") == "full_book"
    ]
    assert normalization_entries
    assert normalization_entries[0]["normalized_unit_id"] == "book"


@pytest.mark.unit
def test_tc_migration_001_04() -> None:
    """TC-MIGRATION-001-04 — bookId/project_id: LegacyBookはbookIdをproject_idへ決定的に写像する。"""
    book = LegacyBook(bookId="physics-101", title="Physics 101")

    assert book.project_id == "physics-101"
    assert book.title == "Physics 101"
    # 再実行しても同じ論理結果(決定的)。
    assert LegacyBook(bookId="physics-101").project_id == book.project_id

    with pytest.raises(AppError) as exc_info:
        LegacyBook(title="missing id")
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_migration_001_06(tmp_path) -> None:
    """TC-MIGRATION-001-06 — approval.yaml/approvals.yaml: 承認済みだけ後工程へ進み、それ以外は安定errorで停止する。"""
    source = tmp_path / "legacy_project"
    project_dir = source / "project"
    project_dir.mkdir(parents=True)
    (source / "book.json").write_text(json.dumps({"bookId": "book-1"}), encoding="utf-8")
    destination = tmp_path / "dest"

    for unapproved_status in ("changes_requested", "invalidated", "pending"):
        (project_dir / "approval.yaml").write_text(f"status: {unapproved_status}\n", encoding="utf-8")
        with pytest.raises(AppError) as exc_info:
            migrate_legacy_project(source, destination)
        assert exc_info.value.code is ErrorCode.PERMISSION_DENIED
        assert not (destination / "migration-report.json").exists()

    (project_dir / "approval.yaml").write_text("status: approved\n", encoding="utf-8")
    result = migrate_legacy_project(source, destination)

    assert result.skipped is False
    assert (destination / "migration-report.json").exists()
    assert any("approval" in note for note in result.report["conversions"])


@pytest.mark.unit
def test_tc_migration_001_08(tmp_path) -> None:
    """TC-MIGRATION-001-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    destination = tmp_path / "dest"

    with pytest.raises(AppError) as exc_info:
        migrate_legacy_project(None, destination)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert not destination.exists()

    source = tmp_path / "legacy_project"
    source.mkdir(parents=True)
    (source / "book.json").write_text(json.dumps({"bookId": "book-1"}), encoding="utf-8")
    with pytest.raises(AppError) as exc_info:
        migrate_legacy_project(source, None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert not destination.exists()

    with pytest.raises(AppError) as exc_info:
        LegacyBook()
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        LegacySection()
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_migration_001_10(tmp_path) -> None:
    """TC-MIGRATION-001-10 — 入力・既存成果物の不変性: 入力と既存正常成果物のbyte/hashが変化しない。"""
    source = tmp_path / "legacy_project"
    source.mkdir(parents=True)
    book_path = source / "book.json"
    book_path.write_text(json.dumps({"bookId": "book-1"}), encoding="utf-8")
    destination = tmp_path / "dest"

    before_hash = hashlib.sha256(book_path.read_bytes()).hexdigest()
    migrate_legacy_project(source, destination)
    after_hash = hashlib.sha256(book_path.read_bytes()).hexdigest()
    assert before_hash == after_hash

    report_path = destination / "migration-report.json"
    successful_report_bytes = report_path.read_bytes()

    project_dir = source / "project"
    project_dir.mkdir()
    (project_dir / "approval.yaml").write_text("status: invalidated\n", encoding="utf-8")
    with pytest.raises(AppError):
        migrate_legacy_project(source, destination)

    # 意図的な失敗の後も、既存の正常成果物は変更されない。
    assert report_path.read_bytes() == successful_report_bytes
    assert hashlib.sha256(book_path.read_bytes()).hexdigest() == before_hash
