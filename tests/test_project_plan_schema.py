"""Implementation for TASK-PROJECT-001: Project作成・一覧・取得サービス (plan schema).

Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
Production files exercised: script/schemas/project_plan.py, script/services/projects.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError, ErrorCode
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository
from script.schemas.project_plan import ProjectPlan
from script.services.projects import CreateProject, ProjectService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"

_MINIMAL_VALID_PLAN: dict = {
    "schema_version": "1.0",
    "project_id": "database-foundations",
    "content_revision": 1,
    "title": "データベース基礎",
    "domain": "database",
    "purpose": "purpose",
    "usage_purpose": "personal_learning",
    "planning_stage": "registered",
    "target_audience": {"description": "d"},
    "difficulty": {"vocabulary_level": "elementary_4", "conceptual_level": "adult_beginner"},
    "scope": {"included_topics": [], "excluded_topics": []},
    "source_strategy": ["hybrid_reconstruction"],
    "source_policy": {"unsupported_claim_policy": "block"},
    "narration": {"mode": "single_speaker_per_chapter"},
    "approval_policy": {"required": []},
}


@pytest.mark.integration_mock
def test_tc_project_001_02(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-PROJECT-001-02 — DB失敗cleanup

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P0
    Layer: integration_mock
    Given: file作成後のDB insertを失敗させる
    When: createする
    Then: 不完全Projectを一覧へ出さずcleanup/rollbackする
    """
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    service = ProjectService(tmp_path, connection)

    def _boom(self: ProjectRepository, project: object) -> None:
        raise AppError(ErrorCode.INTERNAL_ERROR, "simulated DB failure")

    monkeypatch.setattr(ProjectRepository, "insert", _boom)

    with pytest.raises(AppError):
        service.create(
            CreateProject(
                project_id="database-foundations", title="データベース基礎", domain="database", purpose="p",
            )
        )

    plan_path = tmp_path / "library" / "database-foundations" / "project" / "project-plan.yaml"
    assert not plan_path.exists()

    monkeypatch.undo()
    assert ProjectRepository(connection).list_all() == []


@pytest.mark.unit
def test_tc_project_001_04() -> None:
    """TC-PROJECT-001-04 — 入力validation

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ProjectPlan.from_mapping()/to_mapping()/validate()`を通じて「入力validation」を実行する
    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    """
    plan = ProjectPlan.from_mapping(_MINIMAL_VALID_PLAN)
    assert plan.to_mapping()["project_id"] == "database-foundations"

    invalid_stage = dict(_MINIMAL_VALID_PLAN, planning_stage="not_a_real_stage")
    with pytest.raises(AppError):
        ProjectPlan.from_mapping(invalid_stage)

    invalid_strategy = dict(_MINIMAL_VALID_PLAN, source_strategy=["not_a_real_strategy"])
    with pytest.raises(AppError):
        ProjectPlan.from_mapping(invalid_strategy)

    review_pending_without_chapters = dict(_MINIMAL_VALID_PLAN, planning_stage="review_pending", chapters=[])
    with pytest.raises(AppError):
        ProjectPlan.from_mapping(review_pending_without_chapters)


@pytest.mark.unit
def test_tc_project_001_06() -> None:
    """TC-PROJECT-001-06 — 再実行時の決定性

    Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ProjectPlan.from_mapping()/to_mapping()/validate()`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    first = ProjectPlan.from_mapping(_MINIMAL_VALID_PLAN)
    second = ProjectPlan.from_mapping(_MINIMAL_VALID_PLAN)
    assert first.to_mapping() == second.to_mapping()
    first.validate()
    first.validate()
