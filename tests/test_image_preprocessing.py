"""STEP3->STEP4 test suite for TASK-IMAGE-002: 画像前処理・品質flag・見開き分割.

Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
Spec: docs/specifications/image-material-ingestion.md, docs/specifications/source-preprocessing.md
Production files:
- script/source_processing/images/preprocess.py
- script/source_processing/images/quality.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from script.core.errors import AppError
from script.source_processing.images.manifest import PageEntry
from script.source_processing.images.preprocess import ImagePreprocessor, PreprocessOptions, split_spread

pytestmark = pytest.mark.mvp


def _make_png(path: Path, color: str = "white", size: tuple[int, int] = (20, 20)) -> None:
    Image.new("RGB", size, color=color).save(path, format="PNG")


def _page_for(path: Path, *, page_index: int = 1, image_id: str = "image-000001") -> PageEntry:
    content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    return PageEntry(page_index=page_index, image_id=image_id, original_path=str(path), content_hash=content_hash)


@pytest.mark.unit
def test_tc_image_002_01(tmp_path: Path) -> None:
    """TC-IMAGE-002-01 — 原画像不変

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: 回転・contrast処理対象
    When: preprocessする
    Then: 原画像hash不変で派生PNGとparametersを保存
    """
    source = tmp_path / "page1.png"
    _make_png(source, color="red")
    original_bytes = source.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()

    page = _page_for(source)
    options = PreprocessOptions(rotate_degrees=90, contrast_factor=1.3)
    preprocessor = ImagePreprocessor(destination_dir=tmp_path / "out")

    result = preprocessor.process(page, options)

    # 原画像は変更されない。
    assert source.read_bytes() == original_bytes
    assert result.original_hash == original_hash

    # 派生PNGとparametersが保存される。
    derivative_path = Path(result.derivative_path)
    assert derivative_path.exists()
    assert derivative_path != source
    assert result.parameters == {"rotate_degrees": 90, "contrast_factor": 1.3}


@pytest.mark.unit
def test_tc_image_002_03(tmp_path: Path) -> None:
    """TC-IMAGE-002-03 — 見開きlocator

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: 見開き画像
    When: splitする
    Then: 左右の元page座標対応を保持する
    """
    spread = tmp_path / "spread.png"
    # 左半分と右半分で色を変え、split後の内容が異なることを確認できるようにする。
    image = Image.new("RGB", (40, 20), color="white")
    for x in range(20):
        for y in range(20):
            image.putpixel((x, y), (255, 0, 0))
    for x in range(20, 40):
        for y in range(20):
            image.putpixel((x, y), (0, 0, 255))
    image.save(spread, format="PNG")

    page = _page_for(spread, image_id="image-000005")
    preprocessor = ImagePreprocessor(destination_dir=tmp_path / "out")
    preprocessed = preprocessor.process(page, PreprocessOptions())

    left, right = split_spread(preprocessed)

    assert left.locator.original_image_id == "image-000005"
    assert left.locator.spread_side == "left"
    assert left.locator.crop_x == 0
    assert left.locator.crop_width == 20
    assert left.locator.crop_height == 20

    assert right.locator.original_image_id == "image-000005"
    assert right.locator.spread_side == "right"
    assert right.locator.crop_x == 20
    assert right.locator.crop_width == 20

    assert left.derivative_hash != right.derivative_hash
    assert Path(left.derivative_path).exists()
    assert Path(right.derivative_path).exists()

    with Image.open(left.derivative_path) as left_image:
        assert left_image.getpixel((0, 0))[:3] == (255, 0, 0)
    with Image.open(right.derivative_path) as right_image:
        assert right_image.getpixel((0, 0))[:3] == (0, 0, 255)


@pytest.mark.unit
def test_tc_image_002_05(tmp_path: Path) -> None:
    """TC-IMAGE-002-05 — before/after hash

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「before/after hash」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    """
    source = tmp_path / "page1.png"
    _make_png(source, color="green")
    page = _page_for(source)

    preprocessor_a = ImagePreprocessor(destination_dir=tmp_path / "out_a")
    preprocessor_b = ImagePreprocessor(destination_dir=tmp_path / "out_b")

    options = PreprocessOptions(rotate_degrees=0, contrast_factor=1.0)
    result_a = preprocessor_a.process(page, options)
    result_b = preprocessor_b.process(page, options)
    assert result_a.derivative_hash == result_b.derivative_hash

    preprocessor_c = ImagePreprocessor(destination_dir=tmp_path / "out_c")
    different_options = PreprocessOptions(rotate_degrees=45, contrast_factor=1.0)
    result_c = preprocessor_c.process(page, different_options)
    assert result_c.derivative_hash != result_a.derivative_hash


@pytest.mark.unit
def test_tc_image_002_07(tmp_path: Path) -> None:
    """TC-IMAGE-002-07 — 再実行時の決定性

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ImagePreprocessor.process(page, options) -> PreprocessedPage`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    source = tmp_path / "page1.png"
    _make_png(source, color="orange")
    page = _page_for(source)
    options = PreprocessOptions(rotate_degrees=10, contrast_factor=1.1)

    preprocessor = ImagePreprocessor(destination_dir=tmp_path / "out")
    first = preprocessor.process(page, options)
    second = preprocessor.process(page, options)

    assert first == second
