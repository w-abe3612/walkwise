"""script/migration/report.py — 公開契約: MigrationReport.

Contract: docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md
Spec: docs/specifications/15-migration-and-compatibility.md(5節, 10節)
"""

from __future__ import annotations

from typing import Any


class MigrationReport:
    """変換、warning、provenance、未移行項目を記録する(15-migration-and-compatibility.md 5, 10節)。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
        self.data.setdefault("conversions", [])
        self.data.setdefault("warnings", [])
        self.data.setdefault("provenance", [])
        self.data.setdefault("unmigrated", [])

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def add_conversion(self, description: str) -> None:
        """行われた変換の説明を記録する。"""
        self.data["conversions"].append(description)

    def add_warning(self, message: str) -> None:
        """推測せず残したwarningを記録する(15節 10節)。"""
        self.data["warnings"].append(message)

    def add_provenance(self, record: dict[str, Any]) -> None:
        """旧入力由来を示すprovenanceを記録する(15節 5節)。"""
        self.data["provenance"].append(record)

    def add_unmigrated(self, field_name: str, value: Any) -> None:
        """変換不能な項目を推測せずに残す(15節 5節)。"""
        self.data["unmigrated"].append({"field": field_name, "value": value})

    def to_dict(self) -> dict[str, Any]:
        """report内容をJSON化可能なdictとして返す。"""
        return dict(self.data)
