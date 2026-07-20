"""script/core/logging.py — 公開契約: configure_logging(log_dir, *, level='INFO') -> logging.Logger.

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

_LOGGER_NAME = "walkwise"
_LOG_FILE_NAME = "walkwise.log"
_REDACTED = "***REDACTED***"

_SECRET_PATTERN = re.compile(
    r"(?i)(['\"]?\b(?:api[_-]?key|access[_-]?token|secret|password)\b['\"]?\s*[:=]\s*['\"]?)"
    r"([^\s,'\"}\]]+)"
)


def _redact(text: str) -> str:
    return _SECRET_PATTERN.sub(lambda m: f"{m.group(1)}{_REDACTED}", text)


class _RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            record.msg = _redact(record.getMessage())
            record.args = ()
        else:
            record.msg = _redact(str(record.msg))
        return True


class _UtcIsoFormatter(logging.Formatter):
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()


def configure_logging(log_dir: Path, *, level: str = "INFO") -> logging.Logger:
    """ISO 8601 timestampでファイルログを設定し秘密値をredactする。"""
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    for existing_handler in list(logger.handlers):
        logger.removeHandler(existing_handler)
    for existing_filter in list(logger.filters):
        logger.removeFilter(existing_filter)

    handler = logging.FileHandler(log_dir / _LOG_FILE_NAME, encoding="utf-8")
    handler.setFormatter(_UtcIsoFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.addFilter(_RedactingFilter())
    return logger
