"""Implementation for TASK-RIGHTS-001: 権利・ライセンス・配布gate (distribution/credit manifest).

Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
Production files exercised: script/services/rights.py, script/schemas/rights.py
"""

from __future__ import annotations

import copy

import pytest

from script.core.errors import AppError
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
def test_tc_rights_001_02() -> None:
    """TC-RIGHTS-001-02 — 配布hard gate

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P0
    Layer: unit
    Given: 1資料でもrights未確認
    When: distributionを評価
    Then: blockedになり不足項目を列挙する
    """
    service = RightsService()
    records = [
        RightsRecord(
            source_id="verified-book",
            status=RightsStatus.VERIFIED_PUBLIC_DOMAIN,
            usage_purpose=UsagePurpose.PUBLIC_DISTRIBUTION,
            confirmed_by=ConfirmedBy(type="human"),
        ),
        RightsRecord(
            source_id="unverified-book",
            status=RightsStatus.UNVERIFIED,
            usage_purpose=UsagePurpose.PUBLIC_DISTRIBUTION,
        ),
    ]

    decision = service.evaluate_distribution(records)
    assert decision.allowed is False
    assert any("unverified-book" in reason for reason in decision.reasons)


@pytest.mark.unit
def test_tc_rights_001_04() -> None:
    """TC-RIGHTS-001-04 — 4 usage purposes

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `RightsRecord/CreditEntry/DistributionDecision`を通じて「4 usage purposes」を実行する
    Then: 「4 usage purposes」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    assert {purpose.value for purpose in UsagePurpose} == {
        "personal_learning", "internal_use", "public_distribution", "commercial_distribution",
    }

    service = RightsService()
    for purpose in UsagePurpose:
        record = RightsRecord(
            source_id="public-domain-book",
            status=RightsStatus.VERIFIED_PUBLIC_DOMAIN,
            usage_purpose=purpose,
            confirmed_by=ConfirmedBy(type="human"),
        )
        decision = service.evaluate_local_generation(record)
        assert decision.allowed is True  # verified_public_domain permits all 4 purposes


@pytest.mark.unit
def test_tc_rights_001_06() -> None:
    """TC-RIGHTS-001-06 — human confirmation

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `RightsRecord/CreditEntry/DistributionDecision`を通じて「human confirmation」を実行する
    Then: 「human confirmation」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    with pytest.raises(AppError):
        RightsRecord(
            source_id="no-confirmation",
            status=RightsStatus.VERIFIED_PUBLIC_DOMAIN,
            usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            confirmed_by=None,
        )

    record = RightsRecord(
        source_id="confirmed",
        status=RightsStatus.VERIFIED_PUBLIC_DOMAIN,
        usage_purpose=UsagePurpose.PERSONAL_LEARNING,
        confirmed_by=ConfirmedBy(type="human"),
    )
    manifest = build_credit_manifest([record])
    assert manifest["credits"][0]["source_id"] == "confirmed"

    unconfirmed_manifest = build_credit_manifest(
        [
            RightsRecord(
                source_id="user-asserted",
                status=RightsStatus.USER_ASSERTED_PRIVATE_USE,
                usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            )
        ]
    )
    assert unconfirmed_manifest["credits"] == []


@pytest.mark.unit
def test_tc_rights_001_08() -> None:
    """TC-RIGHTS-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `RightsRecord/CreditEntry/DistributionDecision`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError):
        RightsRecord(source_id="", status=RightsStatus.UNVERIFIED, usage_purpose=UsagePurpose.PERSONAL_LEARNING)

    service = RightsService()
    with pytest.raises(AppError):
        service.evaluate_local_generation(None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        service.evaluate_distribution([])

    with pytest.raises(AppError):
        build_credit_manifest(None)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_rights_001_10() -> None:
    """TC-RIGHTS-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    records = [
        RightsRecord(
            source_id="stable-book",
            status=RightsStatus.VERIFIED_OPEN_LICENSE,
            usage_purpose=UsagePurpose.PERSONAL_LEARNING,
            evidence=Evidence(license_name="CC BY-SA 4.0"),
            confirmed_by=ConfirmedBy(type="human"),
        )
    ]
    snapshot = copy.deepcopy(records)

    build_credit_manifest(records)
    RightsService().evaluate_distribution(
        [
            RightsRecord(
                source_id="unverified-book",
                status=RightsStatus.UNVERIFIED,
                usage_purpose=UsagePurpose.PUBLIC_DISTRIBUTION,
            )
        ]
    )

    assert records == snapshot
