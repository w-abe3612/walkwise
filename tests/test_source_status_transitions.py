"""Implementation for TASK-SOURCE-001: Source登録・状態管理サービス (status transitions).

Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
Production files exercised: script/services/sources.py, script/schemas/source_metadata.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import script.persistence as _persistence_pkg
from script.core.errors import AppError
from script.domain.enums import PlanningStage, SourceStatus
from script.domain.models import Project
from script.persistence.database import connect_database
from script.persistence.migrations import MigrationRunner
from script.persistence.paths import ProjectPaths
from script.persistence.repositories import ProjectRepository
from script.schemas.source_metadata import SourceMetadata
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


@pytest.mark.unit
def test_tc_source_001_02(tmp_path: Path) -> None:
    """TC-SOURCE-001-02 — PDF/image processing

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: unit
    Given: PDFまたは画像を登録
    When: registerする
    Then: status registered/processingとなり後続Jobへ渡せる
    """
    service = _service(tmp_path)
    pdf_input = _write_input_file(tmp_path, "book.pdf", b"%PDF-1.4 fixture bytes")
    image_input = _write_input_file(tmp_path, "page-000001.png", b"\x89PNG fixture bytes")

    pdf_result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-pdf", source_path=pdf_input)
    )
    assert pdf_result.source.status is SourceStatus.REGISTERED
    assert pdf_result.source.media_type == "pdf"

    image_result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-image", source_path=image_input)
    )
    assert image_result.source.status is SourceStatus.REGISTERED
    assert image_result.source.media_type == "image"

    processing = service.transition("src-pdf", SourceStatus.PROCESSING)
    assert processing.status is SourceStatus.PROCESSING

    with pytest.raises(AppError):
        service.transition("src-image", SourceStatus.READY)  # registered -> ready is not a legal direct transition

    ready = service.transition("src-pdf", SourceStatus.READY)
    assert ready.status is SourceStatus.READY
    with pytest.raises(AppError):
        service.transition("src-pdf", SourceStatus.PROCESSING)  # ready is terminal


@pytest.mark.unit
def test_tc_source_001_04(tmp_path: Path) -> None:
    """TC-SOURCE-001-04 — SHA-256

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `SourceMetadata.from_file(...) -> SourceMetadata`を通じて「SHA-256」を実行する
    Then: 「SHA-256」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    import hashlib

    paths = ProjectPaths.for_root(tmp_path, "database-foundations")
    input_file = _write_input_file(tmp_path, "chapter1.txt", b"hash me")

    metadata = SourceMetadata.from_file(
        input_file, project_paths=paths, destination_relative="sources/originals/chapter1.txt"
    )
    assert metadata.content_hash == hashlib.sha256(b"hash me").hexdigest()
    assert metadata.media_type == "text"


@pytest.mark.unit
def test_tc_source_001_06(tmp_path: Path) -> None:
    """TC-SOURCE-001-06 — 必須入力欠落

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `SourceMetadata.from_file(...) -> SourceMetadata`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    paths = ProjectPaths.for_root(tmp_path, "database-foundations")
    existing_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError):
        SourceMetadata.from_file(None, project_paths=paths, destination_relative="sources/originals/x.txt")

    with pytest.raises(AppError):
        SourceMetadata.from_file(
            tmp_path / "does-not-exist.txt", project_paths=paths, destination_relative="sources/originals/x.txt"
        )

    assert sorted(tmp_path.iterdir()) == existing_before


@pytest.mark.unit
def test_tc_source_001_08(tmp_path: Path) -> None:
    """TC-SOURCE-001-08 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-SOURCE-001-source-metadata-service.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    service = _service(tmp_path)
    input_file = _write_input_file(tmp_path, "chapter1.txt", b"stable content")
    content_before = input_file.read_bytes()

    result = service.register(
        RegisterSource(project_id="database-foundations", source_id="src-1", source_path=input_file)
    )
    stored_path = tmp_path / "library" / "database-foundations" / result.source.original_file_path
    stored_before = stored_path.read_bytes()

    with pytest.raises(AppError):
        service.transition("src-1", SourceStatus.PROCESSING)  # ready is terminal, must fail without side effects

    assert input_file.read_bytes() == content_before
    assert stored_path.read_bytes() == stored_before
