"""script/source_processing/normalize.py — 公開契約: normalize_text(text, rules) -> NormalizationResult.

Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
Spec: docs/specifications/source-preprocessing.md
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

from script.core.errors import AppError, ErrorCode
from script.core.hashing import canonical_sha256

_FENCE_RE = re.compile(r"(```.*?```)", re.DOTALL)
_FOOTNOTE_LINE_RE = re.compile(r"^\[(\d+)\]:\s*(.+)$")
_MAX_REPEATED_LINE_LENGTH = 80


@dataclass(frozen=True)
class NormalizationRules:
    """低リスク・決定的な正規化の設定(source-preprocessing.md 5.2節)。"""

    unicode_form: str = "NFKC"
    remove_repeated_headers_footers: bool = True
    separate_footnotes: bool = True
    preserve_fenced_blocks: bool = True


@dataclass(frozen=True)
class NormalizationResult:
    """normalize_textの戻り値。before/after hashとdiffを保持する。"""

    original_text: str
    normalized_text: str
    input_hash: str
    output_hash: str
    diff: tuple[str, ...] = ()
    removed_lines: tuple[str, ...] = ()
    footnotes: dict[str, str] = field(default_factory=dict)


def _remove_repeated_headers_footers(lines: list[str]) -> tuple[list[str], list[str]]:
    counts = Counter(line for line in lines if line.strip())
    repeated = {line for line, count in counts.items() if count >= 2 and len(line) <= _MAX_REPEATED_LINE_LENGTH}

    kept: list[str] = []
    removed: list[str] = []
    seen_once: set[str] = set()
    for line in lines:
        if line in repeated:
            if line in seen_once:
                removed.append(line)
                continue
            seen_once.add(line)
        kept.append(line)
    return kept, removed


def _extract_footnotes(lines: list[str]) -> tuple[list[str], dict[str, str]]:
    kept: list[str] = []
    footnotes: dict[str, str] = {}
    for line in lines:
        match = _FOOTNOTE_LINE_RE.match(line.strip())
        if match:
            footnotes[match.group(1)] = match.group(2)
            continue
        kept.append(line)
    return kept, footnotes


def _normalize_segment(text: str, rules: NormalizationRules) -> tuple[str, list[str], dict[str, str]]:
    working = unicodedata.normalize(rules.unicode_form, text) if rules.unicode_form else text
    working = working.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in working.split("\n")]

    removed_lines: list[str] = []
    if rules.remove_repeated_headers_footers:
        lines, removed_lines = _remove_repeated_headers_footers(lines)

    footnotes: dict[str, str] = {}
    if rules.separate_footnotes:
        lines, footnotes = _extract_footnotes(lines)

    return "\n".join(lines), removed_lines, footnotes


def normalize_text(text: str, rules: NormalizationRules) -> NormalizationResult:
    """低リスク・決定的変換とdiff/hashを返す。"""
    if not text:
        raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")
    if rules is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "rules is required")

    input_hash = canonical_sha256({"text": text})

    if rules.preserve_fenced_blocks:
        segments = _FENCE_RE.split(text)
    else:
        segments = [text]

    normalized_segments: list[str] = []
    all_removed_lines: list[str] = []
    all_footnotes: dict[str, str] = {}
    for segment in segments:
        if segment.startswith("```") and segment.endswith("```"):
            # structured Markdown/YAML/JSON等のfenced blockは正規化対象外(内容を変えない)。
            normalized_segments.append(segment)
            continue
        normalized_segment, removed_lines, footnotes = _normalize_segment(segment, rules)
        normalized_segments.append(normalized_segment)
        all_removed_lines.extend(removed_lines)
        all_footnotes.update(footnotes)

    normalized_text = "".join(normalized_segments)
    output_hash = canonical_sha256({"text": normalized_text})
    diff = tuple(
        difflib.unified_diff(
            text.splitlines(),
            normalized_text.splitlines(),
            lineterm="",
        )
    )

    return NormalizationResult(
        original_text=text,
        normalized_text=normalized_text,
        input_hash=input_hash,
        output_hash=output_hash,
        diff=diff,
        removed_lines=tuple(all_removed_lines),
        footnotes=all_footnotes,
    )
