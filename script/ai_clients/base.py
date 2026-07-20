"""script/ai_clients/base.py — 公開契約: AIClient Protocol, AIRequest/AIResult/AIUsage/AIClientError.

Contract: docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md
Spec: docs/specifications/18-ai-model-routing-and-cost-control.md
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import yaml

from script.core.errors import AppError, ErrorCode

ResponseValidator = Callable[[str], None]


class AIClientError(AppError):
    """AI呼び出し特有の、retry可否を型付けしたerror。"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        retryable: bool = False,
        technical_detail: str | None = None,
    ) -> None:
        super().__init__(code, message, technical_detail)
        self.retryable = retryable


@dataclass(frozen=True)
class AIUsage:
    """token使用量。providerがusageを返さない場合はすべてNoneでよい。"""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class AIRequest:
    """generate()への入力。validate_responseはJSON/YAML等のschema検証hook。"""

    user_text: str
    system_instruction: str = ""
    model: str | None = None
    temperature: float = 0.1
    timeout_sec: float | None = None
    response_mime_type: str | None = None
    validate_response: ResponseValidator | None = None

    def __post_init__(self) -> None:
        if not self.user_text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "user_text is required")


@dataclass(frozen=True)
class AIResult:
    """generate()の戻り値。text/provider/model/usageを共通形式で保持する。"""

    text: str
    provider: str
    model: str
    usage: AIUsage
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.provider:
            raise AppError(ErrorCode.VALIDATION_ERROR, "provider is required")
        if not self.model:
            raise AppError(ErrorCode.VALIDATION_ERROR, "model is required")


def make_json_response_validator() -> ResponseValidator:
    """応答本文がJSONとして解釈可能であることを検証するhookを作る。"""

    def _validate(text: str) -> None:
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIClientError(
                ErrorCode.VALIDATION_ERROR,
                "AI response is not valid JSON",
                retryable=False,
                technical_detail=str(exc),
            ) from exc

    return _validate


def make_yaml_response_validator() -> ResponseValidator:
    """応答本文がYAMLとして解釈可能であることを検証するhookを作る。"""

    def _validate(text: str) -> None:
        try:
            yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise AIClientError(
                ErrorCode.VALIDATION_ERROR,
                "AI response is not valid YAML",
                retryable=False,
                technical_detail=str(exc),
            ) from exc

    return _validate


@runtime_checkable
class AIClient(Protocol):
    """health確認と生成を分離した、providerに依存しない共通契約。"""

    def check_connectivity(self) -> object:
        """認証を含む軽量な疎通確認を副作用なく行う。"""
        ...

    def generate(self, request: AIRequest) -> AIResult:
        """promptを実行しAIResultへ変換する。"""
        ...
