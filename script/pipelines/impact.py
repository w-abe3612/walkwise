"""script/pipelines/impact.py — 公開契約: ImpactAnalyzer.analyze(change, graph) -> ImpactSet.

Contract: docs/test-cases/TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md
Spec: docs/specifications/02-process-input-output.md(14節: 再利用と部分再生成)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from script.core.errors import AppError, ErrorCode


class ChangeType(str, Enum):
    SOURCE_TEXT = "source_text"
    CURRICULUM = "curriculum"
    CHAPTER_SPEC = "chapter_spec"
    TEXT = "text"
    TTS_TEXT = "tts_text"
    CHARACTER_PROFILE = "character_profile"
    VOICE_PROFILE = "voice_profile"
    MP3_TAG = "mp3_tag"


class TargetCategory(str, Enum):
    TOPIC = "topic"
    CLAIM = "claim"
    DRAFT_SCRIPT = "draft_script"
    PROJECT_PLAN = "project_plan"
    CHAPTER_SPEC = "chapter_spec"
    NARRATION = "narration"
    SEGMENT_AUDIO = "segment_audio"
    CHAPTER_MP3 = "chapter_mp3"
    AUDIO_MANIFEST = "audio_manifest"
    MP3_PACKAGING = "mp3_packaging"


# 02-process-input-output.md 14節「再利用と部分再生成」表の型化。
_REPROCESS_TARGETS: dict[ChangeType, tuple[TargetCategory, ...]] = {
    ChangeType.SOURCE_TEXT: (TargetCategory.TOPIC, TargetCategory.CLAIM, TargetCategory.DRAFT_SCRIPT),
    ChangeType.CURRICULUM: (TargetCategory.PROJECT_PLAN, TargetCategory.CHAPTER_SPEC, TargetCategory.DRAFT_SCRIPT),
    ChangeType.CHAPTER_SPEC: (
        TargetCategory.DRAFT_SCRIPT,
        TargetCategory.NARRATION,
        TargetCategory.SEGMENT_AUDIO,
        TargetCategory.CHAPTER_MP3,
        TargetCategory.AUDIO_MANIFEST,
    ),
    ChangeType.TEXT: (TargetCategory.SEGMENT_AUDIO, TargetCategory.CHAPTER_MP3, TargetCategory.AUDIO_MANIFEST),
    ChangeType.TTS_TEXT: (TargetCategory.SEGMENT_AUDIO, TargetCategory.CHAPTER_MP3, TargetCategory.AUDIO_MANIFEST),
    ChangeType.CHARACTER_PROFILE: (
        TargetCategory.NARRATION,
        TargetCategory.SEGMENT_AUDIO,
        TargetCategory.CHAPTER_MP3,
        TargetCategory.AUDIO_MANIFEST,
    ),
    ChangeType.VOICE_PROFILE: (TargetCategory.SEGMENT_AUDIO, TargetCategory.CHAPTER_MP3, TargetCategory.AUDIO_MANIFEST),
    ChangeType.MP3_TAG: (TargetCategory.MP3_PACKAGING,),
}

# segment_id/chapter_idの指定が必須なchange_type(仕様表でsegment/章単位と明記されたもの)。
_REQUIRES_SEGMENT = frozenset({ChangeType.TEXT, ChangeType.TTS_TEXT})
_REQUIRES_CHAPTER = frozenset({ChangeType.TEXT, ChangeType.TTS_TEXT, ChangeType.CHAPTER_SPEC, ChangeType.MP3_TAG})


@dataclass(frozen=True)
class Change:
    """1件の変更(source本文、curriculum、章仕様、segment text/tts_text、profile、MP3 tag等)。"""

    change_type: ChangeType
    project_id: str
    chapter_id: str | None = None
    segment_id: str | None = None
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        if self.change_type in _REQUIRES_CHAPTER and not self.chapter_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"{self.change_type.value} change requires chapter_id")
        if self.change_type in _REQUIRES_SEGMENT and not self.segment_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"{self.change_type.value} change requires segment_id")


@dataclass(frozen=True)
class DependencyGraph:
    """作品内のchapter/segment実在集合を表す依存graphの最小表現。"""

    project_id: str
    chapter_ids: frozenset[str] = frozenset()
    segment_ids_by_chapter: Mapping[str, frozenset[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")


@dataclass(frozen=True)
class ImpactSet:
    """ImpactAnalyzer.analyze()の戻り値。"""

    project_id: str
    change_type: ChangeType
    chapter_id: str | None
    segment_id: str | None
    targets: tuple[TargetCategory, ...]
    content_hash: str


class ImpactAnalyzer:
    """変更種別と依存graphから、再処理が必要な対象categoryを決定的に導出する。"""

    def analyze(self, change: Change, graph: DependencyGraph) -> ImpactSet:
        """変更種別から再処理対象を決定する。"""
        if change is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "change is required")
        if graph is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "graph is required")
        if change.project_id != graph.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "change references a different project than graph")

        if change.chapter_id is not None and change.chapter_id not in graph.chapter_ids:
            raise AppError(ErrorCode.NOT_FOUND, f"unknown chapter_id: {change.chapter_id}")

        if change.segment_id is not None:
            known_segments = graph.segment_ids_by_chapter.get(change.chapter_id, frozenset())
            if change.segment_id not in known_segments:
                raise AppError(ErrorCode.NOT_FOUND, f"unknown segment_id: {change.segment_id}")

        targets = _REPROCESS_TARGETS[change.change_type]
        content_hash = self._compute_content_hash(change)

        return ImpactSet(
            project_id=change.project_id,
            change_type=change.change_type,
            chapter_id=change.chapter_id,
            segment_id=change.segment_id,
            targets=targets,
            content_hash=content_hash,
        )

    @staticmethod
    def _compute_content_hash(change: Change) -> str:
        payload = "|".join(
            [
                change.change_type.value,
                change.project_id,
                change.chapter_id or "",
                change.segment_id or "",
                change.detail,
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
