"""STEP4 test implementation for TASK-AUDIO-002: AudioThresholds / warning-review aggregation.

Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
Release scope: MVP
"""

from __future__ import annotations

import struct
import wave
from pathlib import Path

import pytest

from script.audio.measurements import AudioMeasurement, AudioMeasurementAdapter
from script.audio.thresholds import AudioThresholds
from script.audio.validation import AudioValidator, ValidationStatus
from script.core.errors import AppError

pytestmark = pytest.mark.mvp


def _write_wav(path: Path, *, framerate: int = 24000, nframes: int = 24000, amplitude: int = 5000) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        frame_data = struct.pack(f"<{nframes}h", *([amplitude] * nframes))
        wav_file.writeframes(frame_data)


@pytest.mark.unit
def test_tc_audio_002_02(tmp_path: Path) -> None:
    """TC-AUDIO-002-02 — provisional記録: 暫定thresholdの正常WAVはreportにthreshold_status=provisional。"""
    thresholds = AudioThresholds().load()
    assert thresholds.status == "provisional"

    wav_path = tmp_path / "normal.wav"
    _write_wav(wav_path, nframes=24000 * 4, amplitude=5000)  # 4秒、6文字/秒程度

    report = AudioValidator().validate(wav_path, "これはテスト用の原稿文です。", thresholds)

    assert report.threshold_status == "provisional"
    assert report.status is ValidationStatus.PASS


class _FixedMeasurementAdapter:
    """severity集約規則を検証するため、任意の測定値を返す固定adapter。"""

    def __init__(self, measurement: AudioMeasurement) -> None:
        self._measurement = measurement

    def measure(self, path: object) -> AudioMeasurement:
        return self._measurement


@pytest.mark.unit
def test_tc_audio_002_04() -> None:
    """TC-AUDIO-002-04 — warning/review累積規則は保守的: より重い判定が軽い判定を覆い隠さない。"""
    thresholds = AudioThresholds().load()

    # warningの原因(長い無音)とreview_requiredの原因(clipping)が両方ある場合、review_requiredが勝つ。
    mixed_measurement = AudioMeasurement(
        duration_seconds=4.0, sample_rate_hz=24000, channels=1, peak_dbfs=0.0, silence_ratio=0.6
    )
    mixed_report = AudioValidator(measurement_adapter=_FixedMeasurementAdapter(mixed_measurement)).validate(
        "dummy.wav", "text", thresholds
    )
    assert mixed_report.status is ValidationStatus.REVIEW_REQUIRED

    # fail原因(duration不足)とwarning原因が両方あっても、failが最終判定になる。
    fail_and_warning_measurement = AudioMeasurement(
        duration_seconds=0.1, sample_rate_hz=24000, channels=1, peak_dbfs=-10.0, silence_ratio=0.6
    )
    thresholds_strict_peak = AudioThresholds().load()
    fail_report = AudioValidator(measurement_adapter=_FixedMeasurementAdapter(fail_and_warning_measurement)).validate(
        "dummy.wav", "text", thresholds_strict_peak
    )
    assert fail_report.status is ValidationStatus.FAIL


@pytest.mark.unit
def test_tc_audio_002_06(tmp_path: Path) -> None:
    """TC-AUDIO-002-06 — 必須入力欠落: 副作用前に安定したvalidation errorを返す。"""
    thresholds = AudioThresholds().load()
    validator = AudioValidator()

    with pytest.raises(AppError):
        validator.validate(None, "text", thresholds)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        validator.validate(tmp_path / "x.wav", None, thresholds)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        validator.validate(tmp_path / "x.wav", "text", None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        AudioThresholds().validate_approval(None)  # type: ignore[arg-type]

    with pytest.raises(AppError):
        AudioMeasurementAdapter().measure(None)  # type: ignore[arg-type]


@pytest.mark.unit
def test_tc_audio_002_08(tmp_path: Path) -> None:
    """TC-AUDIO-002-08 — 入力・既存成果物の不変性: 失敗を試みても既存正常成果物は変化しない。"""
    thresholds = AudioThresholds().load()
    validator = AudioValidator()
    wav_path = tmp_path / "normal.wav"
    _write_wav(wav_path, nframes=24000 * 3)

    good_report = validator.validate(wav_path, "短い原稿です。", thresholds)
    before = (good_report.status, good_report.threshold_status, good_report.duration_seconds)

    corrupted_path = tmp_path / "corrupted.wav"
    corrupted_path.write_bytes(b"garbage")
    validator.validate(corrupted_path, "text", thresholds)  # 失敗ではなくfail reportを返すのみ(例外なし)

    after = (good_report.status, good_report.threshold_status, good_report.duration_seconds)
    assert before == after
    assert wav_path.read_bytes()  # 既存の正常WAVは変更されていない


@pytest.mark.integration_live
def test_tc_audio_002_10(ffmpeg_connectivity_gate, tmp_path: Path) -> None:
    """TC-AUDIO-002-10 — ffmpeg/ffprobe runtimeの実機能テスト

    Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
    Priority: P1
    Layer: integration_live
    Given: `ffmpeg_connectivity_gate`が成功済み
    When: 疎通成功後、短い固定WAVを測定しduration/peak等の必須値が取得できることを確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    assert ffmpeg_connectivity_gate.available is True

    wav_path = tmp_path / "live-smoke.wav"
    _write_wav(wav_path, nframes=24000, amplitude=4000)

    adapter = AudioMeasurementAdapter()
    measurement = adapter.measure(wav_path)

    assert measurement.duration_seconds > 0
    assert measurement.sample_rate_hz == 24000
    assert measurement.peak_dbfs is not None
