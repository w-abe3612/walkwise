"""script/schemas/project_plan.py — 公開契約: ProjectPlan.from_mapping/to_mapping/validate.

Contract: docs/test-cases/TASK-PROJECT-001-project-application-service.md
Spec: docs/specifications/03-project-plan-schema.md
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from script.core.errors import AppError, ErrorCode

_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "schema_version", "project_id", "content_revision", "title", "domain", "purpose",
    "usage_purpose", "planning_stage", "target_audience", "difficulty", "scope",
    "source_strategy", "source_policy", "narration", "approval_policy",
)
_VALID_PLANNING_STAGES = {"registered", "curriculum_draft", "review_pending", "approved"}
_VALID_SOURCE_STRATEGIES = {"open_fulltext", "hybrid_reconstruction", "licensed_reference"}
_REQUIRED_APPROVAL_STAGES = {"materials_curriculum", "planning", "verified_script", "preview_audio"}
_STAGES_REQUIRING_CHAPTERS = {"review_pending", "approved"}


@dataclass(frozen=True)
class ProjectPlan:
    """企画書YAML(project-plan.yaml)の必須項目とplanning stage規則を検証する。"""

    data: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "ProjectPlan":
        plan = cls(data=dict(mapping))
        plan.validate()
        return plan

    def to_mapping(self) -> dict[str, Any]:
        return dict(self.data)

    def validate(self) -> None:
        missing = [key for key in _REQUIRED_TOP_LEVEL_KEYS if key not in self.data]
        if missing:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"missing required project-plan fields: {missing}")

        planning_stage = self.data["planning_stage"]
        if planning_stage not in _VALID_PLANNING_STAGES:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown planning_stage: {planning_stage!r}")

        content_revision = self.data["content_revision"]
        if not isinstance(content_revision, int) or content_revision < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_revision must be an integer >= 1")

        source_strategy = self.data["source_strategy"]
        if not source_strategy:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_strategy must not be empty")
        unknown_strategies = [value for value in source_strategy if value not in _VALID_SOURCE_STRATEGIES]
        if unknown_strategies:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown source_strategy value(s): {unknown_strategies}")

        if planning_stage in _STAGES_REQUIRING_CHAPTERS:
            if not self.data.get("chapters"):
                raise AppError(ErrorCode.VALIDATION_ERROR, f"{planning_stage} requires at least one chapter")
            if not self.data.get("learning_outcomes"):
                raise AppError(ErrorCode.VALIDATION_ERROR, f"{planning_stage} requires learning_outcomes")
            required_approvals = set(self.data.get("approval_policy", {}).get("required", []))
            if not _REQUIRED_APPROVAL_STAGES.issubset(required_approvals):
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"{planning_stage} requires all 4 approval stages: {sorted(_REQUIRED_APPROVAL_STAGES)}",
                )
