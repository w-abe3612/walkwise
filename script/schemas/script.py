"""script/schemas/script.py — 公開契約: ScriptDocument/ScriptSegment/SpeakerRef.

Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
Spec: docs/specifications/05-script-segment-schema.md
"""

from __future__ import annotations

from dataclasses import dataclass, field

from script.core.errors import AppError, ErrorCode

_VALID_REVIEW_STATUSES = ("pending_review", "approved", "rejected")


@dataclass(frozen=True)
class SpeakerRef:
    """chapters/<chapter_id>/<stage>/script.yamlのspeaker相当。"""

    character_id: str
    role: str
    voice_profile_id: str | None = None

    def __post_init__(self) -> None:
        if not self.character_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "character_id is required")
        if not self.role:
            raise AppError(ErrorCode.VALIDATION_ERROR, "role is required")


@dataclass(frozen=True)
class SegmentPauses:
    """05-script-segment-schema.md 12節: 負のpauseはerror。"""

    before_ms: int = 0
    after_ms: int = 0

    def __post_init__(self) -> None:
        if self.before_ms < 0 or self.after_ms < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "pause values must not be negative")


@dataclass(frozen=True)
class GenerationProvenance:
    """初稿生成時の入力由来(prompt/input provenance)を記録する。"""

    source_chunk_ids: tuple[str, ...] = ()
    model: str | None = None
    legacy_input: bool = False
    source_path: str | None = None


@dataclass(frozen=True)
class ScriptSegment:
    """script.yamlの1segment相当。"""

    segment_id: str
    order: int
    speaker: SpeakerRef
    segment_type: str
    text: str
    tts_text: str | None = None
    claim_refs: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    pauses: SegmentPauses = field(default_factory=SegmentPauses)
    review_status: str = "pending_review"

    def __post_init__(self) -> None:
        if not self.segment_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "segment_id is required")
        if self.order < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "order must be 1 or greater")
        if self.speaker is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "speaker is required")
        if not self.segment_type:
            raise AppError(ErrorCode.VALIDATION_ERROR, "segment_type is required")
        if not self.text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")
        if self.review_status not in _VALID_REVIEW_STATUSES:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown review_status: {self.review_status}")


@dataclass(frozen=True)
class ScriptDocument:
    """chapters/<chapter_id>/<stage>/script.yaml相当。"""

    project_id: str
    chapter_id: str
    stage: str
    segments: tuple[ScriptSegment, ...]
    content_revision: int = 1
    source_revision: int = 1
    pending_claims: tuple[str, ...] = ()
    provenance: GenerationProvenance | None = None

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_id is required")
        if not self.stage:
            raise AppError(ErrorCode.VALIDATION_ERROR, "stage is required")
        if not self.segments:
            raise AppError(ErrorCode.VALIDATION_ERROR, "segments must not be empty")

        segment_ids = [segment.segment_id for segment in self.segments]
        if len(segment_ids) != len(set(segment_ids)):
            raise AppError(ErrorCode.VALIDATION_ERROR, "duplicate segment_id in ScriptDocument")

        orders = [segment.order for segment in self.segments]
        if len(orders) != len(set(orders)):
            raise AppError(ErrorCode.VALIDATION_ERROR, "duplicate order in ScriptDocument")

        for segment_id in self.pending_claims:
            if segment_id not in segment_ids:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"pending_claims references unknown segment_id: {segment_id}",
                )

    def ordered_segments(self) -> tuple[ScriptSegment, ...]:
        """orderの昇順でsegmentを返す(元の並びは保持したまま安定sort)。"""
        return tuple(sorted(self.segments, key=lambda segment: segment.order))
