"""script/pipelines/draft_generation.py — 公開契約:
DraftGenerationPipeline.generate(chapter_spec, chunks) -> ScriptDocument,
segment_legacy_text(text) -> ScriptDocument.

Contract: docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md
Spec: docs/specifications/05-script-segment-schema.md, docs/specifications/04-chapter-generation-schema.md
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from script.ai_clients.base import AIClient, AIRequest
from script.core.errors import AppError, ErrorCode
from script.schemas.chapter_spec import ChapterSpec
from script.schemas.script import GenerationProvenance, ScriptDocument, ScriptSegment, SpeakerRef

_STANDARD_MODEL_HINT = "gemini-2.5-flash"
_DEFAULT_SEGMENT_TYPE = "explanation"
_SOURCE_REFS_PREFIX = "SOURCE_REFS:"
_TEXT_PREFIX = "TEXT:"

_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")


@dataclass(frozen=True)
class DraftChunkInput:
    """DraftGenerationPipelineへの1 chunk分の入力。"""

    chunk_id: str
    source_id: str
    text: str

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chunk_id is required")
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")
        if not self.text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")


def _parse_ai_segment_response(raw_text: str) -> tuple[tuple[str, ...], str]:
    """AI応答から`SOURCE_REFS:`/`TEXT:`の2行形式を決定的に取り出す。"""
    source_refs: tuple[str, ...] = ()
    text_lines: list[str] = []
    in_text = False

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not in_text and stripped.startswith(_SOURCE_REFS_PREFIX):
            raw_refs = stripped[len(_SOURCE_REFS_PREFIX):]
            source_refs = tuple(part.strip() for part in raw_refs.split(",") if part.strip())
        elif stripped.startswith(_TEXT_PREFIX):
            in_text = True
            remainder = stripped[len(_TEXT_PREFIX):].strip()
            if remainder:
                text_lines.append(remainder)
        elif in_text:
            text_lines.append(line)

    text = "\n".join(text_lines).strip()
    if not text:
        raise AppError(ErrorCode.VALIDATION_ERROR, "AI response did not include TEXT content")
    return source_refs, text


class DraftGenerationPipeline:
    """章仕様が許可するchunkだけをAIへ渡し、章初稿(review未承認)を生成する。"""

    def __init__(self, *, ai_client: AIClient, model: str = _STANDARD_MODEL_HINT) -> None:
        if ai_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "ai_client is required")
        if not model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")
        self._ai_client = ai_client
        self._model = model

    def generate(self, chapter_spec: ChapterSpec, chunks: Sequence[DraftChunkInput]) -> ScriptDocument:
        """指定資料chunkから章初稿を生成しprovenanceを記録する。"""
        if chapter_spec is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapter_spec is required")
        if not chunks:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chunks must not be empty")

        allowed_source_ids = frozenset(chapter_spec.source_ids)
        # 許可されたsource_idのchunkだけを本文に含める(指定外資料を混入させない)。
        allowed_chunks = [chunk for chunk in chunks if chunk.source_id in allowed_source_ids]
        if not allowed_chunks:
            raise AppError(ErrorCode.VALIDATION_ERROR, "no chunks match chapter_spec.source_ids")

        segments: list[ScriptSegment] = []
        pending_claims: list[str] = []

        for order, chunk in enumerate(allowed_chunks, start=1):
            request = AIRequest(
                user_text=chunk.text,
                system_instruction=(
                    "Draft one narration segment for this material. Respond in exactly this "
                    "format:\nSOURCE_REFS: <comma-separated source ids you drew from>\n"
                    "TEXT: <segment text>"
                ),
                model=self._model,
            )
            result = self._ai_client.generate(request)
            source_refs, text = _parse_ai_segment_response(result.text)
            if not source_refs:
                source_refs = (chunk.source_id,)

            segment_id = f"{chapter_spec.chapter_id}-seg{order:03d}"
            out_of_scope = [ref for ref in source_refs if ref not in allowed_source_ids]
            if out_of_scope:
                # 指定外資料の事実を含む場合、黙って承認せずpending claimとして記録する。
                pending_claims.append(segment_id)

            segments.append(
                ScriptSegment(
                    segment_id=segment_id,
                    order=order,
                    speaker=SpeakerRef(character_id="neutral-explainer", role="explainer"),
                    segment_type=_DEFAULT_SEGMENT_TYPE,
                    text=text,
                    source_refs=source_refs,
                    review_status="pending_review",
                )
            )

        return ScriptDocument(
            project_id=chapter_spec.project_id,
            chapter_id=chapter_spec.chapter_id,
            stage="draft",
            segments=tuple(segments),
            pending_claims=tuple(pending_claims),
            provenance=GenerationProvenance(
                source_chunk_ids=tuple(chunk.chunk_id for chunk in allowed_chunks),
                model=self._model,
            ),
        )


def segment_legacy_text(
    text: str,
    *,
    project_id: str = "legacy",
    chapter_id: str = "legacy-chapter",
    source_path: str | None = None,
) -> ScriptDocument:
    """旧TXTを段落単位で決定的にsegment化し未承認扱いにする。"""
    if not text:
        raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")

    paragraphs = [paragraph.strip() for paragraph in _PARAGRAPH_SPLIT_RE.split(text) if paragraph.strip()]
    if not paragraphs:
        raise AppError(ErrorCode.VALIDATION_ERROR, "text must contain at least one non-empty paragraph")

    segments = tuple(
        ScriptSegment(
            segment_id=f"{chapter_id}-seg{order:03d}",
            order=order,
            speaker=SpeakerRef(character_id="legacy-narrator", role="narrator"),
            segment_type=_DEFAULT_SEGMENT_TYPE,
            text=paragraph,
            review_status="pending_review",
        )
        for order, paragraph in enumerate(paragraphs, start=1)
    )

    return ScriptDocument(
        project_id=project_id,
        chapter_id=chapter_id,
        stage="draft",
        segments=segments,
        provenance=GenerationProvenance(legacy_input=True, source_path=source_path),
    )
