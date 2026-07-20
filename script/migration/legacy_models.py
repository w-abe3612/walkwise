"""script/migration/legacy_models.py — 公開契約: LegacyBook/LegacySection/LegacyAudioInput.

Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
Spec: docs/specifications/15-migration-and-compatibility.md(4節), 02-process-input-output.md(12節)
"""

from __future__ import annotations

from typing import Any, Callable

from script.core.errors import AppError, ErrorCode
from script.core.identifiers import normalize_unit_id

# 02-process-input-output.md 12節の優先順位3〜7(新形式のverified/script.yamlは対象外)。
_LEGACY_TEXT_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("text/speech/{unit}/text.txt", "text_speech"),
    ("text/merged/{unit}/speak_dedicated.txt", "speak_dedicated"),
    ("text/merged/{unit}/fixed.txt", "fixed"),
    ("text/merged/{unit}/merged_gemini_fixed.txt", "merged_gemini_fixed"),
    ("text/merged/{unit}/merged.txt", "merged"),
)


class LegacyBook:
    """旧book.jsonを型付けする(15-migration-and-compatibility.md 4節)。"""

    def __init__(self, **data: Any) -> None:
        book_id = data.get("bookId")
        if not book_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "bookId is required")
        self.data = dict(data)
        self.data.setdefault("title", "")
        self.data.setdefault("deliverableTitle", "")
        self.data.setdefault("enableSections", False)
        self.data.setdefault("audioExportUnits", [])
        self.data.setdefault("tts", {})

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def project_id(self) -> str:
        """bookIdをproject_idへ写像する(15節 表: bookId→project_id)。"""
        return str(self.data["bookId"])


class LegacySection:
    """旧sections.jsonの1件を型付けする(15-migration-and-compatibility.md 4節)。"""

    def __init__(self, **data: Any) -> None:
        raw_id = data.get("sectionId") or data.get("fileName")
        if not raw_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "sectionId or fileName is required")
        self.data = dict(data)
        self.data.setdefault("order", 0)
        self.data.setdefault("fileTitle", "")

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def chapter_id(self) -> str:
        """sectionIdまたはfileNameを互換chapter IDとして扱う(15節)。"""
        raw_id = self.data.get("sectionId") or self.data.get("fileName")
        return str(raw_id)


class LegacyAudioInput:
    """旧テキスト入力優先順位を型付けする(02-process-input-output.md 12節 3〜7)。"""

    def __init__(self, **data: Any) -> None:
        unit_id = data.get("unit_id")
        if not unit_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "unit_id is required")
        exists = data.get("exists")
        if exists is None or not callable(exists):
            raise AppError(ErrorCode.VALIDATION_ERROR, "exists callable is required")
        self.data = dict(data)
        self.data["unit_id"] = normalize_unit_id(str(unit_id))

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def resolve(self) -> dict[str, Any]:
        """優先順位に従い最初に存在する旧テキスト入力を返す(02節 12節)。

        戻り値には``legacy_input: True``を含め、旧入力を利用したことを
        呼び出し側がprovenance/warningへ記録できるようにする。
        """
        unit = str(self.data["unit_id"])
        exists: Callable[[str], bool] = self.data["exists"]
        for relative_template, source_label in _LEGACY_TEXT_CANDIDATES:
            relative_path = relative_template.format(unit=unit)
            if exists(relative_path):
                return {
                    "source_path": relative_path,
                    "source_label": source_label,
                    "legacy_input": True,
                }
        raise AppError(ErrorCode.NOT_FOUND, f"no legacy text input found for unit: {unit}")
