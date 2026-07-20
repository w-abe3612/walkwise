"""script/pipelines/regeneration.py — 公開契約:
RegenerationPlanner.plan(impact_set, cache_state) -> RegenerationPlan,
RegenerationPlan.validate_no_unrelated_targets().

Contract: docs/test-cases/TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md
Spec: docs/specifications/02-process-input-output.md, docs/specifications/07-approval-workflow.md
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from script.core.errors import AppError, ErrorCode
from script.pipelines.impact import ImpactSet, TargetCategory

# 07-approval-workflow.md 2節の4承認地点へ、再生成対象categoryを対応付ける。
# MP3_PACKAGING(MP3タグのみ変更)は「原則として維持」(10節)であり承認gate対象外。
_TARGET_TO_APPROVAL_POINT: dict[TargetCategory, str] = {
    TargetCategory.TOPIC: "materials_curriculum",
    TargetCategory.CLAIM: "materials_curriculum",
    TargetCategory.PROJECT_PLAN: "planning",
    TargetCategory.CHAPTER_SPEC: "planning",
    TargetCategory.DRAFT_SCRIPT: "verified_script",
    TargetCategory.NARRATION: "verified_script",
    TargetCategory.SEGMENT_AUDIO: "preview_audio",
    TargetCategory.CHAPTER_MP3: "preview_audio",
    TargetCategory.AUDIO_MANIFEST: "preview_audio",
}

_APPROVED_STATUS = "approved"


@dataclass(frozen=True)
class CacheState:
    """既存成果物の承認状態とhashの現況。"""

    approvals: Mapping[str, str]
    existing_artifact_hashes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.approvals is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "approvals is required")


@dataclass(frozen=True)
class RegenerationStep:
    """1つの再生成対象categoryに対する処理単位。"""

    target: TargetCategory
    scope: str
    reason: str


@dataclass(frozen=True)
class RegenerationPlan:
    """RegenerationPlanner.plan()の戻り値。"""

    impact_set: ImpactSet
    steps: tuple[RegenerationStep, ...]

    def __post_init__(self) -> None:
        if self.impact_set is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "impact_set is required")
        if not self.steps:
            raise AppError(ErrorCode.VALIDATION_ERROR, "steps must not be empty")

    def validate_no_unrelated_targets(self) -> None:
        """impact_setが宣言した対象category以外を、無関係成果物として再生成しない。"""
        allowed = set(self.impact_set.targets)
        unrelated = [step for step in self.steps if step.target not in allowed]
        if unrelated:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"plan contains unrelated targets: {[step.target.value for step in unrelated]}",
            )


class RegenerationPlanner:
    """impact_setと既存cache状態から、承認gateを尊重した再生成計画を作る。"""

    def plan(self, impact_set: ImpactSet, cache_state: CacheState) -> RegenerationPlan:
        """segment/章/manifest単位の再生成順を作る。"""
        if impact_set is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "impact_set is required")
        if cache_state is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "cache_state is required")

        required_points = sorted(
            {
                _TARGET_TO_APPROVAL_POINT[target]
                for target in impact_set.targets
                if target in _TARGET_TO_APPROVAL_POINT
            }
        )
        for point in required_points:
            status = cache_state.approvals.get(point)
            if status != _APPROVED_STATUS:
                raise AppError(
                    ErrorCode.PERMISSION_DENIED,
                    f"regeneration blocked: {point} is not approved (status={status!r})",
                )

        scope = self._resolve_scope(impact_set)
        steps = tuple(
            RegenerationStep(target=target, scope=scope, reason=impact_set.change_type.value)
            for target in impact_set.targets
        )
        return RegenerationPlan(impact_set=impact_set, steps=steps)

    @staticmethod
    def _resolve_scope(impact_set: ImpactSet) -> str:
        if impact_set.segment_id is not None:
            return f"segment:{impact_set.segment_id}"
        if impact_set.chapter_id is not None:
            return f"chapter:{impact_set.chapter_id}"
        return f"project:{impact_set.project_id}"
