"""script/audio/thresholds.py — 公開契約: AudioThresholds.load()/validate_approval().

Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
Spec: docs/specifications/13-audio-validation.md(5節),
      docs/spec-proposals/audio-validation-thresholds.md(5.3節)
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from script.core.errors import AppError, ErrorCode

_VALID_STATUSES = ("provisional", "approved")


@dataclass(frozen=True)
class LoudnessThreshold:
    target_lufs: float = -18.0
    warning_tolerance_lu: float = 4.0


@dataclass(frozen=True)
class PeakThreshold:
    maximum_dbfs: float = -0.5


@dataclass(frozen=True)
class TextDurationRatioThreshold:
    minimum_characters_per_second: float = 2.0
    maximum_characters_per_second: float = 12.0


@dataclass(frozen=True)
class ThresholdEvidence:
    """audio-validation-thresholds.md 5.1/5.3節: 実測状況の記録。"""

    measured: bool = False
    measured_speakers: tuple[str, ...] = ()
    sample_count: int = 0
    minimum_required_speakers: int = 2

    def __post_init__(self) -> None:
        if self.sample_count < 0:
            raise AppError(ErrorCode.VALIDATION_ERROR, "sample_count must not be negative")
        if self.minimum_required_speakers < 1:
            raise AppError(ErrorCode.VALIDATION_ERROR, "minimum_required_speakers must be at least 1")


@dataclass(frozen=True)
class AudioThresholdSet:
    """13-audio-validation.md 5節/audio-validation-thresholds.md 5.3節の仮設定をそのまま転記。"""

    schema_version: str = "1.0"
    status: str = "provisional"
    minimum_duration_seconds: float = 0.5
    maximum_silence_seconds: float = 3.0
    minimum_non_silent_ratio: float = 0.2
    loudness: LoudnessThreshold = field(default_factory=LoudnessThreshold)
    peak: PeakThreshold = field(default_factory=PeakThreshold)
    text_duration_ratio: TextDurationRatioThreshold = field(default_factory=TextDurationRatioThreshold)
    evidence: ThresholdEvidence = field(default_factory=ThresholdEvidence)

    def __post_init__(self) -> None:
        if self.status not in _VALID_STATUSES:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"unknown threshold status: {self.status}")
        if self.status == "approved":
            # 実測なしapproved禁止(構造的な二重防御。validate_approval()が正式な昇格経路)。
            if not self.evidence.measured:
                raise AppError(ErrorCode.VALIDATION_ERROR, "approved thresholds require evidence.measured=True")
            if self.evidence.sample_count < self.evidence.minimum_required_speakers:
                raise AppError(
                    ErrorCode.VALIDATION_ERROR,
                    f"approved thresholds require sample_count >= {self.evidence.minimum_required_speakers}",
                )


class AudioThresholds:
    """provisional値を読込み、実測不足でapprovedを拒否する。"""

    def load(self, *, evidence: ThresholdEvidence | None = None) -> AudioThresholdSet:
        """provisional threshold値を読み込む(13-audio-validation.md 5節の仮値と一致)。"""
        return AudioThresholdSet(status="provisional", evidence=evidence if evidence is not None else ThresholdEvidence())

    def validate_approval(self, thresholds: AudioThresholdSet) -> AudioThresholdSet:
        """実測(evidence.measured)と必要話者数を満たす場合だけapprovedへ昇格する。"""
        if thresholds is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "thresholds is required")

        if not thresholds.evidence.measured:
            raise AppError(ErrorCode.PERMISSION_DENIED, "cannot approve thresholds: evidence.measured is False")
        if thresholds.evidence.sample_count < thresholds.evidence.minimum_required_speakers:
            raise AppError(
                ErrorCode.PERMISSION_DENIED,
                f"cannot approve thresholds: sample_count {thresholds.evidence.sample_count} "
                f"< required {thresholds.evidence.minimum_required_speakers}",
            )

        return dataclasses.replace(thresholds, status="approved")
