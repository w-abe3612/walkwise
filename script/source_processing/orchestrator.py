"""script/source_processing/orchestrator.py — 公開契約: MaterialInputOrchestrator.register_adapter/process.

Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
Spec: docs/specifications/material-input-pipeline.md
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from script.core.errors import AppError, ErrorCode

# 19-application-scope-and-mvp.md 5.5節: 動画・録音・Kindle操作は製品の恒久的対象外。
# epub-text-extraction.mdはpost-MVP承認済みだが、本タスク(MVP)の対象外。
_PERMANENTLY_UNSUPPORTED_MEDIA_TYPES = frozenset({"epub", "video", "audio_recording", "kindle_capture"})

ProgressHook = Callable[[int, int, str], None]


class MediaAdapter(Protocol):
    """orchestratorが呼び出すmedia typeごとの処理adapterの形状。"""

    def process(self, path: Path, context: Mapping[str, Any]) -> Any: ...


@dataclass(frozen=True)
class IngestSource:
    """処理対象1件の入力。"""

    source_id: str
    media_type: str
    path: Path
    context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProcessingResult:
    """dispatch結果。status='structured'のときのみstructuredを持つ。"""

    source_id: str
    media_type: str
    status: str
    structured: Any | None = None
    error: dict[str, str] | None = None


class MaterialInputOrchestrator:
    """media typeとadapterを登録し、Sourceを対応adapterへdispatchする。"""

    def __init__(self, *, progress_hook: ProgressHook | None = None) -> None:
        self._adapters: dict[str, MediaAdapter] = {}
        self._progress_hook = progress_hook

    def register_adapter(self, media_type: str, adapter: MediaAdapter) -> None:
        """media typeとadapterを一意に登録する。"""
        if not media_type:
            raise AppError(ErrorCode.VALIDATION_ERROR, "media_type is required")
        if adapter is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "adapter is required")
        if media_type in self._adapters:
            raise AppError(ErrorCode.CONFLICT, f"adapter already registered for media_type: {media_type}")
        self._adapters[media_type] = adapter

    def process(self, source: IngestSource) -> ProcessingResult:
        """text/pdf/imageを対応adapterへdispatchし状態・進捗を更新する。"""
        if source is None or not source.source_id or not source.media_type or not source.path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id, media_type and path are required")

        if source.media_type in _PERMANENTLY_UNSUPPORTED_MEDIA_TYPES:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"unsupported_media_type: {source.media_type}",
            )

        adapter = self._adapters.get(source.media_type)
        if adapter is None:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"unsupported_media_type: {source.media_type}",
            )

        self._notify(0, 1, f"processing {source.source_id}")
        try:
            structured = adapter.process(source.path, source.context)
        except AppError as exc:
            self._notify(1, 1, f"failed {source.source_id}")
            return ProcessingResult(
                source_id=source.source_id,
                media_type=source.media_type,
                status="failed",
                structured=None,
                error=exc.to_public_dict(),
            )

        self._notify(1, 1, f"structured {source.source_id}")
        return ProcessingResult(
            source_id=source.source_id,
            media_type=source.media_type,
            status="structured",
            structured=structured,
            error=None,
        )

    def _notify(self, current: int, total: int, message: str) -> None:
        if self._progress_hook is not None:
            self._progress_hook(current, total, message)
