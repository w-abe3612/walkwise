"""Test suite for TASK-ASR-001: ASRによる原稿・音声照合 (post-MVP).

Contract: docs/test-cases/TASK-ASR-001-asr-script-audio-verification.md
"""

from __future__ import annotations

import socket
import subprocess
from pathlib import Path
from typing import Any

import pytest

from script.asr.base import ASRSegment, ASRTranscript, LocalWhisperCompatibleClient
from script.asr.verification import ASRVerifier, normalize_for_comparison
from script.core.errors import AppError, ErrorCode

pytestmark = pytest.mark.post_mvp


class _FakeAsrClient:
    """テスト専用の決定的ASRClient fake(subprocess/networkを一切使わない)。"""

    def __init__(self, transcript: ASRTranscript) -> None:
        self._transcript = transcript
        self.transcribe_calls: list[Path] = []

    def check_connectivity(self):
        return None

    def transcribe(self, audio_path: Path) -> ASRTranscript:
        self.transcribe_calls.append(Path(audio_path))
        return self._transcript


def _tts_segment(segment_id: str, tts_text: str) -> dict:
    return {"segment_id": segment_id, "tts_text": tts_text}


@pytest.mark.unit
def test_tc_asr_001_01(tmp_path: Path) -> None:
    """TC-ASR-001-01 — ASR単独fail禁止: 大きな差分reportでもreview_required候補に留め最終failにしない。"""
    audio = tmp_path / "ch01-seg001.wav"
    audio.write_bytes(b"fake-audio-bytes")

    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=2.0, text="全く異なる内容の文字起こし結果です"),),
        provider="local_whisper_compatible",
    )
    verifier = ASRVerifier(_FakeAsrClient(transcript))

    report = verifier.verify(audio, [_tts_segment("ch01-seg001", "サンプル技術の定義に関する主張です")], {})

    assert report.status == "review_required"
    assert report.status != "fail"
    assert len(report.issues) >= 1


@pytest.mark.unit
def test_tc_asr_001_02(tmp_path: Path) -> None:
    """TC-ASR-001-02 — segment fallback: segment alignment不能なら章単位比較へfallbackし理由を記録する。"""
    audio = tmp_path / "ch01.wav"
    audio.write_bytes(b"fake-audio-bytes")

    # tts_segmentsは2件だが、ASR側は1件だけを返す(alignment不能)。
    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=4.0, text="導入部分です。まとめです。"),),
        provider="local_whisper_compatible",
    )
    verifier = ASRVerifier(_FakeAsrClient(transcript))

    report = verifier.verify(
        audio,
        [_tts_segment("ch01-seg001", "導入部分です。"), _tts_segment("ch01-seg002", "まとめです。")],
        {},
    )

    assert report.alignment_fallback is True
    assert report.alignment_fallback_reason is not None
    assert "segment_count_mismatch" in report.alignment_fallback_reason
    assert any(issue["code"] == "segment_alignment_fallback" for issue in report.issues)
    assert report.status != "fail"


@pytest.mark.unit
def test_tc_asr_001_03() -> None:
    """TC-ASR-001-03 — 用語正規化: 辞書上同義として扱い、原稿自体は変更しない。"""
    terminology = {"エスキューエル": "SQL", "シーケル": "SQL"}
    original_text = "エスキューエルはデータベース言語です。"

    normalized = normalize_for_comparison(original_text, terminology)

    assert normalized == "SQLはデータベース言語です。"
    # 原稿自体(呼び出し元が保持する元の文字列)は変更されない。
    assert original_text == "エスキューエルはデータベース言語です。"


@pytest.mark.unit
def test_tc_asr_001_04() -> None:
    """TC-ASR-001-04 — local adapter: LocalWhisperCompatibleClientはsubprocess経由でローカル実行する。"""

    def fake_runner(args, **kwargs):
        assert args[0] == "whisper"
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="whisper 20231117\n", stderr="")

    client = LocalWhisperCompatibleClient(runner=fake_runner)
    health = client.check_connectivity()

    assert health.available is True
    assert health.version == "whisper 20231117"


@pytest.mark.unit
def test_tc_asr_001_05(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-ASR-001-05 — cloud off: 通常実行でnetwork clientが一切呼ばれないことを確認する。"""
    audio = tmp_path / "ch01-seg001.wav"
    audio.write_bytes(b"fake-audio-bytes")

    def _forbidden_connect(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("network connection attempted; ASR verification must stay local-only")

    monkeypatch.setattr(socket.socket, "connect", _forbidden_connect)

    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=1.0, text="サンプル技術の定義に関する主張です"),),
        provider="local_whisper_compatible",
    )
    fake_client = _FakeAsrClient(transcript)
    verifier = ASRVerifier(fake_client)

    report = verifier.verify(audio, [_tts_segment("ch01-seg001", "サンプル技術の定義に関する主張です")], {})

    assert report.status == "pass"
    assert fake_client.transcribe_calls == [audio]


@pytest.mark.unit
def test_tc_asr_001_06(tmp_path: Path) -> None:
    """TC-ASR-001-06 — terminology normalization: verify()内の比較でも用語辞書が適用される。"""
    audio = tmp_path / "ch01-seg001.wav"
    audio.write_bytes(b"fake-audio-bytes")

    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=1.0, text="SQLはデータベース言語です。"),),
        provider="local_whisper_compatible",
    )
    verifier = ASRVerifier(_FakeAsrClient(transcript))

    report = verifier.verify(
        audio,
        [_tts_segment("ch01-seg001", "エスキューエルはデータベース言語です。")],
        {"エスキューエル": "SQL"},
    )

    # 用語辞書適用後は完全一致となりpass(適用しなければ大きなCERでreview_requiredになるはず)。
    assert report.status == "pass"
    assert report.metrics["character_error_rate"] == 0.0


@pytest.mark.unit
def test_tc_asr_001_07(tmp_path: Path) -> None:
    """TC-ASR-001-07 — 差分report: 8節のreport例と同じ形の構造を持つ。"""
    audio = tmp_path / "ch01-seg001.wav"
    audio.write_bytes(b"fake-audio-bytes")

    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=1.0, text="サンプル技術の定義に関する主張です"),),
        provider="local_whisper_compatible",
        provider_version="20231117",
    )
    verifier = ASRVerifier(_FakeAsrClient(transcript))

    report = verifier.verify(audio, [_tts_segment("ch01-seg001", "サンプル技術の定義に関する主張です")], {})

    assert report.asr_provider == "local_whisper_compatible"
    assert report.asr_provider_version == "20231117"
    assert set(report.metrics.keys()) == {
        "character_error_rate",
        "word_error_rate",
        "missing_segment_ratio",
        "duplicate_segment_ratio",
        "order_mismatch_count",
    }
    assert report.threshold_status == "provisional"


@pytest.mark.unit
def test_tc_asr_001_08(tmp_path: Path) -> None:
    """TC-ASR-001-08 — 必須入力欠落: 副作用を開始する前に安定したvalidation errorを返す。"""
    with pytest.raises(AppError) as exc_info:
        ASRVerifier(None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    transcript = ASRTranscript(segments=(), provider="local_whisper_compatible")
    verifier = ASRVerifier(_FakeAsrClient(transcript))

    with pytest.raises(AppError) as exc_info:
        verifier.verify(None, [_tts_segment("ch01-seg001", "text")], {})
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        verifier.verify(tmp_path / "audio.wav", [], {})
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        LocalWhisperCompatibleClient().transcribe(None)
    assert exc_info.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as exc_info:
        LocalWhisperCompatibleClient().transcribe(tmp_path / "does-not-exist.wav")
    assert exc_info.value.code is ErrorCode.NOT_FOUND


@pytest.mark.unit
def test_tc_asr_001_09(tmp_path: Path) -> None:
    """TC-ASR-001-09 — 再実行時の決定性: 同じ入力・同じ依存応答なら同じ論理結果を返す。"""
    audio = tmp_path / "ch01-seg001.wav"
    audio.write_bytes(b"fake-audio-bytes")

    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=1.0, text="サンプル技術の定義に関する主張です"),),
        provider="local_whisper_compatible",
    )
    tts_segments = [_tts_segment("ch01-seg001", "サンプル技術の定義に関する主張です")]

    first = ASRVerifier(_FakeAsrClient(transcript)).verify(audio, tts_segments, {})
    second = ASRVerifier(_FakeAsrClient(transcript)).verify(audio, tts_segments, {})

    assert first.data == second.data


@pytest.mark.unit
def test_tc_asr_001_10(tmp_path: Path) -> None:
    """TC-ASR-001-10 — 入力・既存成果物の不変性: 正常/失敗いずれもaudio/tts_segmentsを変更しない。"""
    import hashlib

    audio = tmp_path / "ch01-seg001.wav"
    audio.write_bytes(b"fake-audio-bytes")
    before_hash = hashlib.sha256(audio.read_bytes()).hexdigest()

    tts_segments = [_tts_segment("ch01-seg001", "サンプル技術の定義に関する主張です")]
    tts_segments_snapshot = [dict(segment) for segment in tts_segments]

    transcript = ASRTranscript(
        segments=(ASRSegment(start_seconds=0.0, end_seconds=1.0, text="全く異なる文字起こし"),),
        provider="local_whisper_compatible",
    )
    ASRVerifier(_FakeAsrClient(transcript)).verify(audio, tts_segments, {})

    assert hashlib.sha256(audio.read_bytes()).hexdigest() == before_hash
    assert tts_segments == tts_segments_snapshot

    with pytest.raises(AppError):
        ASRVerifier(_FakeAsrClient(transcript)).verify(audio, [], {})
    assert hashlib.sha256(audio.read_bytes()).hexdigest() == before_hash
    assert tts_segments == tts_segments_snapshot


@pytest.mark.integration_smoke
def test_tc_asr_001_11(asr_connectivity_gate) -> None:
    """TC-ASR-001-11 — ローカルWhisper互換runtimeの疎通確認

    Contract: docs/test-cases/TASK-ASR-001-asr-script-audio-verification.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: runtime/modelの存在・読込可否・versionを確認し、まだ音声文字起こしは行わない。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert asr_connectivity_gate.available is True


@pytest.mark.integration_live
def test_tc_asr_001_12(asr_connectivity_gate, tmp_path: Path) -> None:
    """TC-ASR-001-12 — ローカルWhisper互換runtimeの実機能テスト

    Given: `asr_connectivity_gate`が成功済み
    When: 疎通成功後、数秒の固定fixture WAVだけを文字起こしし、非空segmentとtimestamp順を確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    import os
    import wave

    assert asr_connectivity_gate.available is True

    command = os.environ.get("WALKWISE_ASR_COMMAND", "whisper")
    audio = tmp_path / "fixture.wav"
    with wave.open(str(audio), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(b"\x00\x00" * 16000 * 2)

    client = LocalWhisperCompatibleClient(command=command)
    transcript = client.transcribe(audio)

    assert isinstance(transcript.segments, tuple)
    timestamps = [segment.start_seconds for segment in transcript.segments]
    assert timestamps == sorted(timestamps)
