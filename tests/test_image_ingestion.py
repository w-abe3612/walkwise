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


def _make_jpeg(path: Path, *, color: str = "white", with_gps: bool = False) -> None:
    image = Image.new("RGB", (4, 4), color=color)
    if with_gps:
        exif = image.getexif()
        exif[34853] = {1: "N", 2: (10, 0, 0), 3: "E", 4: (20, 0, 0)}
        image.save(path, format="JPEG", exif=exif)
    else:
        image.save(path, format="JPEG")


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.mark.unit
def test_tc_image_001_01(tmp_path: Path) -> None:
    """TC-IMAGE-001-01 — 自然順

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: page1,page2,page10のファイル
    When: ingestする
    Then: natural orderで1,2,10となる
    """
    page1 = tmp_path / "page1.png"
    page2 = tmp_path / "page2.png"
    page10 = tmp_path / "page10.png"
    _make_png(page1, color="red")
    _make_png(page2, color="green")
    _make_png(page10, color="blue")

    service = ImageIngestionService(destination_dir=tmp_path / "out")
    # 入力順をあえてalphabetical順(1,10,2)で渡し、natural sortが効くことを確認する。
    result = service.ingest([page10, page1, page2])

    assert [entry.page_index for entry in result.pages] == [1, 2, 3]
    assert result.pages[0].content_hash == _hash_bytes(page1.read_bytes())
    assert result.pages[1].content_hash == _hash_bytes(page2.read_bytes())
    assert result.pages[2].content_hash == _hash_bytes(page10.read_bytes())


@pytest.mark.unit
def test_tc_image_001_03(tmp_path: Path) -> None:
    """TC-IMAGE-001-03 — EXIF privacy

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: 位置情報付きJPEG
    When: manifest/exportを作る
    Then: 内部warningは保持しても公開成果物に位置情報を含めない
    """
    gps_jpeg = tmp_path / "with_gps.jpg"
    _make_jpeg(gps_jpeg, with_gps=True)

    service = ImageIngestionService(destination_dir=tmp_path / "out")
    result = service.ingest([gps_jpeg])

    assert "exif_location_present" in result.warnings
    assert result.pages[0].quality_flags == ("exif_location_present",)

    # 公開成果物(manifest)には位置情報の生値(座標・GPSタグ)が一切含まれない。
    for page in result.manifest["pages"]:
        assert set(page.keys()) == {
            "page_index",
            "image_id",
            "original_path",
            "content_hash",
            "locator",
            "quality_flags",
        }
        assert "gps" not in str(page).lower()
        assert "latitude" not in str(page).lower()
        assert "longitude" not in str(page).lower()


@pytest.mark.unit
def test_tc_image_001_05(tmp_path: Path) -> None:
    """TC-IMAGE-001-05 — 壊れた画像検出

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「壊れた画像検出」を実行する
    Then: 「壊れた画像検出」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    good = tmp_path / "good.png"
    _make_png(good)
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not a real image at all")

    destination_dir = tmp_path / "out"
    service = ImageIngestionService(destination_dir=destination_dir)

    with pytest.raises(AppError) as excinfo:
        service.ingest([good, broken])
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR

    # 1件でも壊れていれば、検証済みの他画像も含めて一切コピーされない(副作用なし)。
    assert not destination_dir.exists() or list(destination_dir.iterdir()) == []

    # 0 byteファイルも同様に壊れた画像として拒否される。
    empty = tmp_path / "empty.png"
    empty.write_bytes(b"")
    with pytest.raises(AppError) as excinfo_empty:
        service.ingest([good, empty])
    assert excinfo_empty.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_image_001_07(tmp_path: Path) -> None:
    """TC-IMAGE-001-07 — hash

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「hash」を実行する
    Then: 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。
    """
    same_bytes = (tmp_path / "a.png")
    _make_png(same_bytes, color="purple")
    same_copy = tmp_path / "b.png"
    same_copy.write_bytes(same_bytes.read_bytes())

    different = tmp_path / "c.png"
    _make_png(different, color="orange")

    service_a = ImageIngestionService(destination_dir=tmp_path / "out_a")
    service_b = ImageIngestionService(destination_dir=tmp_path / "out_b")

    result_a = service_a.ingest([same_bytes])
    result_b = service_b.ingest([same_copy])
    assert result_a.pages[0].content_hash == result_b.pages[0].content_hash

    service_c = ImageIngestionService(destination_dir=tmp_path / "out_c")
    result_c = service_c.ingest([different])
    assert result_c.pages[0].content_hash != result_a.pages[0].content_hash


@pytest.mark.unit
def test_tc_image_001_09(tmp_path: Path) -> None:
    """TC-IMAGE-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    page = tmp_path / "page1.png"
    _make_png(page)

    destination_dir = tmp_path / "out"
    service = ImageIngestionService(destination_dir=destination_dir)

    first = service.ingest([page])
    second = service.ingest([page])

    assert first.pages == second.pages
    assert first.manifest == second.manifest
    assert first.warnings == second.warnings
