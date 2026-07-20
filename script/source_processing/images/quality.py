"""script/source_processing/images/quality.py — 公開契約: assess_image_quality(page) -> ImageQualityReport.

Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
Spec: docs/specifications/image-material-ingestion.md (13節 品質判定)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageStat

from script.core.errors import AppError, ErrorCode
from script.source_processing.images.manifest import PageEntry

# 画素値のstddevが極めて低い(ほぼ均一な白紙)場合にblank候補とする。
# 具体的な閾値はimage-material-ingestion.md 19節の未決定事項であり、
# 実測後にprofileへ切り出す前提の暫定値。
_BLANK_STDDEV_THRESHOLD = 5.0
_LOW_RESOLUTION_PIXEL_THRESHOLD = 300 * 300


@dataclass(frozen=True)
class ImageQualityReport:
    """blank/低解像度等の品質flag(削除は行わない、warningとして記録するのみ)。"""

    image_id: str
    warnings: tuple[str, ...] = ()


def assess_image_quality(page: PageEntry) -> ImageQualityReport:
    """blank/blur/skew/contrast/vertical候補をflag化する。"""
    if page is None or not page.original_path or not page.image_id:
        raise AppError(ErrorCode.VALIDATION_ERROR, "page (with original_path and image_id) is required")

    path = Path(page.original_path)
    if not path.is_file():
        raise AppError(ErrorCode.NOT_FOUND, f"image does not exist: {path}")

    warnings: list[str] = []
    with Image.open(path) as image:
        width, height = image.size
        grayscale = image.convert("L")
        stat = ImageStat.Stat(grayscale)
        stddev = stat.stddev[0]

    if stddev < _BLANK_STDDEV_THRESHOLD:
        # image-material-ingestion.md 11節: blank page候補は削除せずmanifestへ残す。
        warnings.append("blank_candidate")

    if width * height < _LOW_RESOLUTION_PIXEL_THRESHOLD:
        warnings.append("low_resolution")

    return ImageQualityReport(image_id=page.image_id, warnings=tuple(warnings))
