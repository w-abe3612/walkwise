"""Implementation for TASK-RIGHTS-001: 権利・ライセンス・配布gate (local generation gate).

Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
Production files exercised: script/services/rights.py, script/schemas/rights.py
"""

from __future__ import annotations

import pytest

from script.schemas.rights import (
    ConfirmedBy,
    Evidence,
    RightsRecord,
    RightsStatus,
    UsagePurpose,
)
from script.services.rights import RightsService, build_credit_manifest

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_rights_001_01() -> None:
    """TC-RIGHTS-001-01 — 個人学習未確認

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P0
    Layer: unit
    Given: personal_learningかつrights unverified
    When: local generationを評価
    Then: 条件付き許可しdistributionは許可しない
    """
    service = RightsService()
    record = RightsRecord(
        source_id="mysql-8-reference",
        status=RightsStatus.UNVERIFIED,
        usage_purpose=UsagePurpose.PERSONAL_LEARNING,
    )

    local_decision = service.evaluate_local_generation(record)
    assert local_decision.allowed is True

    distribution_decision = service.evaluate_distribution(
        [
            RightsRecord(
                source_id="mysql-8-reference",
                status=RightsStatus.UNVERIFIED,
                usage_purpose=UsagePurpose.PUBLIC_DISTRIBUTION,
            )
        ]
    )
    assert distribution_decision.allowed is False


@pytest.mark.unit
def test_tc_rights_001_03() -> None:
    """TC-RIGHTS-001-03 — credit決定性

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P0
    Layer: unit
    Given: 複数の確認済みcredit
    When: manifestを生成
    Then: 安定順で重複なく出力する
    """
    records = [
        RightsRecord(
            source_id="zeta-book",
            status=RightsStatus.VERIFIED_OPEN_LICENSE,
            usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            evidence=Evidence(license_name="CC BY-SA 4.0"),
            confirmed_by=ConfirmedBy(type="human"),
        ),
        RightsRecord(
            source_id="alpha-book",
            status=RightsStatus.VERIFIED_PUBLIC_DOMAIN,
            usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            confirmed_by=ConfirmedBy(type="human"),
        ),
        # duplicate source_id must not appear twice
        RightsRecord(
            source_id="alpha-book",
            status=RightsStatus.VERIFIED_PUBLIC_DOMAIN,
            usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            confirmed_by=ConfirmedBy(type="human"),
        ),
    ]

    manifest = build_credit_manifest(records)
    source_ids = [entry["source_id"] for entry in manifest["credits"]]
    assert source_ids == ["alpha-book", "zeta-book"]
    assert len(source_ids) == len(set(source_ids))


@pytest.mark.unit
def test_tc_rights_001_05() -> None:
    """TC-RIGHTS-001-05 — unverified personal local generation許可

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `RightsRecord/CreditEntry/DistributionDecision`を通じて「unverified personal local generation許可」を実行する
    Then: 「unverified personal local generation許可」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    service = RightsService()
    record = RightsRecord(
        source_id="unverified-source",
        status=RightsStatus.UNVERIFIED,
        usage_purpose=UsagePurpose.PERSONAL_LEARNING,
    )
    decision = service.evaluate_local_generation(record)
    assert decision.allowed is True
    assert decision.review_required is False


@pytest.mark.unit
def test_tc_rights_001_07() -> None:
    """TC-RIGHTS-001-07 — evidence記録

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `RightsRecord/CreditEntry/DistributionDecision`を通じて「evidence記録」を実行する
    Then: 「evidence記録」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    evidence = Evidence(
        license_name="CC BY-SA 4.0",
        license_version="4.0",
        source_url="https://example.invalid/license",
        retrieved_at="2026-07-19T00:00:00+09:00",
        evidence_file="sources/reports/rights/mysql-8-reference-license.pdf",
    )
    record = RightsRecord(
        source_id="mysql-8-reference",
        status=RightsStatus.VERIFIED_OPEN_LICENSE,
        usage_purpose=UsagePurpose.PERSONAL_LEARNING,
        evidence=evidence,
        confirmed_by=ConfirmedBy(type="human", name="reviewer", confirmed_at="2026-07-19T00:00:00+09:00"),
    )
    assert record.evidence.license_name == "CC BY-SA 4.0"
    assert record.evidence.evidence_file == "sources/reports/rights/mysql-8-reference-license.pdf"

    with pytest.raises(Exception):
        RightsRecord(
            source_id="ai-confirmed",
            status=RightsStatus.VERIFIED_OPEN_LICENSE,
            usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            evidence=evidence,
            confirmed_by=ConfirmedBy(type="ai"),
        )


@pytest.mark.unit
def test_tc_rights_001_09() -> None:
    """TC-RIGHTS-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `RightsRecord/CreditEntry/DistributionDecision`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    service = RightsService()
    record = RightsRecord(
        source_id="database-book",
        status=RightsStatus.USER_ASSERTED_PRIVATE_USE,
        usage_purpose=UsagePurpose.PERSONAL_LEARNING,
    )
    first = service.evaluate_local_generation(record)
    second = service.evaluate_local_generation(record)
    assert first == second
