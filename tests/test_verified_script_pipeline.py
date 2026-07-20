"""STEP4 test implementation for TASK-NARRATION-001: SemanticReview / apply_character / build_verified_script.

Contract: docs/test-cases/TASK-NARRATION-001-narration-transformations-and-verified-script.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.ai.routing import AIRouter, ModelPolicy
from script.core.errors import AppError, ErrorCode
from script.pipelines.narration import NarrationPipeline, build_verified_script
from script.pipelines.semantic_review import SemanticReview, SemanticReviewStatus
from script.profiles.characters import CharacterProfileRepository
from script.schemas.claims import Claim, ClaimStatus, ClaimType, SourceEvidence, SourceLocator
from script.schemas.profiles import CharacterProfile, CharacterProfileStatus
from script.schemas.script import ScriptDocument, ScriptSegment, SpeakerRef

pytestmark = pytest.mark.mvp


def _speaker() -> SpeakerRef:
    return SpeakerRef(character_id="neutral-explainer", role="explainer")


def _script(text_1: str = "A for loop repeats 10 times.", text_2: str = "It does not stop early.") -> ScriptDocument:
    segments = (
        ScriptSegment(segment_id="ch01-seg001", order=1, speaker=_speaker(), segment_type="explanation", text=text_1),
        ScriptSegment(segment_id="ch01-seg002", order=2, speaker=_speaker(), segment_type="explanation", text=text_2),
    )
    return ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=segments)


def _verified_claim() -> Claim:
    return Claim(
        claim_id="ch01-seg001-claim001",
        statement="A for loop repeats a fixed number of times.",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg001",
        status=ClaimStatus.VERIFIED,
        source_evidence=(SourceEvidence(source_id="src-1", locator=SourceLocator(section="1")),),
        verified_by_human=True,
    )


class _NullAIClient:
    """narration.pyのNarrationPipelineに渡すが、apply_characterはAI呼出しを行わない。"""

    def check_connectivity(self) -> object:
        return object()

    def generate(self, request: object) -> object:  # pragma: no cover - 使用されない想定
        raise AssertionError("apply_character must not call the AI client")


@pytest.mark.unit
def test_tc_narration_001_02() -> None:
    """TC-NARRATION-001-02 — 意味差: 数値・否定・条件を変更した変換はreview_required/fail候補を返す。"""
    source = _script()

    numeric_change = _script(text_1="A for loop repeats 99 times.")
    result_numeric = SemanticReview().compare(source, numeric_change)
    assert result_numeric.status in (SemanticReviewStatus.REVIEW_REQUIRED, SemanticReviewStatus.FAIL)

    negation_change = _script(text_2="It does stop early.")
    result_negation = SemanticReview().compare(source, negation_change)
    assert result_negation.status in (SemanticReviewStatus.REVIEW_REQUIRED, SemanticReviewStatus.FAIL)

    unchanged = SemanticReview().compare(source, _script())
    assert unchanged.status is SemanticReviewStatus.PASS


@pytest.mark.unit
def test_tc_narration_001_04() -> None:
    """TC-NARRATION-001-04 — 表示名へ依存せずengineの識別子から解決し、不在時はspeaker_not_foundまたは局所disable。"""
    script = _script()
    pipeline = NarrationPipeline(ai_client=_NullAIClient())  # type: ignore[arg-type]
    character_repo = CharacterProfileRepository(
        (CharacterProfile(character_id="kasukabe-tsumugi", display_name="つむぎ", status=CharacterProfileStatus.APPROVED),)
    )

    # character_id未指定: 局所disable(中立原稿のまま、errorにしない)。
    neutral_result = pipeline.apply_character(script, character_repository=character_repo, character_id=None)
    assert neutral_result.stage == "character_styled"
    assert tuple(segment.text for segment in neutral_result.segments) == tuple(segment.text for segment in script.segments)

    # 不明なcharacter_id: speaker_not_found。
    with pytest.raises(AppError) as excinfo:
        pipeline.apply_character(script, character_repository=character_repo, character_id="unknown-character")
    assert excinfo.value.code is ErrorCode.NOT_FOUND
    assert "speaker_not_found" in excinfo.value.message

    # 既知かつ承認済みのcharacter_id: speakerへ反映されるがtextは変わらない。
    resolved = pipeline.apply_character(script, character_repository=character_repo, character_id="kasukabe-tsumugi")
    assert all(segment.speaker.character_id == "kasukabe-tsumugi" for segment in resolved.segments)
    assert tuple(segment.text for segment in resolved.segments) == tuple(segment.text for segment in script.segments)


@pytest.mark.unit
def test_tc_narration_001_06() -> None:
    """TC-NARRATION-001-06 — 未検証claim block: 正常値を受理し、仕様違反を副作用前に検出する。"""
    source = _script()
    router = AIRouter(env={})
    policy = ModelPolicy(
        provider="google",
        tiers={"high_assurance_review": {"model": "gemini-2.5-pro"}},
    )

    unverified_claim = Claim(
        claim_id="ch01-seg001-claim001",
        statement="A for loop repeats a fixed number of times.",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg001",
        status=ClaimStatus.PENDING,
    )

    with pytest.raises(AppError) as excinfo:
        build_verified_script(
            transformed_script=source,
            source_script=source,
            claims=(unverified_claim,),
            router=router,
            model_policy=policy,
        )
    assert excinfo.value.code is ErrorCode.CONFLICT

    result = build_verified_script(
        transformed_script=source,
        source_script=source,
        claims=(_verified_claim(),),
        router=router,
        model_policy=policy,
    )
    assert result.stage == "verified"


@pytest.mark.unit
def test_tc_narration_001_08() -> None:
    """TC-NARRATION-001-08 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    source = _script()
    router = AIRouter(env={})
    policy = ModelPolicy(provider="google", tiers={"high_assurance_review": {"model": "gemini-2.5-pro"}})

    with pytest.raises(AppError) as excinfo:
        build_verified_script(
            transformed_script=None,  # type: ignore[arg-type]
            source_script=source,
            claims=(_verified_claim(),),
            router=router,
            model_policy=policy,
        )
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        build_verified_script(
            transformed_script=source, source_script=source, claims=None, router=router, model_policy=policy  # type: ignore[arg-type]
        )

    with pytest.raises(AppError):
        build_verified_script(
            transformed_script=source,
            source_script=source,
            claims=(_verified_claim(),),
            router=None,  # type: ignore[arg-type]
            model_policy=policy,
        )


@pytest.mark.unit
def test_tc_narration_001_10() -> None:
    """TC-NARRATION-001-10 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    source = _script()
    router = AIRouter(env={})
    policy = ModelPolicy(provider="google", tiers={"high_assurance_review": {"model": "gemini-2.5-pro"}})
    verified_claim = _verified_claim()

    result = build_verified_script(
        transformed_script=source,
        source_script=source,
        claims=(verified_claim,),
        router=router,
        model_policy=policy,
    )
    before = (source.segments, verified_claim.status)

    unverified_claim = Claim(
        claim_id="ch01-seg002-claim001",
        statement="unrelated",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg002",
        status=ClaimStatus.PENDING,
    )
    with pytest.raises(AppError):
        build_verified_script(
            transformed_script=source,
            source_script=source,
            claims=(verified_claim, unverified_claim),
            router=router,
            model_policy=policy,
        )

    assert (source.segments, verified_claim.status) == before
    assert result.stage == "verified"
