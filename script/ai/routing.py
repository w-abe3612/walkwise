"""script/ai/routing.py — 公開契約: AIRouter.resolve(task_class, policy) -> ModelSelection.

Contract: docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from script.core.errors import AppError, ErrorCode

# 18-ai-model-routing-and-cost-control.md 4.1節: 処理仕様は論理層のみを参照する。
LOGICAL_TIERS = ("economy_structuring", "standard_generation", "high_assurance_review")


@dataclass(frozen=True)
class ModelPolicy:
    """project/ai/model-policy.yaml相当の、論理層->物理モデル解決設定。"""

    provider: str
    tiers: Mapping[str, Mapping[str, Any]]

    def __post_init__(self) -> None:
        if not self.provider:
            raise AppError(ErrorCode.VALIDATION_ERROR, "provider is required")
        if not self.tiers:
            raise AppError(ErrorCode.VALIDATION_ERROR, "tiers must not be empty")

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "ModelPolicy":
        """model-policy.yamlの読込結果(dict)からModelPolicyを作る。"""
        if not mapping or "tiers" not in mapping:
            raise AppError(ErrorCode.VALIDATION_ERROR, "policy mapping must contain 'tiers'")
        return cls(provider=mapping.get("provider", "google"), tiers=dict(mapping["tiers"]))


@dataclass(frozen=True)
class ModelSelection:
    """resolve()の戻り値。物理provider/modelとescalation有無を保持する。"""

    logical_tier: str
    model: str
    provider: str = "google"
    escalated: bool = False

    def __post_init__(self) -> None:
        if self.logical_tier not in LOGICAL_TIERS:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown logical tier: {self.logical_tier}")
        if not self.model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")


class AIRouter:
    """論理層(economy/standard/high_assurance)から物理provider/modelを解決する。"""

    def __init__(self, *, env: Mapping[str, str] | None = None) -> None:
        self._env = env if env is not None else os.environ

    def resolve(self, task_class: str, policy: ModelPolicy) -> ModelSelection:
        """論理層から物理provider/modelを解決し黙った降格をしない。"""
        if not task_class:
            raise AppError(ErrorCode.VALIDATION_ERROR, "task_class is required")
        if policy is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "policy is required")
        if task_class not in policy.tiers:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown logical tier: {task_class}")

        tier_config = policy.tiers[task_class]
        env_override_name = tier_config.get("env_override")
        model = (self._env.get(env_override_name) if env_override_name else None) or tier_config.get("model")

        if not model:
            if tier_config.get("required_when_invoked"):
                # 18-ai-model-routing-and-cost-control.md 5.3節:
                # high_assurance未設定時はstandardへ黙って降格せずblockedにする。
                raise AppError(
                    ErrorCode.EXTERNAL_UNAVAILABLE,
                    f"{task_class} requires a configured model; refusing to silently downgrade",
                )
            raise AppError(ErrorCode.VALIDATION_ERROR, f"no model configured for tier: {task_class}")

        return ModelSelection(logical_tier=task_class, model=model, provider=policy.provider)
