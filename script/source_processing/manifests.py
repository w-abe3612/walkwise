"""script/source_processing/manifests.py — 公開契約: build_chunk_manifest(chunks) / build_topic_index(...).

Contract: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
Spec: docs/specifications/source-storage-and-common-schema.md
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.source_processing.chunking import SourceChunk


def build_chunk_manifest(chunks: Sequence[SourceChunk]) -> dict[str, Any]:
    """参照可能なmanifest/indexを生成する(chunk_id/orderの重複を拒否する)。"""
    if not chunks:
        raise AppError(ErrorCode.VALIDATION_ERROR, "chunks must not be empty")

    seen_ids: set[str] = set()
    seen_orders: set[int] = set()
    for chunk in chunks:
        if chunk.chunk_id in seen_ids:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate chunk_id: {chunk.chunk_id}")
        if chunk.order in seen_orders:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate order: {chunk.order}")
        seen_ids.add(chunk.chunk_id)
        seen_orders.add(chunk.order)

    ordered = sorted(chunks, key=lambda chunk: chunk.order)
    return {
        "schema_version": "1.0",
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "order": chunk.order,
                "locator": {
                    "chapter": chunk.locator.chapter,
                    "section": chunk.locator.section,
                    "page": chunk.locator.page,
                },
                "input_hash": chunk.input_hash,
            }
            for chunk in ordered
        ],
    }


def build_topic_index(topics: Mapping[str, Sequence[str]], *, chunk_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """参照可能なmanifest/indexを生成する(存在しないchunk_idへの参照を拒否する)。"""
    if not topics:
        raise AppError(ErrorCode.VALIDATION_ERROR, "topics must not be empty")
    if chunk_manifest is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "chunk_manifest is required")

    known_chunk_ids = {chunk["chunk_id"] for chunk in chunk_manifest.get("chunks", [])}

    entries = []
    for topic_id, chunk_refs in topics.items():
        if not chunk_refs:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"topic {topic_id!r} must reference at least one chunk_id")
        for chunk_ref in chunk_refs:
            if chunk_ref not in known_chunk_ids:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"topic {topic_id!r} references unknown chunk_id: {chunk_ref!r}",
                )
        entries.append({"topic_id": topic_id, "chunk_refs": list(chunk_refs)})

    return {"schema_version": "1.0", "topics": entries}
