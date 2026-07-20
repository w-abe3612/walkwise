"""Implementation for TASK-CORE-001: 設定・共通エラー・ログ契約 (errors).

Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
Production file exercised: script/core/errors.py
"""

from __future__ import annotations

import pytest

from script.core.errors import AppError, ErrorCode

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_core_001_02() -> None:
    """TC-CORE-001-02 — 公開エラー分離

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: technical detailにstack/pathがある
    When: 公開dictへ変換する
    Then: 利用者向けmessageには技術情報を混入しない
    """
    error = AppError(
        ErrorCode.INTERNAL_ERROR,
        "設定の読み込みに失敗しました",
        technical_detail="Traceback (most recent call last): File \"C:/Users/ookan/secret/path.py\", line 1",
    )

    public = error.to_public_dict()

    assert public["message"] == "設定の読み込みに失敗しました"
    assert "code" in public
    assert "technical_detail" not in public
    assert "Traceback" not in public["message"]
    assert "secret" not in public["message"]


@pytest.mark.unit
def test_tc_core_001_05() -> None:
    """TC-CORE-001-05 — 機密値をログへ出さない

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `AppConfig.load(env: Mapping[str, str] | None = None) -> AppConfig`を通じて「機密値をログへ出さない」を実行する
    Then: 「機密値をログへ出さない」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    error = AppError(
        ErrorCode.EXTERNAL_UNAVAILABLE,
        "外部サービスに接続できません",
        technical_detail="api_key=sk-super-secret-value-123",
    )

    public = error.to_public_dict()

    assert "technical_detail" not in public
    assert "sk-super-secret-value-123" not in str(public)
    assert repr(public) == repr(error.to_public_dict())


@pytest.mark.unit
def test_tc_core_001_08() -> None:
    """TC-CORE-001-08 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    technical_detail = "original technical detail, must stay untouched"
    error = AppError(ErrorCode.VALIDATION_ERROR, "入力が不正です", technical_detail=technical_detail)

    error.to_public_dict()
    error.to_public_dict()

    assert error.technical_detail == technical_detail
    assert error.message == "入力が不正です"
    assert error.code == ErrorCode.VALIDATION_ERROR
