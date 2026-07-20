"""Implementation for TASK-PROJECT-001: Project作成・一覧・取得サービス (service).

Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
Production files exercised: script/services/projects.py, script/schemas/project_plan.py
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.core.serialization import load_yaml
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository
from script.schemas.project_plan import ProjectPlan
from script.services.projects import CreateProject, ProjectService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _service(tmp_path: Path, name: str = "app.db") -> ProjectService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    return ProjectService(tmp_path, connection)


@pytest.mark.integration_mock
def test_tc_project_001_01(tmp_path: Path) -> None:
    """TC-PROJECT-001-01 — Project作成atomicity

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: integration_mock
    Given: 有効入力
    When: createする
    Then: plan fileとDB行が同じproject_id/revisionで作成される
    """
    service = _service(tmp_path)
    project = service.create(
        CreateProject(
            project_id="database-foundations",
            title="データベース基礎",
            domain="database",
            purpose="データベースの基本を学べるようにする",
        )
    )

    plan_path = tmp_path / "library" / "database-foundations" / "project" / "project-plan.yaml"
    assert plan_path.is_file()
    plan_data = load_yaml(plan_path)
    assert plan_data["project_id"] == project.project_id == "database-foundations"
    assert plan_data["content_revision"] == project.content_revision == 1

    stored = service.get("database-foundations")
    assert stored == project


@pytest.mark.unit
def test_tc_project_001_03(tmp_path: Path) -> None:
    """TC-PROJECT-001-03 — archive除外

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: unit
    Given: activeとarchived Projectがある
    When: list_activeする
    Then: activeだけを返す
    """
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    service = ProjectService(tmp_path, connection)

    active = service.create(
        CreateProject(
            project_id="active-project", title="Active", domain="database", purpose="p",
        )
    )
    archived = service.create(
        CreateProject(
            project_id="archived-project", title="Archived", domain="database", purpose="p",
        )
    )

    repository = ProjectRepository(connection)
    now = datetime.now(timezone.utc).isoformat()
    repository.update(dataclasses.replace(archived, archived_at=now, updated_at=now))
    connection.commit()

    result = service.list_active()
    assert [project.project_id for project in result] == ["active-project"]
    assert active in result


@pytest.mark.unit
def test_tc_project_001_05(tmp_path: Path) -> None:
    """TC-PROJECT-001-05 — 必須入力欠落

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ProjectPlan.from_mapping()/to_mapping()/validate()`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    existing_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError):
        ProjectPlan.from_mapping({"schema_version": "1.0"})  # missing most required keys

    service = _service(tmp_path, name="app2.db")
    with pytest.raises(AppError):
        service.create(CreateProject(project_id="", title="", domain="database", purpose="p"))

    remaining = [p for p in sorted(tmp_path.iterdir()) if p.name != "app2.db"]
    assert remaining == existing_before


@pytest.mark.unit
def test_tc_project_001_07(tmp_path: Path) -> None:
    """TC-PROJECT-001-07 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    service = _service(tmp_path)
    service.create(
        CreateProject(project_id="database-foundations", title="タイトル", domain="database", purpose="p")
    )
    plan_path = tmp_path / "library" / "database-foundations" / "project" / "project-plan.yaml"
    content_before = plan_path.read_bytes()

    with pytest.raises(AppError):
        service.create(
            CreateProject(project_id="database-foundations", title="別タイトル", domain="database", purpose="p")
        )  # duplicate PK -> AppError, must not corrupt the existing plan file

    assert plan_path.read_bytes() == content_before
