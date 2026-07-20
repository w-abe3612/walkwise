"""STEP4 test implementation for TASK-CLAIM-001: ClaimPipeline / claim gate.

Contract: docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.core.errors import AppError, ErrorCode
from script.pipelines.claims import ClaimPipeline, assert_script_claims_publishable
from script.schemas.claims import Claim, ClaimConflict, ClaimStatus, ClaimType
from script.schemas.script import ScriptDocument, ScriptSegment, SpeakerRef

pytestmark = pytest.mark.mvp


def _speaker() -> SpeakerRef:
    return SpeakerRef(character_id="neutral-explainer", role="explainer")


def _script(*, source_refs: tuple[str, ...] = ("src-1",)) -> ScriptDocument:
    segments = (
        ScriptSegment(
            segment_id="ch01-seg001",
            order=1,
            speaker=_speaker(),
            segment_type="heading",
            text="Loops",
        ),
        ScriptSegment(
            segment_id="ch01-seg002",
            order=2,
            speaker=_speaker(),
            segment_type="explanation",
            text="A for loop repeats a block of code a fixed number of times.",
            source_refs=source_refs,
        ),
        ScriptSegment(
            segment_id="ch01-seg003",
            order=3,
            speaker=_speaker(),
            segment_type="definition",
            text="An iterator is an object representing a stream of data.",
            source_refs=source_refs,
        ),
    )
    return ScriptDocument(project_id="proj-1", chapter_id="ch01", stage="draft", segments=segments)


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


def _default_responses() -> dict[str, str]:
    return {
        "for loop repeats": "CLAIM_TYPE: technical_fact\nSTATEMENT: A for loop repeats a fixed number of times.",
        "iterator is an object": "CLAIM_TYPE: definition\nSTATEMENT: An iterator represents a stream of data.",
    }


@pytest.mark.unit
def test_tc_claim_001_01() -> None:
    """TC-CLAIM-001-01 — 抽出初期状態: 技術文を含むscriptをextractすると全claimはpending。"""
    fake_client = _ScriptedAIClient(_default_responses())
    pipeline = ClaimPipeline(ai_client=fake_client)

    claims = pipeline.extract(_script())

    assert len(claims) == 2  # heading segmentは抽出対象外
    assert all(claim.status is ClaimStatus.PENDING for claim in claims)


@pytest.mark.unit
def test_tc_claim_001_03() -> None:
    """TC-CLAIM-001-03 — conflict gate: conflict claimを含むscriptは本番TTS前に停止する。"""
    script = _script()
    claims = (
        Claim(
            claim_id="ch01-seg002-claim001",
            statement="conflicting statement",
            claim_type=ClaimType.TECHNICAL_FACT,
            segment_id="ch01-seg002",
            status=ClaimStatus.CONFLICT,
            conflict=ClaimConflict(source_ids=("src-1", "src-2")),
        ),
    )

    with pytest.raises(AppError) as excinfo:
        assert_script_claims_publishable(script, claims)
    assert excinfo.value.code is ErrorCode.CONFLICT


@pytest.mark.unit
def test_tc_claim_001_05() -> None:
    """TC-CLAIM-001-05 — evidence mapping: 抽出結果はsegmentのsource_refsをsource_evidenceへ写像する。"""
    fake_client = _ScriptedAIClient(_default_responses())
    pipeline = ClaimPipeline(ai_client=fake_client)

    claims = pipeline.extract(_script(source_refs=("src-1", "src-2")))

    for claim in claims:
        assert {evidence.source_id for evidence in claim.source_evidence} == {"src-1", "src-2"}


@pytest.mark.unit
def test_tc_claim_001_07() -> None:
    """TC-CLAIM-001-07 — unsupported block: evidence皆無の主張はunsupportedになり公開を遮断する。"""
    script = _script()
    claim = Claim(
        claim_id="ch01-seg002-claim001",
        statement="unsupported statement",
        claim_type=ClaimType.TECHNICAL_FACT,
        segment_id="ch01-seg002",
        status=ClaimStatus.PENDING,
        source_evidence=(),
    )

    pipeline = ClaimPipeline(ai_client=_ScriptedAIClient({}))
    report = pipeline.verify((claim,), sources=("src-1",))

    assert report.claims[0].status is ClaimStatus.UNSUPPORTED
    with pytest.raises(AppError):
        assert_script_claims_publishable(script, report.claims)


@pytest.mark.unit
def test_tc_claim_001_09() -> None:
    """TC-CLAIM-001-09 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    fake_client = _ScriptedAIClient(_default_responses())
    pipeline = ClaimPipeline(ai_client=fake_client)
    script = _script()

    claims_1 = pipeline.extract(script)
    claims_2 = pipeline.extract(script)

    assert claims_1 == claims_2
    assert len(fake_client.calls) == 4  # 2 factual segments x 2 runs
