"""script/core/config.py — 公開契約: AppConfig.load(env=None) -> AppConfig.

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from script.core.errors import AppError, ErrorCode

_DEFAULTS: dict[str, str] = {
    "WALKWISE_LOG_LEVEL": "INFO",
}

# WALKWISE_DATA_ROOT is the one setting every task needing local persistence
# depends on (docs/specifications/17-local-data-persistence-policy.md); no
# concrete env var name is mandated upstream, so this is recorded as an
# assumption in docs/notes/implementation_assumptions.md.
_REQUIRED_KEYS: tuple[str, ...] = ("WALKWISE_DATA_ROOT",)


class AppConfig:
    """既定値・環境変数・明示値の優先順位で解決した不変設定。"""

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values: dict[str, str] = dict(values)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._values.get(key, default)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AppConfig):
            return NotImplemented
        return self._values == other._values

    def __repr__(self) -> str:
        return f"AppConfig({self._values!r})"

    @classmethod
    def load(cls, env: Mapping[str, str] | None = None) -> "AppConfig":
        """既定値 < 実行環境変数(os.environ) < 明示的に渡されたenv の優先順位で解決する。"""
        merged: dict[str, str] = dict(_DEFAULTS)
        merged.update(os.environ)
        if env is not None:
            merged.update(env)

        missing = [key for key in _REQUIRED_KEYS if not merged.get(key)]
        if missing:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                f"missing required configuration: {', '.join(missing)}",
            )
        return cls(merged)
