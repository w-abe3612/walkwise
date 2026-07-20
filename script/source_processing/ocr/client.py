"""script/source_processing/ocr/client.py — 公開契約: OcrClient.check_runtime/recognize.

Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
Spec: docs/specifications/ocr-and-scanned-pdf.md
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from script.core.errors import AppError, ErrorCode

SubprocessRunner = Callable[[Sequence[str]], subprocess.CompletedProcess]

_DEFAULT_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class RuntimeHealth:
    """Tesseract runtimeの存在・version・言語一覧(副作用なしの確認結果)。"""

    available: bool
    version: str | None = None
    available_languages: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class OcrOptions:
    """1ページOCRの設定(ocr-and-scanned-pdf.md 5.3節: 既定はjpn+eng)。"""

    language_mode: str = "jpn+eng"


@dataclass(frozen=True)
class OcrPageResult:
    """1ページ分のOCR結果とconfidence。"""

    image_path: str
    text: str
    confidence: float
    language_mode: str
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.image_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "image_path is required")
        if not self.language_mode:
            raise AppError(ErrorCode.VALIDATION_ERROR, "language_mode is required")


def _default_runner(args: Sequence[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        timeout=_DEFAULT_TIMEOUT_SECONDS,
        check=False,
    )


def _parse_tesseract_tsv(tsv_text: str) -> tuple[str, float]:
    """tesseractのtsv出力からtextとconfidence(0.0-1.0)を再構成する。"""
    lines = tsv_text.splitlines()
    if not lines:
        return "", 0.0

    header = lines[0].split("\t")
    try:
        conf_index = header.index("conf")
        text_index = header.index("text")
    except ValueError:
        return "", 0.0

    words: list[str] = []
    confidences: list[float] = []
    for line in lines[1:]:
        columns = line.split("\t")
        if len(columns) <= max(conf_index, text_index):
            continue
        text = columns[text_index]
        try:
            confidence = float(columns[conf_index])
        except ValueError:
            continue
        if confidence >= 0 and text.strip():
            words.append(text)
            confidences.append(confidence)

    full_text = " ".join(words)
    overall_confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0
    return full_text, overall_confidence


class OcrClient:
    """Tesseractをsubprocess経由で呼び出すadapter(クラウドOCRは使用しない)。"""

    def __init__(
        self,
        *,
        tesseract_cmd: str | None = None,
        runner: SubprocessRunner | None = None,
    ) -> None:
        self._tesseract_cmd = tesseract_cmd or os.environ.get("TESSERACT_CMD") or "tesseract"
        self._runner = runner or _default_runner

    def check_runtime(self) -> RuntimeHealth:
        """Tesseractの存在・version・言語を副作用なく確認する。"""
        try:
            version_result = self._runner([self._tesseract_cmd, "--version"])
        except FileNotFoundError:
            return RuntimeHealth(available=False, error="tesseract executable not found")
        except Exception as exc:  # noqa: BLE001 - 外部subprocessの任意の失敗を安全に握りつぶす
            return RuntimeHealth(available=False, error=str(exc))

        if version_result.returncode != 0:
            error_message = (version_result.stderr or "tesseract --version failed").strip()
            return RuntimeHealth(available=False, error=error_message)

        version_line = version_result.stdout.splitlines()[0].strip() if version_result.stdout else ""

        languages: tuple[str, ...] = ()
        try:
            lang_result = self._runner([self._tesseract_cmd, "--list-langs"])
        except Exception:  # noqa: BLE001 - 言語一覧取得の失敗はrutime判定自体を失敗にしない
            lang_result = None

        if lang_result is not None and lang_result.returncode == 0:
            lang_lines = [line.strip() for line in lang_result.stdout.splitlines() if line.strip()]
            languages = tuple(lang_lines[1:]) if len(lang_lines) > 1 else tuple(lang_lines)

        return RuntimeHealth(available=True, version=version_line, available_languages=languages)

    def recognize(self, image_path: Path, options: OcrOptions) -> OcrPageResult:
        """subprocessを介して1ページをOCRする。"""
        if not image_path:
            raise AppError(ErrorCode.VALIDATION_ERROR, "image_path is required")
        if options is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "options is required")

        image_path = Path(image_path)
        if not image_path.is_file():
            raise AppError(ErrorCode.NOT_FOUND, f"image does not exist: {image_path}")

        args = [self._tesseract_cmd, str(image_path), "stdout", "-l", options.language_mode, "tsv"]
        try:
            result = self._runner(args)
        except FileNotFoundError as exc:
            raise AppError(
                ErrorCode.EXTERNAL_UNAVAILABLE,
                "tesseract executable not found",
                technical_detail=str(exc),
            ) from exc
        except Exception as exc:  # noqa: BLE001 - subprocessの任意の失敗をAppErrorへ変換する
            raise AppError(
                ErrorCode.EXTERNAL_UNAVAILABLE,
                f"tesseract subprocess failed for {image_path}",
                technical_detail=str(exc),
            ) from exc

        if result.returncode != 0:
            raise AppError(
                ErrorCode.EXTERNAL_UNAVAILABLE,
                f"tesseract exited with a non-zero status for {image_path}",
                technical_detail=(result.stderr or "").strip(),
            )

        text, confidence = _parse_tesseract_tsv(result.stdout)
        warnings: list[str] = []
        if not text.strip():
            warnings.append("empty_ocr_result")

        return OcrPageResult(
            image_path=str(image_path),
            text=text,
            confidence=confidence,
            language_mode=options.language_mode,
            warnings=tuple(warnings),
        )
