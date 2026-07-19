"""STEP3 test scaffold configuration.

This file contains only safe collection controls and placeholder connectivity gates.
It never opens a network connection or starts an external runtime.

The real connectivity implementations are created in STEP4/STEP7.  Until then:
- integration_smoke and integration_live are opt-in;
- live fixtures skip explicitly;
- performance and resilience suites are opt-in;
- all generated test bodies remain strict xfail scaffolds.
"""

from __future__ import annotations

import os
from collections.abc import Iterable

import pytest


_LAYER_MARKERS = (
    "unit",
    "integration_mock",
    "integration_smoke",
    "integration_live",
    "e2e",
    "static",
    "contract",
    "performance",
    "resilience",
)
_SCOPE_MARKERS = ("mvp", "post_mvp", "blocked")


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def pytest_configure(config: pytest.Config) -> None:
    for marker in _LAYER_MARKERS:
        config.addinivalue_line("markers", f"{marker}: STEP2 test layer")
    for marker in _SCOPE_MARKERS:
        config.addinivalue_line("markers", f"{marker}: release scope")


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    del config
    opt_in_rules: tuple[tuple[str, str], ...] = (
        ("integration_smoke", "WALKWISE_RUN_INTEGRATION_SMOKE"),
        ("integration_live", "WALKWISE_RUN_INTEGRATION_LIVE"),
        ("performance", "WALKWISE_RUN_PERFORMANCE"),
        ("resilience", "WALKWISE_RUN_RESILIENCE"),
    )
    for item in items:
        for marker_name, env_name in opt_in_rules:
            if item.get_closest_marker(marker_name) and not _enabled(env_name):
                item.add_marker(
                    pytest.mark.skip(
                        reason=(
                            f"{marker_name} is opt-in; set {env_name}=1 after "
                            "the corresponding runtime and STEP4 gate exist"
                        )
                    )
                )


def _unimplemented_connectivity_gate(name: str) -> None:
    pytest.skip(
        f"{name} is a STEP3 placeholder. Implement the smoke check first in "
        "STEP4/STEP7; live tests must depend on its successful result."
    )


@pytest.fixture(scope="session")
def asr_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("asr_connectivity_gate")


@pytest.fixture(scope="session")
def coeiroink_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("coeiroink_connectivity_gate")


@pytest.fixture(scope="session")
def desktop_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("desktop_connectivity_gate")


@pytest.fixture(scope="session")
def ffmpeg_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("ffmpeg_connectivity_gate")


@pytest.fixture(scope="session")
def gemini_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("gemini_connectivity_gate")


@pytest.fixture(scope="session")
def release_runtime_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("release_runtime_connectivity_gate")


@pytest.fixture(scope="session")
def tesseract_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("tesseract_connectivity_gate")


@pytest.fixture(scope="session")
def voicevox_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("voicevox_connectivity_gate")


@pytest.fixture(scope="session")
def worker_connectivity_gate() -> None:
    """Placeholder gate: never performs external I/O in STEP3."""
    _unimplemented_connectivity_gate("worker_connectivity_gate")


# ---------------------------------------------------------------------------
# TASK-DEV-001 public contract implementations.
# ---------------------------------------------------------------------------

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-DEV-001', 'external_tests_enabled() -> bool', '外部接続テストの明示的有効化を判定する。既定はFalse。'),
    ('TASK-DEV-001', 'require_environment(name: str) -> str', '必要な環境変数がない場合、秘密値を表示せず明示的にskipする。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-DEV-001-01', 'priority': 'P0', 'layer': 'static', 'title': 'pytest収集', 'given': 'リポジトリ直下で依存が揃い、外部サービス環境変数は未設定', 'when': '`pytest --collect-only -q`を実行する', 'then': '全テストモジュールをnetwork接続なしで収集し、未知marker warningがない', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-02', 'priority': 'P0', 'layer': 'contract', 'title': '外部テスト既定無効', 'given': '通常pytest実行', 'when': 'integration_smoke/live marker付きテストを収集・実行する', 'then': '明示opt-inがなければ外部接続せずskip理由が表示される', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-03', 'priority': 'P0', 'layer': 'unit', 'title': '秘密値非表示', 'given': 'API key環境変数が設定済み', 'when': 'skip/error/logを生成する', 'then': '秘密値本体が出力へ含まれない', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'script配下のPython package境界', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「script配下のPython package境界」を実行する', 'then': '「script配下のPython package境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '共通fixture配置', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「共通fixture配置」を実行する', 'then': '「共通fixture配置」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '外部サービスを通常テストから除外する既定値', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「外部サービスを通常テストから除外する既定値」を実行する', 'then': '「外部サービスを通常テストから除外する既定値」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-07', 'priority': 'P1', 'layer': 'unit', 'title': '構文・import・collection確認の入口', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`pytest markers`を通じて「構文・import・collection確認の入口」を実行する', 'then': '「構文・import・collection確認の入口」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`pytest markers`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`pytest markers`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_test_environment_contract.py`'},
    {'id': 'TC-DEV-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_test_environment_contract.py`'},
)

def external_tests_enabled() -> bool:
    """外部接続テストの明示的有効化を判定する。既定はFalse。

    Public contract: ``external_tests_enabled() -> bool``.
    """
    return _enabled("WALKWISE_RUN_INTEGRATION_SMOKE") or _enabled("WALKWISE_RUN_INTEGRATION_LIVE")

def require_environment(name: str) -> str:
    """必要な環境変数がない場合、秘密値を表示せず明示的にskipする。

    Public contract: ``require_environment(name: str) -> str``.
    """
    if not name or not name.strip():
        raise ValueError("require_environment: environment variable name must not be empty")
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"required environment variable {name!r} is not set")
    return value
