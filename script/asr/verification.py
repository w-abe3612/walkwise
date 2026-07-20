"""script/asr/verification.py — 公開契約:
ASRVerifier.verify(audio, tts_segments, terminology) -> ASRVerificationReport,
normalize_for_comparison(text, terminology) -> str.

Contract: docs/test-cases/TASK-ASR-001-asr-script-audio-verification.md
Spec: docs/specifications/asr-script-audio-verification.md(5.1〜5.6節, 8節)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from script.asr.base import ASRClient
from script.core.errors import AppError, ErrorCode

# 15節: CER/WERの具体的閾値は未決定事項。仕様確定までの安全側の暫定値。
_REVIEW_REQUIRED_CER_THRESHOLD = 0.15
_REVIEW_REQUIRED_WER_THRESHOLD = 0.2
_ALLOWED_STATUSES = ("pass", "warning", "review_required")


def normalize_for_comparison(text: Any, terminology: Mapping[str, str]) -> str:
    """用語辞書を用いて比較用にだけ正規化する(原稿自体は変更しない)。

    Public contract: ``normalize_for_comparison(text, terminology) -> str``.
    """
    if text is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")
    if terminology is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "terminology is required")

    normalized = str(text)
    # 長い変則表記から先に置換し、短い表記による部分一致誤変換を避ける。
    for variant in sorted(terminology, key=len, reverse=True):
        normalized = normalized.replace(variant, terminology[variant])
    return normalized


def _levenshtein(reference: Sequence[Any], hypothesis: Sequence[Any]) -> int:
    previous_row = list(range(len(hypothesis) + 1))
    for i, ref_item in enumerate(reference, start=1):
        current_row = [i] + [0] * len(hypothesis)
        for j, hyp_item in enumerate(hypothesis, start=1):
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            substitute_cost = previous_row[j - 1] + (0 if ref_item == hyp_item else 1)
            current_row[j] = min(insert_cost, delete_cost, substitute_cost)
        previous_row = current_row
    return previous_row[-1]


def _character_error_rate(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return _levenshtein(list(reference), list(hypothesis)) / len(reference)


def _word_error_rate(reference: str, hypothesis: str) -> float:
    reference_words = reference.split()
    hypothesis_words = hypothesis.split()
    if not reference_words:
        return 0.0 if not hypothesis_words else 1.0
    return _levenshtein(reference_words, hypothesis_words) / len(reference_words)


class ASRVerificationReport:
    """`ASRVerifier.verify()`の戻り値(8節report例に対応)。"""

    def __init__(self, **data: Any) -> None:
        status = data.get("status")
        if status not in _ALLOWED_STATUSES:
            # 12節: auto_fail_policy.allowed=falseの間、ASR単独結果でstatus: failを設定できない。
            raise AppError(ErrorCode.VALIDATION_ERROR, f"invalid or disallowed status: {status!r}")
        self.data = dict(data)
        self.data.setdefault("threshold_status", "provisional")
        self.data.setdefault("issues", ())
        self.data["issues"] = tuple(self.data["issues"])

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class ASRVerifier:
    """segment alignmentと章fallbackを行い、review候補の差分reportを返す(5.2, 5.4, 5.5節)。"""

    def __init__(self, asr_client: ASRClient) -> None:
        if asr_client is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "asr_client is required")
        self._asr_client = asr_client

    def verify(
        self,
        audio: Any,
        tts_segments: Sequence[Mapping[str, Any]],
        terminology: Mapping[str, str],
    ) -> ASRVerificationReport:
        """segment alignmentと章fallbackを行い差分候補を返す。

        Public contract: ``ASRVerifier.verify(audio, tts_segments, terminology) -> ASRVerificationReport``.
        """
        if not audio:
            raise AppError(ErrorCode.VALIDATION_ERROR, "audio is required")
        if not tts_segments:
            raise AppError(ErrorCode.VALIDATION_ERROR, "tts_segments is required")
        if terminology is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "terminology is required")

        transcript = self._asr_client.transcribe(Path(audio))
        asr_segments = list(transcript.segments)
        tts_segment_list = list(tts_segments)

        issues: list[dict[str, Any]] = []
        alignment_fallback = False
        alignment_fallback_reason: str | None = None

        if len(asr_segments) == len(tts_segment_list):
            # 5.2節: 原則segment単位でアラインメントする。
            pairs = [
                (tts_segment.get("segment_id"), str(tts_segment["tts_text"]), asr_segment.text)
                for tts_segment, asr_segment in zip(tts_segment_list, asr_segments)
            ]
        else:
            # 5.2節: segment alignmentが不能な場合は章単位比較へfallbackし、理由を記録する。
            alignment_fallback = True
            alignment_fallback_reason = (
                f"segment_count_mismatch: tts_segments={len(tts_segment_list)} asr_segments={len(asr_segments)}"
            )
            combined_tts_text = " ".join(str(segment["tts_text"]) for segment in tts_segment_list)
            combined_asr_text = " ".join(segment.text for segment in asr_segments)
            pairs = [(None, combined_tts_text, combined_asr_text)]

        cer_values: list[float] = []
        wer_values: list[float] = []
        for segment_id, tts_text, asr_text in pairs:
            reference = normalize_for_comparison(tts_text, terminology)
            hypothesis = normalize_for_comparison(asr_text, terminology)
            cer = _character_error_rate(reference, hypothesis)
            wer = _word_error_rate(reference, hypothesis)
            cer_values.append(cer)
            wer_values.append(wer)
            if cer > _REVIEW_REQUIRED_CER_THRESHOLD or wer > _REVIEW_REQUIRED_WER_THRESHOLD:
                issues.append(
                    {"code": "possible_mispronunciation_or_diff", "severity": "review_required", "segment_id": segment_id}
                )

        if alignment_fallback:
            issues.append(
                {
                    "code": "segment_alignment_fallback",
                    "severity": "review_required",
                    "segment_id": None,
                    "reason": alignment_fallback_reason,
                }
            )

        duplicate_segment_ratio = 0.0
        if not alignment_fallback:
            segment_ids = [segment.get("segment_id") for segment in tts_segment_list]
            if len(set(segment_ids)) != len(segment_ids):
                duplicate_segment_ratio = 1.0 - (len(set(segment_ids)) / len(segment_ids))

        average_cer = sum(cer_values) / len(cer_values) if cer_values else 0.0
        average_wer = sum(wer_values) / len(wer_values) if wer_values else 0.0

        # 5.5節: 大きな差分であっても"fail"にはせず、review_requiredに留める(自動fail禁止)。
        if issues:
            status = "review_required"
        elif average_cer > 0.0 or average_wer > 0.0:
            status = "warning"
        else:
            status = "pass"

        return ASRVerificationReport(
            schema_version="1.0",
            asr_provider=transcript.provider,
            asr_provider_version=transcript.provider_version,
            status=status,
            metrics={
                "character_error_rate": round(average_cer, 4),
                "word_error_rate": round(average_wer, 4),
                "missing_segment_ratio": 0.0,
                "duplicate_segment_ratio": duplicate_segment_ratio,
                "order_mismatch_count": 0,
            },
            issues=tuple(issues),
            alignment_fallback=alignment_fallback,
            alignment_fallback_reason=alignment_fallback_reason,
            threshold_status="provisional",
        )
