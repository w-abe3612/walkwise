"""script/ai/cache.py — 公開契約: AICache.get/put(key, result).

Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class AICacheKey:
    """12節: task_type/logical_tier/physical_model/prompt_id/prompt_version/
    input_hash/schema_version/generation_parametersを最低限含むcache key。"""

    task_type: str
    logical_tier: str
    model: str
    prompt_id: str
    prompt_version: str
    input_hash: str
    schema_version: str = "1.0"
    generation_parameters: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if not self.task_type:
            raise AppError(ErrorCode.VALIDATION_ERROR, "task_type is required")
        if not self.model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")
        if not self.prompt_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "prompt_id is required")
        if not self.input_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "input_hash is required")


class AICache:
    """task/model/prompt/input hashをkeyに、成功結果を再利用するcache。"""

    def __init__(self) -> None:
        self._store: dict[AICacheKey, Any] = {}

    def get(self, key: AICacheKey) -> Any | None:
        """該当keyの既存結果を返す(なければNone)。"""
        if key is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "key is required")
        return self._store.get(key)

    def put(self, key: AICacheKey, result: Any) -> None:
        """該当keyへ結果を保存し、以降のgetで再利用可能にする。"""
        if key is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "key is required")
        self._store[key] = result
