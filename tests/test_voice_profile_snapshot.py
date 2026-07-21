"""Tests for TASK-BUILD-EXEC-001 §10: VoiceProfile snapshot(Job開始時に一度だけ読み込む不変表現)。

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(10, 14.4節)
Production file exercised: script/services/voice_profile_snapshot.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import PlanningStage, VoiceProfileRecordStatus
from script.domain.models import Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository
from script.services.voice_profile_snapshot import capture_voice_profile_snapshot
from script.services.voice_profiles import CreateVoiceProfile, UpdateVoiceProfile, VoiceProfileService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"
_NOW = "2026-07-22T00:00:00+09:00"


def _setup(tmp_path: Path, project_id: str = "proj-1"):
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    ProjectRepository(connection).insert(
        Project(
            project_id=project_id, title="t", domain="d", planning_stage=PlanningStage.REGISTERED,
            content_revision=1, plan_file_path="project/project-plan.yaml", created_at=_NOW, updated_at=_NOW,
        )
    )
    voice_service = VoiceProfileService(connection)
    voice_service.create(
        CreateVoiceProfile(
            voice_profile_id="vp-1", project_id=project_id, name="ナレーター1", engine="voicevox", speaker_id="3",
            settings_json='{"note": "initial"}',
        )
    )
    voice_service.update(UpdateVoiceProfile(voice_profile_id="vp-1", status=VoiceProfileRecordStatus.APPROVED))
    return connection, voice_service


@pytest.mark.unit
def test_tc_voice_snapshot_001_01_captures_all_fields(tmp_path: Path) -> None:
    """TC-VOICE-SNAPSHOT-001-01 — snapshotはVoiceProfileの全設定フィールドを保持する。"""
    connection, _ = _setup(tmp_path)
    snapshot = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")

    assert snapshot.voice_profile_id == "vp-1"
    assert snapshot.voice_profile_name == "ナレーター1"
    assert snapshot.project_id == "proj-1"
    assert snapshot.engine == "voicevox"
    assert snapshot.speaker_id == "3"
    assert snapshot.settings_json == '{"note": "initial"}'
    assert snapshot.voice_profile_config_hash


@pytest.mark.unit
def test_tc_voice_snapshot_001_02_same_config_same_hash(tmp_path: Path) -> None:
    """TC-VOICE-SNAPSHOT-001-02 — 同じ設定なら同じconfig_hashになる(決定的)。"""
    connection, _ = _setup(tmp_path)
    first = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")
    second = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")

    assert first.voice_profile_config_hash == second.voice_profile_config_hash


@pytest.mark.unit
def test_tc_voice_snapshot_001_03_changed_config_changes_hash(tmp_path: Path) -> None:
    """TC-VOICE-SNAPSHOT-001-03 — 設定が変わればconfig_hashも変わる。"""
    connection, voice_service = _setup(tmp_path)
    before = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")

    voice_service.update(UpdateVoiceProfile(voice_profile_id="vp-1", speed_scale=1.5))
    after = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")

    assert before.voice_profile_config_hash != after.voice_profile_config_hash


@pytest.mark.unit
def test_tc_voice_snapshot_001_04_mid_job_update_does_not_leak_into_existing_snapshot(tmp_path: Path) -> None:
    """TC-VOICE-SNAPSHOT-001-04 — 一度取得したsnapshotは、その後Profileが更新されても変化しない(不変)。"""
    connection, voice_service = _setup(tmp_path)
    snapshot_at_job_start = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")

    # Job実行中にVoiceProfileが更新されたと仮定する。
    voice_service.update(UpdateVoiceProfile(voice_profile_id="vp-1", speed_scale=2.0, name="更新後の名前"))

    assert snapshot_at_job_start.speed_scale == 1.0
    assert snapshot_at_job_start.voice_profile_name == "ナレーター1"

    # 新たにcaptureすれば更新後の値になる(=このモジュールはJobあたり1回だけ呼ばれる契約)。
    snapshot_after_update = capture_voice_profile_snapshot(connection, "proj-1", "vp-1")
    assert snapshot_after_update.speed_scale == 2.0
    assert snapshot_after_update.voice_profile_name == "更新後の名前"


@pytest.mark.unit
def test_tc_voice_snapshot_001_05_rejects_draft_profile(tmp_path: Path) -> None:
    """TC-VOICE-SNAPSHOT-001-05 — draft状態のVoiceProfileはsnapshot化できない(voice_profile_not_approved)。"""
    connection = connect_database(tmp_path / "app.db")
    MigrationRunner().apply_all(connection, _MIGRATIONS_DIR)
    ProjectRepository(connection).insert(
        Project(
            project_id="proj-1", title="t", domain="d", planning_stage=PlanningStage.REGISTERED,
            content_revision=1, plan_file_path="project/project-plan.yaml", created_at=_NOW, updated_at=_NOW,
        )
    )
    VoiceProfileService(connection).create(
        CreateVoiceProfile(voice_profile_id="vp-draft", project_id="proj-1", name="n", engine="voicevox", speaker_id="3")
    )

    with pytest.raises(AppError, match="voice_profile_not_approved"):
        capture_voice_profile_snapshot(connection, "proj-1", "vp-draft")


@pytest.mark.unit
def test_tc_voice_snapshot_001_06_rejects_cross_project_reference(tmp_path: Path) -> None:
    """TC-VOICE-SNAPSHOT-001-06 — 別ProjectのVoiceProfileはsnapshot化できない(voice_profile_project_mismatch)。"""
    connection, _ = _setup(tmp_path, project_id="proj-1")
    ProjectRepository(connection).insert(
        Project(
            project_id="proj-2", title="t2", domain="d", planning_stage=PlanningStage.REGISTERED,
            content_revision=1, plan_file_path="project/project-plan.yaml", created_at=_NOW, updated_at=_NOW,
        )
    )

    with pytest.raises(AppError, match="voice_profile_project_mismatch"):
        capture_voice_profile_snapshot(connection, "proj-2", "vp-1")
