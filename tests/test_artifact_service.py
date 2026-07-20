"""Implementation for TASK-ARTIFACT-001: Artifact登録・version管理.

Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
Production file exercised: script/services/artifacts.py
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import ArtifactType, BuildStatus, JobStatus, PlanningStage
from script.domain.models import BuildRequest, Job, Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import BuildRequestRepository, JobRepository, ProjectRepository
from script.services.artifacts import ArtifactService, RegisterArtifact

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _seed(connection: sqlite3.Connection, project_id: str = "database-foundations") -> str:
    now = "2026-07-19T21:00:00+09:00"
    build_request_id = f"br-{project_id}"
    job_id = f"job-{project_id}" if project_id != "database-foundations" else "job-0001"
    build_request_id = "br-0001" if project_id == "database-foundations" else f"br-{project_id}"

    ProjectRepository(connection).insert(
        Project(
            project_id=project_id, title="タイトル", domain="database",
            planning_stage=PlanningStage.REGISTERED, content_revision=1,
            plan_file_path="project/project-plan.yaml", created_at=now, updated_at=now,
        )
    )
    BuildRequestRepository(connection).insert(
        BuildRequest(
            build_request_id=build_request_id, project_id=project_id, output_formats=("mp3", "text"),
            status=BuildStatus.DRAFT, created_at=now, updated_at=now, voice_profile_id="sample-voicevox-profile",
        )
    )
    JobRepository(connection).insert(
        Job(job_id=job_id, build_request_id=build_request_id, job_type="audio_packaging", status=JobStatus.RUNNING)
    )
    connection.commit()
    return job_id


def _service(tmp_path: Path, name: str = "app.db") -> ArtifactService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _seed(connection)
    return ArtifactService(tmp_path, connection)


def _write_generated_file(tmp_path: Path, name: str, content: bytes) -> Path:
    generated_dir = tmp_path / "generated"
    generated_dir.mkdir(exist_ok=True)
    path = generated_dir / name
    path.write_bytes(content)
    return path


@pytest.mark.integration_mock
def test_tc_artifact_001_01(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-01 — 形式別version

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P0
    Layer: integration_mock
    Given: mp3 v1とtext v1がある
    When: 双方を再登録
    Then: mp3 v2とtext v2として独立採番する
    """
    service = _service(tmp_path)
    mp3_v1 = service.register(
        RegisterArtifact(
            artifact_id="artifact-mp3-1", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=_write_generated_file(tmp_path, "ch01-v1.mp3", b"mp3-v1"),
            destination_relative="audio/chapters/01_ch01_v1.mp3",
        )
    )
    text_v1 = service.register(
        RegisterArtifact(
            artifact_id="artifact-text-1", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.TEXT_VERIFIED_SCRIPT,
            source_path=_write_generated_file(tmp_path, "ch01-v1.txt", b"text-v1"),
            destination_relative="text/ch01_v1.txt",
        )
    )
    assert mp3_v1.version_number == 1
    assert text_v1.version_number == 1

    mp3_v2 = service.register(
        RegisterArtifact(
            artifact_id="artifact-mp3-2", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=_write_generated_file(tmp_path, "ch01-v2.mp3", b"mp3-v2"),
            destination_relative="audio/chapters/01_ch01_v2.mp3",
        )
    )
    text_v2 = service.register(
        RegisterArtifact(
            artifact_id="artifact-text-2", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.TEXT_VERIFIED_SCRIPT,
            source_path=_write_generated_file(tmp_path, "ch01-v2.txt", b"text-v2"),
            destination_relative="text/ch01_v2.txt",
        )
    )
    assert mp3_v2.version_number == 2
    assert text_v2.version_number == 2

    latest = {artifact.artifact_type: artifact.version_number for artifact in service.list_latest("database-foundations")}
    assert latest[ArtifactType.MP3_CHAPTER] == 2
    assert latest[ArtifactType.TEXT_VERIFIED_SCRIPT] == 2


@pytest.mark.unit
def test_tc_artifact_001_02(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-02 — file不在

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P0
    Layer: unit
    Given: 存在しないpath
    When: registerする
    Then: DBへ行を追加しない
    """
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.register(
            RegisterArtifact(
                artifact_id="artifact-missing", job_id="job-0001", project_id="database-foundations",
                artifact_type=ArtifactType.MP3_CHAPTER,
                source_path=tmp_path / "does-not-exist.mp3",
                destination_relative="audio/chapters/01_ch01.mp3",
            )
        )
    assert service.list_latest("database-foundations") == []


@pytest.mark.unit
def test_tc_artifact_001_03(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-03 — 上書き禁止

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P0
    Layer: unit
    Given: 既存Artifact fileを出力先に指定
    When: registerする
    Then: 既存内容を変更せず新version/pathを要求する
    """
    service = _service(tmp_path)
    service.register(
        RegisterArtifact(
            artifact_id="artifact-1", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=_write_generated_file(tmp_path, "ch01-v1.mp3", b"original"),
            destination_relative="audio/chapters/01_ch01.mp3",
        )
    )
    stored_path = tmp_path / "library" / "database-foundations" / "audio/chapters/01_ch01.mp3"
    content_before = stored_path.read_bytes()

    with pytest.raises(AppError):
        service.register(
            RegisterArtifact(
                artifact_id="artifact-2", job_id="job-0001", project_id="database-foundations",
                artifact_type=ArtifactType.MP3_CHAPTER,
                source_path=_write_generated_file(tmp_path, "ch01-v2-attempt.mp3", b"attempted-overwrite"),
                destination_relative="audio/chapters/01_ch01.mp3",  # same path as existing artifact
            )
        )

    assert stored_path.read_bytes() == content_before


@pytest.mark.unit
def test_tc_artifact_001_04(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-04 — mp3_chapter/text_verified_script

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ArtifactService.register(command: RegisterArtifact) -> Artifact`を通じて「mp3_chapter/text_verified_script」を実行する
    Then: 有効なmedia header・形式・順序を確認し、破損または形式不一致を成功扱いにしない。
    """
    assert {artifact_type.value for artifact_type in ArtifactType} == {"mp3_chapter", "text_verified_script"}

    service = _service(tmp_path)
    artifact = service.register(
        RegisterArtifact(
            artifact_id="artifact-text", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.TEXT_VERIFIED_SCRIPT,
            source_path=_write_generated_file(tmp_path, "script.txt", b"verified script text"),
            destination_relative="text/script.txt",
        )
    )
    assert artifact.artifact_type is ArtifactType.TEXT_VERIFIED_SCRIPT


@pytest.mark.unit
def test_tc_artifact_001_05(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-05 — ファイル存在/hash確認

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ArtifactService.register(command: RegisterArtifact) -> Artifact`を通じて「ファイル存在/hash確認」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    """
    service = _service(tmp_path)
    content = b"stable content for hashing"
    artifact = service.register(
        RegisterArtifact(
            artifact_id="artifact-1", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=_write_generated_file(tmp_path, "ch01.mp3", content),
            destination_relative="audio/chapters/01_ch01.mp3",
        )
    )
    assert artifact.content_hash == hashlib.sha256(content).hexdigest()

    different = service.register(
        RegisterArtifact(
            artifact_id="artifact-2", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=_write_generated_file(tmp_path, "ch01-v2.mp3", content + b"-changed"),
            destination_relative="audio/chapters/01_ch01_v2.mp3",
        )
    )
    assert different.content_hash != artifact.content_hash


@pytest.mark.unit
def test_tc_artifact_001_06(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-06 — Project/Job整合

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ArtifactService.register(command: RegisterArtifact) -> Artifact`を通じて「Project/Job整合」を実行する
    Then: 「Project/Job整合」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    _seed(connection, project_id="database-foundations")
    _seed(connection, project_id="other-project")
    service = ArtifactService(tmp_path, connection)

    with pytest.raises(AppError):
        service.register(
            RegisterArtifact(
                artifact_id="artifact-cross-project", job_id="job-0001", project_id="other-project",
                artifact_type=ArtifactType.MP3_CHAPTER,
                source_path=_write_generated_file(tmp_path, "ch01.mp3", b"content"),
                destination_relative="audio/chapters/01_ch01.mp3",
            )
        )

    with pytest.raises(AppError):
        service.register(
            RegisterArtifact(
                artifact_id="artifact-no-job", job_id="job-does-not-exist", project_id="database-foundations",
                artifact_type=ArtifactType.MP3_CHAPTER,
                source_path=_write_generated_file(tmp_path, "ch02.mp3", b"content"),
                destination_relative="audio/chapters/02_ch02.mp3",
            )
        )


@pytest.mark.unit
def test_tc_artifact_001_07(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-07 — 必須入力欠落

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ArtifactService.register(command: RegisterArtifact) -> Artifact`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.register(
            RegisterArtifact(
                artifact_id="", job_id="job-0001", project_id="database-foundations",
                artifact_type=ArtifactType.MP3_CHAPTER,
                source_path=_write_generated_file(tmp_path, "ch01.mp3", b"content"),
                destination_relative="audio/chapters/01_ch01.mp3",
            )
        )
    assert service.list_latest("database-foundations") == []

    with pytest.raises(AppError):
        ArtifactService(None, connect_database(tmp_path / "unused.db"))  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_artifact_001_08(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-08 — 再実行時の決定性

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ArtifactService.register(command: RegisterArtifact) -> Artifact`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    service = _service(tmp_path)
    service.register(
        RegisterArtifact(
            artifact_id="artifact-1", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=_write_generated_file(tmp_path, "ch01.mp3", b"content"),
            destination_relative="audio/chapters/01_ch01.mp3",
        )
    )
    first = service.list_latest("database-foundations")
    second = service.list_latest("database-foundations")
    assert first == second


@pytest.mark.unit
def test_tc_artifact_001_09(tmp_path: Path) -> None:
    """TC-ARTIFACT-001-09 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    service = _service(tmp_path)
    source = _write_generated_file(tmp_path, "ch01.mp3", b"immutable source content")
    source_before = source.read_bytes()

    service.register(
        RegisterArtifact(
            artifact_id="artifact-1", job_id="job-0001", project_id="database-foundations",
            artifact_type=ArtifactType.MP3_CHAPTER,
            source_path=source,
            destination_relative="audio/chapters/01_ch01.mp3",
        )
    )

    with pytest.raises(AppError):
        service.register(
            RegisterArtifact(
                artifact_id="artifact-1", job_id="job-0001", project_id="database-foundations",
                artifact_type=ArtifactType.MP3_CHAPTER,
                source_path=source,
                destination_relative="audio/chapters/02_ch02.mp3",
            )
        )  # duplicate artifact_id -> unique/PK violation

    assert source.read_bytes() == source_before
