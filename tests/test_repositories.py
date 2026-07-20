"""Implementation for TASK-DB-002: Repository・transaction境界 (repositories).

Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
Production files exercised: script/persistence/repositories.py, script/persistence/unit_of_work.py
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import BuildStatus, PlanningStage, SourceStatus
from script.domain.models import BuildRequest, Project, Source
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository, SourceRepository, map_integrity_error
from script.persistence.unit_of_work import SqliteUnitOfWork

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _migrated_connection(tmp_path: Path, name: str = "app.db") -> sqlite3.Connection:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    return connection


def _sample_project(project_id: str = "database-foundations") -> Project:
    now = "2026-07-19T21:00:00+09:00"
    return Project(
        project_id=project_id,
        title="データベース基礎",
        domain="database",
        planning_stage=PlanningStage.REGISTERED,
        content_revision=1,
        plan_file_path="project/project-plan.yaml",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.integration_mock
def test_tc_db_002_01(tmp_path: Path) -> None:
    """TC-DB-002-01 — transaction rollback

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: integration_mock
    Given: 2つ目の書込みでconstraint errorを発生
    When: UnitOfWorkを終了する
    Then: 1つ目を含め全変更がrollbackされる
    """
    connection = _migrated_connection(tmp_path)

    with pytest.raises(AppError):
        with SqliteUnitOfWork(connection) as uow:
            uow.projects.insert(_sample_project())
            uow.sources.insert(
                Source(
                    source_id="src-1",
                    project_id="does-not-exist",  # FK violation
                    media_type="text",
                    status=SourceStatus.REGISTERED,
                    original_file_path="sources/originals/src-1.txt",
                    content_hash="sha256:x",
                    created_at="2026-07-19T21:00:00+09:00",
                    updated_at="2026-07-19T21:00:00+09:00",
                )
            )

    fresh_reader = SqliteUnitOfWork(connection)
    assert fresh_reader.projects.list_all() == []


@pytest.mark.unit
def test_tc_db_002_03(tmp_path: Path) -> None:
    """TC-DB-002-03 — Project/Source/BuildRequest/Job/Artifact repository契約

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「Project/Source/BuildRequest/Job/Artifact repository契約」を実行する
    Then: 「Project/Source/BuildRequest/Job/Artifact repository契約」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    connection = _migrated_connection(tmp_path)
    uow = SqliteUnitOfWork(connection)

    uow.projects.insert(_sample_project())
    uow.build_requests.insert(
        BuildRequest(
            build_request_id="br-0001",
            project_id="database-foundations",
            output_formats=("text",),
            status=BuildStatus.DRAFT,
            created_at="2026-07-19T21:00:00+09:00",
            updated_at="2026-07-19T21:00:00+09:00",
        )
    )
    uow.commit()

    found_project = uow.projects.find("database-foundations")
    assert found_project is not None
    assert found_project.title == "データベース基礎"

    found_build_request = uow.build_requests.find("br-0001")
    assert found_build_request is not None
    assert found_build_request.output_formats == ("text",)

    assert uow.sources.find("does-not-exist") is None


@pytest.mark.unit
def test_tc_db_002_05(tmp_path: Path) -> None:
    """TC-DB-002-05 — FK/constraint例外変換

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「FK/constraint例外変換」を実行する
    Then: 「FK/constraint例外変換」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    connection = _migrated_connection(tmp_path)
    project_repo = ProjectRepository(connection)
    source_repo = SourceRepository(connection)

    project_repo.insert(_sample_project())
    connection.commit()

    with pytest.raises(AppError):
        project_repo.insert(_sample_project())  # duplicate PK -> unique violation

    with pytest.raises(AppError):
        source_repo.insert(
            Source(
                source_id="src-2",
                project_id="does-not-exist",
                media_type="text",
                status=SourceStatus.REGISTERED,
                original_file_path="sources/originals/src-2.txt",
                content_hash="sha256:y",
                created_at="2026-07-19T21:00:00+09:00",
                updated_at="2026-07-19T21:00:00+09:00",
            )
        )

    direct_error = sqlite3.IntegrityError("FOREIGN KEY constraint failed")
    assert map_integrity_error(direct_error).code.value == "validation_error"


@pytest.mark.unit
def test_tc_db_002_07(tmp_path: Path) -> None:
    """TC-DB-002-07 — 再実行時の決定性

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    connection = _migrated_connection(tmp_path)
    project_repo = ProjectRepository(connection)
    project_repo.insert(_sample_project())
    connection.commit()

    first = project_repo.find("database-foundations")
    second = project_repo.find("database-foundations")
    assert first == second
