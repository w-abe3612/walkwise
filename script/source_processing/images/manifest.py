"""script/source_processing/images/manifest.py — 公開契約: ImageManifest/PageEntry/Locator, build_image_manifest.

Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
Spec: docs/specifications/image-material-ingestion.md
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class Locator:
    """見開き分割等における元画像座標への参照(image-material-ingestion.md 10節)。"""

    original_image_id: str
    crop_x: int = 0
    crop_y: int = 0
    crop_width: int | None = None
    crop_height: int | None = None
    spread_side: str | None = None


@dataclass(frozen=True)
class PageEntry:
    """manifest中の1ページ分の情報。"""

    page_index: int
    image_id: str
    original_path: str
    content_hash: str
    locator: Locator | None = None
    quality_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.image_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "image_id is required")
        if not self.original_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "original_path is required")
        if not self.content_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "content_hash is required")


@dataclass(frozen=True)
class ImageManifest:
    """canonical化済みの画像manifest本体。"""

    pages: tuple[PageEntry, ...]


def build_image_manifest(entries: Sequence[PageEntry]) -> dict[str, Any]:
    """重複indexを拒否しcanonical manifestを作る。"""
    if not entries:
        raise AppError(ErrorCode.VALIDATION_ERROR, "entries must not be empty")

    seen_page_indexes: set[int] = set()
    seen_image_ids: set[str] = set()
    for entry in entries:
        if entry.page_index in seen_page_indexes:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate page_index: {entry.page_index}")
        if entry.image_id in seen_image_ids:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate image_id: {entry.image_id}")
        seen_page_indexes.add(entry.page_index)
        seen_image_ids.add(entry.image_id)

    ordered = sorted(entries, key=lambda entry: entry.page_index)

    return {
        "schema_version": "1.0",
        "pages": [
            {
                "page_index": entry.page_index,
                "image_id": entry.image_id,
                "original_path": entry.original_path,
                "content_hash": entry.content_hash,
                "locator": (
                    {
                        "original_image_id": entry.locator.original_image_id,
                        "crop_x": entry.locator.crop_x,
                        "crop_y": entry.locator.crop_y,
                        "crop_width": entry.locator.crop_width,
                        "crop_height": entry.locator.crop_height,
                        "spread_side": entry.locator.spread_side,
                    }
                    if entry.locator is not None
                    else None
                ),
                "quality_flags": list(entry.quality_flags),
            }
            for entry in ordered
        ],
    }
