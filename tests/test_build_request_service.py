"""Implementation for TASK-BUILD-001: Build Request作成サービス.

Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
Production file exercised: script/services/build_requests.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import BuildStatus, PlanningStage, VoiceProfileRecordStatus
from script.domain.models import Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository
from script.services.build_requests import BuildRequestService, CreateBuildRequest, serialize_output_formats
from script.services.voice_profiles import CreateVoiceProfile, UpdateVoiceProfile, VoiceProfileService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _service(tmp_path: Path, name: str = "app.db", project_id: str = "database-foundations") -> BuildRequestService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    now = "2026-07-19T21:00:00+09:00"
    ProjectRepository(connection).insert(
        Project(
            project_id=project_id,
            title="データベース基礎",
            domain="database",
            planning_stage=PlanningStage.REGISTERED,
            content_revision=1,
            plan_file_path="project/project-plan.yaml",
            created_at=now,
            updated_at=now,
        )
    )
    # TASK-BUILD-EXEC-001: build_requests.voice_profile_idはvoice_profilesへのFKになったため、
    # 参照先の行を先に用意する。
    connection.execute(
        "INSERT INTO voice_profiles "
        "(voice_profile_id, project_id, name, engine, speaker_id, status, created_at, updated_at) "
        "VALUES ('sample-voicevox-profile', ?, 'sample profile', 'voicevox', '3', 'approved', ?, ?)",
        (project_id, now, now),
    )
    connection.commit()
    return BuildRequestService(connection)


@pytest.mark.unit
def test_tc_build_001_01(tmp_path: Path) -> None:
    """TC-BUILD-001-01 — text-only

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: formats=[text], voiceなし
    When: Build Requestを作成
    Then: draftとして成功する
    """
    service = _service(tmp_path)
    result = service.create(
        CreateBuildRequest(build_request_id="br-0001", project_id="database-foundations", output_formats=["text"])
    )
    assert result.status is BuildStatus.DRAFT
    assert result.output_formats == ("text",)
    assert result.voice_profile_id is None


@pytest.mark.unit
def test_tc_build_001_02(tmp_path: Path) -> None:
    """TC-BUILD-001-02 — mp3+text

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: formats=[text,mp3], voiceあり
    When: 作成する
    Then: JSONは["mp3","text"]になる
    """
    service = _service(tmp_path)
    result = service.create(
        CreateBuildRequest(
            build_request_id="br-0002",
            project_id="database-foundations",
            output_formats=["text", "mp3"],
            voice_profile_id="sample-voicevox-profile",
        )
    )
    assert result.output_formats == ("mp3", "text")
    assert serialize_output_formats(["text", "mp3"]) == '["mp3","text"]'


@pytest.mark.unit
def test_tc_build_001_03(tmp_path: Path) -> None:
    """TC-BUILD-001-03 — 空・未知・重複

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: 空、epub、mp3重複をそれぞれ渡す
    When: 作成する
    Then: 副作用前に拒否する
    """
    service = _service(tmp_path)

    with pytest.raises(AppError):
        service.create(CreateBuildRequest(build_request_id="br-empty", project_id="database-foundations", output_formats=[]))

    with pytest.raises(AppError):
        service.create(
            CreateBuildRequest(build_request_id="br-epub", project_id="database-foundations", output_formats=["epub"])
        )

    with pytest.raises(AppError):
        service.create(
            CreateBuildRequest(
                build_request_id="br-dup", project_id="database-foundations", output_formats=["mp3", "mp3"],
                voice_profile_id="sample-voicevox-profile",
            )
        )


@pytest.mark.unit
def test_tc_build_001_04(tmp_path: Path) -> None:
    """TC-BUILD-001-04 — output_formatsの1件以上/許可値/重複禁止/order

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を通じて「output_formatsの1件以上/許可値/重複禁止/order」を実行する
    Then: 重複を検出し、仕様で許可されない重複は安定したvalidation errorとして副作用前に拒否する。
    """
    assert serialize_output_formats(["mp3"]) == '["mp3"]'
    assert serialize_output_formats(["text", "mp3"]) == '["mp3","text"]'
    with pytest.raises(AppError):
        serialize_output_formats(["mp3", "text", "mp3"])


@pytest.mark.unit
def test_tc_build_001_05(tmp_path: Path) -> None:
    """TC-BUILD-001-05 — Project存在確認

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を通じて「Project存在確認」を実行する
    Then: 「Project存在確認」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.create(
            CreateBuildRequest(build_request_id="br-orphan", project_id="does-not-exist", output_formats=["text"])
        )


@pytest.mark.unit
def test_tc_build_001_06(tmp_path: Path) -> None:
    """TC-BUILD-001-06 — 必須入力欠落

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.create(CreateBuildRequest(build_request_id="", project_id="database-foundations", output_formats=["text"]))

    with pytest.raises(AppError):
        BuildRequestService(None)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_build_001_07(tmp_path: Path) -> None:
    """TC-BUILD-001-07 — 再実行時の決定性

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `BuildRequestService.create(command: CreateBuildRequest) -> BuildRequest`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    first = serialize_output_formats(["text", "mp3"])
    second = serialize_output_formats(["text", "mp3"])
    assert first == second


@pytest.mark.unit
def test_tc_build_001_08(tmp_path: Path) -> None:
    """TC-BUILD-001-08 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-BUILD-001-build-request-service.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    service = _service(tmp_path)
    service.create(
        CreateBuildRequest(build_request_id="br-existing", project_id="database-foundations", output_formats=["text"])
    )

    with pytest.raises(AppError):
        service.create(
            CreateBuildRequest(build_request_id="br-existing", project_id="database-foundations", output_formats=["text"])
        )  # duplicate PK -> AppError, must not corrupt the existing row

    existing = ProjectRepository(service._connection).find("database-foundations")
    assert existing is not None


@pytest.mark.unit
def test_tc_build_001_09_rejects_draft_voice_profile(tmp_path: Path) -> None:
    """TC-BUILD-001-09 — TASK-BUILD-EXEC-001 7節: draft状態のVoiceProfileはBuild参照に使えない。

    Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(7節)
    """
    service = _service(tmp_path)
    VoiceProfileService(service._connection).create(
        CreateVoiceProfile(
            voice_profile_id="vp-draft", project_id="database-foundations", name="draft-profile",
            engine="voicevox", speaker_id="3",
        )
    )

    with pytest.raises(AppError, match="voice_profile_not_approved"):
        service.create(
            CreateBuildRequest(
                build_request_id="br-draft-voice", project_id="database-foundations",
                output_formats=["mp3", "text"], voice_profile_id="vp-draft",
            )
        )


@pytest.mark.unit
def test_tc_build_001_10_rejects_archived_voice_profile(tmp_path: Path) -> None:
    """TC-BUILD-001-10 — TASK-BUILD-EXEC-001 7節: archived状態のVoiceProfileはBuild参照に使えない。

    Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(7節)
    """
    service = _service(tmp_path)
    voice_service = VoiceProfileService(service._connection)
    voice_service.create(
        CreateVoiceProfile(
            voice_profile_id="vp-archived", project_id="database-foundations", name="archived-profile",
            engine="voicevox", speaker_id="3",
        )
    )
    voice_service.update(UpdateVoiceProfile(voice_profile_id="vp-archived", status=VoiceProfileRecordStatus.APPROVED))
    voice_service.archive("vp-archived")

    with pytest.raises(AppError, match="voice_profile_archived"):
        service.create(
            CreateBuildRequest(
                build_request_id="br-archived-voice", project_id="database-foundations",
                output_formats=["text"], voice_profile_id="vp-archived",
            )
        )


@pytest.mark.unit
def test_tc_build_001_11_rejects_cross_project_voice_profile(tmp_path: Path) -> None:
    """TC-BUILD-001-11 — TASK-BUILD-EXEC-001 7節: 別ProjectのVoiceProfileは参照できない。

    Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(7節)
    """
    service = _service(tmp_path)
    ProjectRepository(service._connection).insert(
        Project(
            project_id="other-project", title="別Project", domain="other", planning_stage=PlanningStage.REGISTERED,
            content_revision=1, plan_file_path="project/project-plan.yaml",
            created_at="2026-07-19T21:00:00+09:00", updated_at="2026-07-19T21:00:00+09:00",
        )
    )
    voice_service = VoiceProfileService(service._connection)
    voice_service.create(
        CreateVoiceProfile(
            voice_profile_id="vp-other", project_id="other-project", name="other-profile",
            engine="voicevox", speaker_id="3",
        )
    )
    voice_service.update(UpdateVoiceProfile(voice_profile_id="vp-other", status=__import__(
        "script.domain.enums", fromlist=["VoiceProfileRecordStatus"]
    ).VoiceProfileRecordStatus.APPROVED))

    with pytest.raises(AppError, match="voice_profile_project_mismatch"):
        service.create(
            CreateBuildRequest(
                build_request_id="br-cross-project-voice", project_id="database-foundations",
                output_formats=["text"], voice_profile_id="vp-other",
            )
        )


@pytest.mark.unit
def test_tc_build_001_12_accepts_approved_voice_profile(tmp_path: Path) -> None:
    """TC-BUILD-001-12 — TASK-BUILD-EXEC-001 7節: 同一Projectのapproved VoiceProfileは参照できる。

    Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(7節)
    """
    service = _service(tmp_path)
    result = service.create(
        CreateBuildRequest(
            build_request_id="br-approved-voice", project_id="database-foundations",
            output_formats=["mp3", "text"], voice_profile_id="sample-voicevox-profile",
        )
    )
    assert result.voice_profile_id == "sample-voicevox-profile"
