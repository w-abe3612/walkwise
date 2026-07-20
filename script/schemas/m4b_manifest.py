"""script/schemas/m4b_manifest.py — 公開契約: M4BManifest.

Contract: docs/test-cases/TASK-M4B-001-m4b-output.md
Spec: docs/specifications/m4b-output.md(5.2, 5.3, 5.5節, 12節)
"""

from __future__ import annotations

from typing import Any

from script.core.errors import AppError, ErrorCode


class M4BManifest:
    """章開始時刻、cover/metadata由来、threshold statusを保持する(5.3, 5.5節, 8節例)。"""

    def __init__(self, **data: Any) -> None:
        if not data.get("project_id"):
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")
        chapters = data.get("chapters")
        if not chapters:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapters is required")
        chapter_ids = [chapter["chapter_id"] for chapter in chapters]
        if len(set(chapter_ids)) != len(chapter_ids):
            # 12節: 全chapterのchapter_idが一意である。
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate chapter_id detected: {chapter_ids}")

        validation = data.get("validation") or {}
        if not validation.get("all_chapters_passed"):
            # 12節: validation.all_chapters_passedがtrueのときのみ生成を許可する。
            raise AppError(ErrorCode.PERMISSION_DENIED, "all_chapters_passed must be true to construct a manifest")

        compatibility = data.get("compatibility") or {"status": "provisional", "tested_players": ()}
        if compatibility.get("status") == "approved" and not compatibility.get("tested_players"):
            # 12節: tested_playersが空の場合、statusをprovisionalのままapprovedにしない。
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "compatibility.status cannot be 'approved' without at least one tested_players entry",
            )

        self.data = dict(data)
        self.data["output_type"] = "m4b"
        self.data["chapters"] = tuple(chapters)
        self.data.setdefault("source_chapter_mp3s", ())
        self.data["source_chapter_mp3s"] = tuple(self.data["source_chapter_mp3s"])
        self.data.setdefault("metadata", {"title": None, "author": None, "narrator": None, "year": None})
        self.data["validation"] = dict(validation)
        self.data["compatibility"] = {
            "status": compatibility.get("status", "provisional"),
            "tested_players": tuple(compatibility.get("tested_players") or ()),
        }
        self.data.setdefault("content_revision", 1)
        self.data.setdefault("schema_version", "1.0")

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def to_mapping(self) -> dict[str, Any]:
        """8節のM4B manifest例と同じ形の決定的なdictを返す。"""
        return dict(self.data)
