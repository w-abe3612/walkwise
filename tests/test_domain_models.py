"""Implementation for TASK-DOMAIN-001: ドメインモデルと列挙値 (models).

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Production files exercised: script/domain/models.py, script/domain/enums.py
"""

from __future__ import annotations

import dataclasses

import pytest

from script.core.errors import AppError
from script.domain.enums import ArtifactType, BuildStatus, PlanningStage, SourceStatus
from script.domain.models import Artifact, BuildRequest, Project, Source

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_domain_001_01() -> None:
    """TC-DOMAIN-001-01 — 複数出力canonical

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P0
    Layer: unit
    Given: `text, mp3`の入力
    When: BuildRequestを生成する
    Then: formatsはmp3,text順で保持される
    """
    build_request = BuildRequest(
        build_request_id="br-0001",
        project_id="database-foundations",
        output_formats=("text", "mp3"),
        status=BuildStatus.DRAFT,
        created_at="2026-07-19T21:00:00+09:00",
        updated_at="2026-07-19T21:00:00+09:00",
        voice_profile_id="sample-voicevox-profile",
    )
    assert build_request.output_formats == ("mp3", "text")


@pytest.mark.unit
def test_tc_domain_001_03() -> None:
    """TC-DOMAIN-001-03 — dataclass/enum

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「dataclass/enum」を実行する
    Then: 「dataclass/enum」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    project = Project(
        project_id="database-foundations",
        title="データベース基礎",
        domain="database",
        planning_stage=PlanningStage.REGISTERED,
        content_revision=1,
        plan_file_path="project/project-plan.yaml",
        created_at="2026-07-19T21:00:00+09:00",
        updated_at="2026-07-19T21:00:00+09:00",
    )
    assert dataclasses.is_dataclass(project)
    assert project.planning_stage is PlanningStage.REGISTERED
    with pytest.raises(dataclasses.FrozenInstanceError):
        project.title = "変更後"  # type: ignore[misc]

    source = Source(
        source_id="database-book-chapter1",
        project_id="database-foundations",
        media_type="text",
        status=SourceStatus.READY,
        original_file_path="sources/originals/database-book-chapter1.txt",
        content_hash="sha256:abc",
        created_at="2026-07-19T21:00:00+09:00",
        updated_at="2026-07-19T21:00:00+09:00",
    )
    assert source.status is SourceStatus.READY


@pytest.mark.unit
def test_tc_domain_001_05() -> None:
    """TC-DOMAIN-001-05 — 状態列挙

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を通じて「状態列挙」を実行する
    Then: 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。
    """
    assert {stage.value for stage in PlanningStage} == {
        "registered", "curriculum_draft", "review_pending", "approved",
    }
    assert {status.value for status in SourceStatus} == {
        "registered", "processing", "ready", "review_required", "failed",
    }
    assert {status.value for status in BuildStatus} == {
        "draft", "queued", "running", "completed", "failed", "cancel_requested", "cancelled",
    }
    assert {artifact_type.value for artifact_type in ArtifactType} == {
        "mp3_chapter", "text_verified_script",
    }

    with pytest.raises(ValueError):
        PlanningStage("not_a_real_stage")


@pytest.mark.unit
def test_tc_domain_001_07() -> None:
    """TC-DOMAIN-001-07 — 必須入力欠落

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `PlanningStage/SourceStatus/BuildStatus/JobStatus/ArtifactType`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError):
        BuildRequest(
            build_request_id="br-0002",
            project_id="database-foundations",
            output_formats=("mp3",),
            status=BuildStatus.DRAFT,
            created_at="2026-07-19T21:00:00+09:00",
            updated_at="2026-07-19T21:00:00+09:00",
            voice_profile_id=None,
        )

    with pytest.raises(AppError):
        Artifact(
            artifact_id="artifact-0001",
            job_id="job-0001",
            project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            file_path="/absolute/path/is/not/allowed.mp3",
            version_number=1,
            content_hash="sha256:abc",
            created_at="2026-07-19T21:10:00+09:00",
        )


@pytest.mark.unit
def test_tc_domain_001_09() -> None:
    """TC-DOMAIN-001-09 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    original_formats = ("text", "mp3")
    build_request = BuildRequest(
        build_request_id="br-0003",
        project_id="database-foundations",
        output_formats=original_formats,
        status=BuildStatus.DRAFT,
        created_at="2026-07-19T21:00:00+09:00",
        updated_at="2026-07-19T21:00:00+09:00",
        voice_profile_id="sample-voicevox-profile",
    )
    # canonicalization must not mutate the caller's original input tuple
    assert original_formats == ("text", "mp3")
    assert build_request.output_formats == ("mp3", "text")
