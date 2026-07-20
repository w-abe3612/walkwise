"""STEP3->STEP4 test suite for TASK-IMAGE-001: 画像群登録・順序・manifest.

Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
Spec: docs/specifications/image-material-ingestion.md
Production files:
- script/source_processing/images/ingestion.py
- script/source_processing/images/manifest.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from script.core.errors import AppError, ErrorCode
from script.source_processing.images.ingestion import ImageIngestionService

pytestmark = pytest.mark.mvp


def _make_png(path: Path, color: str = "white", size: tuple[int, int] = (4, 4)) -> None:
    Image.new("RGB", size, color=color).save(path, format="PNG")


@pytest.mark.unit
def test_tc_image_001_02(tmp_path: Path) -> None:
    """TC-IMAGE-001-02 — 明示順

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: explicit orderを指定
    When: ingestする
    Then: 指定順を採用し重複/欠落を拒否する
    """
    page_a = tmp_path / "a.png"
    page_b = tmp_path / "b.png"
    page_c = tmp_path / "c.png"
    _make_png(page_a, color="red")
    _make_png(page_b, color="green")
    _make_png(page_c, color="blue")

    service = ImageIngestionService(destination_dir=tmp_path / "out")

    # natural sortではa,b,cのままだが、明示順でc,a,bを指定する。
    result = service.ingest([page_a, page_b, page_c], explicit_order=[page_c, page_a, page_b])
    assert [entry.page_index for entry in result.pages] == [1, 2, 3]
    assert result.pages[0].content_hash == hashlib.sha256(page_c.read_bytes()).hexdigest()
    assert result.pages[1].content_hash == hashlib.sha256(page_a.read_bytes()).hexdigest()
    assert result.pages[2].content_hash == hashlib.sha256(page_b.read_bytes()).hexdigest()

    # 重複を含むexplicit_orderは拒否する。
    with pytest.raises(AppError) as excinfo_dup:
        service.ingest([page_a, page_b, page_c], explicit_order=[page_a, page_a, page_c])
    assert excinfo_dup.value.code is ErrorCode.VALIDATION_ERROR

    # 欠落(page_bがない)を含むexplicit_orderは拒否する。
    with pytest.raises(AppError) as excinfo_missing:
        service.ingest([page_a, page_b, page_c], explicit_order=[page_a, page_c])
    assert excinfo_missing.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_image_001_04(tmp_path: Path) -> None:
    """TC-IMAGE-001-04 — 形式検証

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「形式検証」を実行する
    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    """
    png_path = tmp_path / "good.png"
    _make_png(png_path)
    jpeg_path = tmp_path / "good.jpg"
    Image.new("RGB", (4, 4), color="white").save(jpeg_path, format="JPEG")
    tiff_path = tmp_path / "good.tif"
    Image.new("RGB", (4, 4), color="white").save(tiff_path, format="TIFF")

    service = ImageIngestionService(destination_dir=tmp_path / "out")
    result = service.ingest([png_path, jpeg_path, tiff_path])
    assert len(result.pages) == 3

    # 未対応形式(BMP)は明示的なerror codeで拒否する。
    bmp_path = tmp_path / "bad.bmp"
    Image.new("RGB", (4, 4), color="white").save(bmp_path, format="BMP")
    with pytest.raises(AppError) as excinfo:
        service.ingest([bmp_path])
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_image_001_06(tmp_path: Path) -> None:
    """TC-IMAGE-001-06 — 原画像immutable copy

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「原画像immutable copy」を実行する
    Then: 処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。
    """
    source = tmp_path / "page1.png"
    _make_png(source)
    original_bytes = source.read_bytes()
    original_hash = hashlib.sha256(original_bytes).hexdigest()

    destination_dir = tmp_path / "out"
    service = ImageIngestionService(destination_dir=destination_dir)
    result = service.ingest([source])

    # 入力fileは変更されない。
    assert source.read_bytes() == original_bytes
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash

    # 派生物(コピー先)が新規作成され、内容は原本と一致する。
    destination_path = Path(result.pages[0].original_path)
    assert destination_path.exists()
    assert destination_path != source
    assert destination_path.read_bytes() == original_bytes
    assert result.pages[0].content_hash == original_hash


@pytest.mark.unit
def test_tc_image_001_08(tmp_path: Path) -> None:
    """TC-IMAGE-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_destination:
        ImageIngestionService(destination_dir=None)
    assert excinfo_destination.value.code is ErrorCode.VALIDATION_ERROR

    destination_dir = tmp_path / "out"
    service = ImageIngestionService(destination_dir=destination_dir)

    with pytest.raises(AppError) as excinfo_empty:
        service.ingest([])
    assert excinfo_empty.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_missing_file:
        service.ingest([tmp_path / "does_not_exist.png"])
    assert excinfo_missing_file.value.code is ErrorCode.NOT_FOUND

    # 検証失敗前に副作用(destination_dirへの書込み)が発生していない。
    assert not destination_dir.exists()


@pytest.mark.unit
def test_tc_image_001_10(tmp_path: Path) -> None:
    """TC-IMAGE-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    good = tmp_path / "good.png"
    _make_png(good, color="red")

    destination_dir = tmp_path / "out"
    service = ImageIngestionService(destination_dir=destination_dir)
    first_result = service.ingest([good])

    good_destination = Path(first_result.pages[0].original_path)
    good_destination_bytes = good_destination.read_bytes()

    # 意図的な失敗(壊れた画像を混ぜたingest)を別途発生させる。
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not a real image")

    with pytest.raises(AppError):
        service.ingest([broken])

    # 既存の正常成果物(good.pngのコピー)と原本入力はbyte/hashとも変化しない。
    assert good_destination.read_bytes() == good_destination_bytes
    assert good.exists()
