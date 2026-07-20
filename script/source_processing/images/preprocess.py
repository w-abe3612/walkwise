"""script/source_processing/images/preprocess.py — 公開契約: ImagePreprocessor.process, split_spread.

Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
Spec: docs/specifications/image-material-ingestion.md, docs/specifications/source-preprocessing.md
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance

from script.core.errors import AppError, ErrorCode
from script.source_processing.images.manifest import Locator, PageEntry


@dataclass(frozen=True)
class PreprocessOptions:
    """低リスク・決定的な補正parameter(image-material-ingestion.md 10節)。"""

    rotate_degrees: float = 0.0
    contrast_factor: float = 1.0


@dataclass(frozen=True)
class PreprocessedPage:
    """派生PNGと再処理可能なparameter manifestを保持する。"""

    page_index: int
    image_id: str
    original_path: str
    original_hash: str
    derivative_path: str
    derivative_hash: str
    parameters: dict[str, Any] = field(default_factory=dict)
    locator: Locator | None = None

    def __post_init__(self) -> None:
        if not self.image_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "image_id is required")
        if not self.original_path or not self.original_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "original_path and original_hash are required")
        if not self.derivative_path or not self.derivative_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "derivative_path and derivative_hash are required")


def _write_derivative_idempotent(destination: Path, data: bytes) -> str:
    """destinationへ書込む。同一内容の再実行は冪等成功、異なる内容の上書きは拒否する。"""
    new_hash = hashlib.sha256(data).hexdigest()
    if destination.exists():
        existing_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
        if existing_hash != new_hash:
            raise AppError(
                ErrorCode.CONFLICT,
                f"cannot overwrite existing derivative with different content: {destination}",
            )
        return existing_hash
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return new_hash


class ImagePreprocessor:
    """原画像を変えず、OCR向け派生PNGと再処理可能なparameter manifestを生成する。"""

    def __init__(self, destination_dir: Path) -> None:
        if not destination_dir:
            raise AppError(ErrorCode.VALIDATION_ERROR, "destination_dir is required")
        self._destination_dir = Path(destination_dir)

    def process(self, page: PageEntry, options: PreprocessOptions) -> PreprocessedPage:
        """原画像を変えずOCR用PNGと変換manifestを生成する。"""
        if page is None or not page.original_path or not page.image_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "page (with original_path and image_id) is required")
        if options is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "options is required")

        original_path = Path(page.original_path)
        if not original_path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"original image does not exist: {original_path}")

        original_bytes_before = original_path.read_bytes()
        original_hash = hashlib.sha256(original_bytes_before).hexdigest()

        with Image.open(original_path) as image:
            working = image.convert("RGB")
            if options.rotate_degrees:
                working = working.rotate(-options.rotate_degrees, expand=True, fillcolor="white")
            if options.contrast_factor != 1.0:
                working = ImageEnhance.Contrast(working).enhance(options.contrast_factor)

            buffer = io.BytesIO()
            working.save(buffer, format="PNG")
            derivative_bytes = buffer.getvalue()

        destination = self._destination_dir / f"{page.image_id}.png"
        derivative_hash = _write_derivative_idempotent(destination, derivative_bytes)

        # 原画像不変性の確認(image-material-ingestion.md 10節: 原画像を自動補正画像で置き換えない)。
        if original_path.read_bytes() != original_bytes_before:
            raise AppError(ErrorCode.INTERNAL_ERROR, "original image must not be modified during preprocessing")

        parameters = {
            "rotate_degrees": options.rotate_degrees,
            "contrast_factor": options.contrast_factor,
        }

        return PreprocessedPage(
            page_index=page.page_index,
            image_id=page.image_id,
            original_path=str(original_path),
            original_hash=original_hash,
            derivative_path=str(destination),
            derivative_hash=derivative_hash,
            parameters=parameters,
            locator=page.locator,
        )


def split_spread(page: PreprocessedPage) -> tuple[PreprocessedPage, PreprocessedPage]:
    """左右locatorを保持して見開きを分割する(既存派生PNGを元に左右2枚を生成する)。"""
    if page is None or not page.derivative_path or not page.image_id:
        raise AppError(ErrorCode.VALIDATION_ERROR, "page (with derivative_path and image_id) is required")

    derivative_path = Path(page.derivative_path)
    if not derivative_path.is_file():
        raise AppError(ErrorCode.NOT_FOUND, f"derivative image does not exist: {derivative_path}")

    with Image.open(derivative_path) as image:
        width, height = image.size
        half_width = width // 2
        left_crop = image.crop((0, 0, half_width, height)).convert("RGB")
        right_crop = image.crop((half_width, 0, width, height)).convert("RGB")

        left_buffer = io.BytesIO()
        left_crop.save(left_buffer, format="PNG")
        right_buffer = io.BytesIO()
        right_crop.save(right_buffer, format="PNG")

    left_path = derivative_path.with_name(f"{derivative_path.stem}-left{derivative_path.suffix}")
    right_path = derivative_path.with_name(f"{derivative_path.stem}-right{derivative_path.suffix}")

    left_hash = _write_derivative_idempotent(left_path, left_buffer.getvalue())
    right_hash = _write_derivative_idempotent(right_path, right_buffer.getvalue())

    left_locator = Locator(
        original_image_id=page.image_id,
        crop_x=0,
        crop_y=0,
        crop_width=half_width,
        crop_height=height,
        spread_side="left",
    )
    right_locator = Locator(
        original_image_id=page.image_id,
        crop_x=half_width,
        crop_y=0,
        crop_width=width - half_width,
        crop_height=height,
        spread_side="right",
    )

    left_page = PreprocessedPage(
        page_index=page.page_index,
        image_id=f"{page.image_id}-left",
        original_path=page.original_path,
        original_hash=page.original_hash,
        derivative_path=str(left_path),
        derivative_hash=left_hash,
        parameters={**page.parameters, "split_from": page.image_id, "spread_side": "left"},
        locator=left_locator,
    )
    right_page = PreprocessedPage(
        page_index=page.page_index,
        image_id=f"{page.image_id}-right",
        original_path=page.original_path,
        original_hash=page.original_hash,
        derivative_path=str(right_path),
        derivative_hash=right_hash,
        parameters={**page.parameters, "split_from": page.image_id, "spread_side": "right"},
        locator=right_locator,
    )
    return (left_page, right_page)
