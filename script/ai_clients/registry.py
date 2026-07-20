"""script/ai_clients/registry.py — 公開契約: AIClientRegistry.register/get.

Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
"""

from __future__ import annotations

from script.ai_clients.base import AIClient
from script.core.errors import AppError, ErrorCode


class AIClientRegistry:
    """provider名でAIClient adapterを選択する。"""

    def __init__(self) -> None:
        self._clients: dict[str, AIClient] = {}

    def register(self, provider: str, client: AIClient) -> None:
        """provider名でadapterを一意に登録する。"""
        if not provider:
            raise AppError(ErrorCode.VALIDATION_ERROR, "provider is required")
        if client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "client is required")
        self._clients[provider] = client

    def get(self, provider: str) -> AIClient:
        """登録済みのadapterをprovider名で取得する。"""
        if not provider:
            raise AppError(ErrorCode.VALIDATION_ERROR, "provider is required")
        client = self._clients.get(provider)
        if client is None:
            raise AppError(ErrorCode.NOT_FOUND, f"no AI client registered for provider: {provider}")
        return client
