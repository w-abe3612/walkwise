"""script/pipelines/claims.py — 公開契約:
ClaimPipeline.extract(script) -> list[Claim],
ClaimPipeline.verify(claims, sources) -> FactCheckReport,
assert_script_claims_publishable(script, claims) -> None.

Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
Spec: docs/specifications/06-claims-and-sources.md
"""

from __future__ import annotations

import dataclasses
from collections.abc import Collection, Sequence

from script.ai.routing import AIRouter, ModelPolicy
from script.ai_clients.base import AIClient, AIRequest
from script.core.errors import AppError, ErrorCode
from script.schemas.claims import Claim, ClaimStatus, ClaimType, FACTUAL_CLAIM_TYPES, FactCheckReport, SourceEvidence
from script.schemas.script import ScriptDocument

_ECONOMY_MODEL_HINT = "gemini-2.5-flash-lite"
_CLAIM_TYPE_PREFIX = "CLAIM_TYPE:"
_STATEMENT_PREFIX = "STATEMENT:"
_NO_CLAIM_MARKER = "NONE"

# 05-script-segment-schema.md 7節のsegment_typeのうち、技術的事実を主張しないもの。
_NON_FACTUAL_SEGMENT_TYPES = frozenset({"heading", "transition", "introduction", "summary", "question"})


def _parse_claim_response(raw_text: str) -> tuple[ClaimType, str] | None:
    """AI応答から`CLAIM_TYPE:`/`STATEMENT:`の2行形式を決定的に取り出す。`NONE`ならNoneを返す。"""
    if raw_text.strip() == _NO_CLAIM_MARKER:
        return None

    claim_type_value: str | None = None
    statement_lines: list[str] = []
    in_statement = False

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not in_statement and stripped.startswith(_CLAIM_TYPE_PREFIX):
            claim_type_value = stripped[len(_CLAIM_TYPE_PREFIX):].strip()
        elif stripped.startswith(_STATEMENT_PREFIX):
            in_statement = True
            remainder = stripped[len(_STATEMENT_PREFIX):].strip()
            if remainder:
                statement_lines.append(remainder)
        elif in_statement:
            statement_lines.append(line)

    statement = "\n".join(statement_lines).strip()
    if not statement:
        raise AppError(ErrorCode.VALIDATION_ERROR, "AI claim response did not include STATEMENT content")

    try:
        claim_type = ClaimType(claim_type_value) if claim_type_value else ClaimType.TECHNICAL_FACT
    except ValueError as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown claim_type in AI response: {claim_type_value}") from exc

    return claim_type, statement


class ClaimPipeline:
    """初稿から主張候補を抽出し(economy_structuring)、evidence/人間承認を反映してverifyする。"""

    def __init__(
        self,
        *,
        ai_client: AIClient,
        extraction_model: str = _ECONOMY_MODEL_HINT,
        router: AIRouter | None = None,
        model_policy: ModelPolicy | None = None,
    ) -> None:
        if ai_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "ai_client is required")
        if not extraction_model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "extraction_model is required")
        self._ai_client = ai_client
        self._extraction_model = extraction_model
        self._router = router
        self._model_policy = model_policy

    def extract(self, script: ScriptDocument) -> list[Claim]:
        """抽出結果はpendingで生成する。"""
        if script is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script is required")
        if not script.segments:
            raise AppError(ErrorCode.VALIDATION_ERROR, "script.segments must not be empty")

        claims: list[Claim] = []
        for segment in script.segments:
            if segment.segment_type in _NON_FACTUAL_SEGMENT_TYPES:
                continue

            request = AIRequest(
                user_text=segment.text,
                system_instruction=(
                    "Extract one technical claim candidate from this narration segment. "
                    "Respond in exactly this format:\nCLAIM_TYPE: <claim type>\n"
                    "STATEMENT: <statement text>\nOr respond exactly 'NONE' if there is no "
                    "factual claim to extract."
                ),
                model=self._extraction_model,
            )
            result = self._ai_client.generate(request)
            parsed = _parse_claim_response(result.text)
            if parsed is None:
                continue
            claim_type, statement = parsed

            claims.append(
                Claim(
                    claim_id=f"{segment.segment_id}-claim001",
                    statement=statement,
                    claim_type=claim_type,
                    segment_id=segment.segment_id,
                    status=ClaimStatus.PENDING,
                    source_evidence=tuple(SourceEvidence(source_id=source_id) for source_id in segment.source_refs),
                )
            )

        return claims

    def verify(self, claims: Sequence[Claim], sources: Collection[str]) -> FactCheckReport:
        """evidenceと人間承認なしにverifiedへしない。"""
        if not claims:
            raise AppError(ErrorCode.VALIDATION_ERROR, "claims must not be empty")
        if sources is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "sources is required")

        known_source_ids = frozenset(sources)
        resolved: list[Claim] = []

        for claim in claims:
            for evidence in claim.source_evidence:
                if evidence.source_id not in known_source_ids:
                    raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown source_id referenced: {evidence.source_id}")

            if claim.status is ClaimStatus.CONFLICT or claim.conflict is not None:
                # 資料間矛盾は黙って解決しない。high_assurance未設定/未解決でも常にhuman review。
                if self._router is not None and self._model_policy is not None:
                    try:
                        self._router.resolve("high_assurance_review", self._model_policy)
                    except AppError:
                        pass
                resolved.append(dataclasses.replace(claim, status=ClaimStatus.HUMAN_REVIEW_REQUIRED))
                continue

            if claim.claim_type in FACTUAL_CLAIM_TYPES:
                has_locator_evidence = any(evidence.locator is not None for evidence in claim.source_evidence)
                if claim.verified_by_human and has_locator_evidence:
                    resolved.append(dataclasses.replace(claim, status=ClaimStatus.VERIFIED))
                elif claim.source_evidence:
                    # AI由来のevidenceはあるが人間承認またはlocatorが欠けている: 黙って承認しない。
                    resolved.append(dataclasses.replace(claim, status=ClaimStatus.HUMAN_REVIEW_REQUIRED))
                else:
                    resolved.append(dataclasses.replace(claim, status=ClaimStatus.UNSUPPORTED))
            else:
                # generated_analogy/generated_explanation/opinion: sourceは必須ではないが人間承認は必要。
                if claim.verified_by_human:
                    resolved.append(dataclasses.replace(claim, status=ClaimStatus.VERIFIED))
                else:
                    resolved.append(claim)

        return FactCheckReport(claims=tuple(resolved))


def assert_script_claims_publishable(script: ScriptDocument, claims: Sequence[Claim]) -> None:
    """unsupported/conflictを本番工程から遮断する。"""
    if script is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "script is required")
    if claims is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "claims is required")

    blocking_ids = [
        claim.claim_id
        for claim in claims
        if not (
            claim.status is ClaimStatus.VERIFIED
            or (claim.status is ClaimStatus.PARTIALLY_VERIFIED and claim.verified_by_human)
        )
    ]

    if blocking_ids:
        raise AppError(
            ErrorCode.CONFLICT,
            f"unpublishable claims block production TTS: {', '.join(sorted(blocking_ids))}",
        )
