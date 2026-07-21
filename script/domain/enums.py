"""script/domain/enums.py — 公開契約: PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType/
VoiceProfileRecordStatus.

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Spec: docs/db/01-projects-table.md, 02-sources-table.md, 03-build-requests-table.md,
docs/db/04-jobs-table.md, docs/db/05-artifacts-table.md, docs/db/06-voice-profiles-table.md
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


class VoiceProfileRecordStatus(str, Enum):
    """`voice_profiles`テーブル(DB正本、TASK-BUILD-EXEC-001)専用の状態。

    `script/schemas/profiles.py`の`VoiceProfileStatus`(YAML時代の6値:
    provisional/approved/approved_for_limited_use/on_hold/rejected/deprecated)とは
    別concept。DB正本化にあたり、承認済み設計(TASK-BUILD-EXEC-001 5.1節)で
    draft/approved/archivedの3値のみと明確に定義された。
    """

    DRAFT = "draft"
    APPROVED = "approved"
    ARCHIVED = "archived"
