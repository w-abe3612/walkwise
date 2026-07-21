"""Tests for TASK-BUILD-EXEC-001 §8-9: chapter順序解決とverified script検証。

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(8, 9, 14.3節)
Production file exercised: script/services/build_target_resolution.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.core.serialization import dump_yaml, load_yaml
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.schemas.approvals import ApprovalGate, ApprovalTarget
from script.services.build_target_resolution import (
    ChapterOrderEntry,
    resolve_build_target,
    resolve_chapter_order,
)
from script.services.approvals import ApprovalService
from script.services.projects import CreateProject, ProjectService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _make_project(data_root: Path, db_path: Path, project_id: str = "proj-1"):
    connection = connect_database(db_path)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    service = ProjectService(data_root, connection)
    service.create(CreateProject(project_id=project_id, title="テストProject", domain="test", purpose="p"))
    return connection


def _set_plan_chapters(data_root: Path, project_id: str, chapters: list[dict]) -> None:
    plan_path = data_root / "library" / project_id / "project" / "project-plan.yaml"
    plan = load_yaml(plan_path)
    plan["chapters"] = chapters
    plan["planning_stage"] = "registered"
    dump_yaml(plan_path, plan)


def _write_verified_script(data_root: Path, project_id: str, chapter_id: str, *, document_chapter_id: str | None = None) -> None:
    script_path = data_root / "library" / project_id / "chapters" / chapter_id / "verified" / "script.yaml"
    dump_yaml(
        script_path,
        {
            "schema_version": "1.0",
            "chapter_id": document_chapter_id if document_chapter_id is not None else chapter_id,
            "segments": [
                {"segment_id": "segment-01", "order": 1, "text": "本文1", "tts_text": "音声1", "claim_ids": []},
                {"segment_id": "segment-02", "order": 2, "text": "本文2", "tts_text": "音声2", "claim_ids": []},
            ],
        },
    )


def _approve_verified_script_gate(data_root: Path, project_id: str) -> None:
    approvals = ApprovalService(data_root)
    target = ApprovalTarget(paths=("chapters/ch01/verified/script.yaml",), content_hash="dummy-hash")
    approvals.submit(project_id, ApprovalGate.VERIFIED_SCRIPT, target=target)
    approvals.approve(project_id, ApprovalGate.VERIFIED_SCRIPT, approved_by="tester")


@pytest.mark.unit
def test_tc_build_target_001_01_order_follows_plan_not_folder_name(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-01 — chapter順序はproject-plan.yamlのorderに従い、folder名の文字列順ではない。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(
        data_root, "proj-1",
        [
            {"chapter_id": "ch-zeta", "order": 1, "title": "第1章"},
            {"chapter_id": "ch-alpha", "order": 2, "title": "第2章"},
        ],
    )

    entries = resolve_chapter_order(data_root, connection, "proj-1")
    assert entries == (
        ChapterOrderEntry(chapter_id="ch-zeta", order=1, title="第1章"),
        ChapterOrderEntry(chapter_id="ch-alpha", order=2, title="第2章"),
    )


@pytest.mark.unit
def test_tc_build_target_001_02_no_chapters_rejected(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-02 — chaptersが空のProjectはbuild_target_not_readyで拒否される。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")

    with pytest.raises(AppError, match="build_target_not_ready"):
        resolve_chapter_order(data_root, connection, "proj-1")


@pytest.mark.unit
def test_tc_build_target_001_03_duplicate_chapter_id_rejected(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-03 — 重複するchapter_idはbuild_target_not_readyで拒否される。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(
        data_root, "proj-1",
        [{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch01", "order": 2}],
    )

    with pytest.raises(AppError, match="build_target_not_ready"):
        resolve_chapter_order(data_root, connection, "proj-1")


@pytest.mark.unit
def test_tc_build_target_001_04_duplicate_order_rejected(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-04 — 重複するorderはbuild_target_not_readyで拒否される。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(
        data_root, "proj-1",
        [{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 1}],
    )

    with pytest.raises(AppError, match="build_target_not_ready"):
        resolve_chapter_order(data_root, connection, "proj-1")


@pytest.mark.unit
def test_tc_build_target_001_05_fully_ready_project(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-05 — 全chapterが検証済み・承認済みならis_readyはTrueになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(
        data_root, "proj-1",
        [{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 2}],
    )
    _write_verified_script(data_root, "proj-1", "ch01")
    _write_verified_script(data_root, "proj-1", "ch02")
    _approve_verified_script_gate(data_root, "proj-1")

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert resolution.is_ready
    assert [chapter.chapter_id for chapter in resolution.chapters] == ["ch01", "ch02"]
    assert resolution.errors == ()
    assert all(chapter.content_hash for chapter in resolution.chapters)


@pytest.mark.unit
def test_tc_build_target_001_06_missing_chapter_directory(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-06 — chapterのdirectory自体が存在しない場合はchapter_not_foundになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(data_root, "proj-1", [{"chapter_id": "ch01", "order": 1}])
    _approve_verified_script_gate(data_root, "proj-1")

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert not resolution.is_ready
    assert len(resolution.errors) == 1
    assert resolution.errors[0].chapter_id == "ch01"
    assert resolution.errors[0].error_code == "chapter_not_found"


@pytest.mark.unit
def test_tc_build_target_001_07_missing_verified_script(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-07 — chapter directoryはあるがverified/script.yamlがない場合はverified_script_not_foundになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(data_root, "proj-1", [{"chapter_id": "ch01", "order": 1}])
    (data_root / "library" / "proj-1" / "chapters" / "ch01" / "draft").mkdir(parents=True)
    _approve_verified_script_gate(data_root, "proj-1")

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert not resolution.is_ready
    assert resolution.errors[0].error_code == "verified_script_not_found"


@pytest.mark.unit
def test_tc_build_target_001_08_chapter_id_mismatch_is_invalid(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-08 — script.yaml内のchapter_idが対象chapterと一致しない場合はverified_script_invalidになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(data_root, "proj-1", [{"chapter_id": "ch01", "order": 1}])
    _write_verified_script(data_root, "proj-1", "ch01", document_chapter_id="ch-wrong")
    _approve_verified_script_gate(data_root, "proj-1")

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert not resolution.is_ready
    assert resolution.errors[0].error_code == "verified_script_invalid"
    assert "mismatch" in resolution.errors[0].detail


@pytest.mark.unit
def test_tc_build_target_001_09_empty_segments_is_invalid(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-09 — segmentsが空のscript.yamlはverified_script_invalidになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(data_root, "proj-1", [{"chapter_id": "ch01", "order": 1}])
    script_path = data_root / "library" / "proj-1" / "chapters" / "ch01" / "verified" / "script.yaml"
    dump_yaml(script_path, {"schema_version": "1.0", "chapter_id": "ch01", "segments": []})
    _approve_verified_script_gate(data_root, "proj-1")

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert not resolution.is_ready
    assert resolution.errors[0].error_code == "verified_script_invalid"


@pytest.mark.unit
def test_tc_build_target_001_10_gate_not_approved_rejects_all_chapters(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-10 — verified_script gateが未承認なら、全chapterがverified_script_not_approvedになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(
        data_root, "proj-1",
        [{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 2}],
    )
    _write_verified_script(data_root, "proj-1", "ch01")
    _write_verified_script(data_root, "proj-1", "ch02")
    # 承認を行わない(draftのまま)。

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert not resolution.is_ready
    assert [error.error_code for error in resolution.errors] == ["verified_script_not_approved", "verified_script_not_approved"]
    assert resolution.chapters == ()


@pytest.mark.unit
def test_tc_build_target_001_11_one_bad_chapter_rejects_whole_job_with_full_diagnostics(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-11 — 1chapterでも問題があれば全体が拒否され、正常chapterの情報も併せて分かる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")
    _set_plan_chapters(
        data_root, "proj-1",
        [{"chapter_id": "ch01", "order": 1}, {"chapter_id": "ch02", "order": 2}],
    )
    _write_verified_script(data_root, "proj-1", "ch01")
    # ch02は意図的にverified scriptを用意しない。
    _approve_verified_script_gate(data_root, "proj-1")

    resolution = resolve_build_target(data_root, connection, "proj-1")
    assert not resolution.is_ready
    assert [chapter.chapter_id for chapter in resolution.chapters] == ["ch01"]
    assert len(resolution.errors) == 1
    assert resolution.errors[0].chapter_id == "ch02"
    assert resolution.errors[0].error_code == "chapter_not_found"


@pytest.mark.unit
def test_tc_build_target_001_12_project_not_found(tmp_path: Path) -> None:
    """TC-BUILD-TARGET-001-12 — 存在しないProjectはnot_foundになる。"""
    data_root = tmp_path / "data"
    connection = _make_project(data_root, tmp_path / "app.db")

    with pytest.raises(AppError):
        resolve_chapter_order(data_root, connection, "does-not-exist")
