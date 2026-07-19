"""STEP3 test scaffold for TASK-IMAGE-001: 画像群登録・順序・manifest.

Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
Release scope: MVP
Planned production files:
- script/source_processing/images/ingestion.py
- script/source_processing/images/manifest.py

This file is the test-generation source of truth for the cases below.
STEP3 intentionally imports no production module because STEP4 source
scaffolds do not exist yet. Claude Code must replace each explicit
failure with assertions without changing case IDs or contract meaning."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.mvp

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-02 is not implemented")
def test_tc_image_001_02() -> None:
    """TC-IMAGE-001-02 — 明示順
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: explicit orderを指定
    When: ingestする
    Then: 指定順を採用し重複/欠落を拒否する
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-02")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-04 is not implemented")
def test_tc_image_001_04() -> None:
    """TC-IMAGE-001-04 — 形式検証
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「形式検証」を実行する
    Then: 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-04")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-06 is not implemented")
def test_tc_image_001_06() -> None:
    """TC-IMAGE-001-06 — 原画像immutable copy
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を通じて「原画像immutable copy」を実行する
    Then: 処理前後で入力ファイルのbyte列とSHA-256が一致し、派生物だけが新規作成される。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-06")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-08 is not implemented")
def test_tc_image_001_08() -> None:
    """TC-IMAGE-001-08 — 必須入力欠落
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `ImageIngestionService.ingest(paths, *, explicit_order=None) -> ImageIngestionResult`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-08")

@pytest.mark.unit
@pytest.mark.xfail(strict=True, reason="STEP3 scaffold: TC-IMAGE-001-10 is not implemented")
def test_tc_image_001_10() -> None:
    """TC-IMAGE-001-10 — 入力・既存成果物の不変性
    
    Contract: docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    
    Implementation handoff:
    - Import only the approved symbols listed in the contract.
    - Replace pytest.fail with concrete arrange/act/assert logic.
    - Preserve this case ID, layer, Given/When/Then, and strict xfail
    until the intended Red state has been demonstrated."""
    pytest.fail("STEP3 scaffold not implemented: TC-IMAGE-001-10")
