"""Implementation for TASK-CORE-001: 設定・共通エラー・ログ契約 (logging).

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
Production file exercised: script/core/logging.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.core.config import AppConfig
from script.core.errors import AppError
from script.core.logging import configure_logging

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_core_001_03(tmp_path: Path) -> None:
    """TC-CORE-001-03 — ログredaction

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: API keyを含むcontextがある
    When: ログを出力する
    Then: keyを伏せ、timestampはtimezone付きISO 8601になる
    """
    logger = configure_logging(tmp_path, level="INFO")
    secret_value = "sk-super-secret-value-123"
    context = {"api_key": secret_value, "project_id": "database-introduction"}

    logger.info("calling external client with context: %s", context)
    for handler in logger.handlers:
        handler.flush()

    log_file = tmp_path / "walkwise.log"
    assert log_file.is_file()
    log_text = log_file.read_text(encoding="utf-8")

    assert secret_value not in log_text
    assert "REDACTED" in log_text
    assert "project_id" in log_text and "database-introduction" in log_text

    first_line = log_text.splitlines()[0]
    timestamp = first_line.split(" ", 1)[0]
    assert "T" in timestamp
    assert timestamp[-6] in "+-" or timestamp.endswith("Z")


@pytest.mark.unit
def test_tc_core_001_06(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-CORE-001-06 — 必須入力欠落

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `AppConfig.load(env: Mapping[str, str] | None = None) -> AppConfig`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    monkeypatch.delenv("WALKWISE_DATA_ROOT", raising=False)
    existing_files_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError) as exc_info:
        AppConfig.load(env={})

    assert exc_info.value.code.value == "validation_error"
    assert "WALKWISE_DATA_ROOT" in exc_info.value.message
    assert sorted(tmp_path.iterdir()) == existing_files_before
