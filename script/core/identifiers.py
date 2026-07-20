"""script/core/identifiers.py — 公開契約: validate_identifier, normalize_unit_id.

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Spec: docs/specifications/01-common-identifiers-and-versioning.md
"""

from __future__ import annotations

import re
import unicodedata

from script.core.errors import AppError, ErrorCode

_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_UNIT_ID_ALIASES: dict[str, str] = {"full_book": "book"}


def validate_identifier(value: str) -> str:
    """`^[a-z0-9]+(?:-[a-z0-9]+)*$`へ適合するIDだけを返す。"""
    if not isinstance(value, str) or not value:
        raise AppError(ErrorCode.VALIDATION_ERROR, "identifier must be a non-empty string")
    if not _ID_PATTERN.fullmatch(value):
        raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid identifier: {value!r}")
    return value


def normalize_unit_id(value: str) -> str:
    """`full_book`を`book`へ正規化し、新規値は変えない。"""
    normalized = unicodedata.normalize("NFC", value)
    return _UNIT_ID_ALIASES.get(normalized, normalized)
