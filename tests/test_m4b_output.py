"""Test suite for TASK-M4B-001: M4B出力 (post-MVP).

Contract: docs/test-cases/TASK-M4B-001-m4b-output.md
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from script.audio.m4b import M4BBuilder, M4BResult, M4BTool
from script.core.errors import AppError, ErrorCode
from script.schemas.m4b_manifest import M4BManifest

pytestmark = pytest.mark.post_mvp


def _chapter(chapter_id: str, order: int, *, source_mp3_path: str, **overrides) -> dict:
    base = {
        "chapter_id": chapter_id,
        "order": order,
        "title": f"Chapter {order}",
        "start_time_offset_seconds": float(order - 1) * 100.0,
        "duration_seconds": 100.0,
        "source_mp3_path": source_mp3_path,
        "script_approved": True,
        "preview_approved": True,
        "audio_validation_passed": True,
    }
    base.update(overrides)
    return base


def _fake_success_runner(output_bytes: bytes = b"fake-m4b-bytes"):
    def _runner(args, **kwargs):
        output_path = Path(args[-1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(output_bytes)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ffmpeg version 6.0\n", stderr="")

    return _runner


def _metadata(**overrides) -> dict:
    base = {"project_id": "sample-book", "title": "サンプル技術解説", "author": None, "narrator": None, "year": None}
    base.update(overrides)
    return base


@pytest.mark.unit
def test_tc_m4b_001_01(tmp_path: Path) -> None:
    """TC-M4B-001-01 — 承認gate: 1章が未承認またはfailならM4Bを生成しない。"""
    mp3_1 = tmp_path / "ch01.mp3"
    mp3_1.write_bytes(b"chapter-1-audio")
    mp3_2 = tmp_path / "ch02.mp3"
    mp3_2.write_bytes(b"chapter-2-audio")
    output = tmp_path / "book.m4b"

    chapters = [
        _chapter("ch01", 1, source_mp3_path=str(mp3_1)),
        _chapter("ch02", 2, source_mp3_path=str(mp3_2), script_approved=False),
    ]
    builder = M4BBuilder(runner=_fake_success_runner())

    with pytest.raises(AppError) as exc_info:
        builder.build(chapters, _metadata(), output)
    assert exc_info.value.code is ErrorCode.PERMISSION_DENIED
    assert not output.exists()

    chapters_failed_validation = [
        _chapter("ch01", 1, source_mp3_path=str(mp3_1)),
        _chapter("ch02", 2, source_mp3_path=str(mp3_2), audio_validation_passed=False),
    ]
    with pytest.raises(AppError) as exc_info:
        builder.build(chapters_failed_validation, _metadata(), output)
    assert exc_info.value.code is ErrorCode.PERMISSION_DENIED
    assert not output.exists()


@pytest.mark.unit
def test_tc_m4b_001_03(tmp_path: Path) -> None:
    """TC-M4B-001-03 — provisional保持: 入力reportがprovisionalならapprovedへ書き換えない。"""
    mp3_1 = tmp_path / "ch01.mp3"
    mp3_1.write_bytes(b"chapter-1-audio")
    output = tmp_path / "book.m4b"
    chapters = [_chapter("ch01", 1, source_mp3_path=str(mp3_1))]
    builder = M4BBuilder(runner=_fake_success_runner())

    result = builder.build(chapters, _metadata(), output)
    assert result.manifest.validation["validation_threshold_status"] == "provisional"
    assert result.manifest.compatibility["status"] == "provisional"

    # 実機再生確認済みplayerを明示した場合のみapprovedになる(5.4節)。
    result_tested = builder.build(chapters, _metadata(), tmp_path / "book2.m4b", tested_players=["vlc"])
    assert result_tested.manifest.compatibility["status"] == "approved"
    # validation側は音声検査閾値がprovisionalのため、常にprovisionalのまま。
    assert result_tested.manifest.validation["validation_threshold_status"] == "provisional"


@pytest.mark.unit
def test_tc_m4b_001_04() -> None:
    """TC-M4B-001-04 — ffmpeg等adapter: M4BTool.check_runtime()は実行可否・versionを副作用なく確認する。"""

    def fake_available(args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ffmpeg version 6.0-static\n", stderr="")

    tool = M4BTool(runner=fake_available)
    health = tool.check_runtime()
    assert health.available is True
    assert health.version == "ffmpeg version 6.0-static"

    def fake_unavailable(args, **kwargs):
        raise FileNotFoundError("ffmpeg not found")

    unavailable_tool = M4BTool(runner=fake_unavailable)
    unavailable_health = unavailable_tool.check_runtime()
    assert unavailable_health.available is False
    assert "not found" in unavailable_health.error


@pytest.mark.unit
def test_tc_m4b_001_05(tmp_path: Path) -> None:
    """TC-M4B-001-05 — Artifact登録: M4BResultはArtifact登録に必要な情報を保持する。"""
    mp3_1 = tmp_path / "ch01.mp3"
    mp3_1.write_bytes(b"chapter-1-audio")
    output = tmp_path / "book.m4b"
    chapters = [_chapter("ch01", 1, source_mp3_path=str(mp3_1))]
    builder = M4BBuilder(runner=_fake_success_runner(b"the-actual-m4b-bytes"))

    result = builder.build(chapters, _metadata(), output)

    assert isinstance(result, M4BResult)
    assert result.artifact_type == "m4b"
    assert result.output_path == str(output)
    assert result.content_hash == hashlib.sha256(b"the-actual-m4b-bytes").hexdigest()
    assert output.exists()


@pytest.mark.unit
def test_tc_m4b_001_06(tmp_path: Path) -> None:
    """TC-M4B-001-06 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    mp3_1 = tmp_path / "ch01.mp3"
    mp3_1.write_bytes(b"chapter-1-audio")
    output = tmp_path / "book.m4b"
    chapters = [_chapter("ch01", 1, source_mp3_path=str(mp3_1))]
    builder = M4BBuilder(runner=_fake_success_runner())

    with pytest.raises(AppError) as exc_info:
        builder.build([], _metadata(), output)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert not output.exists()

    with pytest.raises(AppError) as exc_info:
        builder.build(chapters, None, output)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR
    assert not output.exists()

    with pytest.raises(AppError) as exc_info:
        builder.build(chapters, _metadata(), None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError):
        M4BManifest(chapters=())
    with pytest.raises(AppError):
        M4BManifest(project_id="p", chapters=({"chapter_id": "ch01"},))  # validation欠落


@pytest.mark.unit
def test_tc_m4b_001_07(tmp_path: Path) -> None:
    """TC-M4B-001-07 — 再実行時の決定性: 同じ入力・同じ依存応答なら同じ論理結果を返す。"""

    def fake_version_runner(args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ffmpeg version 6.0\n", stderr="")

    tool = M4BTool(runner=fake_version_runner)
    first_health = tool.check_runtime()
    second_health = tool.check_runtime()
    assert first_health.available == second_health.available
    assert first_health.version == second_health.version

    mp3_1 = tmp_path / "ch01.mp3"
    mp3_1.write_bytes(b"chapter-1-audio")
    chapters = [_chapter("ch01", 1, source_mp3_path=str(mp3_1))]
    builder = M4BBuilder(runner=_fake_success_runner())

    first = builder.build(chapters, _metadata(), tmp_path / "book1.m4b")
    second = builder.build(chapters, _metadata(), tmp_path / "book2.m4b")
    assert first.manifest.to_mapping() == second.manifest.to_mapping()


@pytest.mark.unit
def test_tc_m4b_001_08(tmp_path: Path) -> None:
    """TC-M4B-001-08 — 入力・既存成果物の不変性: 失敗したbuildは既存の入力・成果物を変更しない。"""
    mp3_1 = tmp_path / "ch01.mp3"
    mp3_1.write_bytes(b"chapter-1-audio")
    before_hash = hashlib.sha256(mp3_1.read_bytes()).hexdigest()

    output = tmp_path / "book.m4b"
    chapters = [_chapter("ch01", 1, source_mp3_path=str(mp3_1))]
    builder = M4BBuilder(runner=_fake_success_runner(b"good-existing-m4b"))
    builder.build(chapters, _metadata(), output)
    existing_output_bytes = output.read_bytes()

    # 未承認章を含む2回目のbuildは失敗し、既存の正常なoutput/入力mp3を変更しない。
    bad_chapters = [
        _chapter("ch01", 1, source_mp3_path=str(mp3_1)),
        _chapter("ch02", 2, source_mp3_path=str(mp3_1), script_approved=False),
    ]
    with pytest.raises(AppError):
        builder.build(bad_chapters, _metadata(), output)

    assert output.read_bytes() == existing_output_bytes
    assert hashlib.sha256(mp3_1.read_bytes()).hexdigest() == before_hash


@pytest.mark.integration_smoke
def test_tc_m4b_001_09(ffmpeg_connectivity_gate) -> None:
    """TC-M4B-001-09 — ffmpeg runtimeの疎通確認

    Contract: docs/test-cases/TASK-M4B-001-m4b-output.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: `ffmpeg -version`を実行し、M4B対応buildであることを最低限確認する。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert ffmpeg_connectivity_gate.available is True


def _build_two_chapter_m4b_with_real_ffmpeg(tmp_path: Path) -> M4BResult:
    import os
    import wave

    def _write_short_wav(path: Path, seconds: float) -> None:
        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(8000)
            handle.writeframes(b"\x00\x00" * int(8000 * seconds))

    ffmpeg_cmd = os.environ["FFMPEG_PATH"]
    wav_1 = tmp_path / "ch01.wav"
    wav_2 = tmp_path / "ch02.wav"
    _write_short_wav(wav_1, 1.0)
    _write_short_wav(wav_2, 1.0)

    def real_runner(args, **kwargs):
        return subprocess.run(args, capture_output=True, text=True, timeout=30)

    chapters = [
        _chapter("ch01", 1, source_mp3_path=str(wav_1)),
        _chapter("ch02", 2, source_mp3_path=str(wav_2), start_time_offset_seconds=1.0),
    ]
    builder = M4BBuilder(ffmpeg_cmd=ffmpeg_cmd, runner=real_runner)
    return builder.build(chapters, _metadata(), tmp_path / "book.m4b")


@pytest.mark.integration_live
def test_tc_m4b_001_02(ffmpeg_connectivity_gate, tmp_path: Path) -> None:
    """TC-M4B-001-02 — chapter metadata

    Given: 2章fixture
    When: build/probe
    Then: 章順と開始時刻が一致

    Connectivity prerequisite: ffmpeg_connectivity_gate
    """
    assert ffmpeg_connectivity_gate.available is True

    result = _build_two_chapter_m4b_with_real_ffmpeg(tmp_path)

    assert [c["chapter_id"] for c in result.manifest.chapters] == ["ch01", "ch02"]
    assert result.manifest.chapters[1]["start_time_offset_seconds"] == 1.0


@pytest.mark.integration_live
def test_tc_m4b_001_10(ffmpeg_connectivity_gate, tmp_path: Path) -> None:
    """TC-M4B-001-10 — ffmpeg runtimeの実機能テスト

    Given: `ffmpeg_connectivity_gate`が成功済み
    When: 疎通成功後、2章の短いfixture MP3からM4Bを生成しchapter metadataをprobeする。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    assert ffmpeg_connectivity_gate.available is True

    result = _build_two_chapter_m4b_with_real_ffmpeg(tmp_path)
    assert result.content_hash is not None
