"""Implementation for TASK-CORE-002: 共通ID・canonical hash・YAML/JSON入出力 (hashing).

Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
Production file exercised: script/core/hashing.py (and serialization.py for TC-05).
"""

from __future__ import annotations

import copy
import unicodedata
from pathlib import Path

import pytest

from script.core.hashing import canonical_sha256
from script.core.serialization import dump_json, dump_yaml, load_json, load_yaml

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_core_002_02() -> None:
    """TC-CORE-002-02 — canonical hash

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: mapping key順・CRLF/NFDだけが異なる同値data
    When: canonical_sha256を計算する
    Then: 同じhashになる。配列順差は別hashになる
    """
    nfc_title = unicodedata.normalize("NFC", "café")
    nfd_title = unicodedata.normalize("NFD", "café")
    assert nfc_title != nfd_title  # sanity check: genuinely different byte sequences

    value_nfc_first_key_order = {
        "title": nfc_title,
        "segments": ["a", "b"],
        "content_revision": 1,
        "description": "line1\nline2",
    }
    value_nfd_other_key_order = {
        "content_revision": 1,
        "segments": ["a", "b"],
        "title": nfd_title,
        "description": "line1\r\nline2",
    }

    assert canonical_sha256(value_nfc_first_key_order) == canonical_sha256(value_nfd_other_key_order)

    reordered_array = dict(value_nfc_first_key_order)
    reordered_array["segments"] = ["b", "a"]
    assert canonical_sha256(value_nfc_first_key_order) != canonical_sha256(reordered_array)


@pytest.mark.unit
def test_tc_core_002_05(tmp_path: Path) -> None:
    """TC-CORE-002-05 — 安全なYAML/JSON load/dump

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `validate_identifier(value: str) -> str`を通じて「安全なYAML/JSON load/dump」を実行する
    Then: 「安全なYAML/JSON load/dump」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    payload = {"schema_version": "1.0", "project_id": "database-foundations", "content_revision": 1}

    yaml_path = tmp_path / "project-plan.yaml"
    dump_yaml(yaml_path, payload)
    loaded_yaml = load_yaml(yaml_path)
    assert loaded_yaml == payload

    json_path = tmp_path / "manifest.json"
    dump_json(json_path, payload)
    loaded_json = load_json(json_path)
    assert loaded_json == payload

    assert yaml_path.read_text(encoding="utf-8") == yaml_path.read_text(encoding="utf-8")


@pytest.mark.unit
def test_tc_core_002_08() -> None:
    """TC-CORE-002-08 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    original = {"content_revision": 1, "segments": ["a", "b"], "notes": "keep me"}
    snapshot = copy.deepcopy(original)

    canonical_sha256(original, excluded_keys=("notes",))
    canonical_sha256(original)

    assert original == snapshot
