"""script/migration/adapters.py — 公開契約: migrate_legacy_project(path, destination) -> MigrationResult.

Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
Spec: docs/specifications/15-migration-and-compatibility.md(3, 4, 5, 6節), 02-process-input-output.md(12節)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from script.core.errors import AppError, ErrorCode
from script.core.serialization import dump_json, load_json, load_yaml
from script.migration.legacy_models import LegacyAudioInput, LegacyBook, LegacySection
from script.migration.report import MigrationReport

_KNOWN_BOOK_FIELDS = frozenset(
    {"bookId", "title", "deliverableTitle", "enableSections", "audioExportUnits", "tts"}
)
_KNOWN_SECTION_FIELDS = frozenset(
    {"sectionId", "fileName", "order", "fileTitle", "startPage", "endPage", "sourceId"}
)
_APPROVED_LEGACY_STATUSES = frozenset({"approved"})


def _default_clock() -> str:
    return datetime.now(timezone.utc).isoformat()


class MigrationResult:
    """`migrate_legacy_project`の戻り値を型付けする。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _has_new_format(source: Path) -> bool:
    return (source / "project" / "project-plan.yaml").exists()


def _read_legacy_approval(source: Path) -> dict[str, Any] | None:
    for candidate in (source / "project" / "approval.yaml", source / "approval.yaml"):
        if candidate.exists():
            data = load_yaml(candidate)
            if not isinstance(data, dict):
                raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid legacy approval file: {candidate}")
            return data
    return None


def migrate_legacy_project(
    path: Any,
    destination: Any,
    *,
    exists: Callable[[str], bool] | None = None,
    clock: Callable[[], str] | None = None,
) -> MigrationResult:
    """新形式を優先し、不足時だけ旧形式を変換する(15-migration-and-compatibility.md 3節)。

    Public contract: ``migrate_legacy_project(path, destination) -> MigrationResult``.
    """
    if not path:
        raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")
    if not destination:
        raise AppError(ErrorCode.VALIDATION_ERROR, "destination is required")

    source = Path(path)
    dest = Path(destination)
    resolve_clock = clock or _default_clock

    if _has_new_format(source):
        # 3節「新形式を優先して読む」: 旧形式を上書きしない。destinationへも書込まない。
        return MigrationResult(
            project_id=None,
            skipped=True,
            reason="new_format_present",
            chapters=(),
            report=MigrationReport().to_dict(),
        )

    book_path = source / "book.json"
    if not book_path.exists():
        raise AppError(ErrorCode.NOT_FOUND, f"legacy book.json not found: {book_path}")

    book_data = load_json(book_path)
    if not isinstance(book_data, dict):
        raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid legacy book.json: {book_path}")

    legacy_book = LegacyBook(**book_data)

    approval_data = _read_legacy_approval(source)
    if approval_data is not None:
        status = approval_data.get("status")
        if status not in _APPROVED_LEGACY_STATUSES:
            # 副作用(destinationへの書込)を一切開始する前に安定errorで停止する。
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"legacy approval is not migratable from status: {status!r}",
            )

    report = MigrationReport()
    for field_name in book_data:
        if field_name not in _KNOWN_BOOK_FIELDS:
            report.add_unmigrated(field_name, book_data[field_name])
            report.add_warning(f"unknown book.json field ignored: {field_name}")
    if approval_data is not None:
        report.add_conversion("legacy approval.yaml recognized as approved (approvals.yaml conversion deferred)")

    sections_path = source / "sections.json"
    section_entries: list[dict[str, Any]] = []
    if sections_path.exists():
        sections_data = load_json(sections_path)
        if not isinstance(sections_data, list):
            raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid legacy sections.json: {sections_path}")
        for entry in sections_data:
            if not isinstance(entry, dict):
                raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid legacy section entry: {entry!r}")
            legacy_section = LegacySection(**entry)
            for field_name in entry:
                if field_name not in _KNOWN_SECTION_FIELDS:
                    report.add_unmigrated(field_name, entry[field_name])
                    report.add_warning(f"unknown sections.json field ignored: {field_name}")
            section_entries.append(
                {
                    "chapter_id": legacy_section.chapter_id,
                    "order": entry.get("order", 0),
                    "file_title": entry.get("fileTitle", ""),
                    "source_id": entry.get("sourceId"),
                }
            )
    else:
        section_entries.append(
            {"chapter_id": "book", "order": 0, "file_title": legacy_book.title, "source_id": None}
        )

    resolve_exists = exists or (lambda relative: (source / relative).exists())

    chapters: list[dict[str, Any]] = []
    for entry in sorted(section_entries, key=lambda item: item["order"]):
        is_full_book = entry["chapter_id"] == "book" and not sections_path.exists()
        unit_id = "full_book" if is_full_book else entry["chapter_id"]

        if is_full_book:
            report.add_conversion("full_book unit normalized to book-level chapter")
            report.add_provenance(
                {"chapter_id": "book", "legacy_unit_id": "full_book", "normalized_unit_id": "book"}
            )

        audio_input = LegacyAudioInput(unit_id=unit_id, exists=resolve_exists)
        try:
            resolved = audio_input.resolve()
        except AppError:
            resolved = None

        if resolved is not None:
            report.add_provenance(
                {
                    "chapter_id": entry["chapter_id"],
                    "legacy_input": True,
                    "source_path": resolved["source_path"],
                    "imported_at": resolve_clock(),
                }
            )
            report.add_warning(f"legacy text input used for chapter: {entry['chapter_id']}")

        chapters.append(
            {
                "chapter_id": entry["chapter_id"],
                "order": entry["order"],
                "file_title": entry["file_title"],
                "source_id": entry["source_id"],
                "legacy_text_source": resolved["source_path"] if resolved else None,
            }
        )

    result_payload: dict[str, Any] = {
        "project_id": legacy_book.project_id,
        "skipped": False,
        "reason": None,
        "chapters": tuple(chapters),
        "report": report.to_dict(),
    }

    dump_json(
        dest / "migration-report.json",
        {
            "project_id": result_payload["project_id"],
            "chapters": result_payload["chapters"],
            "report": result_payload["report"],
        },
    )

    return MigrationResult(**result_payload)
