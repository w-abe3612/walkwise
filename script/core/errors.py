"""script/core/errors.py — 公開契約: AppError(code, message, technical_detail=None).

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """業務上予測可能な失敗を表す安定したerror code。"""

    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    PERMISSION_DENIED = "permission_denied"
    EXTERNAL_UNAVAILABLE = "external_unavailable"
    INTERNAL_ERROR = "internal_error"


class AppError(RuntimeError):
    """利用者向けmessageとtechnical detailを分離するerror。

    Public contract: ``AppError(code: ErrorCode, message: str, technical_detail: str | None = None)``.
    """

    def __init__(self, code: ErrorCode, message: str, technical_detail: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.technical_detail = technical_detail

    def to_public_dict(self) -> dict[str, str]:
        """利用者向け公開表現。technical_detailは含めない。"""
        return {"code": self.code.value, "message": self.message}
