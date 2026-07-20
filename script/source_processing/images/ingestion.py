"""script/source_processing/images/ingestion.py — 公開契約: ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult.

Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
Spec: docs/specifications/image-material-ingestion.md
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from script.core.errors import AppError, ErrorCode
from script.persistence.files import copy_immutable
from script.source_processing.images.manifest import PageEntry, build_image_manifest

# image-material-ingestion.md 5.1節: 初期必須形式。
_SUPPORTED_FORMATS = frozenset({"PNG", "JPEG", "TIFF"})
_JPEG_LIKE_FORMATS_WITH_EXIF = frozenset({"JPEG", "TIFF"})
_DIGIT_RE = re.compile(r"(\d+)")
_GPS_EXIF_TAG_ID = 34853  # PIL.ExifTags: "GPSInfo"


@dataclass(frozen=True)
class ImageIngestionResult:
    """ingest結果。manifestは公開成果物であり位置情報等の生値を含まない。"""

    pages: tuple[PageEntry, ...]
    manifest: dict[str, Any]
    warnings: tuple[str, ...] = ()


def _natural_sort_key(path: Path) -> list[Any]:
    return [int(part) if part.isdigit() else part.lower() for part in _DIGIT_RE.split(path.name)]


def _validate_image(path: Path) -> str:
    """形式検証と壊れた画像検出(image-material-ingestion.md 13節Error)を行う。"""
    if path.stat().st_size == 0:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"image file is empty (0 byte): {path}")

    try:
        with Image.open(path) as probe:
            probe.verify()
    except Exception as exc:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            f"corrupted or unreadable image: {path}",
            technical_detail=str(exc),
        ) from exc

    try:
        with Image.open(path) as probe:
            image_format = probe.format
    except Exception as exc:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            f"corrupted or unreadable image: {path}",
            technical_detail=str(exc),
        ) from exc

    if image_format not in _SUPPORTED_FORMATS:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"unsupported image format: {image_format} ({path})")
    return image_format


def _has_exif_gps_location(path: Path, image_format: str) -> bool:
    """位置情報の有無だけを検出し、実際のGPS値は一切保持・返却しない。"""
    if image_format not in _JPEG_LIKE_FORMATS_WITH_EXIF:
        return False
    try:
        with Image.open(path) as probe:
            exif = probe.getexif()
    except Exception:
        return False
    return bool(exif) and _GPS_EXIF_TAG_ID in exif


def _apply_explicit_order(input_paths: list[Path], explicit_order: Sequence[Any]) -> list[Path]:
    ordered = [Path(item) for item in explicit_order]
    ordered_keys = [str(path.resolve()) for path in ordered]
    if len(ordered_keys) != len(set(ordered_keys)):
        raise AppError(ErrorCode.VALIDATION_ERROR, "explicit_order contains duplicate entries")

    input_keys = {str(path.resolve()) for path in input_paths}
    if set(ordered_keys) != input_keys:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            "explicit_order must be exactly a permutation of paths (no missing or extra entries)",
        )
    return ordered


def _copy_original_immutable(source: Path, destination: Path) -> str:
    """originalへの上書きを拒否しつつ、同一内容での再実行は冪等に成功させる。"""
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if destination.exists():
        existing_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
        if existing_hash != source_hash:
            raise AppError(
                ErrorCode.CONFLICT,
                f"cannot overwrite existing original with different content: {destination}",
            )
        return existing_hash
    digest = copy_immutable(source, destination)
    return digest.value


class ImageIngestionService:
    """PNG/JPEG/TIFFの画像群を検証し、決定的順序でimmutable登録する。"""

    def __init__(self, destination_dir: Path) -> None:
        if not destination_dir:
            raise AppError(ErrorCode.VALIDATION_ERROR, "destination_dir is required")
        self._destination_dir = Path(destination_dir)

    def ingest(self, paths: Sequence[Any], *, explicit_order: Sequence[Any] | None = None) -> ImageIngestionResult:
        """画像を検証し決定的順序でimmutable登録する。"""
        if not paths:
            raise AppError(ErrorCode.VALIDATION_ERROR, "paths must not be empty")

        input_paths = [Path(item) for item in paths]
        for path in input_paths:
            if not path.is_file():
                raise AppError(ErrorCode.NOT_FOUND, f"image source file does not exist: {path}")

        global_warnings: list[str] = []
        if explicit_order is not None:
            ordered_paths = _apply_explicit_order(input_paths, explicit_order)
        else:
            ordered_paths = sorted(input_paths, key=_natural_sort_key)
            # image-material-ingestion.md 9節: natural sortのみでの確定は人間プレビュー必須。
            global_warnings.append("order_requires_human_preview")

        # 副作用(コピー)を開始する前に全件を検証する(1件でも不正なら何も書き込まない)。
        validated_formats = [_validate_image(path) for path in ordered_paths]

        entries: list[PageEntry] = []
        for page_index, (path, image_format) in enumerate(zip(ordered_paths, validated_formats), start=1):
            image_id = f"image-{page_index:06d}"
            destination = self._destination_dir / f"original-{page_index:06d}{path.suffix.lower()}"
            content_hash = _copy_original_immutable(path, destination)

            quality_flags: list[str] = []
            if _has_exif_gps_location(path, image_format):
                quality_flags.append("exif_location_present")

            entries.append(
                PageEntry(
                    page_index=page_index,
                    image_id=image_id,
                    original_path=str(destination),
                    content_hash=content_hash,
                    locator=None,
                    quality_flags=tuple(quality_flags),
                )
            )

        manifest = build_image_manifest(entries)
        all_warnings = tuple(global_warnings) + tuple(
            flag for entry in entries for flag in entry.quality_flags
        )
        return ImageIngestionResult(pages=tuple(entries), manifest=manifest, warnings=all_warnings)
