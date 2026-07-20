"""script/pipelines/narration.py — 公開契約:
NarrationPipeline.simplify/adapt_for_audio/apply_character,
build_verified_script(...) -> ScriptDocument.

Contract: docs/test-cases/TASK-NARRATION-001-narration-transformations-and-verified-script.md
Spec: docs/specifications/05-script-segment-schema.md, docs/specifications/06-claims-and-sources.md,
      docs/specifications/07-approval-workflow.md, docs/specifications/08-character-profile-schema.md
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence

from script.ai.routing import AIRouter, ModelPolicy
from script.ai_clients.base import AIClient, AIRequest
from script.core.errors import AppError, ErrorCode
from script.pipelines.claims import assert_script_claims_publishable
from script.pipelines.semantic_review import SemanticReview, SemanticReviewStatus
from script.profiles.characters import CharacterProfileRepository
from script.schemas.claims import Claim
from script.schemas.script import ScriptDocument, ScriptSegment

_STANDARD_MODEL_HINT = "gemini-2.5-flash"
_TEXT_PREFIX = "TEXT:"


def _parse_text_response(raw_text: str) -> str:
    """AI応答から`TEXT:`形式で本文を決定的に取り出す。"""
    text_lines: list[str] = []
    in_text = False
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(_TEXT_PREFIX):
            in_text = True
            remainder = stripped[len(_TEXT_PREFIX):].strip()
            if remainder:
                text_lines.append(remainder)
        elif in_text:
            text_lines.append(line)

    text = "\n".join(text_lines).strip()
    if not text:
        raise AppError(ErrorCode.VALIDATION_ERROR, "AI response did not include TEXT content")
    return text


class NarrationPipeline:
    """draft scriptをsimplified/audio-adapted/character-styledの各段階へ独立に変換する。"""

    def __init__(self, *, ai_client: AIClient, model: str = _STANDARD_MODEL_HINT) -> None:
        if ai_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "ai_client is required")
        if not model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")
        self._ai_client = ai_client
        self._model = model

    def simplify(self, script: ScriptDocument) -> ScriptDocument:
        """分かりやすさのためtextを書き換えた新しいScriptDocumentを生成する。"""
        if script is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script is required")

        segments = tuple(self._simplify_segment(segment) for segment in script.segments)
        return dataclasses.replace(script, stage="simplified", segments=segments)

    def _simplify_segment(self, segment: ScriptSegment) -> ScriptSegment:
        request = AIRequest(
            user_text=segment.text,
            system_instruction=(
                "Rewrite this narration segment for clarity without changing its technical "
                "meaning, numbers, or conditions. Respond as:\nTEXT: <rewritten text>"
            ),
            model=self._model,
        )
        result = self._ai_client.generate(request)
        new_text = _parse_text_response(result.text)
        return dataclasses.replace(segment, text=new_text)

    def adapt_for_audio(self, script: ScriptDocument) -> ScriptDocument:
        """textを変更せず、tts_textだけを発音向けに調整した新しいScriptDocumentを生成する。"""
        if script is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script is required")

        segments = tuple(self._adapt_segment(segment) for segment in script.segments)
        return dataclasses.replace(script, stage="audio_adapted", segments=segments)

    def _adapt_segment(self, segment: ScriptSegment) -> ScriptSegment:
        request = AIRequest(
            user_text=segment.text,
            system_instruction=(
                "Adjust pronunciation, symbols, and reading of numbers/acronyms for "
                "text-to-speech only. Do not change the meaning. Respond as:\n"
                "TEXT: <tts reading>"
            ),
            model=self._model,
        )
        result = self._ai_client.generate(request)
        tts_text = _parse_text_response(result.text)
        # textはこの段階の対象外(tts_textのみ発音調整)。
        return dataclasses.replace(segment, tts_text=tts_text)

    def apply_character(
        self,
        script: ScriptDocument,
        *,
        character_repository: CharacterProfileRepository,
        character_id: str | None = None,
    ) -> ScriptDocument:
        """character_idをengineの識別子から解決し、speakerへ反映する(textは変更しない)。"""
        if script is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script is required")
        if character_repository is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "character_repository is required")

        if character_id is None:
            # 中立原稿として扱う(局所disable): speakerもtextも変更しない。
            return dataclasses.replace(script, stage="character_styled")

        try:
            character_repository.select(character_id)
        except AppError as exc:
            if exc.code is ErrorCode.NOT_FOUND:
                raise AppError(
                    ErrorCode.NOT_FOUND,
                    f"speaker_not_found: {character_id}",
                    technical_detail=str(exc),
                ) from exc
            raise

        segments = tuple(
            dataclasses.replace(segment, speaker=dataclasses.replace(segment.speaker, character_id=character_id))
            for segment in script.segments
        )
        return dataclasses.replace(script, stage="character_styled", segments=segments)


def build_verified_script(
    *,
    transformed_script: ScriptDocument,
    source_script: ScriptDocument,
    claims: Sequence[Claim],
    router: AIRouter,
    model_policy: ModelPolicy,
) -> ScriptDocument:
    """fact checkとsemantic review通過後だけ、stage="verified"の候補を作る。"""
    if transformed_script is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "transformed_script is required")
    if source_script is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "source_script is required")
    if claims is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "claims is required")
    if router is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "router is required")
    if model_policy is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "model_policy is required")

    # 未検証claim block: 本番工程を汚す前に安定したerrorで停止する。
    assert_script_claims_publishable(source_script, claims)

    # semantic review: 変換前後で意味差がないか確認する。
    review_result = SemanticReview().compare(source_script, transformed_script)
    if review_result.status is not SemanticReviewStatus.PASS:
        raise AppError(
            ErrorCode.CONFLICT,
            f"semantic review did not pass: {review_result.status.value}",
        )

    # high assurance final review: tier未設定/未解決でも黙って降格せず停止する。
    router.resolve("high_assurance_review", model_policy)

    return dataclasses.replace(transformed_script, stage="verified")
