"""STEP4 test implementation for TASK-AUDIO-001: PreviewService.

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.audio.preview import PreviewRequest, PreviewService
from script.audio.synthesis import SegmentAudio
from script.core.errors import AppError

pytestmark = pytest.mark.mvp


def _segment_audio(segment_id: str = "ch01-seg001", *, duration: float = 4.2, sample_rate: int = 24000) -> SegmentAudio:
    return SegmentAudio(
        segment_id=segment_id,
        audio_id=f"{segment_id}-audio-id",
        output_path=f"audio/cache/wav/segments/{segment_id}.wav",
        duration_seconds=duration,
        sample_rate_hz=sample_rate,
        channels=1,
    )


@pytest.mark.integration_mock
def test_tc_audio_001_03() -> None:
    """TC-AUDIO-001-03 — preview version: 同条件で再試聴生成しても既存を上書きせず新versionを作る。"""
    service = PreviewService()
    request = PreviewRequest(project_id="proj-1", chapter_id="ch01", segment_audios=(_segment_audio(),))

    preview_1 = service.generate(request)
    preview_2 = service.generate(request)

    assert preview_1.version == 1
    assert preview_2.version == 2
    assert preview_1.preview_id != preview_2.preview_id
    assert preview_1.output_path != preview_2.output_path


@pytest.mark.unit
def test_tc_audio_001_06() -> None:
    """TC-AUDIO-001-06 — audio_id: 破損(duration/sample_rate不正)なsegment audioは成功扱いにしない。"""
    good_audio = _segment_audio()
    assert good_audio.audio_id == "ch01-seg001-audio-id"

    with pytest.raises(AppError):
        SegmentAudio(
            segment_id="ch01-seg002",
            audio_id="ch01-seg002-audio-id",
            output_path="audio/cache/wav/segments/ch01-seg002.wav",
            duration_seconds=-1.0,
            sample_rate_hz=24000,
            channels=1,
        )

    service = PreviewService()
    zero_rate_audio = SegmentAudio.__new__(SegmentAudio)
    object.__setattr__(zero_rate_audio, "segment_id", "ch01-seg003")
    object.__setattr__(zero_rate_audio, "audio_id", "ch01-seg003-audio-id")
    object.__setattr__(zero_rate_audio, "output_path", "audio/cache/wav/segments/ch01-seg003.wav")
    object.__setattr__(zero_rate_audio, "duration_seconds", 1.0)
    object.__setattr__(zero_rate_audio, "sample_rate_hz", 0)
    object.__setattr__(zero_rate_audio, "channels", 1)
    object.__setattr__(zero_rate_audio, "parts", ())
    object.__setattr__(zero_rate_audio, "cache_hit", False)

    with pytest.raises(AppError):
        service.generate(PreviewRequest(project_id="proj-1", chapter_id="ch01", segment_audios=(zero_rate_audio,)))


@pytest.mark.unit
def test_tc_audio_001_09() -> None:
    """TC-AUDIO-001-09 — 再実行時の決定性: versionを除き同じ論理結果を返す。"""
    service = PreviewService()
    request = PreviewRequest(
        project_id="proj-1", chapter_id="ch01", segment_audios=(_segment_audio("ch01-seg001"), _segment_audio("ch01-seg002"))
    )

    preview_1 = service.generate(request)
    preview_2 = service.generate(request)

    assert preview_1.segment_ids == preview_2.segment_ids
    assert preview_1.duration_seconds == preview_2.duration_seconds
    assert preview_1.project_id == preview_2.project_id
    assert preview_1.chapter_id == preview_2.chapter_id
    assert preview_2.version == preview_1.version + 1
