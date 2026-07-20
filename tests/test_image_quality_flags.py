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

from script.core.errors import AppError, ErrorCode
from script.source_processing.images.manifest import PageEntry
from script.source_processing.images.preprocess import ImagePreprocessor, PreprocessOptions
from script.source_processing.images.quality import assess_image_quality

pytestmark = pytest.mark.mvp


def _make_png(path: Path, color: str = "white", size: tuple[int, int] = (400, 400)) -> None:
    Image.new("RGB", size, color=color).save(path, format="PNG")


def _page_for(path: Path, *, page_index: int = 1, image_id: str = "image-000001") -> PageEntry:
    content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    return PageEntry(page_index=page_index, image_id=image_id, original_path=str(path), content_hash=content_hash)


@pytest.mark.unit
def test_tc_image_002_02(tmp_path: Path) -> None:
    """TC-IMAGE-002-02 — blank候補

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: ほぼ白紙の画像
    When: quality評価する
    Then: 削除せずblank_candidate warningにする
    """
    blank_path = tmp_path / "blank.png"
    _make_png(blank_path, color="white")

    report = assess_image_quality(_page_for(blank_path, image_id="image-blank"))
    assert "blank_candidate" in report.warnings

    # blank pageはファイルとして削除されない(warningとして記録するのみ)。
    assert blank_path.exists()

    # 非blank(模様あり)画像はblank_candidateにならない。
    patterned_path = tmp_path / "patterned.png"
    image = Image.new("RGB", (400, 400), color="white")
    for x in range(0, 400, 2):
        for y in range(0, 400, 2):
            image.putpixel((x, y), (0, 0, 0))
    image.save(patterned_path, format="PNG")

    patterned_report = assess_image_quality(_page_for(patterned_path, image_id="image-patterned"))
    assert "blank_candidate" not in patterned_report.warnings


@pytest.mark.unit
def test_tc_image_002_04(tmp_path: Path) -> None:
    """TC-IMAGE-002-04 — 決定的な低リスク補正

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「決定的な低リスク補正」を実行する
    Then: 「決定的な低リスク補正」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    source = tmp_path / "page1.png"
    _make_png(source, color="teal")
    page = _page_for(source)
    options = PreprocessOptions(rotate_degrees=15, contrast_factor=1.2)

    # 補正処理そのものが決定的であることを、異なるdestinationを持つ別instanceで確認する。
    result_1 = ImagePreprocessor(destination_dir=tmp_path / "out_1").process(page, options)
    result_2 = ImagePreprocessor(destination_dir=tmp_path / "out_2").process(page, options)

    assert result_1.derivative_hash == result_2.derivative_hash
    assert result_1.parameters == result_2.parameters == {"rotate_degrees": 15, "contrast_factor": 1.2}


@pytest.mark.unit
def test_tc_image_002_06(tmp_path: Path) -> None:
    """TC-IMAGE-002-06 — 必須入力欠落

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ImagePreprocessor.process(page, options) -> PreprocessedPage`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_destination:
        ImagePreprocessor(destination_dir=None)
    assert excinfo_destination.value.code is ErrorCode.VALIDATION_ERROR

    destination_dir = tmp_path / "out"
    preprocessor = ImagePreprocessor(destination_dir=destination_dir)

    with pytest.raises(AppError) as excinfo_page:
        preprocessor.process(None, PreprocessOptions())
    assert excinfo_page.value.code is ErrorCode.VALIDATION_ERROR

    source = tmp_path / "page1.png"
    _make_png(source)
    page = _page_for(source)

    with pytest.raises(AppError) as excinfo_options:
        preprocessor.process(page, None)
    assert excinfo_options.value.code is ErrorCode.VALIDATION_ERROR

    missing_page = PageEntry(
        page_index=1,
        image_id="image-missing",
        original_path=str(tmp_path / "does_not_exist.png"),
        content_hash="a" * 64,
    )
    with pytest.raises(AppError) as excinfo_missing_file:
        preprocessor.process(missing_page, PreprocessOptions())
    assert excinfo_missing_file.value.code is ErrorCode.NOT_FOUND

    # 検証失敗前に副作用(destination_dirへの書込み)が発生していない。
    assert not destination_dir.exists()


@pytest.mark.unit
def test_tc_image_002_08(tmp_path: Path) -> None:
    """TC-IMAGE-002-08 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    good_source = tmp_path / "good.png"
    _make_png(good_source, color="navy")
    good_page = _page_for(good_source, image_id="image-good")

    preprocessor = ImagePreprocessor(destination_dir=tmp_path / "out")
    result = preprocessor.process(good_page, PreprocessOptions())

    good_derivative_path = Path(result.derivative_path)
    good_derivative_bytes = good_derivative_path.read_bytes()
    good_source_bytes = good_source.read_bytes()

    # 意図的な失敗: 存在しないoriginal_pathを持つpageを処理させる。
    missing_page = PageEntry(
        page_index=2,
        image_id="image-missing",
        original_path=str(tmp_path / "does_not_exist.png"),
        content_hash="b" * 64,
    )
    with pytest.raises(AppError):
        preprocessor.process(missing_page, PreprocessOptions())

    # 既存の正常成果物と入力は変化しない。
    assert good_source.read_bytes() == good_source_bytes
    assert good_derivative_path.read_bytes() == good_derivative_bytes
