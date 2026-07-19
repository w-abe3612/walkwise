"""Implementation for TASK-DEV-001: Pythonパッケージ・pytest収集基盤.

Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
Production files exercised:
- pyproject.toml (pytest markers)
- tests/conftest.py (external_tests_enabled, require_environment)
- script/__init__.py (package boundary)

Each test below verifies an observable, black-box contract (subprocess pytest
invocations or direct calls to the two approved public functions) rather than
production internals, per the task's "do not over-couple to internals" rule.
"""

from __future__ import annotations

import hashlib
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import external_tests_enabled, require_environment

pytestmark = pytest.mark.mvp

_REPO_ROOT = Path(__file__).resolve().parent.parent

_EXTERNAL_ENV_VARS = (
    "WALKWISE_RUN_INTEGRATION_SMOKE",
    "WALKWISE_RUN_INTEGRATION_LIVE",
    "WALKWISE_RUN_PERFORMANCE",
    "WALKWISE_RUN_RESILIENCE",
    "GEMINI_API_KEY",
    "VOICEVOX_URL",
    "TESSERACT_CMD",
    "FFMPEG_PATH",
    "FFPROBE_PATH",
    "WALKWISE_ASR_ENABLED",
)


def _clean_subprocess_env() -> dict[str, str]:
    """Environment with all external-service opt-in/secret variables removed."""
    return {k: v for k, v in os.environ.items() if k not in _EXTERNAL_ENV_VARS}


@pytest.mark.static
def test_tc_dev_001_01() -> None:
    """TC-DEV-001-01 — pytest収集

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P0
    Layer: static
    Given: リポジトリ直下で依存が揃い、外部サービス環境変数は未設定
    When: `pytest --collect-only -q`を実行する
    Then: 全テストモジュールをnetwork接続なしで収集し、未知marker warningがない
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=str(_REPO_ROOT),
        env=_clean_subprocess_env(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "PytestUnknownMarkWarning" not in combined
    assert "collected" in combined


@pytest.mark.contract
def test_tc_dev_001_02() -> None:
    """TC-DEV-001-02 — 外部テスト既定無効

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P0
    Layer: contract
    Given: 通常pytest実行
    When: integration_smoke/live marker付きテストを収集・実行する
    Then: 明示opt-inがなければ外部接続せずskip理由が表示される
    """
    target = _REPO_ROOT / "tests" / "test_ocr_client.py"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-ra", "-m", "integration_smoke", str(target)],
        cwd=str(_REPO_ROOT),
        env=_clean_subprocess_env(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "skipped" in combined.lower()
    assert "opt-in" in combined
    assert "WALKWISE_RUN_INTEGRATION_SMOKE" in combined


@pytest.mark.unit
def test_tc_dev_001_03(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-DEV-001-03 — 秘密値非表示

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P0
    Layer: unit
    Given: API key環境変数が設定済み
    When: skip/error/logを生成する
    Then: 秘密値本体が出力へ含まれない
    """
    secret_value = "sk-test-super-secret-abc123"
    monkeypatch.setenv("GEMINI_API_KEY", secret_value)
    monkeypatch.delenv("WALKWISE_DEV_001_03_MISSING", raising=False)

    with pytest.raises(pytest.skip.Exception) as exc_info:
        require_environment("WALKWISE_DEV_001_03_MISSING")

    message = str(exc_info.value)
    assert secret_value not in message
    assert "WALKWISE_DEV_001_03_MISSING" in message


@pytest.mark.unit
def test_tc_dev_001_04(capsys: pytest.CaptureFixture[str]) -> None:
    """TC-DEV-001-04 — script配下のPython package境界

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `pytest markers`を通じて「script配下のPython package境界」を実行する
    Then: 「script配下のPython package境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    sys.modules.pop("script", None)
    capsys.readouterr()

    module = importlib.import_module("script")
    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""
    assert hasattr(module, "__path__")

    module_again = importlib.import_module("script")
    assert module_again is module


@pytest.mark.unit
def test_tc_dev_001_05() -> None:
    """TC-DEV-001-05 — 共通fixture配置

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `pytest markers`を通じて「共通fixture配置」を実行する
    Then: 「共通fixture配置」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """

    def _collect_markers() -> str:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--markers"],
            cwd=str(_REPO_ROOT),
            env=_clean_subprocess_env(),
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        return result.stdout

    first = _collect_markers()
    second = _collect_markers()
    assert first == second

    for expected in (
        "unit:",
        "integration_mock:",
        "integration_smoke:",
        "integration_live:",
        "e2e:",
        "performance:",
        "resilience:",
    ):
        assert expected in first


@pytest.mark.unit
def test_tc_dev_001_06(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-DEV-001-06 — 外部サービスを通常テストから除外する既定値

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `pytest markers`を通じて「外部サービスを通常テストから除外する既定値」を実行する
    Then: 「外部サービスを通常テストから除外する既定値」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    monkeypatch.delenv("WALKWISE_RUN_INTEGRATION_SMOKE", raising=False)
    monkeypatch.delenv("WALKWISE_RUN_INTEGRATION_LIVE", raising=False)

    assert external_tests_enabled() is False
    assert external_tests_enabled() is False

    monkeypatch.setenv("WALKWISE_RUN_INTEGRATION_SMOKE", "1")
    assert external_tests_enabled() is True


@pytest.mark.unit
def test_tc_dev_001_07() -> None:
    """TC-DEV-001-07 — 構文・import・collection確認の入口

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `pytest markers`を通じて「構文・import・collection確認の入口」を実行する
    Then: 「構文・import・collection確認の入口」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    first = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "script", "tests"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    second = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "script", "tests"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert first.stdout == "" and first.stderr == ""


@pytest.mark.unit
def test_tc_dev_001_08(tmp_path: Path) -> None:
    """TC-DEV-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `pytest markers`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    marker_file = tmp_path / "existing-artifact.txt"
    marker_file.write_text("pre-existing", encoding="utf-8")
    before = marker_file.read_bytes()

    with pytest.raises(ValueError):
        require_environment("")

    with pytest.raises(pytest.skip.Exception):
        require_environment("WALKWISE_DEV_001_08_UNSET")

    assert marker_file.read_bytes() == before
    assert list(tmp_path.iterdir()) == [marker_file]


@pytest.mark.unit
def test_tc_dev_001_09(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-DEV-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `pytest markers`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    monkeypatch.setenv("WALKWISE_DEV_001_09_VAR", "same-value")
    first = require_environment("WALKWISE_DEV_001_09_VAR")
    second = require_environment("WALKWISE_DEV_001_09_VAR")
    assert first == second == "same-value"

    monkeypatch.delenv("WALKWISE_DEV_001_09_MISSING", raising=False)
    with pytest.raises(pytest.skip.Exception) as first_skip:
        require_environment("WALKWISE_DEV_001_09_MISSING")
    with pytest.raises(pytest.skip.Exception) as second_skip:
        require_environment("WALKWISE_DEV_001_09_MISSING")
    assert str(first_skip.value) == str(second_skip.value)


@pytest.mark.unit
def test_tc_dev_001_10(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-DEV-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"stable-content-0123456789")
    digest_before = hashlib.sha256(artifact.read_bytes()).hexdigest()

    monkeypatch.setenv("WALKWISE_DEV_001_10_VAR", "value")
    require_environment("WALKWISE_DEV_001_10_VAR")

    monkeypatch.delenv("WALKWISE_DEV_001_10_MISSING", raising=False)
    with pytest.raises(pytest.skip.Exception):
        require_environment("WALKWISE_DEV_001_10_MISSING")

    digest_after = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert digest_before == digest_after
