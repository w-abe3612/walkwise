"""script/services/approvals.py — 公開契約: ApprovalService.submit/approve/request_changes/invalidate_changed_targets/assert_gate.

Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
Spec: docs/specifications/07-approval-workflow.md
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from script.core.errors import AppError, ErrorCode
from script.core.serialization import dump_yaml, load_yaml
from script.persistence.paths import ProjectPaths
from script.schemas.approvals import (
    ApprovalBundle,
    ApprovalGate,
    ApprovalRecord,
    ApprovalStatus,
    ApprovalTarget,
    can_transition_approval,
)

_APPROVALS_RELATIVE_PATH = "approvals.yaml"

# docs/specifications/07-approval-workflow.md 10節 変更種別ごとの無効化対象gate
_INVALIDATION_TABLE: dict[str, tuple[ApprovalGate, ...]] = {
    "materials_list_changed": (
        ApprovalGate.MATERIALS_CURRICULUM,
        ApprovalGate.PLANNING,
        ApprovalGate.VERIFIED_SCRIPT,
        ApprovalGate.PREVIEW_AUDIO,
    ),
    "project_plan_changed": (
        ApprovalGate.PLANNING,
        ApprovalGate.VERIFIED_SCRIPT,
        ApprovalGate.PREVIEW_AUDIO,
    ),
    "chapter_spec_changed": (ApprovalGate.VERIFIED_SCRIPT, ApprovalGate.PREVIEW_AUDIO),
    "script_text_changed": (ApprovalGate.VERIFIED_SCRIPT, ApprovalGate.PREVIEW_AUDIO),
    "tts_text_changed": (ApprovalGate.PREVIEW_AUDIO,),
    "voice_profile_changed": (ApprovalGate.PREVIEW_AUDIO,),
    "character_profile_changed": (ApprovalGate.VERIFIED_SCRIPT, ApprovalGate.PREVIEW_AUDIO),
    "tts_engine_version_changed": (ApprovalGate.PREVIEW_AUDIO,),
    "mp3_tag_only_changed": (),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ApprovalService:
    """4承認地点の遷移・差し戻し・hash変更による無効化を管理する。"""

    def __init__(self, data_root: Path) -> None:
        if not data_root:
            raise AppError(ErrorCode.VALIDATION_ERROR, "data_root is required")
        self._data_root = Path(data_root)

    def _approvals_path(self, project_id: str) -> Path:
        paths = ProjectPaths.for_root(self._data_root, project_id)
        return paths.resolve_relative(_APPROVALS_RELATIVE_PATH)

    def _load_bundle(self, project_id: str) -> ApprovalBundle:
        path = self._approvals_path(project_id)
        if not path.exists():
            return ApprovalBundle.empty(project_id)
        data = load_yaml(path)
        return ApprovalBundle.from_mapping(data)

    def _save_bundle(self, bundle: ApprovalBundle) -> None:
        path = self._approvals_path(bundle.project_id)
        dump_yaml(path, bundle.to_mapping())

    def _require_gate(self, gate) -> ApprovalGate:
        if isinstance(gate, ApprovalGate):
            return gate
        try:
            return ApprovalGate(gate)
        except ValueError as exc:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown approval gate: {gate!r}") from exc

    def _transition(self, project_id: str, gate, target_status: ApprovalStatus, **updates) -> ApprovalRecord:
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        gate = self._require_gate(gate)
        bundle = self._load_bundle(project_id)
        current = bundle.approvals[gate]

        if not can_transition_approval(current.status, target_status):
            raise AppError(
                ErrorCode.CONFLICT,
                f"illegal approval transition for gate {gate.value}: {current.status.value} -> {target_status.value}",
            )

        fields = {
            "approval_id": current.approval_id,
            "gate": gate,
            "status": target_status,
            "target": current.target,
            "approved_by": current.approved_by,
            "approved_at": current.approved_at,
            "comment": current.comment,
        }
        fields.update(updates)
        updated_record = ApprovalRecord(**fields)

        updated_bundle = bundle.with_record(gate, updated_record)
        self._save_bundle(updated_bundle)
        return updated_record

    def submit(self, project_id: str, gate, *, target: ApprovalTarget) -> ApprovalRecord:
        """draft/revisedからreview_pendingへ提出する。"""
        if target is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "target is required to submit for review")
        return self._transition(project_id, gate, ApprovalStatus.REVIEW_PENDING, target=target, comment=None)

    def approve(self, project_id: str, gate, *, approved_by: str) -> ApprovalRecord:
        """review_pendingからapprovedへ承認する。"""
        if not approved_by:
            raise AppError(ErrorCode.VALIDATION_ERROR, "approved_by is required")
        return self._transition(
            project_id,
            gate,
            ApprovalStatus.APPROVED,
            approved_by=approved_by,
            approved_at=_now_iso(),
        )

    def request_changes(self, project_id: str, gate, *, reason: str) -> ApprovalRecord:
        """review_pendingからchanges_requestedへ差し戻す(理由必須)。"""
        if not reason or not reason.strip():
            raise AppError(ErrorCode.VALIDATION_ERROR, "reason is required to request changes")
        return self._transition(project_id, gate, ApprovalStatus.CHANGES_REQUESTED, comment=reason)

    def mark_revised(self, project_id: str, gate) -> ApprovalRecord:
        """changes_requestedからrevisedへ進める。"""
        return self._transition(project_id, gate, ApprovalStatus.REVISED)

    def resubmit(self, project_id: str, gate, *, target: ApprovalTarget) -> ApprovalRecord:
        """revisedからreview_pendingへ再提出する。"""
        if target is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "target is required to resubmit for review")
        return self._transition(project_id, gate, ApprovalStatus.REVIEW_PENDING, target=target, comment=None)

    def reject(self, project_id: str, gate, *, reason: str) -> ApprovalRecord:
        """review_pendingからrejectedへ却下する。"""
        if not reason or not reason.strip():
            raise AppError(ErrorCode.VALIDATION_ERROR, "reason is required to reject")
        return self._transition(project_id, gate, ApprovalStatus.REJECTED, comment=reason)

    def invalidate_changed_targets(self, project_id: str, change_type: str) -> list[str]:
        """変更種別に応じて、approved状態のgateのみをinvalidatedへ遷移させ、無効化したgate名を返す。"""
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if change_type not in _INVALIDATION_TABLE:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown change_type: {change_type!r}")

        bundle = self._load_bundle(project_id)
        invalidated: list[str] = []
        for gate in _INVALIDATION_TABLE[change_type]:
            record = bundle.approvals[gate]
            if record.status is not ApprovalStatus.APPROVED:
                continue
            updated_record = ApprovalRecord(
                approval_id=record.approval_id,
                gate=gate,
                status=ApprovalStatus.INVALIDATED,
                target=record.target,
                approved_by=record.approved_by,
                approved_at=record.approved_at,
                comment=f"invalidated by change_type={change_type}",
            )
            bundle = bundle.with_record(gate, updated_record)
            invalidated.append(gate.value)

        if invalidated:
            self._save_bundle(bundle)
        return invalidated

    def assert_gate(self, project_id: str, gate) -> None:
        """指定gateがapproved状態でなければ、安定したerror codeで停止する。"""
        if not project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        gate = self._require_gate(gate)
        bundle = self._load_bundle(project_id)
        record = bundle.approvals[gate]
        if record.status is not ApprovalStatus.APPROVED:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"gate {gate.value} is not approved (current status: {record.status.value})",
            )

    def get_bundle(self, project_id: str) -> ApprovalBundle:
        """現在のapprovals.yaml内容を返す(存在しなければ全gate draftの初期値)。"""
        return self._load_bundle(project_id)
