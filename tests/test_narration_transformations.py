"""STEP4 test implementation for TASK-NARRATION-001: NarrationPipeline / verified gate.

Contract: docs/test-cases/TASK-NARRATION-001-narration-transformations-and-verified-script.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.ai.routing import AIRouter, ModelPolicy
from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.core.errors import AppError, ErrorCode
from script.pipelines.narration import NarrationPipeline, build_verified_script
from script.profiles.characters import CharacterProfileRepository
from script.schemas.claims import Claim, ClaimStatus, ClaimType, SourceEvidence, SourceLocator
from script.schemas.profiles import CharacterProfile, CharacterProfileStatus
from script.schemas.script import ScriptDocument, ScriptSegment, SpeakerRef

pytestmark = pytest.mark.mvp


def _speaker() -> SpeakerRef:
    return SpeakerRef(character_id="neutral-explainer", role="explainer")


def _draft_script(text_1: str = "A for loop repeats 10 times.", text_2: str = "It does not stop early.") -> ScriptDocument:
    segments = (
        ScriptSegment(segment_id="ch01-seg001", order=1, speaker=_speaker(), segment_type="explanation", text=text_1),
        ScriptSegment(segment_id="ch01-seg002", order=2, speaker=_speaker(), segment_type="explanation", text=text_2),
    )
    return ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=segments)


def _verified_claim(claim_id: str = "ch01-seg001-claim001") -> Claim:
    return Claim(
        claim_id=claim_id,
        statement="A for loop repeats a fixed number of times.",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg001",
        status=ClaimStatus.VERIFIED,
        source_evidence=(SourceEvidence(source_id="src-1", locator=SourceLocator(section="1")),),
        verified_by_human=True,
    )


def _model_policy(*, with_high_assurance: bool) -> ModelPolicy:
    tiers = {"economy_structuring": {"model": "gemini-2.5-flash-lite"}}
    if with_high_assurance:
        tiers["high_assurance_review"] = {"model": "gemini-2.5-pro"}
    return ModelPolicy(provider="google", tiers=tiers)


class _ScriptedAIClient:
    def __init__(self, responses: dict[str, str]) -> None:
        self._responses = responses
        self.calls: list[AIRequest] = []

    def check_connectivity(self) -> object:
        return object()

    def generate(self, request: AIRequest) -> AIResult:
        self.calls.append(request)
        for marker, response_text in self._responses.items():
            if marker in request.user_text:
                return AIResult(text=response_text, provider="fake", model=request.model or "fake-model", usage=AIUsage())
        raise AssertionError(f"no scripted response for request: {request.user_text!r}")


def _identity_responses(script: ScriptDocument) -> dict[str, str]:
    return {segment.text: f"TEXT: {segment.text}" for segment in script.segments}


@pytest.mark.unit
def test_tc_narration_001_01() -> None:
    """TC-NARRATION-001-01 — 段階不変: 3変換それぞれが別成果物になり、元のtextを変更しない。"""
    draft = _draft_script()
    before_texts = tuple(segment.text for segment in draft.segments)

    fake_client = _ScriptedAIClient(_identity_responses(draft))
    pipeline = NarrationPipeline(ai_client=fake_client)
    character_repo = CharacterProfileRepository(
        (CharacterProfile(character_id="neutral-explainer", display_name="x", status=CharacterProfileStatus.APPROVED),)
    )

    simplified = pipeline.simplify(draft)
    audio_adapted = pipeline.adapt_for_audio(simplified)
    character_styled = pipeline.apply_character(audio_adapted, character_repository=character_repo, character_id=None)

    assert simplified.stage == "simplified"
    assert audio_adapted.stage == "audio_adapted"
    assert character_styled.stage == "character_styled"
    assert len({draft.stage, simplified.stage, audio_adapted.stage, character_styled.stage}) == 4

    # 元のdraft scriptは一切変更されていない。
    assert tuple(segment.text for segment in draft.segments) == before_texts
    assert draft.stage == "draft"


@pytest.mark.integration_mock
def test_tc_narration_001_03() -> None:
    """TC-NARRATION-001-03 — verified gate: fact checkまたはsemantic review未完なら拒否する。"""
    source = _draft_script()
    policy = _model_policy(with_high_assurance=True)
    router = AIRouter(env={})

    unverified_claim = Claim(
        claim_id="ch01-seg001-claim001",
        statement="A for loop repeats a fixed number of times.",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg001",
        status=ClaimStatus.PENDING,
    )
    with pytest.raises(AppError) as excinfo_fact_check:
        build_verified_script(
            transformed_script=source,
            source_script=source,
            claims=(unverified_claim,),
            router=router,
            model_policy=policy,
        )
    assert excinfo_fact_check.value.code is ErrorCode.CONFLICT

    semantically_changed = _draft_script(text_1="A for loop repeats 99 times.")
    with pytest.raises(AppError) as excinfo_semantic:
        build_verified_script(
            transformed_script=semantically_changed,
            source_script=source,
            claims=(_verified_claim(),),
            router=router,
            model_policy=policy,
        )
    assert excinfo_semantic.value.code is ErrorCode.CONFLICT


@pytest.mark.unit
def test_tc_narration_001_05() -> None:
    """TC-NARRATION-001-05 — tts_textのみ発音調整: textは不変でtts_textだけが設定される。"""
    draft = _draft_script()
    fake_client = _ScriptedAIClient(
        {segment.text: f"TEXT: tts-reading-of({segment.text})" for segment in draft.segments}
    )
    pipeline = NarrationPipeline(ai_client=fake_client)

    adapted = pipeline.adapt_for_audio(draft)

    for original, transformed in zip(draft.segments, adapted.segments):
        assert transformed.text == original.text
        assert transformed.tts_text != original.text
        assert transformed.tts_text is not None


@pytest.mark.unit
def test_tc_narration_001_07() -> None:
    """TC-NARRATION-001-07 — high assurance final review: tier未設定/未解決なら黙って降格せず停止する。"""
    source = _draft_script()
    router = AIRouter(env={})

    with pytest.raises(AppError):
        build_verified_script(
            transformed_script=source,
            source_script=source,
            claims=(_verified_claim(),),
            router=router,
            model_policy=_model_policy(with_high_assurance=False),
        )

    result = build_verified_script(
        transformed_script=source,
        source_script=source,
        claims=(_verified_claim(),),
        router=router,
        model_policy=_model_policy(with_high_assurance=True),
    )
    assert result.stage == "verified"


@pytest.mark.unit
def test_tc_narration_001_09() -> None:
    """TC-NARRATION-001-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    draft = _draft_script()
    fake_client = _ScriptedAIClient(_identity_responses(draft))
    pipeline = NarrationPipeline(ai_client=fake_client)

    result_1 = pipeline.simplify(draft)
    result_2 = pipeline.simplify(draft)

    assert result_1 == result_2
    assert len(fake_client.calls) == len(draft.segments) * 2
