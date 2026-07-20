"""Implementation for TASK-DB-002: Repository・transaction境界 (unit of work).

Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
Production files exercised: script/persistence/unit_of_work.py, script/persistence/repositories.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import ArtifactType, BuildStatus, JobStatus, PlanningStage
from script.domain.models import Artifact, BuildRequest, Job, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.unit_of_work import SqliteUnitOfWork

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _migrated_uow(tmp_path: Path, name: str = "app.db") -> SqliteUnitOfWork:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    return SqliteUnitOfWork(connection)


def _seed_project_build_job(uow: SqliteUnitOfWork) -> None:
    now = "2026-07-19T21:00:00+09:00"
    uow.projects.insert(
        Project(
            project_id="database-foundations",
            title="データベース基礎",
            domain="database",
            planning_stage=PlanningStage.REGISTERED,
            content_revision=1,
            plan_file_path="project/project-plan.yaml",
            created_at=now,
            updated_at=now,
        )
    )
    uow.build_requests.insert(
        BuildRequest(
            build_request_id="br-0001",
            project_id="database-foundations",
            output_formats=("text",),
            status=BuildStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
    )
    uow.jobs.insert(
        Job(job_id="job-0001", build_request_id="br-0001", job_type="tts", status=JobStatus.QUEUED)
    )
    uow.commit()


@pytest.mark.unit
def test_tc_db_002_02(tmp_path: Path) -> None:
    """TC-DB-002-02 — Artifact追記専用

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: unit
    Given: 既存Artifactをupdateしようとする
    When: Repository APIを呼ぶ
    Then: 操作を拒否し既存行を変更しない
    """
    uow = _migrated_uow(tmp_path)
    _seed_project_build_job(uow)

    artifact = Artifact(
        artifact_id="artifact-0001",
        job_id="job-0001",
        project_id="database-foundations",
        artifact_type=ArtifactType.MP3_CHAPTER,
        file_path="audio/chapters/01_ch01.mp3",
        version_number=1,
        content_hash="sha256:abc",
        created_at="2026-07-19T21:10:00+09:00",
    )
    uow.artifacts.insert(artifact)
    uow.commit()

    with pytest.raises(AppError):
        uow.artifacts.update(artifact)

    stored = uow.artifacts.find("artifact-0001")
    assert stored == artifact


@pytest.mark.unit
def test_tc_db_002_04(tmp_path: Path) -> None:
    """TC-DB-002-04 — insert/find/list/updateの許可範囲

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を通じて「insert/find/list/updateの許可範囲」を実行する
    Then: 必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。
    """
    uow = _migrated_uow(tmp_path)

    assert uow.projects.list_all() == []

    now = "2026-07-19T21:00:00+09:00"
    uow.projects.insert(
        Project(
            project_id="b-project",
            title="B",
            domain="database",
            planning_stage=PlanningStage.REGISTERED,
            content_revision=1,
            plan_file_path="project/project-plan.yaml",
            created_at=now,
            updated_at=now,
        )
    )
    uow.projects.insert(
        Project(
            project_id="a-project",
            title="A",
            domain="database",
            planning_stage=PlanningStage.REGISTERED,
            content_revision=1,
            plan_file_path="project/project-plan.yaml",
            created_at=now,
            updated_at=now,
        )
    )
    uow.commit()

    listed = uow.projects.list_all()
    assert [project.project_id for project in listed] == ["a-project", "b-project"]

    updated = uow.projects.find("a-project")
    assert updated is not None
    uow.projects.update(
        Project(
            project_id="a-project",
            title="A (updated)",
            domain="database",
            planning_stage=PlanningStage.CURRICULUM_DRAFT,
            content_revision=2,
            plan_file_path="project/project-plan.yaml",
            created_at=now,
            updated_at="2026-07-19T22:00:00+09:00",
        )
    )
    uow.commit()
    reloaded = uow.projects.find("a-project")
    assert reloaded is not None
    assert reloaded.title == "A (updated)"
    assert reloaded.content_revision == 2


@pytest.mark.unit
def test_tc_db_002_06(tmp_path: Path) -> None:
    """TC-DB-002-06 — 必須入力欠落

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ProjectRepository/SourceRepository/BuildRequestRepository/JobRepository/ArtifactRepository`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    existing_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError):
        SqliteUnitOfWork(None)  # type: ignore[arg-type]

    assert sorted(tmp_path.iterdir()) == existing_before

    uow = _migrated_uow(tmp_path)
    with pytest.raises(AppError):
        uow.projects.find(None)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_db_002_08(tmp_path: Path) -> None:
    """TC-DB-002-08 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    uow = _migrated_uow(tmp_path)
    _seed_project_build_job(uow)

    artifact = Artifact(
        artifact_id="artifact-0002",
        job_id="job-0001",
        project_id="database-foundations",
        artifact_type=ArtifactType.MP3_CHAPTER,
        file_path="audio/chapters/01_ch01.mp3",
        version_number=1,
        content_hash="sha256:stable",
        created_at="2026-07-19T21:10:00+09:00",
    )
    uow.artifacts.insert(artifact)
    uow.commit()

    with pytest.raises(AppError):
        uow.artifacts.update(artifact)

    unchanged = uow.artifacts.find("artifact-0002")
    assert unchanged == artifact
