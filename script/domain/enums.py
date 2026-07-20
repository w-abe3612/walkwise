"""script/domain/enums.py — 公開契約: PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType.

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Spec: docs/db/01-projects-table.md, 02-sources-table.md, 03-build-requests-table.md,
docs/db/04-jobs-table.md, docs/db/05-artifacts-table.md
"""

from __future__ import annotations

from enum import Enum


class PlanningStage(str, Enum):
    REGISTERED = "registered"
    CURRICULUM_DRAFT = "curriculum_draft"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"


class SourceStatus(str, Enum):
    REGISTERED = "registered"
    PROCESSING = "processing"
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"


class BuildStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"


class ArtifactType(str, Enum):
    MP3_CHAPTER = "mp3_chapter"
    TEXT_VERIFIED_SCRIPT = "text_verified_script"
