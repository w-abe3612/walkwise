"""Test suite for TASK-EPUB-001: EPUBテキスト抽出 (post-MVP).

Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
"""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from script.core.errors import AppError, ErrorCode
from script.source_processing.epub.extract import EpubTextExtractor, detect_drm_or_encryption
from script.source_processing.epub.models import EpubChapter, EpubExtractionReport

pytestmark = pytest.mark.post_mvp

_CONTAINER_XML = (
    '<?xml version="1.0"?>'
    '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
    '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>'
    "</container>"
)

_CHAPTER_1 = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
    "<head><title>Chapter 1</title></head>"
    "<body><h1>第1章</h1><p>導入部分です。</p></body></html>"
)

_CHAPTER_2 = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
    "<head><title>Chapter 2</title></head>"
    "<body><h1>第2章</h1><p>まとめです。</p></body></html>"
)

_CHAPTER_WITH_ANNOTATIONS = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
    "<head><title>Chapter 1</title></head>"
    "<body>"
    "<h1>第1章</h1>"
    '<p>この<ruby>音声<rt>おんせい</rt></ruby>技術は重要です<a epub:type="noteref" href="#fn1">1</a>。</p>'
    '<p><img src="images/fig01.png" alt="図1"/></p>'
    '<aside epub:type="footnote" id="fn1"><p>脚注本文です。</p></aside>'
    "</body></html>"
)


def _write_epub(
    destination: Path,
    *,
    version: str = "3.0",
    manifest_items: list[tuple[str, str, str]],
    spine_idrefs: list[str],
    files: dict[str, str],
    encrypted: bool = False,
) -> Path:
    with zipfile.ZipFile(destination, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr("META-INF/container.xml", _CONTAINER_XML)
        if encrypted:
            archive.writestr(
                "META-INF/encryption.xml",
                '<encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container"/>',
            )

        manifest_xml = "".join(
            f'<item id="{item_id}" href="{href}" media-type="{media_type}"/>'
            for item_id, href, media_type in manifest_items
        )
        spine_xml = "".join(f'<itemref idref="{idref}"/>' for idref in spine_idrefs)
        opf = (
            '<?xml version="1.0"?>'
            f'<package xmlns="http://www.idpf.org/2007/opf" version="{version}" unique-identifier="uid">'
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Sample</dc:title></metadata>'
            f"<manifest>{manifest_xml}</manifest>"
            f"<spine>{spine_xml}</spine>"
            "</package>"
        )
        archive.writestr("OEBPS/content.opf", opf)

        for href, content in files.items():
            archive.writestr(f"OEBPS/{href}", content)

    return destination


def _simple_two_chapter_epub(path: Path, *, version: str = "3.0") -> Path:
    return _write_epub(
        path,
        version=version,
        # manifestの記載順はspine順とわざと逆にする(TC-02: spine順を採用する)。
        manifest_items=[
            ("chap2", "z-second.xhtml", "application/xhtml+xml"),
            ("chap1", "a-first.xhtml", "application/xhtml+xml"),
        ],
        spine_idrefs=["chap1", "chap2"],
        files={"z-second.xhtml": _CHAPTER_2, "a-first.xhtml": _CHAPTER_1},
    )


@pytest.mark.integration_mock
def test_tc_epub_001_01(tmp_path: Path) -> None:
    """TC-EPUB-001-01 — DRM拒否: 暗号化EPUBを解除せずunsupported_drmで停止する。"""
    epub_path = _write_epub(
        tmp_path / "encrypted.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1"],
        files={"a-first.xhtml": _CHAPTER_1},
        encrypted=True,
    )

    assert detect_drm_or_encryption(epub_path) is True

    with pytest.raises(AppError) as exc_info:
        EpubTextExtractor().extract(epub_path)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert "unsupported_drm" in exc_info.value.message


@pytest.mark.integration_mock
def test_tc_epub_001_02(tmp_path: Path) -> None:
    """TC-EPUB-001-02 — spine順: manifest順とfile名順が異なっていてもspine順を採用する。"""
    epub_path = _simple_two_chapter_epub(tmp_path / "book.epub")

    report = EpubTextExtractor().extract(epub_path)

    assert [chapter.xhtml_path for chapter in report.chapters] == ["OEBPS/a-first.xhtml", "OEBPS/z-second.xhtml"]
    assert "導入部分です" in report.chapters[0].text
    assert "まとめです" in report.chapters[1].text


@pytest.mark.unit
def test_tc_epub_001_03(tmp_path: Path) -> None:
    """TC-EPUB-001-03 — footnote保持: annotation/footnoteを別構造で保持し、本文へ自動挿入しない。"""
    epub_path = _write_epub(
        tmp_path / "annotated.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1"],
        files={"a-first.xhtml": _CHAPTER_WITH_ANNOTATIONS},
    )

    report = EpubTextExtractor().extract(epub_path)
    chapter = report.chapters[0]

    assert "脚注本文です" not in chapter.text
    assert len(chapter.annotations["footnotes"]) == 1
    assert chapter.annotations["footnotes"][0]["ref_id"] == "fn1"
    assert chapter.annotations["footnotes"][0]["text"] == "脚注本文です。"


@pytest.mark.unit
def test_tc_epub_001_04(tmp_path: Path) -> None:
    """TC-EPUB-001-04 — EPUB2/3判定"""
    epub2_path = _simple_two_chapter_epub(tmp_path / "book2.epub", version="2.0")
    epub3_path = _simple_two_chapter_epub(tmp_path / "book3.epub", version="3.0")

    report2 = EpubTextExtractor().extract(epub2_path)
    report3 = EpubTextExtractor().extract(epub3_path)

    assert report2.epub_version == "2.0"
    assert report3.epub_version == "3.0"


@pytest.mark.unit
def test_tc_epub_001_05(tmp_path: Path) -> None:
    """TC-EPUB-001-05 — container/OPF/spine解決: 論理順を維持し再実行しても同じ順序、重複・欠落を検出する。"""
    epub_path = _simple_two_chapter_epub(tmp_path / "book.epub")

    first = EpubTextExtractor().extract(epub_path)
    second = EpubTextExtractor().extract(epub_path)
    assert [c.xhtml_path for c in first.chapters] == [c.xhtml_path for c in second.chapters]

    # 未知manifest idはwarningとして記録し、処理は継続する。
    missing_ref_path = _write_epub(
        tmp_path / "missing-ref.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1", "chap-unknown"],
        files={"a-first.xhtml": _CHAPTER_1},
    )
    report = EpubTextExtractor().extract(missing_ref_path)
    assert len(report.chapters) == 1
    assert any("chap-unknown" in warning for warning in report.warnings)

    # spineの重複itemrefは検出してerrorにする。
    duplicate_path = _write_epub(
        tmp_path / "duplicate.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1", "chap1"],
        files={"a-first.xhtml": _CHAPTER_1},
    )
    with pytest.raises(AppError) as exc_info:
        EpubTextExtractor().extract(duplicate_path)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_epub_001_06(tmp_path: Path) -> None:
    """TC-EPUB-001-06 — 章/節locator: spine_index/xhtml_pathで元HTMLへ追跡できる。"""
    epub_path = _simple_two_chapter_epub(tmp_path / "book.epub")

    report = EpubTextExtractor().extract(epub_path)

    assert report.chapters[0].spine_index == 0
    assert report.chapters[0].order == 0
    assert report.chapters[0].xhtml_path == "OEBPS/a-first.xhtml"
    assert report.chapters[0].chapter_title == "第1章"
    assert report.chapters[1].spine_index == 1
    assert report.chapters[1].xhtml_path == "OEBPS/z-second.xhtml"


@pytest.mark.unit
def test_tc_epub_001_07(tmp_path: Path) -> None:
    """TC-EPUB-001-07 — annotation分離: ruby/footnote/imageをchar_offset付きで分離保持する。"""
    epub_path = _write_epub(
        tmp_path / "annotated.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1"],
        files={"a-first.xhtml": _CHAPTER_WITH_ANNOTATIONS},
    )

    report = EpubTextExtractor().extract(epub_path)
    annotations = report.chapters[0].annotations
    chapter_text = report.chapters[0].text

    # char_offsetは見出し(h1)を含む本文全体における位置(5.4節: 見出しも意味構造として保持する)。
    assert annotations["ruby"][0]["base"] == "音声"
    assert annotations["ruby"][0]["reading"] == "おんせい"
    ruby_offset = annotations["ruby"][0]["char_offset"]
    assert chapter_text[ruby_offset : ruby_offset + 2] == "音声"
    assert "音声" in report.chapters[0].text
    assert "おんせい" not in report.chapters[0].text  # ルビの読みは本文へ挿入しない

    assert len(annotations["images"]) == 1
    assert annotations["images"][0]["src"] == "images/fig01.png"
    assert annotations["images"][0]["alt"] == "図1"
    assert "図1" not in report.chapters[0].text  # alt textは本文へ挿入しない


@pytest.mark.unit
def test_tc_epub_001_08(tmp_path: Path) -> None:
    """TC-EPUB-001-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as exc_info:
        EpubTextExtractor().extract(None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        detect_drm_or_encryption(None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        EpubTextExtractor().extract(tmp_path / "does-not-exist.epub")
    assert exc_info.value.code is ErrorCode.NOT_FOUND

    with pytest.raises(AppError):
        EpubChapter(xhtml_path="a.xhtml")  # spine_index欠落
    with pytest.raises(AppError):
        EpubChapter(spine_index=0)  # xhtml_path欠落
    with pytest.raises(AppError):
        EpubExtractionReport(chapters=())  # epub_version欠落


@pytest.mark.unit
def test_tc_epub_001_09(tmp_path: Path) -> None:
    """TC-EPUB-001-09 — 再実行時の決定性: 同じ入力を2回抽出しても同じ論理結果を返す。"""
    epub_path = _write_epub(
        tmp_path / "annotated.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1"],
        files={"a-first.xhtml": _CHAPTER_WITH_ANNOTATIONS},
    )

    first = EpubTextExtractor().extract(epub_path)
    second = EpubTextExtractor().extract(epub_path)

    assert first.epub_version == second.epub_version
    assert [c.text for c in first.chapters] == [c.text for c in second.chapters]
    assert [c.annotations for c in first.chapters] == [c.annotations for c in second.chapters]


@pytest.mark.unit
def test_tc_epub_001_10(tmp_path: Path) -> None:
    """TC-EPUB-001-10 — 入力・既存成果物の不変性: 正常処理・失敗処理いずれも入力EPUBのbyteを変えない。"""
    epub_path = _simple_two_chapter_epub(tmp_path / "book.epub")
    before_hash = hashlib.sha256(epub_path.read_bytes()).hexdigest()

    EpubTextExtractor().extract(epub_path)
    assert hashlib.sha256(epub_path.read_bytes()).hexdigest() == before_hash

    encrypted_path = _write_epub(
        tmp_path / "encrypted.epub",
        manifest_items=[("chap1", "a-first.xhtml", "application/xhtml+xml")],
        spine_idrefs=["chap1"],
        files={"a-first.xhtml": _CHAPTER_1},
        encrypted=True,
    )
    encrypted_before_hash = hashlib.sha256(encrypted_path.read_bytes()).hexdigest()
    with pytest.raises(AppError):
        EpubTextExtractor().extract(encrypted_path)
    assert hashlib.sha256(encrypted_path.read_bytes()).hexdigest() == encrypted_before_hash
    # 失敗した処理は、既存の正常なEPUB(book.epub)にも影響しない。
    assert hashlib.sha256(epub_path.read_bytes()).hexdigest() == before_hash
