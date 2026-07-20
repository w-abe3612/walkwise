"""Implementation for TASK-CORE-001: 設定・共通エラー・ログ契約 (config).

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
Production file exercised: script/core/config.py
"""

from __future__ import annotations

import pytest

from script.core.config import AppConfig

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_core_001_01(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-CORE-001-01 — 設定優先順位

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: 既定値・env・明示値が異なる
    When: AppConfigを読込む
    Then: 明示値>env>既定値の順で採用する
    """
    monkeypatch.setenv("WALKWISE_DATA_ROOT", "/from/os/environ")
    monkeypatch.setenv("WALKWISE_LOG_LEVEL", "from-env")

    default_only = AppConfig.load(env={"WALKWISE_DATA_ROOT": "/from/os/environ"})
    assert default_only.get("WALKWISE_LOG_LEVEL") == "from-env"

    explicit = AppConfig.load(env={
        "WALKWISE_DATA_ROOT": "/from/os/environ",
        "WALKWISE_LOG_LEVEL": "from-explicit",
    })
    assert explicit.get("WALKWISE_LOG_LEVEL") == "from-explicit"


@pytest.mark.unit
def test_tc_core_001_04(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-CORE-001-04 — 設定読込の優先順位

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AppConfig.load(env: Mapping[str, str] | None = None) -> AppConfig`を通じて「設定読込の優先順位」を実行する
    Then: 「設定読込の優先順位」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    monkeypatch.delenv("WALKWISE_LOG_LEVEL", raising=False)
    config = AppConfig.load(env={"WALKWISE_DATA_ROOT": "/tmp/root"})
    assert config.get("WALKWISE_LOG_LEVEL") == "INFO"


@pytest.mark.unit
def test_tc_core_001_07(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-CORE-001-07 — 再実行時の決定性

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `AppConfig.load(env: Mapping[str, str] | None = None) -> AppConfig`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    monkeypatch.delenv("WALKWISE_LOG_LEVEL", raising=False)
    env = {"WALKWISE_DATA_ROOT": "/tmp/root", "WALKWISE_LOG_LEVEL": "DEBUG"}
    first = AppConfig.load(env=env)
    second = AppConfig.load(env=env)
    assert first == second
