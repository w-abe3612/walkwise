"""STEP4 test implementation for TASK-CLAIM-001: Claim/SourceEvidence/FactCheckReport validation.

Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.core.errors import AppError, ErrorCode
from script.pipelines.claims import ClaimPipeline
from script.schemas.claims import Claim, ClaimStatus, ClaimType, FactCheckReport, SourceEvidence, SourceLocator
from script.schemas.script import ScriptDocument, ScriptSegment, SpeakerRef

pytestmark = pytest.mark.mvp


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


def _factual_claim(**overrides: object) -> Claim:
    fields: dict[str, object] = dict(
        claim_id="ch01-seg002-claim001",
        statement="A for loop repeats a fixed number of times.",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg002",
        status=ClaimStatus.PENDING,
        source_evidence=(SourceEvidence(source_id="src-1"),),
    )
    fields.update(overrides)
    return Claim(**fields)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_claim_001_02() -> None:
    """TC-CLAIM-001-02 — verified条件: source locator+人間承認があればverified、AI出力のみでは不可。"""
    pipeline = ClaimPipeline(ai_client=_ScriptedAIClient({}))

    claim_with_locator_and_approval = _factual_claim(
        source_evidence=(SourceEvidence(source_id="src-1", locator=SourceLocator(section="13.1")),),
        verified_by_human=True,
    )
    report = pipeline.verify((claim_with_locator_and_approval,), sources=("src-1",))
    assert report.claims[0].status is ClaimStatus.VERIFIED

    ai_output_only_claim = _factual_claim(
        source_evidence=(SourceEvidence(source_id="src-1", locator=SourceLocator(section="13.1")),),
        verified_by_human=False,
    )
    report_2 = pipeline.verify((ai_output_only_claim,), sources=("src-1",))
    assert report_2.claims[0].status is not ClaimStatus.VERIFIED


@pytest.mark.unit
def test_tc_claim_001_04() -> None:
    """TC-CLAIM-001-04 — economy抽出はpending: extractは既定でeconomy tierのmodelを使い、常にpending。"""

    def _speaker() -> SpeakerRef:
        return SpeakerRef(character_id="neutral-explainer", role="explainer")

    script = ScriptDocument(
        project_id="proj-1",
        chapter_id="ch01",
        stage="draft",
        segments=(
            ScriptSegment(
                segment_id="ch01-seg001",
                order=1,
                speaker=_speaker(),
                segment_type="explanation",
                text="A for loop repeats a block of code.",
            ),
        ),
    )
    fake_client = _ScriptedAIClient(
        {"for loop repeats": "CLAIM_TYPE: technical_fact\nSTATEMENT: A for loop repeats code."}
    )
    pipeline = ClaimPipeline(ai_client=fake_client)

    claims = pipeline.extract(script)

    assert len(fake_client.calls) == 1
    assert fake_client.calls[0].model == "gemini-2.5-flash-lite"
    assert claims[0].status is ClaimStatus.PENDING


@pytest.mark.unit
def test_tc_claim_001_06() -> None:
    """TC-CLAIM-001-06 — source locator: 存在しないsource_idを検出する。"""
    pipeline = ClaimPipeline(ai_client=_ScriptedAIClient({}))
    claim = _factual_claim(source_evidence=(SourceEvidence(source_id="unknown-source"),))

    with pytest.raises(AppError) as excinfo:
        pipeline.verify((claim,), sources=("src-1",))
    assert "unknown-source" in excinfo.value.message


@pytest.mark.unit
def test_tc_claim_001_08() -> None:
    """TC-CLAIM-001-08 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as excinfo:
        Claim(claim_id="", statement="x", claim_type=ClaimType.TECHNICAL_FACT)
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        Claim(claim_id="c1", statement="", claim_type=ClaimType.TECHNICAL_FACT)

    pipeline = ClaimPipeline(ai_client=_ScriptedAIClient({}))
    with pytest.raises(AppError):
        pipeline.extract(None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        pipeline.verify((), sources=("src-1",))

    with pytest.raises(AppError):
        FactCheckReport(claims=())


@pytest.mark.unit
def test_tc_claim_001_10() -> None:
    """TC-CLAIM-001-10 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    pipeline = ClaimPipeline(ai_client=_ScriptedAIClient({}))
    good_claim = _factual_claim(verified_by_human=True, source_evidence=(SourceEvidence(source_id="src-1", locator=SourceLocator(section="13.1")),))
    report = pipeline.verify((good_claim,), sources=("src-1",))
    before = report.claims

    bad_claim = _factual_claim(source_evidence=(SourceEvidence(source_id="unknown-source"),))
    with pytest.raises(AppError):
        pipeline.verify((good_claim, bad_claim), sources=("src-1",))

    assert report.claims == before
    assert good_claim.status is ClaimStatus.PENDING  # 元のclaimは不変(frozen dataclass)
