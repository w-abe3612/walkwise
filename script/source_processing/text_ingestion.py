"""script/source_processing/text_ingestion.py — 公開契約: TextIngestionAdapter.process(path, context) -> StructuredSource.

Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
Spec: docs/specifications/material-input-pipeline.md
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class StructuredSource:
    """original/extracted/normalized/structuredの各段階を保持する共通資料構造。"""

    original_path: str
    extracted_text: str
    normalized_text: str
    structured_text: str
    encoding: str = "utf-8"


def _normalize(text: str) -> str:
    """改行をLFへ統一し、行末の空白を除去する(source-preprocessing.mdの範囲外の最小限の正規化)。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines)


class TextIngestionAdapter:
    """UTF-8本文を共通資料構造(original/extracted/normalized/structured)へ変換する。"""

    def process(self, path: Path, context: Mapping[str, Any] | None = None) -> StructuredSource:
        if not path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")

        path = Path(path)
        if not path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"text source file does not exist: {path}")

        raw_bytes = path.read_bytes()
        try:
            extracted_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"text source is not valid UTF-8: {path}",
                technical_detail=str(exc),
            ) from exc

        normalized_text = _normalize(extracted_text)
        return StructuredSource(
            original_path=str(path),
            extracted_text=extracted_text,
            normalized_text=normalized_text,
            structured_text=normalized_text,
        )
