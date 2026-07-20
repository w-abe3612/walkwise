"""script/schemas/approvals.py — 公開契約: ApprovalBundle/ApprovalRecord/ChangeRequest.

Contract: docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md
Spec: docs/specifications/07-approval-workflow.md
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.core.hashing import canonical_sha256


class ApprovalGate(str, Enum):
    MATERIALS_CURRICULUM = "materials_curriculum"
    PLANNING = "planning"
    VERIFIED_SCRIPT = "verified_script"
    PREVIEW_AUDIO = "preview_audio"


class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REVISED = "revised"
    REJECTED = "rejected"
    INVALIDATED = "invalidated"


# docs/specifications/07-approval-workflow.md 4節 基本遷移
_TRANSITIONS: dict[ApprovalStatus, frozenset[ApprovalStatus]] = {
    ApprovalStatus.DRAFT: frozenset({ApprovalStatus.REVIEW_PENDING}),
    ApprovalStatus.REVIEW_PENDING: frozenset(
        {ApprovalStatus.APPROVED, ApprovalStatus.CHANGES_REQUESTED, ApprovalStatus.REJECTED}
    ),
    ApprovalStatus.CHANGES_REQUESTED: frozenset({ApprovalStatus.REVISED}),
    ApprovalStatus.REVISED: frozenset({ApprovalStatus.REVIEW_PENDING}),
    ApprovalStatus.APPROVED: frozenset({ApprovalStatus.INVALIDATED}),
    ApprovalStatus.REJECTED: frozenset(),
    ApprovalStatus.INVALIDATED: frozenset(),
}


def can_transition_approval(current: ApprovalStatus, target: ApprovalStatus) -> bool:
    if current is None or target is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "current and target are required")
    return target in _TRANSITIONS.get(current, frozenset())


def compute_bundle_hash(paths: Sequence[str], file_hashes: Sequence[str]) -> str:
    """対象パス・各ファイルhash・順序をcanonical化してbundle hashを計算する。"""
    if not paths or len(paths) != len(file_hashes):
        raise AppError(ErrorCode.VALIDATION_ERROR, "paths and file_hashes must be equal-length and non-empty")
    return canonical_sha256({"paths": list(paths), "file_hashes": list(file_hashes)})


@dataclass(frozen=True)
class ApprovalTarget:
    """承認対象(単一fileまたはbundle)。"""

    paths: tuple[str, ...]
    content_hash: str

    def __post_init__(self) -> None:
        if not self.paths:
            raise AppError(ErrorCode.VALIDATION_ERROR, "target paths must not be empty")
        if not self.content_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "target content_hash is required")


@dataclass(frozen=True)
class ApprovalRecord:
    """4承認地点のうち1件の状態。"""

    approval_id: str
    gate: ApprovalGate
    status: ApprovalStatus
    target: ApprovalTarget | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    comment: str | None = None

    def __post_init__(self) -> None:
        if not self.approval_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "approval_id is required")
        if self.status is ApprovalStatus.APPROVED and (
            self.target is None or not self.approved_by or not self.approved_at
        ):
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "approved status requires target, approved_by and approved_at",
            )


@dataclass(frozen=True)
class ChangeRequest:
    """差し戻し(change request)。"""

    request_id: str
    gate: ApprovalGate
    category: str
    severity: str
    comment: str
    status: str = "open"

    def __post_init__(self) -> None:
        if not self.request_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request_id is required")
        if not self.comment or not self.comment.strip():
            raise AppError(ErrorCode.VALIDATION_ERROR, "change request comment is required")


def _default_record(gate: ApprovalGate) -> ApprovalRecord:
    return ApprovalRecord(approval_id=f"approval-{gate.value}-draft", gate=gate, status=ApprovalStatus.DRAFT)


@dataclass(frozen=True)
class ApprovalBundle:
    """project/approvals.yamlの内容(4承認地点)。"""

    project_id: str
    content_revision: int
    approvals: Mapping[ApprovalGate, ApprovalRecord]

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        missing = [gate for gate in ApprovalGate if gate not in self.approvals]
        if missing:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"missing required approval gate(s): {[gate.value for gate in missing]}",
            )

    @classmethod
    def empty(cls, project_id: str, content_revision: int = 1) -> "ApprovalBundle":
        return cls(
            project_id=project_id,
            content_revision=content_revision,
            approvals={gate: _default_record(gate) for gate in ApprovalGate},
        )

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "ApprovalBundle":
        if not mapping or "project_id" not in mapping:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")

        approvals_data = mapping.get("approvals", {})
        approvals: dict[ApprovalGate, ApprovalRecord] = {}
        for gate in ApprovalGate:
            entry = approvals_data.get(gate.value)
            if not entry:
                approvals[gate] = _default_record(gate)
                continue
            target_data = entry.get("target")
            target = (
                ApprovalTarget(paths=tuple(target_data["paths"]), content_hash=target_data["content_hash"])
                if target_data
                else None
            )
            approvals[gate] = ApprovalRecord(
                approval_id=entry["approval_id"],
                gate=gate,
                status=ApprovalStatus(entry["status"]),
                target=target,
                approved_by=entry.get("approved_by"),
                approved_at=entry.get("approved_at"),
                comment=entry.get("comment"),
            )

        return cls(
            project_id=mapping["project_id"],
            content_revision=mapping.get("content_revision", 1),
            approvals=approvals,
        )

    def to_mapping(self) -> dict[str, Any]:
        approvals_mapping: dict[str, Any] = {}
        for gate, record in self.approvals.items():
            entry: dict[str, Any] = {
                "approval_id": record.approval_id,
                "status": record.status.value,
                "approved_by": record.approved_by,
                "approved_at": record.approved_at,
                "comment": record.comment,
            }
            if record.target is not None:
                entry["target"] = {"paths": list(record.target.paths), "content_hash": record.target.content_hash}
            approvals_mapping[gate.value] = entry

        return {
            "schema_version": "1.0",
            "project_id": self.project_id,
            "content_revision": self.content_revision,
            "approvals": approvals_mapping,
        }

    def with_record(self, gate: ApprovalGate, record: ApprovalRecord) -> "ApprovalBundle":
        updated = dict(self.approvals)
        updated[gate] = record
        return ApprovalBundle(project_id=self.project_id, content_revision=self.content_revision, approvals=updated)
