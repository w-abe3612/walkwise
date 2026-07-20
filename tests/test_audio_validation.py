"""STEP4 test implementation for TASK-AUDIO-002: AudioValidator / AudioMeasurementAdapter / thresholds.

Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
Release scope: MVP
"""

from __future__ import annotations

import struct
import subprocess
import wave
from pathlib import Path

import pytest

from script.audio.measurements import AudioMeasurementAdapter
from script.audio.thresholds import AudioThresholds, ThresholdEvidence
from script.audio.validation import AudioValidator, ValidationStatus
from script.core.errors import AppError

pytestmark = pytest.mark.mvp


def _write_wav(path: Path, *, framerate: int = 24000, nchannels: int = 1, sampwidth: int = 2, nframes: int = 24000, amplitude: int = 5000) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(nchannels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(framerate)
        frame_data = struct.pack(f"<{nframes}h", *([amplitude] * nframes))
        wav_file.writeframes(frame_data)


@pytest.mark.unit
def test_tc_audio_002_01(tmp_path: Path) -> None:
    """TC-AUDIO-002-01 — 破損/0秒: 破損WAVと0秒WAVは常にfail。"""
    thresholds = AudioThresholds().load()
    validator = AudioValidator()

    corrupted_path = tmp_path / "corrupted.wav"
    corrupted_path.write_bytes(b"not a real wav file")
    corrupted_report = validator.validate(corrupted_path, "some text", thresholds)
    assert corrupted_report.status is ValidationStatus.FAIL

    zero_second_path = tmp_path / "zero_second.wav"
    _write_wav(zero_second_path, nframes=0)
    zero_second_report = validator.validate(zero_second_path, "some text", thresholds)
    assert zero_second_report.status is ValidationStatus.FAIL


@pytest.mark.unit
def test_tc_audio_002_03() -> None:
    """TC-AUDIO-002-03 — approved禁止: measured=falseまたは話者2未満は拒否する。"""
    audio_thresholds = AudioThresholds()

    unmeasured = audio_thresholds.load(evidence=ThresholdEvidence(measured=False, sample_count=0))
    with pytest.raises(AppError):
        audio_thresholds.validate_approval(unmeasured)

    too_few_speakers = audio_thresholds.load(
        evidence=ThresholdEvidence(measured=True, sample_count=1, measured_speakers=("kasukabe-tsumugi",))
    )
    with pytest.raises(AppError):
        audio_thresholds.validate_approval(too_few_speakers)

    enough_evidence = audio_thresholds.load(
        evidence=ThresholdEvidence(
            measured=True, sample_count=2, measured_speakers=("kasukabe-tsumugi", "ouka-miko")
        )
    )
    approved = audio_thresholds.validate_approval(enough_evidence)
    assert approved.status == "approved"


@pytest.mark.unit
def test_tc_audio_002_05() -> None:
    """TC-AUDIO-002-05 — 外部ffmpeg adapter境界: runnerを差し替えて疎通確認をDIできる。"""

    def fake_runner_ok(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(command, 0, stdout=f"{command[0]} version 6.0", stderr="")

    healthy_adapter = AudioMeasurementAdapter(runner=fake_runner_ok)
    result = healthy_adapter.check_runtime()
    assert result.available is True
    assert "6.0" in (result.ffmpeg_version or "")

    def fake_runner_missing(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
        raise FileNotFoundError(f"{command[0]}: command not found")

    missing_adapter = AudioMeasurementAdapter(runner=fake_runner_missing)
    missing_result = missing_adapter.check_runtime()
    assert missing_result.available is False


@pytest.mark.unit
def test_tc_audio_002_07() -> None:
    """TC-AUDIO-002-07 — 再実行時の決定性: 同じ入力なら同じ論理結果を返す。"""
    audio_thresholds = AudioThresholds()

    result_1 = audio_thresholds.load()
    result_2 = audio_thresholds.load()

    assert result_1 == result_2


@pytest.mark.integration_smoke
def test_tc_audio_002_09(ffmpeg_connectivity_gate) -> None:
    """TC-AUDIO-002-09 — ffmpeg/ffprobe runtimeの疎通確認

    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: `ffmpeg -version`と`ffprobe -version`を実行し、実行可能・version取得可能であることだけを確認する。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert ffmpeg_connectivity_gate.available is True
    assert ffmpeg_connectivity_gate.ffmpeg_version
    assert ffmpeg_connectivity_gate.ffprobe_version
