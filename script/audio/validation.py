"""script/audio/validation.py — 公開契約:
AudioValidator.validate(path, text, thresholds) -> ValidationReport.

Contract: docs/test-cases/TASK-AUDIO-002-audio-validation.md
Spec: docs/specifications/13-audio-validation.md(3, 4, 9節)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from script.audio.measurements import AudioMeasurementAdapter
from script.audio.thresholds import AudioThresholdSet
from script.core.errors import AppError, ErrorCode


class ValidationStatus(str, Enum):
    """13-audio-validation.md 3節。"""

    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    REVIEW_REQUIRED = "review_required"


# 保守的な累積規則: fail > review_required > warning > pass の優先順位で、
# より軽い判定がより重い判定を覆い隠さない(13-audio-validation.md 3節)。
_SEVERITY_ORDER = (ValidationStatus.FAIL, ValidationStatus.REVIEW_REQUIRED, ValidationStatus.WARNING)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    value: float | None = None
    threshold: float | None = None


@dataclass(frozen=True)
class ValidationReport:
    """AudioValidator.validate()の戻り値(13-audio-validation.md 9節のreport形式)。"""

    status: ValidationStatus
    threshold_status: str
    issues: tuple[ValidationIssue, ...] = ()
    duration_seconds: float | None = None
    sample_rate_hz: int | None = None
    channels: int | None = None


class AudioValidator:
    """破損・0秒・形式不一致を常にfail、主観品質項目をreview_required扱いにする。"""

    def __init__(self, *, measurement_adapter: AudioMeasurementAdapter | None = None) -> None:
        self._adapter = measurement_adapter if measurement_adapter is not None else AudioMeasurementAdapter()

    def validate(self, path: Path | str, text: str, thresholds: AudioThresholdSet) -> ValidationReport:
        """破損・0秒・形式不一致をfail、主観項目をreview扱いにする。"""
        if path is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "path is required")
        if text is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")
        if thresholds is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "thresholds is required")

        try:
            measurement = self._adapter.measure(path)
        except AppError:
            # 破損・0秒・読込不能は常にfail(audio-validation-thresholds.md 5.2節: warningへ格下げしない)。
            return ValidationReport(
                status=ValidationStatus.FAIL,
                threshold_status=thresholds.status,
                issues=(ValidationIssue(code="corrupted_or_unreadable", severity="fail"),),
            )

        issues: list[ValidationIssue] = []

        if measurement.duration_seconds <= 0 or measurement.duration_seconds < thresholds.minimum_duration_seconds:
            issues.append(
                ValidationIssue(
                    code="duration_too_short",
                    severity="fail",
                    value=measurement.duration_seconds,
                    threshold=thresholds.minimum_duration_seconds,
                )
            )

        if measurement.silence_ratio is not None:
            if measurement.silence_ratio >= (1.0 - thresholds.minimum_non_silent_ratio):
                issues.append(
                    ValidationIssue(code="mostly_silent", severity="fail", value=measurement.silence_ratio)
                )
            elif measurement.silence_ratio > 0.5:
                issues.append(
                    ValidationIssue(code="long_silence", severity="warning", value=measurement.silence_ratio)
                )

        if measurement.peak_dbfs is not None and measurement.peak_dbfs > thresholds.peak.maximum_dbfs:
            issues.append(
                ValidationIssue(
                    code="clipping",
                    severity="review_required",
                    value=measurement.peak_dbfs,
                    threshold=thresholds.peak.maximum_dbfs,
                )
            )

        if text and measurement.duration_seconds > 0:
            characters_per_second = len(text) / measurement.duration_seconds
            ratio = thresholds.text_duration_ratio
            if not (ratio.minimum_characters_per_second <= characters_per_second <= ratio.maximum_characters_per_second):
                issues.append(
                    ValidationIssue(
                        code="text_duration_ratio_out_of_range",
                        severity="warning",
                        value=characters_per_second,
                    )
                )

        status = self._aggregate_status(issues)

        return ValidationReport(
            status=status,
            threshold_status=thresholds.status,
            issues=tuple(issues),
            duration_seconds=measurement.duration_seconds,
            sample_rate_hz=measurement.sample_rate_hz,
            channels=measurement.channels,
        )

    @staticmethod
    def _aggregate_status(issues: list[ValidationIssue]) -> ValidationStatus:
        severities = {issue.severity for issue in issues}
        for status in _SEVERITY_ORDER:
            if status.value in severities:
                return status
        return ValidationStatus.PASS
