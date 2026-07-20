"""Implementation for TASK-ENV-001: Docker開発・テスト実行環境.

Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
Production files exercised:
- Dockerfile (test stage)
- docker-compose.yml (test service, test-live service)
- .dockerignore (build context policy)

Tests are black-box: they invoke the real `docker`/`docker compose` CLI and
inspect `.dockerignore`/`requirements.txt` as plain text, without importing
production internals.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.mvp

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DOCKER_AVAILABLE = shutil.which("docker") is not None


def _require_docker() -> None:
    if not _DOCKER_AVAILABLE:
        pytest.skip("docker CLI is not available in this environment")


def _compose_config() -> dict:
    _require_docker()
    result = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def built_test_image() -> None:
    """Builds the `test` stage once for reuse across cases in this module."""
    _require_docker()
    result = subprocess.run(
        ["docker", "compose", "build", "test"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.integration_mock
def test_tc_env_001_01(built_test_image: None) -> None:
    """TC-ENV-001-01 — 通常コンテナテスト

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P0
    Layer: integration_mock
    Given: Docker Engineが利用可能
    When: test serviceをbuildして実行する
    Then: 外部APIなしでpytest収集と通常テストが実行できる
    """
    result = subprocess.run(
        ["docker", "compose", "run", "--rm", "test", "python", "-m", "pytest", "--collect-only", "-q"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "collected" in combined
    assert "PytestUnknownMarkWarning" not in combined


@pytest.mark.static
def test_tc_env_001_02() -> None:
    """TC-ENV-001-02 — 秘密ファイル除外

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P0
    Layer: static
    Given: .envやdataが作業treeに存在
    When: Docker build contextを検査する
    Then: 秘密・利用者data・cacheがcontextへ入らない
    """
    ignore_text = (_REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")
    ignore_lines = {
        line.strip()
        for line in ignore_text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    required_patterns = {
        ".env",
        ".env.local",
        ".git",
        "node_modules",
        "__pycache__",
        "dumps",
        "dist",
        "build",
        "release",
    }
    missing = required_patterns - ignore_lines
    assert not missing, f"missing .dockerignore entries: {missing}"

    # Confirm the actual working tree contains at least one real secret-like
    # file, and that it is genuinely covered by an ignore pattern (not just
    # coincidentally absent from the tree).
    assert (_REPO_ROOT / ".env").is_file()
    assert ".env" in ignore_lines


@pytest.mark.integration_mock
def test_tc_env_001_03(built_test_image: None) -> None:
    """TC-ENV-001-03 — DockerfileのPython test stage

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `test stage`を通じて「DockerfileのPython test stage」を実行する
    Then: 「DockerfileのPython test stage」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    dockerfile_text = (_REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "AS test" in dockerfile_text
    assert "FROM python:3.12-slim" in dockerfile_text

    result = subprocess.run(
        ["docker", "compose", "run", "--rm", "test", "python", "--version"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Python 3.12" in (result.stdout + result.stderr)


@pytest.mark.integration_mock
def test_tc_env_001_04() -> None:
    """TC-ENV-001-04 — docker-composeのtest service

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `test stage`を通じて「docker-composeのtest service」を実行する
    Then: 「docker-composeのtest service」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    config = _compose_config()
    services = config["services"]

    assert "test" in services
    test_service = services["test"]
    assert test_service["build"]["target"] == "test"
    assert test_service["environment"]["WALKWISE_RUN_INTEGRATION_SMOKE"] == "0"
    assert test_service["environment"]["WALKWISE_RUN_INTEGRATION_LIVE"] == "0"

    assert "test-live" in services
    live_service = services["test-live"]
    assert live_service["build"]["target"] == "test"
    assert "WALKWISE_RUN_INTEGRATION_SMOKE" in live_service["environment"]
    assert "WALKWISE_RUN_INTEGRATION_LIVE" in live_service["environment"]


@pytest.mark.unit
def test_tc_env_001_05() -> None:
    """TC-ENV-001-05 — 依存インストール

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `test stage`を通じて「依存インストール」を実行する
    Then: 「依存インストール」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    dockerfile_text = (_REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "requirements.txt" in dockerfile_text
    assert "pip install" in dockerfile_text

    requirements_text = (_REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")
    for expected in ("pillow", "pydub", "requests", "pytest"):
        assert expected in requirements_text.lower()


@pytest.mark.unit
def test_tc_env_001_06() -> None:
    """TC-ENV-001-06 — ホストVOICEVOX等を要求しない通常テスト

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `test stage`を通じて「ホストVOICEVOX等を要求しない通常テスト」を実行する
    Then: 「ホストVOICEVOX等を要求しない通常テスト」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    config = _compose_config()
    test_env = config["services"]["test"]["environment"]
    assert test_env.get("WALKWISE_RUN_INTEGRATION_SMOKE") == "0"
    assert test_env.get("WALKWISE_RUN_INTEGRATION_LIVE") == "0"
    for host_only_var in ("VOICEVOX_URL", "TESSERACT_CMD", "FFMPEG_PATH", "GEMINI_API_KEY"):
        assert host_only_var not in test_env


@pytest.mark.unit
def test_tc_env_001_07() -> None:
    """TC-ENV-001-07 — Windowsからのボリューム利用方針

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `test stage`を通じて「Windowsからのボリューム利用方針」を実行する
    Then: 「Windowsからのボリューム利用方針」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    config = _compose_config()
    volumes = config["services"]["test"]["volumes"]
    assert len(volumes) == 1
    volume = volumes[0]
    assert volume["type"] == "bind"
    assert volume["target"] == "/app"
    # Resolved source must be an absolute host path (works for a Windows bind mount).
    assert Path(volume["source"]).is_absolute()


@pytest.mark.unit
def test_tc_env_001_08(tmp_path: Path) -> None:
    """TC-ENV-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `test stage`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    _require_docker()

    dockerfile_before = (_REPO_ROOT / "Dockerfile").read_bytes()
    compose_before = (_REPO_ROOT / "docker-compose.yml").read_bytes()

    repo_context = _REPO_ROOT.as_posix()
    broken_compose = tmp_path / "docker-compose.broken.yml"
    broken_compose.write_text(
        "services:\n"
        "  broken:\n"
        "    build:\n"
        f"      context: {repo_context}\n"
        "      target: this_stage_does_not_exist\n",
        encoding="utf-8",
    )

    images_before = subprocess.run(
        ["docker", "images", "-q", "walkwise-broken"],
        capture_output=True, text=True, timeout=30,
    ).stdout.strip()

    result = subprocess.run(
        ["docker", "compose", "-f", str(broken_compose), "build", "broken"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=120,
    )
    combined = result.stdout + result.stderr

    assert result.returncode != 0
    assert "this_stage_does_not_exist" in combined

    images_after = subprocess.run(
        ["docker", "images", "-q", "walkwise-broken"],
        capture_output=True, text=True, timeout=30,
    ).stdout.strip()
    assert images_before == images_after == ""

    # Existing repository files remain byte-identical (no side effects).
    assert (_REPO_ROOT / "Dockerfile").read_bytes() == dockerfile_before
    assert (_REPO_ROOT / "docker-compose.yml").read_bytes() == compose_before


@pytest.mark.unit
def test_tc_env_001_09() -> None:
    """TC-ENV-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `test stage`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    first = _compose_config()
    second = _compose_config()
    assert first == second
