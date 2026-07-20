"""script/core/hashing.py — 公開契約: canonical_sha256(value, *, excluded_keys=()) -> str.

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Spec: docs/specifications/01-common-identifiers-and-versioning.md (11節 正規化)
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Collection
from typing import Any, Union

JsonValue = Union[None, bool, int, float, str, list["JsonValue"], dict[str, "JsonValue"]]


def _normalize_strings(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value).replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(value, dict):
        return {key: _normalize_strings(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_strings(item) for item in value]
    return value


def _exclude_keys(value: Any, excluded_keys: frozenset[str]) -> Any:
    if isinstance(value, dict):
        return {
            key: _exclude_keys(item, excluded_keys)
            for key, item in value.items()
            if key not in excluded_keys
        }
    if isinstance(value, list):
        return [_exclude_keys(item, excluded_keys) for item in value]
    return value


def canonical_sha256(value: JsonValue, *, excluded_keys: Collection[str] = ()) -> str:
    """NFC・LF・key順を正規化しSHA-256を返す。入力valueは変更しない。"""
    excluded = frozenset(excluded_keys)
    stripped = _exclude_keys(value, excluded)
    normalized = _normalize_strings(stripped)
    canonical_json = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
