"""script/domain/validation.py — 公開契約: canonicalize_output_formats, validate_build_request.

Contract: docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md
Spec: docs/db/03-build-requests-table.md (4節)
"""

from __future__ import annotations

from collections.abc import Sequence

from script.core.errors import AppError, ErrorCode

_ALLOWED_FORMATS = ("mp3", "text")
_CANONICAL_ORDER = {"mp3": 0, "text": 1}


def canonicalize_output_formats(values: Sequence[str]) -> tuple[str, ...]:
    """mp3→text順へ正規化し、空・未知・重複を拒否する。"""
    if not values:
        raise AppError(ErrorCode.VALIDATION_ERROR, "output_formats must not be empty")

    unique = list(dict.fromkeys(values))
    if len(unique) != len(values):
        raise AppError(ErrorCode.VALIDATION_ERROR, "output_formats must not contain duplicates")

    unknown = [value for value in unique if value not in _ALLOWED_FORMATS]
    if unknown:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown output format(s): {unknown}")

    return tuple(sorted(unique, key=lambda value: _CANONICAL_ORDER[value]))


def validate_build_request(formats: Sequence[str], voice_profile_id: str | None) -> None:
    """mp3を含む場合だけvoice必須とする。"""
    if "mp3" in formats and not voice_profile_id:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            "voice_profile_required: voice_profile_id is required when output_formats includes mp3",
        )


def _assert_relative_path(field_name: str, value: str) -> None:
    """Project root基準の相対path文字列だけを許可する内部helper。"""
    if not value:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"{field_name} must not be empty")
    if value.startswith("/") or ":" in value or value.startswith("\\"):
        raise AppError(ErrorCode.VALIDATION_ERROR, f"{field_name} must be a relative path: {value!r}")
    if ".." in value.replace("\\", "/").split("/"):
        raise AppError(ErrorCode.VALIDATION_ERROR, f"{field_name} must not escape project root: {value!r}")
