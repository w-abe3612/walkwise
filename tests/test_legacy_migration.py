"""Test suite for TASK-MIGRATION-001: 旧形式・既存client互換adapter.

Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
Cases in this file: TC-MIGRATION-001-01, 03, 05, 07, 09.
"""

from __future__ import annotations

import json

import pytest

from script.core.errors import AppError, ErrorCode
from script.migration.adapters import migrate_legacy_project
from script.migration.legacy_models import LegacyAudioInput, LegacySection

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_migration_001_01(tmp_path) -> None:
    """TC-MIGRATION-001-01 — 新形式優先: 新旧両形式があるとき新形式を採用し旧形式を上書きしない。"""
    source = tmp_path / "legacy_project"
    (source / "project").mkdir(parents=True)
    (source / "project" / "project-plan.yaml").write_text("title: already migrated\n", encoding="utf-8")
    book_path = source / "book.json"
    book_path.write_text(json.dumps({"bookId": "old-book"}), encoding="utf-8")
    destination = tmp_path / "dest"

    before = book_path.read_bytes()
    result = migrate_legacy_project(source, destination)
    after = book_path.read_bytes()

    assert result.skipped is True
    assert result.reason == "new_format_present"
    assert result.chapters == ()
    assert not destination.exists()
    assert before == after


@pytest.mark.unit
def test_tc_migration_001_03(tmp_path) -> None:
    """TC-MIGRATION-001-03 — 不明項目: 変換不能fieldを推測せずwarning/reportへ残す。"""
    source = tmp_path / "legacy_project"
    source.mkdir(parents=True)
    (source / "book.json").write_text(
        json.dumps({"bookId": "book-1", "unknownLegacyFlag": True, "obsoleteSetting": "x"}),
        encoding="utf-8",
    )
    destination = tmp_path / "dest"

    result = migrate_legacy_project(source, destination)

    unmigrated_fields = {item["field"] for item in result.report["unmigrated"]}
    assert unmigrated_fields == {"unknownLegacyFlag", "obsoleteSetting"}
    assert any("unknownLegacyFlag" in warning for warning in result.report["warnings"])
    assert any("obsoleteSetting" in warning for warning in result.report["warnings"])


@pytest.mark.unit
def test_tc_migration_001_05() -> None:
    """TC-MIGRATION-001-05 — sectionId/chapter_id: sectionIdまたはfileNameを互換chapter IDとして扱う。"""
    with_section_id = LegacySection(sectionId="intro", order=1, fileTitle="Intro")
    assert with_section_id.chapter_id == "intro"

    fallback_to_file_name = LegacySection(fileName="chapter02.txt", order=2)
    assert fallback_to_file_name.chapter_id == "chapter02.txt"

    with pytest.raises(AppError) as exc_info:
        LegacySection(order=3)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_migration_001_07() -> None:
    """TC-MIGRATION-001-07 — legacy text priority: 優先順位に従い最初に存在する旧テキストを解決する。"""
    available = {"text/merged/book/fixed.txt", "text/merged/book/merged.txt"}
    audio_input = LegacyAudioInput(unit_id="full_book", exists=lambda relative: relative in available)

    resolved = audio_input.resolve()

    assert resolved["source_path"] == "text/merged/book/fixed.txt"
    assert resolved["legacy_input"] is True

    lowest_priority_only = {"text/merged/book/merged.txt"}
    fallback_input = LegacyAudioInput(unit_id="book", exists=lambda relative: relative in lowest_priority_only)
    fallback_resolved = fallback_input.resolve()
    assert fallback_resolved["source_path"] == "text/merged/book/merged.txt"

    with pytest.raises(AppError) as exc_info:
        LegacyAudioInput(unit_id="book", exists=lambda relative: False).resolve()
    assert exc_info.value.code is ErrorCode.NOT_FOUND


@pytest.mark.unit
def test_tc_migration_001_09(tmp_path) -> None:
    """TC-MIGRATION-001-09 — 再実行時の決定性: 同一入力の2回実行は同じ論理結果・同一成果物を返す。"""
    source = tmp_path / "legacy_project"
    source.mkdir(parents=True)
    (source / "book.json").write_text(json.dumps({"bookId": "book-1"}), encoding="utf-8")
    destination = tmp_path / "dest"
    fixed_clock = lambda: "2026-07-19T00:00:00+00:00"

    first = migrate_legacy_project(source, destination, clock=fixed_clock)
    first_bytes = (destination / "migration-report.json").read_bytes()

    second = migrate_legacy_project(source, destination, clock=fixed_clock)
    second_bytes = (destination / "migration-report.json").read_bytes()

    assert first.project_id == second.project_id
    assert first.chapters == second.chapters
    assert first_bytes == second_bytes
    assert list(destination.iterdir()) == [destination / "migration-report.json"]
