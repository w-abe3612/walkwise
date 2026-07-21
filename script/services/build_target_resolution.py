"""script/services/build_target_resolution.py — 公開契約:
resolve_chapter_order, resolve_build_target.

Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(8, 9節)
Spec: docs/specifications/03-project-plan-schema.md, docs/specifications/05-script-segment-schema.md,
docs/specifications/07-approval-workflow.md

chapter順序の正本はproject-plan.yamlのchapters[]配列(order昇順)であり、folder名の
文字列順ではない(承認済み設計)。verified script
(chapters/<chapter_id>/verified/script.yaml)は、TTS呼び出しを一切開始する前に
全chapter分を検証し、1件でも問題があれば`build_target_not_ready`としてJob全体を
拒否できるよう、検証結果を(部分的に成功していても)集約して返す。draft/legacy原稿
へのfallbackは行わない。
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from script.core.errors import AppError, ErrorCode
from script.core.serialization import load_yaml
from script.persistence.paths import ProjectPaths
from script.persistence.repositories import ProjectRepository
from script.schemas.approvals import ApprovalGate
from script.services.approvals import ApprovalService

_CHAPTERS_DIR_NAME = "chapters"
_VERIFIED_SCRIPT_RELATIVE_PARTS = ("verified", "script.yaml")


@dataclass(frozen=True)
class ChapterOrderEntry:
    """project-plan.yaml chapters[]の1件(order昇順に並べたもの)。"""

    chapter_id: str
    order: int
    title: str | None = None


@dataclass(frozen=True)
class ChapterTarget:
    """検証に成功したchapterのbuild対象情報。"""

    chapter_id: str
    order: int
    script_relative_path: str
    content_hash: str


@dataclass(frozen=True)
class ChapterTargetError:
    """1chapter分の検証失敗(安定したerror_codeと人間向けdetail)。"""

    chapter_id: str
    error_code: str
    detail: str


@dataclass(frozen=True)
class BuildTargetResolution:
    """resolve_build_targetの戻り値。1件でもerrorsがあればis_readyはFalseになる。"""

    project_id: str
    chapters: tuple[ChapterTarget, ...]
    errors: tuple[ChapterTargetError, ...]

    @property
    def is_ready(self) -> bool:
        return not self.errors and bool(self.chapters)


def _extract_error_code(message: str) -> str:
    code, _, _ = message.partition(":")
    return code.strip()


def resolve_chapter_order(
    data_root: Path, connection: sqlite3.Connection, project_id: str
) -> tuple[ChapterOrderEntry, ...]:
    """project-plan.yamlのchapters[]をorder昇順で返す(folder名の文字列順は使わない)。"""
    if not project_id:
        raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")

    project = ProjectRepository(connection).find(project_id)
    if project is None:
        raise AppError(ErrorCode.NOT_FOUND, f"project not found: {project_id}")

    paths = ProjectPaths.for_root(data_root, project_id)
    plan_path = paths.resolve_relative(project.plan_file_path)
    plan_data = load_yaml(plan_path)

    raw_chapters = plan_data.get("chapters") if isinstance(plan_data, dict) else None
    if not raw_chapters:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            f"build_target_not_ready: project {project_id} has no chapters defined in project-plan.yaml",
        )

    entries: list[ChapterOrderEntry] = []
    for raw in raw_chapters:
        if not isinstance(raw, dict) or "chapter_id" not in raw or "order" not in raw:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"build_target_not_ready: malformed chapter entry in project-plan.yaml for project {project_id}",
            )
        entries.append(
            ChapterOrderEntry(chapter_id=raw["chapter_id"], order=raw["order"], title=raw.get("title"))
        )

    chapter_ids = [entry.chapter_id for entry in entries]
    if len(chapter_ids) != len(set(chapter_ids)):
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            f"build_target_not_ready: duplicate chapter_id in project-plan.yaml for project {project_id}",
        )

    orders = [entry.order for entry in entries]
    if len(orders) != len(set(orders)):
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            f"build_target_not_ready: duplicate order in project-plan.yaml for project {project_id}",
        )

    return tuple(sorted(entries, key=lambda entry: entry.order))


def _validate_verified_script(paths: ProjectPaths, chapter_id: str) -> tuple[str, str]:
    """1chapter分のverified script.yamlを検証し(relative_path, content_hash)を返す。

    fallback禁止: draft/narration-derivative/legacyの原稿は一切参照しない。
    """
    chapter_dir = paths.project_root / _CHAPTERS_DIR_NAME / chapter_id
    if not chapter_dir.is_dir():
        raise AppError(ErrorCode.NOT_FOUND, f"chapter_not_found: {chapter_id}")

    script_relative = "/".join((_CHAPTERS_DIR_NAME, chapter_id, *_VERIFIED_SCRIPT_RELATIVE_PARTS))
    script_path = chapter_dir.joinpath(*_VERIFIED_SCRIPT_RELATIVE_PARTS)

    if not script_path.is_file():
        raise AppError(ErrorCode.NOT_FOUND, f"verified_script_not_found: {script_relative}")

    raw_bytes = script_path.read_bytes()
    try:
        data = load_yaml(script_path)
    except AppError as exc:
        raise AppError(
            ErrorCode.VALIDATION_ERROR, f"verified_script_invalid: {script_relative}: {exc.message}"
        ) from exc

    if not isinstance(data, dict):
        raise AppError(
            ErrorCode.VALIDATION_ERROR, f"verified_script_invalid: {script_relative}: must be a mapping"
        )

    document_chapter_id = data.get("chapter_id")
    if document_chapter_id != chapter_id:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            f"verified_script_invalid: {script_relative}: chapter_id mismatch "
            f"(expected {chapter_id!r}, found {document_chapter_id!r})",
        )

    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        raise AppError(
            ErrorCode.VALIDATION_ERROR, f"verified_script_invalid: {script_relative}: segments must be a non-empty list"
        )

    segment_ids: list[str] = []
    orders: list[int] = []
    for segment in segments:
        if not isinstance(segment, dict):
            raise AppError(
                ErrorCode.VALIDATION_ERROR, f"verified_script_invalid: {script_relative}: each segment must be a mapping"
            )
        segment_id = segment.get("segment_id")
        order = segment.get("order")
        text = segment.get("text")
        if not segment_id or not isinstance(order, int) or not text:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"verified_script_invalid: {script_relative}: segment missing required segment_id/order/text",
            )
        segment_ids.append(segment_id)
        orders.append(order)

    if len(segment_ids) != len(set(segment_ids)):
        raise AppError(
            ErrorCode.VALIDATION_ERROR, f"verified_script_invalid: {script_relative}: duplicate segment_id"
        )
    if len(orders) != len(set(orders)):
        raise AppError(
            ErrorCode.VALIDATION_ERROR, f"verified_script_invalid: {script_relative}: duplicate segment order"
        )

    content_hash = hashlib.sha256(raw_bytes).hexdigest()
    return script_relative, content_hash


def resolve_build_target(data_root: Path, connection: sqlite3.Connection, project_id: str) -> BuildTargetResolution:
    """chapter順序解決 + verified script検証 + verified_script承認確認を一括で行う。

    TTS呼び出しを一切開始する前に呼び出すこと。1chapterでも問題があれば、Job全体を
    `build_target_not_ready`として拒否できるよう、全chapterの検証結果を返す
    (`BuildTargetResolution.is_ready`で判定する)。
    """
    order_entries = resolve_chapter_order(data_root, connection, project_id)
    paths = ProjectPaths.for_root(data_root, project_id)

    approval_detail: str | None = None
    try:
        ApprovalService(data_root).assert_gate(project_id, ApprovalGate.VERIFIED_SCRIPT)
    except AppError as exc:
        approval_detail = f"verified_script_not_approved: {exc.message}"

    chapters: list[ChapterTarget] = []
    errors: list[ChapterTargetError] = []

    for entry in order_entries:
        if approval_detail is not None:
            errors.append(
                ChapterTargetError(chapter_id=entry.chapter_id, error_code="verified_script_not_approved", detail=approval_detail)
            )
            continue
        try:
            relative_path, content_hash = _validate_verified_script(paths, entry.chapter_id)
        except AppError as exc:
            errors.append(
                ChapterTargetError(
                    chapter_id=entry.chapter_id, error_code=_extract_error_code(exc.message), detail=exc.message
                )
            )
            continue
        chapters.append(
            ChapterTarget(
                chapter_id=entry.chapter_id, order=entry.order, script_relative_path=relative_path, content_hash=content_hash
            )
        )

    return BuildTargetResolution(project_id=project_id, chapters=tuple(chapters), errors=tuple(errors))
