"""Tests for TASK-BUILD-EXEC-001 §5-6: VoiceProfile DB永続化(Repository/Service).

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(5, 6, 14.2節)
Production files exercised: script/persistence/repositories.py (VoiceProfileRepository),
script/services/voice_profiles.py (VoiceProfileService), script/domain/models.py (VoiceProfileRecord),
script/domain/enums.py (VoiceProfileRecordStatus)
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import PlanningStage, VoiceProfileRecordStatus
from script.domain.models import Project, VoiceProfileRecord
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository, VoiceProfileRepository
from script.services.voice_profiles import CreateVoiceProfile, UpdateVoiceProfile, VoiceProfileService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"
_NOW = "2026-07-22T00:00:00+09:00"


def _service(tmp_path: Path, name: str = "app.db", project_ids: tuple[str, ...] = ("proj-1",)) -> VoiceProfileService:
    connection = connect_database(tmp_path / name)
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    projects = ProjectRepository(connection)
    for project_id in project_ids:
        projects.insert(
            Project(
                project_id=project_id,
                title=f"title-{project_id}",
                domain="test",
                planning_stage=PlanningStage.REGISTERED,
                content_revision=1,
                plan_file_path="project/project-plan.yaml",
                created_at=_NOW,
                updated_at=_NOW,
            )
        )
    return VoiceProfileService(connection)


@pytest.mark.unit
def test_tc_voice_profile_001_01_create_defaults_to_draft(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-01 — 新規作成はdraftになる。"""
    service = _service(tmp_path)
    record = service.create(
        CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="ナレーター1", engine="voicevox", speaker_id="3")
    )
    assert record.status is VoiceProfileRecordStatus.DRAFT
    assert record.settings_json == "{}"


@pytest.mark.unit
def test_tc_voice_profile_001_02_project_must_exist(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-02 — 存在しないProjectを参照する作成は拒否される。"""
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.create(
            CreateVoiceProfile(voice_profile_id="vp-1", project_id="does-not-exist", name="n", engine="voicevox", speaker_id="3")
        )


@pytest.mark.unit
def test_tc_voice_profile_001_03_name_unique_within_project(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-03 — 同一Project内でnameが重複する作成は拒否される。"""
    service = _service(tmp_path, project_ids=("proj-1", "proj-2"))
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="same-name", engine="voicevox", speaker_id="3"))

    with pytest.raises(AppError):
        service.create(
            CreateVoiceProfile(voice_profile_id="vp-2", project_id="proj-1", name="same-name", engine="voicevox", speaker_id="8")
        )

    # 別Projectであれば同名でも許可される。
    other = service.create(
        CreateVoiceProfile(voice_profile_id="vp-3", project_id="proj-2", name="same-name", engine="voicevox", speaker_id="8")
    )
    assert other.voice_profile_id == "vp-3"


@pytest.mark.unit
def test_tc_voice_profile_001_04_required_fields(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-04 — 必須項目欠落(id/project_id/name/engine)は副作用前に拒否される。"""
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.create(CreateVoiceProfile(voice_profile_id="", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))
    with pytest.raises(AppError):
        service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="", name="n", engine="voicevox", speaker_id="3"))
    with pytest.raises(AppError):
        service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="", engine="voicevox", speaker_id="3"))
    with pytest.raises(AppError):
        service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="", speaker_id="3"))
    assert service.list_by_project("proj-1") == []


@pytest.mark.unit
def test_tc_voice_profile_001_05_numeric_ranges_reject_invalid(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-05 — 数値設定は既存VoiceParameters/VoicePauses schemaの範囲外だと拒否される。"""
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.create(
            CreateVoiceProfile(
                voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
                speed_scale=0.0,
            )
        )
    with pytest.raises(AppError):
        service.create(
            CreateVoiceProfile(
                voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
                sentence_pause_ms=-1,
            )
        )


@pytest.mark.unit
def test_tc_voice_profile_001_06_settings_json_must_be_object(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-06 — settings_jsonはJSON objectでなければ拒否される。"""
    service = _service(tmp_path)
    with pytest.raises(AppError):
        service.create(
            CreateVoiceProfile(
                voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
                settings_json="[1,2,3]",
            )
        )
    with pytest.raises(AppError):
        service.create(
            CreateVoiceProfile(
                voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
                settings_json="not json",
            )
        )


@pytest.mark.unit
def test_tc_voice_profile_001_07_get_not_found(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-07 — 存在しないIDのgetはvoice_profile_not_foundを返す。"""
    service = _service(tmp_path)
    with pytest.raises(AppError, match="voice_profile_not_found"):
        service.get("does-not-exist")


@pytest.mark.unit
def test_tc_voice_profile_001_08_cross_project_reference_rejected(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-08 — 別ProjectのVoiceProfileをget_for_projectで参照すると拒否される。"""
    service = _service(tmp_path, project_ids=("proj-1", "proj-2"))
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))

    with pytest.raises(AppError, match="voice_profile_project_mismatch"):
        service.get_for_project("vp-1", "proj-2")


@pytest.mark.unit
def test_tc_voice_profile_001_09_list_by_project_scoped(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-09 — list_by_projectは指定Projectのものだけを返す。"""
    service = _service(tmp_path, project_ids=("proj-1", "proj-2"))
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="a", engine="voicevox", speaker_id="3"))
    service.create(CreateVoiceProfile(voice_profile_id="vp-2", project_id="proj-2", name="b", engine="voicevox", speaker_id="3"))

    proj1_list = service.list_by_project("proj-1")
    assert [record.voice_profile_id for record in proj1_list] == ["vp-1"]


@pytest.mark.unit
def test_tc_voice_profile_001_10_update_status_transitions(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-10 — updateでdraft→approvedへ遷移できる。"""
    service = _service(tmp_path)
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))

    updated = service.update(UpdateVoiceProfile(voice_profile_id="vp-1", status=VoiceProfileRecordStatus.APPROVED))
    assert updated.status is VoiceProfileRecordStatus.APPROVED


@pytest.mark.unit
def test_tc_voice_profile_001_11_update_rejects_duplicate_name(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-11 — 同一Project内で既存の別Profileと同じnameへのupdateは拒否される。"""
    service = _service(tmp_path)
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="a", engine="voicevox", speaker_id="3"))
    service.create(CreateVoiceProfile(voice_profile_id="vp-2", project_id="proj-1", name="b", engine="voicevox", speaker_id="3"))

    with pytest.raises(AppError):
        service.update(UpdateVoiceProfile(voice_profile_id="vp-2", name="a"))


@pytest.mark.unit
def test_tc_voice_profile_001_12_archive_is_not_physical_delete(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-12 — archiveは物理削除せず、statusをarchivedにするだけ(履歴保持)。"""
    service = _service(tmp_path)
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))

    archived = service.archive("vp-1")
    assert archived.status is VoiceProfileRecordStatus.ARCHIVED

    still_there = service.get("vp-1")
    assert still_there.status is VoiceProfileRecordStatus.ARCHIVED

    # 冪等: 二度archiveしてもエラーにならない。
    archived_again = service.archive("vp-1")
    assert archived_again.status is VoiceProfileRecordStatus.ARCHIVED


@pytest.mark.unit
def test_tc_voice_profile_001_13_archived_cannot_be_updated(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-13 — archived状態のProfileは更新できない(voice_profile_archived)。"""
    service = _service(tmp_path)
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))
    service.archive("vp-1")

    with pytest.raises(AppError, match="voice_profile_archived"):
        service.update(UpdateVoiceProfile(voice_profile_id="vp-1", name="renamed"))


@pytest.mark.unit
def test_tc_voice_profile_001_14_assert_usable_for_build_requires_approved(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-14 — draftはBuildに使用できない。approvedのみ使用できる。"""
    service = _service(tmp_path)
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))

    with pytest.raises(AppError, match="voice_profile_not_approved"):
        service.assert_usable_for_build("vp-1", "proj-1")

    service.update(UpdateVoiceProfile(voice_profile_id="vp-1", status=VoiceProfileRecordStatus.APPROVED))
    usable = service.assert_usable_for_build("vp-1", "proj-1")
    assert usable.voice_profile_id == "vp-1"


@pytest.mark.unit
def test_tc_voice_profile_001_15_assert_usable_for_build_rejects_archived(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-15 — archivedは新規Buildで選択できない。"""
    service = _service(tmp_path)
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))
    service.update(UpdateVoiceProfile(voice_profile_id="vp-1", status=VoiceProfileRecordStatus.APPROVED))
    service.archive("vp-1")

    with pytest.raises(AppError, match="voice_profile_archived"):
        service.assert_usable_for_build("vp-1", "proj-1")


@pytest.mark.unit
def test_tc_voice_profile_001_16_assert_usable_for_build_rejects_cross_project(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-16 — 別ProjectのVoiceProfileはBuildで使用できない。"""
    service = _service(tmp_path, project_ids=("proj-1", "proj-2"))
    service.create(CreateVoiceProfile(voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3"))
    service.update(UpdateVoiceProfile(voice_profile_id="vp-1", status=VoiceProfileRecordStatus.APPROVED))

    with pytest.raises(AppError, match="voice_profile_project_mismatch"):
        service.assert_usable_for_build("vp-1", "proj-2")


@pytest.mark.unit
def test_tc_voice_profile_001_17_repository_round_trip(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-17 — Repository単体でinsert/find/list_by_project/updateがそのまま往復する。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    ProjectRepository(connection).insert(
        Project(
            project_id="proj-1", title="t", domain="d", planning_stage=PlanningStage.REGISTERED,
            content_revision=1, plan_file_path="project/project-plan.yaml", created_at=_NOW, updated_at=_NOW,
        )
    )
    repository = VoiceProfileRepository(connection)
    record = VoiceProfileRecord(
        voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
        speed_scale=1.0, pitch_scale=0.0, intonation_scale=1.0, volume_scale=1.0,
        sentence_pause_ms=250, paragraph_pause_ms=600, section_pause_ms=1000, chapter_pause_ms=1500,
        settings_json="{}", status=VoiceProfileRecordStatus.DRAFT, created_at=_NOW, updated_at=_NOW,
    )
    repository.insert(record)
    connection.commit()

    found = repository.find("vp-1")
    assert found == record

    listed = repository.list_by_project("proj-1")
    assert listed == [record]

    updated_record = VoiceProfileRecord(
        voice_profile_id="vp-1", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
        speed_scale=1.0, pitch_scale=0.0, intonation_scale=1.0, volume_scale=1.0,
        sentence_pause_ms=250, paragraph_pause_ms=600, section_pause_ms=1000, chapter_pause_ms=1500,
        settings_json="{}", status=VoiceProfileRecordStatus.APPROVED, created_at=_NOW, updated_at=_NOW,
    )
    repository.update(updated_record)
    connection.commit()
    assert repository.find("vp-1").status is VoiceProfileRecordStatus.APPROVED


@pytest.mark.unit
def test_tc_voice_profile_001_18_repository_update_missing_raises(tmp_path: Path) -> None:
    """TC-VOICE-PROFILE-001-18 — 存在しない行へのRepository.updateは失敗する。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    ProjectRepository(connection).insert(
        Project(
            project_id="proj-1", title="t", domain="d", planning_stage=PlanningStage.REGISTERED,
            content_revision=1, plan_file_path="project/project-plan.yaml", created_at=_NOW, updated_at=_NOW,
        )
    )
    repository = VoiceProfileRepository(connection)
    record = VoiceProfileRecord(
        voice_profile_id="does-not-exist", project_id="proj-1", name="n", engine="voicevox", speaker_id="3",
        speed_scale=1.0, pitch_scale=0.0, intonation_scale=1.0, volume_scale=1.0,
        sentence_pause_ms=250, paragraph_pause_ms=600, section_pause_ms=1000, chapter_pause_ms=1500,
        settings_json="{}", status=VoiceProfileRecordStatus.DRAFT, created_at=_NOW, updated_at=_NOW,
    )
    with pytest.raises(AppError):
        repository.update(record)
