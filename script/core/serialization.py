"""script/core/serialization.py — 公開契約: load_yaml/load_json/dump_yaml/dump_json.

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Spec: docs/specifications/01-common-identifiers-and-versioning.md (8節 スキーマバージョン)
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import yaml

from script.core.errors import AppError, ErrorCode

_SUPPORTED_SCHEMA_MAJOR = 1


class UnknownSchemaMinorWarning(UserWarning):
    """読める未知minorを検出した場合に送出するwarning。"""


def _check_schema_version(data: Any) -> None:
    if not isinstance(data, dict) or "schema_version" not in data:
        return
    version = data["schema_version"]
    if not isinstance(version, str) or "." not in version:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid schema_version: {version!r}")
    major_str, _, minor_str = version.partition(".")
    try:
        major = int(major_str)
        minor = int(minor_str)
    except ValueError as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid schema_version: {version!r}") from exc
    if major != _SUPPORTED_SCHEMA_MAJOR:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"unsupported schema_version major: {major}")
    if minor != 0:
        warnings.warn(f"unknown schema_version minor: {minor}", UnknownSchemaMinorWarning, stacklevel=2)


def load_yaml(path: Path) -> Any:
    """安全なUTF-8読込とschema version検証を行う。"""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise AppError(ErrorCode.NOT_FOUND, f"cannot read yaml file: {path}") from exc
    data = yaml.safe_load(text)
    _check_schema_version(data)
    return data


def load_json(path: Path) -> Any:
    """安全なUTF-8読込とschema version検証を行う。"""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise AppError(ErrorCode.NOT_FOUND, f"cannot read json file: {path}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid json in {path}") from exc
    _check_schema_version(data)
    return data


def dump_yaml(path: Path, data: Any) -> None:
    """安全なUTF-8書込を行う。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    path.write_text(text, encoding="utf-8")


def dump_json(path: Path, data: Any) -> None:
    """安全なUTF-8書込を行う。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)
    path.write_text(text, encoding="utf-8")
