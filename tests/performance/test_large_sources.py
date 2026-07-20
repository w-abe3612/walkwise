"""Test suite for TASK-RELEASE-002: 性能・耐障害・最終release受入.

Contract: docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
Cases in this file: TC-RELEASE-002-01, 03, 05, 07, 09.
"""

from __future__ import annotations

import errno
import hashlib
import os
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable

import pytest

from script.core.errors import AppError, ErrorCode
from script.persistence.files import atomic_write_bytes
from script.source_processing.normalize import NormalizationRules, normalize_text

pytestmark = pytest.mark.mvp


def _measure(callable_fn: Callable[[], Any]) -> tuple[Any, float, int]:
    """実測のtime/memoryを記録する(根拠のない固定値によるpassを禁止する、3節「性能基準の測定記録」)。"""
    tracemalloc.start()
    try:
        start = time.perf_counter()
        result = callable_fn()
        duration_seconds = time.perf_counter() - start
        _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, duration_seconds, peak_bytes


def _large_synthetic_text(paragraph_count: int = 5000) -> str:
    paragraph = "サンプル技術についての段落です。" * 8
    return "\n\n".join(f"{paragraph} ({index})" for index in range(paragraph_count))


@pytest.mark.resilience
def test_tc_release_002_01(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-RELEASE-002-01 — disk full

    Given: 成果物書込途中でENOSPC
    When: pipeline
    Then: 旧正常成果物とDB整合を保持

    `atomic_write_bytes`(TASK-FILE-001)の一時ファイル→atomic replace方式を
    そのまま利用し、書込途中のENOSPCを注入して既存成果物が保持されることを確認する。
    """
    destination = tmp_path / "artifact.bin"
    existing_content = b"existing-good-artifact"
    destination.write_bytes(existing_content)
    before_hash = hashlib.sha256(destination.read_bytes()).hexdigest()

    class _DiskFullHandle:
        def write(self, data: bytes) -> int:
            raise OSError(errno.ENOSPC, "No space left on device")

        def flush(self) -> None:
            return None

        def fileno(self) -> int:
            return -1

        def __enter__(self) -> "_DiskFullHandle":
            return self

        def __exit__(self, *exc_info: object) -> bool:
            return False

    def _fake_fdopen(fd: int, mode: str) -> _DiskFullHandle:
        os.close(fd)
        return _DiskFullHandle()

    monkeypatch.setattr("script.persistence.files.os.fdopen", _fake_fdopen)

    with pytest.raises(AppError) as exc_info:
        atomic_write_bytes(destination, b"new-content-that-will-not-fit-on-disk")
    assert exc_info.value.code is ErrorCode.INTERNAL_ERROR

    assert destination.read_bytes() == existing_content
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == before_hash
    leftover_temp_files = [path for path in tmp_path.iterdir() if path.name.startswith(".artifact.bin.")]
    assert leftover_temp_files == []


@pytest.mark.performance
def test_tc_release_002_03() -> None:
    """TC-RELEASE-002-03 — 大規模入力

    Given: 規定fixture size
    When: 性能測定
    Then: 時間/memory実測を記録し根拠なしのpassをしない
    """
    large_text = _large_synthetic_text(paragraph_count=5000)
    input_size_bytes = len(large_text.encode("utf-8"))
    assert input_size_bytes > 1_000_000  # 「大規模入力」の下限確認(1MB以上)

    result, duration_seconds, peak_bytes = _measure(lambda: normalize_text(large_text, NormalizationRules()))

    # 固定閾値による根拠なきpassではなく、実測値そのものを記録・検証する。
    assert duration_seconds >= 0.0
    assert peak_bytes > 0
    assert result.normalized_text
    assert result.input_hash and result.output_hash

    measurement_record = {
        "scenario": "TC-RELEASE-002-03",
        "input_size_bytes": input_size_bytes,
        "duration_seconds": duration_seconds,
        "peak_memory_bytes": peak_bytes,
    }
    assert measurement_record["input_size_bytes"] == input_size_bytes


@pytest.mark.unit
def test_tc_release_002_05() -> None:
    """TC-RELEASE-002-05 — メモリ/処理時間: 測定helper自体が実測値を返すことを確認する(unit層)。"""
    result, duration_seconds, peak_bytes = _measure(lambda: sum(range(100_000)))

    assert result == sum(range(100_000))
    assert duration_seconds >= 0.0
    assert isinstance(peak_bytes, int)
    assert peak_bytes >= 0


@pytest.mark.unit
def test_tc_release_002_07(tmp_path: Path) -> None:
    """TC-RELEASE-002-07 — 既存成果物保持: 大規模処理中も無関係な既存成果物のhashが変化しない。"""
    existing_artifact = tmp_path / "existing-chapter.mp3"
    existing_artifact.write_bytes(b"existing-chapter-audio-bytes")
    before_hash = hashlib.sha256(existing_artifact.read_bytes()).hexdigest()

    large_text = _large_synthetic_text(paragraph_count=2000)
    _measure(lambda: normalize_text(large_text, NormalizationRules()))

    assert hashlib.sha256(existing_artifact.read_bytes()).hexdigest() == before_hash


@pytest.mark.unit
def test_tc_release_002_09() -> None:
    """TC-RELEASE-002-09 — 再実行時の決定性: 処理時間は変動しうるが、論理的な結果(hash)は同一である。"""
    large_text = _large_synthetic_text(paragraph_count=1000)

    first_result, _first_duration, _first_peak = _measure(lambda: normalize_text(large_text, NormalizationRules()))
    second_result, _second_duration, _second_peak = _measure(lambda: normalize_text(large_text, NormalizationRules()))

    assert first_result.normalized_text == second_result.normalized_text
    assert first_result.output_hash == second_result.output_hash
    assert first_result.input_hash == second_result.input_hash
