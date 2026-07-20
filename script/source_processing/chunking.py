"""script/source_processing/chunking.py — 公開契約: chunk_structured_source(source, *, soft_limit=2000) -> list[SourceChunk].

Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
Spec: docs/specifications/source-storage-and-common-schema.md (5.6節 chunk分割の原則)
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from script.core.errors import AppError, ErrorCode
from script.core.hashing import canonical_sha256

_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")

_DEFAULT_SOFT_LIMIT = 2000


@dataclass(frozen=True)
class ChunkLocator:
    """typed locator(chapter/section/page)。すべて任意項目。"""

    chapter: str | None = None
    section: str | None = None
    page: int | None = None


@dataclass(frozen=True)
class StructuredSourceInput:
    """chunk_structured_sourceへの入力。"""

    source_id: str
    text: str
    locator: ChunkLocator | None = None


@dataclass(frozen=True)
class SourceChunk:
    """決定的に分割された1 chunk。locatorを保持する。"""

    chunk_id: str
    order: int
    text: str
    locator: ChunkLocator
    input_hash: str

    def __post_init__(self) -> None:
        if not self.chunk_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chunk_id is required")
        if self.order < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "order must be 1 or greater")


def _split_paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in _PARAGRAPH_SPLIT_RE.split(text) if paragraph.strip()]


def _pack_paragraphs(paragraphs: Sequence[str], soft_limit: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        paragraph_len = len(paragraph)
        additional_len = paragraph_len + (2 if current else 0)
        if current and current_len + additional_len > soft_limit:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_len = paragraph_len
        else:
            current.append(paragraph)
            current_len += additional_len

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def chunk_structured_source(source: StructuredSourceInput, *, soft_limit: int = _DEFAULT_SOFT_LIMIT) -> list[SourceChunk]:
    """locatorを保持して決定的chunkを作る。"""
    if source is None or not source.source_id or not source.text:
        raise AppError(ErrorCode.VALIDATION_ERROR, "source (with source_id and text) is required")
    if not soft_limit or soft_limit <= 0:
        raise AppError(ErrorCode.VALIDATION_ERROR, "soft_limit must be a positive number")

    paragraphs = _split_paragraphs(source.text)
    if not paragraphs:
        raise AppError(ErrorCode.VALIDATION_ERROR, "source.text must contain at least one non-empty paragraph")

    locator = source.locator or ChunkLocator()
    chunk_texts = _pack_paragraphs(paragraphs, soft_limit)

    chunks: list[SourceChunk] = []
    for order, chunk_text in enumerate(chunk_texts, start=1):
        chunk_id = f"{source.source_id}-chunk-{order:04d}"
        chunks.append(
            SourceChunk(
                chunk_id=chunk_id,
                order=order,
                text=chunk_text,
                locator=locator,
                input_hash=canonical_sha256({"text": chunk_text}),
            )
        )
    return chunks
