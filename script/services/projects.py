"""script/services/projects.py — 公開契約: ProjectService.create/list_active/get.

Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
Spec: docs/screens/01-project-list-and-create.md, docs/db/01-projects-table.md
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from script.core.errors import AppError, ErrorCode
from script.core.serialization import dump_yaml
from script.domain.enums import PlanningStage
from script.domain.models import Project
from script.persistence.paths import ProjectPaths
from script.persistence.repositories import ProjectRepository
from script.persistence.unit_of_work import SqliteUnitOfWork
from script.schemas.project_plan import ProjectPlan

_PLAN_RELATIVE_PATH = "project/project-plan.yaml"


@dataclass(frozen=True)
class CreateProject:
    """Project作成の入力。"""

    project_id: str
    title: str
    domain: str
    purpose: str
    usage_purpose: str = "personal_learning"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_plan_mapping(command: CreateProject) -> dict:
    return {
        "schema_version": "1.0",
        "project_id": command.project_id,
        "content_revision": 1,
        "title": command.title,
        "domain": command.domain,
        "purpose": command.purpose,
        "usage_purpose": command.usage_purpose,
        "planning_stage": "registered",
        "target_audience": {"description": ""},
        "difficulty": {"vocabulary_level": "elementary_4", "conceptual_level": "adult_beginner"},
        "scope": {"included_topics": [], "excluded_topics": []},
        "source_strategy": ["hybrid_reconstruction"],
        "chapters": [],
        "source_policy": {
            "technical_claims_require_sources": True,
            "ai_general_knowledge_allowed_for_ideation": True,
            "ai_generated_analogies_allowed": True,
            "unsupported_claim_policy": "block",
        },
        "narration": {
            "mode": "single_speaker_per_chapter",
            "multi_speaker_schema_supported": True,
            "voice_selection_status": "pending",
            "default_character_id": None,
            "default_voice_profile_id": None,
        },
        "approval_policy": {
            "required": ["materials_curriculum", "planning", "verified_script", "preview_audio"],
        },
    }


class ProjectService:
    """Project root、project-plan.yaml、DB行を一transactionで作成・一覧・取得する。"""

    def __init__(self, data_root: Path, connection: sqlite3.Connection) -> None:
        if not data_root or connection is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root and connection are required")
        self._data_root = Path(data_root)
        self._connection = connection

    def create(self, command: CreateProject) -> Project:
        """Project root、project-plan.yaml、DB行を一transactionで作成する。"""
        if command is None or not command.project_id or not command.title:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id and title are required")

        if ProjectRepository(self._connection).find(command.project_id) is not None:
            raise AppError(ErrorCode.CONFLICT, f"project already exists: {command.project_id}")

        paths = ProjectPaths.for_root(self._data_root, command.project_id)
        plan = ProjectPlan.from_mapping(_default_plan_mapping(command))

        plan_file_path = paths.resolve_relative(_PLAN_RELATIVE_PATH)
        dump_yaml(plan_file_path, plan.to_mapping())

        now = _now_iso()
        project = Project(
            project_id=command.project_id,
            title=command.title,
            domain=command.domain,
            planning_stage=PlanningStage.REGISTERED,
            content_revision=1,
            plan_file_path=_PLAN_RELATIVE_PATH,
            created_at=now,
            updated_at=now,
        )

        try:
            with SqliteUnitOfWork(self._connection) as uow:
                uow.projects.insert(project)
        except AppError:
            if plan_file_path.exists():
                plan_file_path.unlink()
            raise

        return project

    def list_active(self) -> list[Project]:
        """archive済みを除き安定順で返す。"""
        repository = ProjectRepository(self._connection)
        return [project for project in repository.list_all() if project.archived_at is None]

    def get(self, project_id: str) -> Project:
        """存在しないIDはnot_foundへ変換する。"""
        repository = ProjectRepository(self._connection)
        project = repository.find(project_id)
        if project is None:
            raise AppError(ErrorCode.NOT_FOUND, f"project not found: {project_id}")
        return project
