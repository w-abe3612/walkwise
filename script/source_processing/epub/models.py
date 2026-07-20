"""script/source_processing/epub/models.py — 公開契約: EpubChapter/EpubExtractionReport.

Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
Spec: docs/specifications/epub-text-extraction.md(5.3, 5.5節)
"""

from __future__ import annotations

from typing import Any

from script.core.errors import AppError, ErrorCode


class EpubChapter:
    """spineの1itemrefに対応する章を型付けする(5.3, 5.5節)。"""

    def __init__(self, **data: Any) -> None:
        if data.get("spine_index") is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "spine_index is required")
        if not data.get("xhtml_path"):
            raise AppError(ErrorCode.VALIDATION_ERROR, "xhtml_path is required")
        self.data = dict(data)
        self.data.setdefault("order", self.data["spine_index"])
        self.data.setdefault("chapter_title", None)
        self.data.setdefault("text", "")
        self.data.setdefault("annotations", {"ruby": (), "footnotes": (), "images": ()})

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class EpubExtractionReport:
    """EPUB全体の抽出結果(spine順のchapter一覧)を型付けする(5.2, 5.3節)。"""

    def __init__(self, **data: Any) -> None:
        if not data.get("epub_version"):
            raise AppError(ErrorCode.VALIDATION_ERROR, "epub_version is required")
        if data.get("chapters") is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapters is required")
        self.data = dict(data)
        self.data["chapters"] = tuple(self.data["chapters"])
        self.data.setdefault("warnings", ())
        self.data["warnings"] = tuple(self.data["warnings"])
        self.data.setdefault("review_required", False)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
