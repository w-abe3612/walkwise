"""Implementation for TASK-DOMAIN-001: ドメインモデルと列挙値 (validation).

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Production file exercised: script/domain/validation.py (and models.py for TC-06)
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError
from script.domain.enums import ArtifactType, BuildStatus
from script.domain.models import Artifact
from script.domain.validation import canonicalize_output_formats, validate_build_request

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_domain_001_02() -> None:
    """TC-DOMAIN-001-02 — voice条件

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P0
    Layer: unit
    Given: text-onlyとmp3を含む入力
    When: validationを行う
    Then: text-onlyはvoice null可、mp3はnull拒否
    """
    validate_build_request(("text",), None)  # must not raise

    with pytest.raises(AppError):
        validate_build_request(("mp3",), None)

    validate_build_request(("mp3", "text"), "sample-voicevox-profile")  # must not raise


@pytest.mark.unit
def test_tc_domain_001_04() -> None:
    """TC-DOMAIN-001-04 — 必須項目

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「必須項目」を実行する
    Then: 「必須項目」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    with pytest.raises(AppError):
        canonicalize_output_formats(())

    with pytest.raises(AppError):
        canonicalize_output_formats(("epub",))

    with pytest.raises(AppError):
        canonicalize_output_formats(("mp3", "mp3"))


@pytest.mark.unit
def test_tc_domain_001_06() -> None:
    """TC-DOMAIN-001-06 — 相対path value object

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「相対path value object」を実行する
    Then: 保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。
    """
    artifact = Artifact(
        artifact_id="artifact-0002",
        job_id="job-0001",
        project_id="database-foundations",
        artifact_type=ArtifactType.MP3_CHAPTER,
        file_path="audio/chapters/01_ch01.mp3",
        version_number=1,
        content_hash="sha256:abc",
        created_at="2026-07-19T21:10:00+09:00",
    )
    assert artifact.file_path == "audio/chapters/01_ch01.mp3"

    with pytest.raises(AppError):
        Artifact(
            artifact_id="artifact-0003",
            job_id="job-0001",
            project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            file_path="C:/absolute/path.mp3",
            version_number=1,
            content_hash="sha256:abc",
            created_at="2026-07-19T21:10:00+09:00",
        )

    with pytest.raises(AppError):
        Artifact(
            artifact_id="artifact-0004",
            job_id="job-0001",
            project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            file_path="../outside/escape.mp3",
            version_number=1,
            content_hash="sha256:abc",
            created_at="2026-07-19T21:10:00+09:00",
        )


@pytest.mark.unit
def test_tc_domain_001_08() -> None:
    """TC-DOMAIN-001-08 — 再実行時の決定性

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    first = canonicalize_output_formats(("text", "mp3"))
    second = canonicalize_output_formats(("text", "mp3"))
    assert first == second == ("mp3", "text")

    validate_build_request(("mp3",), "sample-voicevox-profile")
    validate_build_request(("mp3",), "sample-voicevox-profile")
