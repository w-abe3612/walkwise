"""Implementation for TASK-SOURCE-001: Source登録・状態管理サービス (service).

Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
Production files exercised: script/services/sources.py, script/schemas/source_metadata.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import PlanningStage, SourceStatus
from script.domain.models import Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.repositories import ProjectRepository
from script.services.sources import RegisterSource, SourceService

pytestmark = pytest.mark.mvp

_MIGRATIONS_DIR = Path(_persistence_pkg.__file__).resolve().parent / "sql"


def _service(tmp_path: Path, name: str = "app.db", project_id: str = "database-foundations") -> SourceService:
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
    connection.commit()
    return SourceService(tmp_path, connection)


def _write_input_file(tmp_path: Path, name: str, content: bytes) -> Path:
    input_dir = tmp_path / "incoming"
    input_dir.mkdir(exist_ok=True)
    path = input_dir / name
    path.write_bytes(content)
    return path


@pytest.mark.integration_mock
def test_tc_source_001_01(tmp_path: Path) -> None:
    """TC-SOURCE-001-01 — text即ready

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: integration_mock
    Given: UTF-8 textを登録
    When: registerする
    Then: immutable原本、hash、status readyが作成される
    """
    service = _service(tmp_path)
    input_file = _write_input_file(tmp_path, "chapter1.txt", "本文テキスト".encode("utf-8"))

    result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-chapter1", source_path=input_file)
    )

    assert result.source.status is SourceStatus.READY
    assert result.source.content_hash == hashlib.sha256(input_file.read_bytes()).hexdigest()

    stored_path = tmp_path / "library" / "database-foundations" / result.source.original_file_path
    assert stored_path.is_file()
    assert stored_path.read_bytes() == input_file.read_bytes()
    assert input_file.is_file()  # original input untouched


@pytest.mark.integration_mock
def test_tc_source_001_03(tmp_path: Path) -> None:
    """TC-SOURCE-001-03 — 重複hash warning

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: integration_mock
    Given: 同一bytesを2回登録
    When: registerする
    Then: 2件を追跡可能に保存しwarningを返す
    """
    service = _service(tmp_path)
    content = "同じ内容".encode("utf-8")
    first_input = _write_input_file(tmp_path, "first.txt", content)
    second_input = _write_input_file(tmp_path, "second.txt", content)

    first_result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-first", source_path=first_input)
    )
    assert first_result.duplicate_of is None

    second_result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-second", source_path=second_input)
    )
    assert second_result.duplicate_of == "src-first"

    listed = service.list_for_project("database-foundations")
    assert {source.source_id for source in listed} == {"src-first", "src-second"}


@pytest.mark.unit
def test_tc_source_001_05(tmp_path: Path) -> None:
    """TC-SOURCE-001-05 — Project相対path

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceMetadata.from_file(...) -> SourceMetadata`を通じて「Project相対path」を実行する
    Then: 保存値はProject root基準の相対pathとなり、絶対path・root外escapeは拒否される。
    """
    service = _service(tmp_path)
    input_file = _write_input_file(tmp_path, "chapter1.txt", b"content")

    result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-1", source_path=input_file)
    )
    assert not Path(result.source.original_file_path).is_absolute()

    with pytest.raises(AppError):
        service.register(
            RegisterSource(
                project_id="database-foundations",
                source_id="src-2",
                source_path=input_file,
                destination_relative="../outside/escape.txt",
            )
        )


@pytest.mark.unit
def test_tc_source_001_07(tmp_path: Path) -> None:
    """TC-SOURCE-001-07 — 再実行時の決定性

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `SourceMetadata.from_file(...) -> SourceMetadata`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    service = _service(tmp_path)
    input_file = _write_input_file(tmp_path, "chapter1.txt", b"same content")

    first_listed = service.list_for_project("database-foundations")
    second_listed = service.list_for_project("database-foundations")
    assert first_listed == second_listed == []

    result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-1", source_path=input_file)
    )
    first_get = service.list_for_project("database-foundations")
    second_get = service.list_for_project("database-foundations")
    assert first_get == second_get == [result.source]


@pytest.mark.unit
def test_tc_review_001_symlink_source_path_rejected(tmp_path: Path) -> None:
    """TASK-REVIEW-001 2.6節 — symlink経由のsource登録はfail-closedで拒否される
    (symlink先の実file内容がProject外にあってもcopy_immutableへ到達させない)。
    """
    service = _service(tmp_path)
    real_file = _write_input_file(tmp_path, "real.txt", b"outside project content")
    symlink_path = tmp_path / "incoming" / "link.txt"
    symlink_path.symlink_to(real_file)

    with pytest.raises(AppError):
        service.register(
            RegisterSource(project_id="database-foundations", source_id="src-symlink", source_path=symlink_path)
        )
