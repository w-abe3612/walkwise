"""script/tts_clients/registry.py — 公開契約: TTSClientRegistry.register/get.

Contract: docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md
Spec: docs/specifications/10-tts-client-common-interface.md
"""

from __future__ import annotations

from script.core.errors import AppError, ErrorCode
from script.tts_clients.base import TTSClient, TTSClientError, TTSErrorCode


class TTSClientRegistry:
    """engine名でTTSClientを選択する。上位処理は具体クライアントを直接importしない。"""

    def __init__(self) -> None:
        self._clients: dict[str, TTSClient] = {}

    def register(self, engine: str, client: TTSClient) -> None:
        """engine名でclientを登録する。"""
        if not engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        if client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "client is required")
        self._clients[engine] = client

    def get(self, engine: str) -> TTSClient:
        """engine名でclientを選択し、未登録engineを拒否する。"""
        if not engine:
            raise AppError(ErrorCode.VALIDATION_ERROR, "engine is required")
        try:
            return self._clients[engine]
        except KeyError as exc:
            raise TTSClientError(TTSErrorCode.UNSUPPORTED_ENGINE, engine_detail=engine) from exc
