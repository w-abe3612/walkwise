"""Implementation for TASK-CORE-002: 共通ID・canonical hash・YAML/JSON入出力 (serialization).

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Production file exercised: script/core/serialization.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.core.errors import AppError
from script.core.serialization import dump_yaml, load_json, load_yaml

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_core_002_03(tmp_path: Path) -> None:
    """TC-CORE-002-03 — 未知schema version

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: 未知majorと未知minorを読む
    When: structured fileをloadする
    Then: 未知majorはerror、読める未知minorはwarning
    """
    unknown_minor_path = tmp_path / "unknown-minor.yaml"
    dump_yaml(unknown_minor_path, {"schema_version": "1.7", "project_id": "database-foundations"})

    with pytest.warns(UserWarning):
        data = load_yaml(unknown_minor_path)
    assert data["project_id"] == "database-foundations"

    unknown_major_path = tmp_path / "unknown-major.yaml"
    dump_yaml(unknown_major_path, {"schema_version": "2.0", "project_id": "database-foundations"})

    with pytest.raises(AppError):
        load_yaml(unknown_major_path)


@pytest.mark.unit
def test_tc_core_002_06(tmp_path: Path) -> None:
    """TC-CORE-002-06 — 必須入力欠落

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `validate_identifier(value: str) -> str`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    missing_path = tmp_path / "does-not-exist.json"
    existing_before = sorted(tmp_path.iterdir())

    with pytest.raises(AppError):
        load_json(missing_path)

    assert sorted(tmp_path.iterdir()) == existing_before
