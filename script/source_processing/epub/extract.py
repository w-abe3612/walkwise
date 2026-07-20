"""script/source_processing/epub/extract.py — 公開契約:
EpubTextExtractor.extract(path) -> EpubExtractionReport, detect_drm_or_encryption(path) -> bool.

Contract: docs/test-cases/TASK-EPUB-001-epub-text-extraction.md
Spec: docs/specifications/epub-text-extraction.md(5.1〜5.5節)
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.source_processing.epub.models import EpubChapter, EpubExtractionReport

_CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
_OPF_NS = "http://www.idpf.org/2007/opf"
_XHTML_NS = "http://www.w3.org/1999/xhtml"
_OPS_NS = "http://www.idpf.org/2007/ops"
_DRM_MARKER = "META-INF/encryption.xml"
_HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
_BLOCK_TAGS = ("p", "li", *_HEADING_TAGS)


def _open_epub_zip(path: Path) -> zipfile.ZipFile:
    try:
        return zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"not a valid EPUB (zip) file: {path}") from exc


def detect_drm_or_encryption(path: Any) -> bool:
    """暗号化・DRM疑いを処理前に検出し拒否する(5.1節)。

    Public contract: ``detect_drm_or_encryption(path) -> bool``.
    """
    if not path:
        raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")
    resolved = Path(path)
    if not resolved.is_file():
        raise AppError(ErrorCode.NOT_FOUND, f"epub file not found: {resolved}")

    with _open_epub_zip(resolved) as archive:
        return _DRM_MARKER in archive.namelist()


def _read_zip_text(archive: zipfile.ZipFile, member: str) -> str:
    try:
        data = archive.read(member)
    except KeyError as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid EPUB: missing file {member}") from exc
    return data.decode("utf-8")


def _resolve_rootfile(container_xml: str) -> str:
    root = ET.fromstring(container_xml)
    rootfile = root.find(f".//{{{_CONTAINER_NS}}}rootfile")
    full_path = rootfile.get("full-path") if rootfile is not None else None
    if not full_path:
        raise AppError(ErrorCode.VALIDATION_ERROR, "invalid EPUB: container.xml is missing a rootfile")
    return full_path


def _parse_opf(opf_xml: str) -> tuple[str, dict[str, str], list[str]]:
    root = ET.fromstring(opf_xml)
    epub_version = root.get("version") or "2.0"

    manifest_elem = root.find(f"{{{_OPF_NS}}}manifest")
    if manifest_elem is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "invalid EPUB: package document is missing manifest")
    manifest: dict[str, str] = {}
    for item in manifest_elem.findall(f"{{{_OPF_NS}}}item"):
        item_id, href = item.get("id"), item.get("href")
        if item_id and href:
            manifest[item_id] = href

    spine_elem = root.find(f"{{{_OPF_NS}}}spine")
    if spine_elem is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "invalid EPUB: package document is missing spine")
    spine_ids: list[str] = []
    seen: set[str] = set()
    for itemref in spine_elem.findall(f"{{{_OPF_NS}}}itemref"):
        idref = itemref.get("idref")
        if not idref:
            continue
        if idref in seen:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid EPUB: duplicate spine itemref: {idref}")
        seen.add(idref)
        spine_ids.append(idref)

    return epub_version, manifest, spine_ids


def _local_tag(elem: ET.Element) -> str:
    tag = elem.tag
    return tag.split("}", 1)[1] if "}" in tag else tag


def _epub_type(elem: ET.Element) -> str | None:
    return elem.get(f"{{{_OPS_NS}}}type")


def _collect_footnote_definitions(root: ET.Element) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for elem in root.iter():
        if _epub_type(elem) == "footnote":
            note_id = elem.get("id")
            if note_id:
                definitions[note_id] = "".join(elem.itertext()).strip()
    return definitions


def _ruby_base_text(elem: ET.Element) -> str:
    rb_children = [child for child in elem if _local_tag(child) == "rb"]
    if rb_children:
        return "".join("".join(child.itertext()) for child in rb_children).strip()
    return (elem.text or "").strip()


def _ruby_reading_text(elem: ET.Element) -> str:
    rt_children = [child for child in elem if _local_tag(child) == "rt"]
    return "".join("".join(child.itertext()) for child in rt_children).strip()


class _ChapterExtraction:
    """1 XHTMLファイルの抽出状態(本文・annotation)を蓄積する非公開helper。"""

    def __init__(self, footnote_definitions: dict[str, str]) -> None:
        self._footnote_definitions = footnote_definitions
        self._body_parts: list[str] = []
        self.ruby: list[dict[str, Any]] = []
        self.footnotes: list[dict[str, Any]] = []
        self.images: list[dict[str, Any]] = []
        self.chapter_title: str | None = None

    def _offset(self) -> int:
        return sum(len(part) for part in self._body_parts)

    def _append_text(self, text: str | None) -> None:
        if text and text.strip():
            self._body_parts.append(text.strip())

    def walk(self, elem: ET.Element) -> None:
        tag = _local_tag(elem)
        elem_id = elem.get("id")

        # 脚注本文自体は本文へ含めない(5.3節: 本文へ無条件で埋め込まない)。
        if _epub_type(elem) == "footnote" or (elem_id and elem_id in self._footnote_definitions):
            return

        if tag == "ruby":
            base_text = _ruby_base_text(elem)
            reading = _ruby_reading_text(elem)
            self.ruby.append({"base": base_text, "reading": reading, "char_offset": self._offset()})
            self._append_text(base_text)
            return

        if tag == "img":
            self.images.append({"src": elem.get("src", ""), "alt": elem.get("alt", ""), "char_offset": self._offset()})
            return

        href = elem.get("href", "")
        ref_id = href.split("#", 1)[1] if "#" in href else None
        if tag == "a" and ref_id and ref_id in self._footnote_definitions:
            self.footnotes.append(
                {"ref_id": ref_id, "text": self._footnote_definitions[ref_id], "char_offset": self._offset()}
            )
            return  # 参照記号自体は本文へ含めない(annotationとしてのみ保持)。

        if tag in _HEADING_TAGS and self.chapter_title is None:
            self.chapter_title = "".join(elem.itertext()).strip()

        self._append_text(elem.text)
        for child in elem:
            self.walk(child)
            self._append_text(child.tail)

        if tag in _BLOCK_TAGS:
            self._body_parts.append("\n\n")

    @property
    def text(self) -> str:
        return "".join(self._body_parts).strip()


def _extract_chapter_content(xhtml_text: str) -> tuple[str, dict[str, tuple[Any, ...]], str | None]:
    try:
        root = ET.fromstring(xhtml_text)
    except ET.ParseError as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"unparsable XHTML: {exc}") from exc

    footnote_definitions = _collect_footnote_definitions(root)
    extraction = _ChapterExtraction(footnote_definitions)

    body_elem = root.find(f".//{{{_XHTML_NS}}}body")
    extraction.walk(body_elem if body_elem is not None else root)

    annotations = {
        "ruby": tuple(extraction.ruby),
        "footnotes": tuple(extraction.footnotes),
        "images": tuple(extraction.images),
    }
    return extraction.text, annotations, extraction.chapter_title


class EpubTextExtractor:
    """DRM-freeなEPUB 2/3をspine順に抽出する(5.1〜5.3節)。"""

    def extract(self, path: Any) -> EpubExtractionReport:
        """DRM-free EPUBをspine順で抽出する。

        Public contract: ``EpubTextExtractor.extract(path) -> EpubExtractionReport``.
        """
        if not path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")
        resolved = Path(path)
        if not resolved.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"epub file not found: {resolved}")

        if detect_drm_or_encryption(resolved):
            # 5.1節: DRM/暗号化は解除せず、処理せずに拒否する。
            raise AppError(ErrorCode.VALIDATION_ERROR, "unsupported_drm: encrypted or DRM-protected EPUB is not supported")

        with _open_epub_zip(resolved) as archive:
            container_xml = _read_zip_text(archive, "META-INF/container.xml")
            opf_path = _resolve_rootfile(container_xml)
            opf_xml = _read_zip_text(archive, opf_path)
            epub_version, manifest, spine_ids = _parse_opf(opf_xml)

            opf_dir = str(Path(opf_path).parent).replace("\\", "/")
            opf_dir = "" if opf_dir == "." else opf_dir

            chapters: list[EpubChapter] = []
            warnings: list[str] = []
            for spine_index, idref in enumerate(spine_ids):
                href = manifest.get(idref)
                if href is None:
                    warnings.append(f"spine itemref references unknown manifest id: {idref}")
                    continue
                xhtml_path = f"{opf_dir}/{href}" if opf_dir else href
                try:
                    xhtml_text = _read_zip_text(archive, xhtml_path)
                except AppError:
                    warnings.append(f"missing spine xhtml file: {xhtml_path}")
                    continue
                try:
                    text, annotations, chapter_title = _extract_chapter_content(xhtml_text)
                except AppError as exc:
                    warnings.append(f"unparsable xhtml, skipped: {xhtml_path} ({exc.message})")
                    continue

                chapters.append(
                    EpubChapter(
                        spine_index=spine_index,
                        order=spine_index,
                        xhtml_path=xhtml_path,
                        chapter_title=chapter_title,
                        text=text,
                        annotations=annotations,
                    )
                )

        return EpubExtractionReport(epub_version=epub_version, chapters=tuple(chapters), warnings=tuple(warnings))
