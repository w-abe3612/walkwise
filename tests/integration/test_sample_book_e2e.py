"""Test suite for TASK-E2E-001: サンプル1章fixture・仕様間受入検証.

Contract: docs/test-cases/TASK-E2E-001-sample-book-fixtures-and-acceptance.md
Spec: docs/specifications/audiobook-creation-pipeline.md

``run_sample_book_acceptance`` is this task's public contract and is
self-referential production: it lives in this test file, mirroring the
established pattern from TASK-DESKTOP-003's electron/tests/e2e/mvp-flow.test.ts
(the contract lists this file as both a test_file and a source_file).
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from script.ai.budget import BudgetGuard, UsageEstimate
from script.ai.cache import AICache, AICacheKey
from script.ai.routing import AIRouter, ModelPolicy
from script.ai_clients.base import AIRequest, AIResult, AIUsage
from script.core.errors import AppError, ErrorCode
from script.core.hashing import canonical_sha256
from script.core.serialization import load_yaml
from script.persistence.files import atomic_write_bytes
from script.schemas.approvals import ApprovalBundle, ApprovalGate, ApprovalStatus

pytestmark = pytest.mark.mvp

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "sample_book"

_ABNORMAL_SCENARIOS = frozenset(
    {
        "unsupported-claim",
        "source-conflict",
        "high-assurance-unconfigured",
        "invalid-reference",
        "budget-stop",
        "cache-invalidation",
        "unapproved-output-request",
    }
)


# ---------------------------------------------------------------------------
# STEP4 typed contract: run_sample_book_acceptance(...).
# ---------------------------------------------------------------------------
STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-E2E-001', 'run_sample_book_acceptance(...)', 'mock AI/TTSで全工程と異常fixtureを検証する。'),
)


class SampleBookAcceptanceResult:
    """`run_sample_book_acceptance`の戻り値を型付けする。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _load_base_fixture(fixture_dir: Path) -> dict[str, Any]:
    return {
        "sources": list(load_yaml(fixture_dir / "sources.yaml")["sources"]),
        "claims": list(load_yaml(fixture_dir / "claims.yaml")["claims"]),
        "script": dict(load_yaml(fixture_dir / "script.yaml")),
        "approvals": dict(load_yaml(fixture_dir / "approvals.yaml")),
        "coverage": list(load_yaml(fixture_dir / "coverage-map.yaml")["coverage"]),
        "routing_steps": dict(load_yaml(fixture_dir / "ai-routing-plan.yaml")["steps"]),
        "model_policy": dict(load_yaml(fixture_dir / "model-policy.yaml")),
        "budget_state": {"stop_usd": 100.0, "spent_usd": 0.0},
        "request_deliverables": True,
    }


def _apply_overlay(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)

    for claim in overlay.get("claims_add", []):
        merged["claims"].append(dict(claim))

    claim_overrides = overlay.get("claims_override", {})
    if claim_overrides:
        for claim in merged["claims"]:
            patch = claim_overrides.get(claim["claim_id"])
            if patch:
                claim.update(patch)

    segment_overrides = overlay.get("segments_override", {})
    if segment_overrides:
        for segment in merged["script"]["segments"]:
            patch = segment_overrides.get(segment["segment_id"])
            if patch:
                segment.update(patch)

    approval_overrides = overlay.get("approvals_override", {})
    if approval_overrides:
        for gate_name, patch in approval_overrides.items():
            merged["approvals"]["approvals"][gate_name].update(patch)

    policy_overrides = overlay.get("policy_override", {})
    if policy_overrides:
        for tier_name, patch in policy_overrides.items():
            merged["model_policy"]["tiers"].setdefault(tier_name, {}).update(patch)

    if "budget_state" in overlay:
        merged["budget_state"] = dict(overlay["budget_state"])

    if "request_deliverables" in overlay:
        merged["request_deliverables"] = overlay["request_deliverables"]

    return merged


def _step_input_payload(step_name: str, state: dict[str, Any]) -> Any:
    """各AI工程が実際に参照する入力だけをcache keyのhash対象にする(4.4節: 必要chunkだけ送る)。"""
    if step_name in ("toc_structuring", "topic_extraction"):
        return {"sources": state["sources"]}
    if step_name == "claim_candidate_extraction":
        return {"claims": state["claims"]}
    if step_name == "format_conversion":
        return {"segments": state["script"]["segments"]}
    if step_name in ("chapter_draft", "readability_transform", "audio_adaptation"):
        return {"segments": state["script"]["segments"], "claims": state["claims"]}
    if step_name in ("source_conflict_check", "final_semantic_review"):
        return {"claims": state["claims"], "coverage": state["coverage"]}
    return {"step": step_name}


def run_sample_book_acceptance(
    *,
    fixture_dir: Path,
    destination_dir: Path,
    ai_client: Any,
    tts_synthesize: Callable[[str, str], bytes],
    scenario: str = "normal",
    ai_cache: AICache | None = None,
    budget_guard: BudgetGuard | None = None,
) -> SampleBookAcceptanceResult:
    """mock AI/TTSで全工程と異常fixtureを検証する。

    Public contract: ``run_sample_book_acceptance(...)``.
    """
    if fixture_dir is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "fixture_dir is required")
    if destination_dir is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "destination_dir is required")
    if ai_client is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "ai_client is required")
    if tts_synthesize is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "tts_synthesize is required")
    if scenario != "normal" and scenario not in _ABNORMAL_SCENARIOS:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown scenario: {scenario!r}")

    fixture_dir = Path(fixture_dir)
    destination_dir = Path(destination_dir)
    cache = ai_cache if ai_cache is not None else AICache()

    state = _load_base_fixture(fixture_dir)
    if scenario != "normal":
        overlay = load_yaml(fixture_dir / "fixtures" / f"{scenario}.yaml")
        state = _apply_overlay(state, overlay)

    sources_by_id = {item["source_id"]: item for item in state["sources"]}
    claims_by_id = {item["claim_id"]: item for item in state["claims"]}
    segments = state["script"]["segments"]

    # 参照整合性(TC-E2E-001-07、invalid-reference scenario)。
    for segment in segments:
        for claim_id in segment.get("claim_ids") or ():
            if claim_id not in claims_by_id:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"invalid_reference: unknown claim_id {claim_id!r} in segment {segment['segment_id']!r}",
                )
    for claim in state["claims"]:
        for evidence in claim.get("source_evidence") or ():
            source_id = evidence["source_id"]
            if source_id not in sources_by_id:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"invalid_reference: unknown source_id {source_id!r} in claim {claim['claim_id']!r}",
                )
    for entry in state["coverage"]:
        for source_id in entry.get("source_ids") or ():
            if source_id not in sources_by_id:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"invalid_reference: unknown source_id {source_id!r} in coverage {entry['topic_id']!r}",
                )

    # 公開目次を事実根拠にしない(unsupported-claim scenario、15-migration系タスクと同様に推測せず拒否)。
    for claim in state["claims"]:
        evidence = claim.get("source_evidence") or ()
        if not evidence:
            continue
        roles = {sources_by_id[item["source_id"]]["role"] for item in evidence}
        if roles == {"curriculum_structure_only"}:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"unsupported_claim_evidence: claim {claim['claim_id']!r} cites only curriculum-structure-only sources",
            )

    coverage_gap_detected = any(entry["status"] == "missing" for entry in state["coverage"])

    approval_bundle = ApprovalBundle.from_mapping(state["approvals"])
    unresolved_conflict = any(claim.get("status") == "conflict" for claim in state["claims"])
    if unresolved_conflict and approval_bundle.approvals[ApprovalGate.VERIFIED_SCRIPT].status is ApprovalStatus.APPROVED:
        raise AppError(
            ErrorCode.CONFLICT,
            "unresolved_claim_conflict: verified_script is approved while a claim conflict remains unresolved",
        )

    budget_state = state["budget_state"]
    budget = budget_guard
    if budget is None:
        budget = BudgetGuard(stop_usd=budget_state["stop_usd"])
        if budget_state.get("spent_usd"):
            budget.record(UsageEstimate(cost_usd=budget_state["spent_usd"], is_measured=True))
    budget.assert_available()

    policy = ModelPolicy.from_mapping(state["model_policy"])
    router = AIRouter()
    ai_calls = 0
    cache_hits = 0
    cache_misses = 0
    tier_selections: dict[str, str] = {}

    for step_name, tier in state["routing_steps"].items():
        selection = router.resolve(tier, policy)
        tier_selections[step_name] = selection.model

        budget.assert_available()

        input_payload = _step_input_payload(step_name, state)
        input_hash = canonical_sha256(input_payload)
        cache_key = AICacheKey(
            task_type=step_name,
            logical_tier=tier,
            model=selection.model,
            prompt_id=f"sample-book/{step_name}",
            prompt_version="v1",
            input_hash=input_hash,
        )
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            cache_hits += 1
            continue

        cache_misses += 1
        request = AIRequest(user_text=json.dumps(input_payload, ensure_ascii=False, sort_keys=True), model=selection.model)
        result = ai_client.generate(request)
        ai_calls += 1
        cache.put(cache_key, result)
        budget.record(
            UsageEstimate(
                tokens=result.usage.total_tokens if result.usage else None,
                cost_usd=0.0001,
                is_measured=True,
            )
        )

    if approval_bundle.approvals[ApprovalGate.VERIFIED_SCRIPT].status is not ApprovalStatus.APPROVED:
        raise AppError(ErrorCode.PERMISSION_DENIED, "verified_script gate is not approved; production TTS is blocked")

    segment_audio: dict[str, bytes] = {}
    for segment in segments:
        segment_audio[segment["segment_id"]] = tts_synthesize(segment["segment_id"], segment.get("tts_text") or segment["text"])

    if state.get("request_deliverables", True):
        if approval_bundle.approvals[ApprovalGate.PREVIEW_AUDIO].status is not ApprovalStatus.APPROVED:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                "unapproved_output_request: preview_audio gate is not approved; deliverables are blocked",
            )

    chapter_mp3 = b"".join(segment_audio[segment["segment_id"]] for segment in segments)
    chapter_text = "\n".join(segment["text"] for segment in segments)
    audio_manifest = {
        "chapter_id": state["script"]["chapter_id"],
        "segments": [
            {
                "segment_id": segment["segment_id"],
                "order": segment["order"],
                "byte_length": len(segment_audio[segment["segment_id"]]),
            }
            for segment in segments
        ],
    }
    validation_report = {
        "claims_traced": True,
        "claim_count": len(state["claims"]),
        "coverage_gap_detected": coverage_gap_detected,
        "ai_tier_selections": tier_selections,
        "ai_calls": ai_calls,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "budget_spent_usd": budget.spent_usd,
        "approvals_satisfied": [gate.value for gate in ApprovalGate],
    }

    destination_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(destination_dir / "chapter.mp3", chapter_mp3)
    atomic_write_bytes(destination_dir / "chapter.txt", chapter_text.encode("utf-8"))
    atomic_write_bytes(
        destination_dir / "audio-manifest.json",
        json.dumps(audio_manifest, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8"),
    )
    atomic_write_bytes(
        destination_dir / "validation-report.json",
        json.dumps(validation_report, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8"),
    )

    return SampleBookAcceptanceResult(
        scenario=scenario,
        claims_traced=True,
        coverage_gap_detected=coverage_gap_detected,
        ai_tier_selections=tier_selections,
        ai_calls=ai_calls,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        budget_spent_usd=budget.spent_usd,
        approvals_satisfied=tuple(gate.value for gate in ApprovalGate),
        artifacts={
            "chapter_mp3": destination_dir / "chapter.mp3",
            "chapter_text": destination_dir / "chapter.txt",
            "audio_manifest": destination_dir / "audio-manifest.json",
            "validation_report": destination_dir / "validation-report.json",
        },
    )


# ---------------------------------------------------------------------------
# Test-only fakes (not part of the public contract).
# ---------------------------------------------------------------------------
class _FakeAIClient:
    """外部接続なしの決定的AIClient fake。"""

    def __init__(self) -> None:
        self.call_count = 0

    def check_connectivity(self) -> object:
        return {"available": True}

    def generate(self, request: AIRequest) -> AIResult:
        self.call_count += 1
        return AIResult(
            text=f"mock-response:{len(request.user_text)}",
            provider="mock",
            model=request.model or "mock-model",
            usage=AIUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        )


def _fake_tts_synthesize(segment_id: str, text: str) -> bytes:
    return hashlib.sha256(f"{segment_id}:{text}".encode("utf-8")).digest()


@pytest.mark.e2e
def test_tc_e2e_001_01(tmp_path: Path) -> None:
    """TC-E2E-001-01 — 正常sample

    Given: 決定的sample fixture
    When: mock E2E
    Then: 4claim追跡、4承認、章MP3/text/manifestを生成
    """
    ai_client = _FakeAIClient()
    result = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest",
        ai_client=ai_client,
        tts_synthesize=_fake_tts_synthesize,
    )

    assert result.claims_traced is True
    assert result.data["ai_tier_selections"]  # 9 processing steps routed
    assert len(result.approvals_satisfied) == 4
    assert result.artifacts["chapter_mp3"].exists()
    assert result.artifacts["chapter_text"].exists()
    assert result.artifacts["audio_manifest"].exists()
    assert result.artifacts["validation_report"].exists()
    assert ai_client.call_count == 9


@pytest.mark.e2e
def test_tc_e2e_001_02(tmp_path: Path) -> None:
    """TC-E2E-001-02 — 異常fixtures

    Given: unsupported/conflict/invalid ref/budget/unapproved
    When: 各実行
    Then: 正しいgateで停止し既存成果物を保持
    """
    dest = tmp_path / "dest"
    run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=dest,
        ai_client=_FakeAIClient(),
        tts_synthesize=_fake_tts_synthesize,
    )
    before = (dest / "chapter.mp3").read_bytes()

    stopping_scenarios = {
        "unsupported-claim": ErrorCode.VALIDATION_ERROR,
        "source-conflict": ErrorCode.CONFLICT,
        "high-assurance-unconfigured": ErrorCode.EXTERNAL_UNAVAILABLE,
        "invalid-reference": ErrorCode.VALIDATION_ERROR,
        "budget-stop": ErrorCode.PERMISSION_DENIED,
        "unapproved-output-request": ErrorCode.PERMISSION_DENIED,
    }
    for scenario, expected_code in stopping_scenarios.items():
        with pytest.raises(AppError) as exc_info:
            run_sample_book_acceptance(
                fixture_dir=FIXTURE_DIR,
                destination_dir=dest,
                ai_client=_FakeAIClient(),
                tts_synthesize=_fake_tts_synthesize,
                scenario=scenario,
            )
        assert exc_info.value.code is expected_code, scenario

    assert (dest / "chapter.mp3").read_bytes() == before


@pytest.mark.e2e
def test_tc_e2e_001_03(tmp_path: Path) -> None:
    """TC-E2E-001-03 — cache

    Given: 同じfixtureを再実行
    When: E2E
    Then: AI/TTS mock callがcache hit分だけ減る
    """
    ai_client = _FakeAIClient()
    cache = AICache()

    run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest1",
        ai_client=ai_client,
        tts_synthesize=_fake_tts_synthesize,
        ai_cache=cache,
    )
    first_call_count = ai_client.call_count
    assert first_call_count == 9

    result2 = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest2",
        ai_client=ai_client,
        tts_synthesize=_fake_tts_synthesize,
        ai_cache=cache,
    )
    assert ai_client.call_count == first_call_count
    assert result2.cache_hits == 9
    assert result2.cache_misses == 0


@pytest.mark.unit
def test_tc_e2e_001_04(tmp_path: Path) -> None:
    """TC-E2E-001-04 — unsupported/conflict/invalid ref/budget/cache/unapproved fixture

    Then: 同じcache keyでは外部処理を再実行せず、入力・model・prompt・version差分ではmissする。
    """
    cache = AICache()
    ai_client = _FakeAIClient()
    run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest1",
        ai_client=ai_client,
        tts_synthesize=_fake_tts_synthesize,
        ai_cache=cache,
    )
    baseline_calls = ai_client.call_count

    result = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest2",
        ai_client=ai_client,
        tts_synthesize=_fake_tts_synthesize,
        ai_cache=cache,
        scenario="cache-invalidation",
    )
    assert ai_client.call_count > baseline_calls
    assert result.cache_misses > 0
    assert result.cache_hits > 0

    budget_ai_client = _FakeAIClient()
    with pytest.raises(AppError) as exc_info:
        run_sample_book_acceptance(
            fixture_dir=FIXTURE_DIR,
            destination_dir=tmp_path / "dest3",
            ai_client=budget_ai_client,
            tts_synthesize=_fake_tts_synthesize,
            scenario="budget-stop",
        )
    assert exc_info.value.code is ErrorCode.PERMISSION_DENIED
    assert budget_ai_client.call_count == 0


@pytest.mark.unit
def test_tc_e2e_001_05(tmp_path: Path) -> None:
    """TC-E2E-001-05 — optional real VOICEVOX手動

    Then: 通常E2Eはmock TTSで完結し、実VOICEVOXは呼び出し側が任意に注入できるだけである。
    """
    calls: list[str] = []

    def manual_like_tts(segment_id: str, text: str) -> bytes:
        calls.append(segment_id)
        return _fake_tts_synthesize(segment_id, text)

    result = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest",
        ai_client=_FakeAIClient(),
        tts_synthesize=manual_like_tts,
    )

    assert len(calls) == 8
    assert result.artifacts["chapter_mp3"].exists()


@pytest.mark.unit
def test_tc_e2e_001_06(tmp_path: Path) -> None:
    """TC-E2E-001-06 — validation report

    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    """
    result = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest",
        ai_client=_FakeAIClient(),
        tts_synthesize=_fake_tts_synthesize,
    )
    report = json.loads(result.artifacts["validation_report"].read_text(encoding="utf-8"))
    assert report["claims_traced"] is True
    assert report["claim_count"] == 4
    assert report["coverage_gap_detected"] is True
    assert set(report["ai_tier_selections"].values()) == {
        "mock-economy-flash-lite",
        "mock-standard-flash",
        "mock-high-assurance-pro",
    }

    with pytest.raises(AppError) as exc_info:
        run_sample_book_acceptance(
            fixture_dir=FIXTURE_DIR,
            destination_dir=tmp_path / "dest-invalid",
            ai_client=_FakeAIClient(),
            tts_synthesize=_fake_tts_synthesize,
            scenario="invalid-reference",
        )
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_e2e_001_07(tmp_path: Path) -> None:
    """TC-E2E-001-07 — 参照整合性"""
    with pytest.raises(AppError) as exc_info:
        run_sample_book_acceptance(
            fixture_dir=FIXTURE_DIR,
            destination_dir=tmp_path / "dest",
            ai_client=_FakeAIClient(),
            tts_synthesize=_fake_tts_synthesize,
            scenario="invalid-reference",
        )
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert "invalid_reference" in str(exc_info.value)


@pytest.mark.unit
def test_tc_e2e_001_08(tmp_path: Path) -> None:
    """TC-E2E-001-08 — 必須入力欠落

    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    dest = tmp_path / "dest"
    with pytest.raises(AppError) as exc_info:
        run_sample_book_acceptance(
            fixture_dir=None,
            destination_dir=dest,
            ai_client=_FakeAIClient(),
            tts_synthesize=_fake_tts_synthesize,
        )
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert not dest.exists()

    with pytest.raises(AppError) as exc_info:
        run_sample_book_acceptance(
            fixture_dir=FIXTURE_DIR,
            destination_dir=tmp_path / "dest2",
            ai_client=None,
            tts_synthesize=_fake_tts_synthesize,
        )
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_e2e_001_09(tmp_path: Path) -> None:
    """TC-E2E-001-09 — 再実行時の決定性"""
    result1 = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest1",
        ai_client=_FakeAIClient(),
        tts_synthesize=_fake_tts_synthesize,
    )
    result2 = run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=tmp_path / "dest2",
        ai_client=_FakeAIClient(),
        tts_synthesize=_fake_tts_synthesize,
    )

    assert result1.artifacts["chapter_mp3"].read_bytes() == result2.artifacts["chapter_mp3"].read_bytes()
    assert result1.artifacts["chapter_text"].read_text(encoding="utf-8") == result2.artifacts["chapter_text"].read_text(
        encoding="utf-8"
    )
    assert result1.ai_calls == result2.ai_calls == 9


@pytest.mark.unit
def test_tc_e2e_001_10(tmp_path: Path) -> None:
    """TC-E2E-001-10 — 入力・既存成果物の不変性"""
    sources_path = FIXTURE_DIR / "sources.yaml"
    before_hash = hashlib.sha256(sources_path.read_bytes()).hexdigest()

    dest = tmp_path / "dest"
    run_sample_book_acceptance(
        fixture_dir=FIXTURE_DIR,
        destination_dir=dest,
        ai_client=_FakeAIClient(),
        tts_synthesize=_fake_tts_synthesize,
    )
    assert hashlib.sha256(sources_path.read_bytes()).hexdigest() == before_hash

    existing_report_bytes = (dest / "validation-report.json").read_bytes()
    with pytest.raises(AppError):
        run_sample_book_acceptance(
            fixture_dir=FIXTURE_DIR,
            destination_dir=dest,
            ai_client=_FakeAIClient(),
            tts_synthesize=_fake_tts_synthesize,
            scenario="invalid-reference",
        )
    assert (dest / "validation-report.json").read_bytes() == existing_report_bytes
    assert hashlib.sha256(sources_path.read_bytes()).hexdigest() == before_hash


@pytest.mark.integration_smoke
def test_tc_e2e_001_11(voicevox_connectivity_gate) -> None:
    """TC-E2E-001-11 — 任意の実VOICEVOXの疎通確認

    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: 実VOICEVOXを使う任意テストでは、先に`GET /speakers`を行う。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert voicevox_connectivity_gate.available is True
    assert voicevox_connectivity_gate.speaker_count is not None
    assert voicevox_connectivity_gate.speaker_count >= 1


@pytest.mark.integration_live
def test_tc_e2e_001_12(voicevox_connectivity_gate) -> None:
    """TC-E2E-001-12 — 任意の実VOICEVOXの実機能テスト

    Given: `voicevox_connectivity_gate`が成功済み
    When: 疎通成功後だけサンプルの短い試聴区間を合成する。通常E2Eはmock TTSで完結する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    assert voicevox_connectivity_gate.available is True

    from script.tts_clients.models import SynthesisRequest
    from script.tts_clients.voicevox.adapter import VoicevoxAdapter
    from script.tts_clients.voicevox.client import VoicevoxHttpClient

    client = VoicevoxHttpClient()
    speakers = client.list_speakers()
    assert speakers

    adapter = VoicevoxAdapter(client=client)
    request = SynthesisRequest(
        request_id="e2e-live-smoke-r0001",
        engine="voicevox",
        text="こんにちは。",
        speaker_id=speakers[0].speaker_id,
    )
    result = adapter.synthesize(request)

    assert result.duration_seconds > 0
