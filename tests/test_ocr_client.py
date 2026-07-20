"""STEP3->STEP4 test suite for TASK-OCR-001: OCR・スキャンPDF処理.

Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
Spec: docs/specifications/ocr-and-scanned-pdf.md
Production files:
- script/source_processing/ocr/client.py
- script/source_processing/ocr/pipeline.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from script.core.errors import AppError, ErrorCode
from script.source_processing.ocr.client import OcrClient, OcrOptions
from script.source_processing.ocr.pipeline import OcrPageRequest, OcrPipeline

pytestmark = pytest.mark.mvp


def _completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _tsv(rows: list[tuple[str, int]]) -> str:
    header = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext"
    lines = [header]
    for text, conf in rows:
        lines.append(f"5\t1\t1\t1\t1\t1\t0\t0\t10\t10\t{conf}\t{text}")
    return "\n".join(lines)


@pytest.mark.integration_mock
def test_tc_ocr_001_01(tmp_path: Path) -> None:
    """TC-OCR-001-01 — runtimeなし

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: integration_mock
    Given: Tesseractが見つからない
    When: OCRを開始
    Then: 疎通確認で停止しSourceをfailed/reviewableにする
    """
    calls: list[list[str]] = []

    def runner(args):
        calls.append(list(args))
        raise FileNotFoundError("tesseract not found")

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    health = client.check_runtime()
    assert health.available is False
    calls.clear()

    image = tmp_path / "page1.png"
    image.write_bytes(b"fake-image-bytes")

    pipeline = OcrPipeline(client)
    manifest = pipeline.process_pages(
        [OcrPageRequest(image_path=str(image), options=OcrOptions())],
        context={},
    )

    assert manifest.runtime_available is False
    assert manifest.pages[0].status == "failed"
    assert manifest.pages[0].review_required is True
    assert "tesseract_runtime_unavailable" in manifest.pages[0].review_reasons

    # pipeline内では疎通確認(--version)だけが呼ばれ、recognize用のsubprocess呼出しは発生していない。
    assert len(calls) == 1
    assert calls[0][1] == "--version"


@pytest.mark.integration_mock
def test_tc_ocr_001_03(tmp_path: Path) -> None:
    """TC-OCR-001-03 — ページ失敗分離

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: integration_mock
    Given: 複数page中1件だけsubprocess失敗
    When: 処理
    Then: 他page結果を保持しmanifestに失敗を記録
    """
    good_1 = tmp_path / "good1.png"
    good_1.write_bytes(b"fake-1")
    bad = tmp_path / "bad.png"
    bad.write_bytes(b"fake-bad")
    good_2 = tmp_path / "good2.png"
    good_2.write_bytes(b"fake-2")

    def runner(args):
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        image_path = args[1]
        if image_path == str(bad):
            return _completed(returncode=1, stderr="simulated subprocess failure")
        return _completed(stdout=_tsv([("hello", 90)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    pipeline = OcrPipeline(client)

    manifest = pipeline.process_pages(
        [
            OcrPageRequest(image_path=str(good_1), options=OcrOptions()),
            OcrPageRequest(image_path=str(bad), options=OcrOptions()),
            OcrPageRequest(image_path=str(good_2), options=OcrOptions()),
        ],
        context={},
    )

    statuses = [page.status for page in manifest.pages]
    assert statuses == ["success", "failed", "success"]
    assert manifest.pages[1].review_required is True
    assert manifest.pages[1].error is not None
    assert manifest.pages[0].result.text == "hello"
    assert manifest.pages[2].result.text == "hello"


@pytest.mark.unit
def test_tc_ocr_001_05(tmp_path: Path) -> None:
    """TC-OCR-001-05 — 言語設定

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「言語設定」を実行する
    Then: 「言語設定」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    calls: list[list[str]] = []

    def runner(args):
        calls.append(list(args))
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\njpn_vert\n")
        return _completed(stdout=_tsv([("ok", 95)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    health = client.check_runtime()
    assert health.available is True
    assert "jpn" in health.available_languages
    assert "eng" in health.available_languages

    image_path = tmp_path / "page.png"
    image_path.write_bytes(b"fake")
    client.recognize(image_path, OcrOptions(language_mode="jpn+eng"))

    recognize_call = calls[-1]
    assert "-l" in recognize_call
    assert recognize_call[recognize_call.index("-l") + 1] == "jpn+eng"


@pytest.mark.unit
def test_tc_ocr_001_07(tmp_path: Path) -> None:
    """TC-OCR-001-07 — table/code/math/figure flag

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「table/code/math/figure flag」を実行する
    Then: 「table/code/math/figure flag」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    image = tmp_path / "formula.png"
    image.write_bytes(b"fake")

    def runner(args):
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        # 高confidenceでも、high_risk_hintがある限りreview_requiredのまま自動確定しない。
        return _completed(stdout=_tsv([("x=1", 99)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    pipeline = OcrPipeline(client)

    for hint in ("formula", "code", "table", "figure"):
        manifest = pipeline.process_pages(
            [OcrPageRequest(image_path=str(image), options=OcrOptions(), high_risk_hint=hint)],
            context={},
        )
        outcome = manifest.pages[0]
        assert outcome.status == "success"
        assert outcome.review_required is True
        assert f"high_risk_{hint}" in outcome.review_reasons

    with pytest.raises(AppError) as excinfo:
        OcrPageRequest(image_path=str(image), options=OcrOptions(), high_risk_hint="not_a_real_hint")
    assert excinfo.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_ocr_001_09(tmp_path: Path) -> None:
    """TC-OCR-001-09 — 再実行時の決定性

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `OcrClient.check_runtime() -> RuntimeHealth`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    image = tmp_path / "page.png"
    image.write_bytes(b"fake")

    def runner(args):
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        return _completed(stdout=_tsv([("stable", 88)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)

    first_health = client.check_runtime()
    second_health = client.check_runtime()
    assert first_health == second_health

    first_result = client.recognize(image, OcrOptions())
    second_result = client.recognize(image, OcrOptions())
    assert first_result == second_result


@pytest.mark.integration_smoke
def test_tc_ocr_001_11(tesseract_connectivity_gate) -> None:
    """TC-OCR-001-11 — Tesseract runtimeの疎通確認

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: integration_smoke
    Given: 実接続テストが明示的に有効化され、必要な設定が存在する
    When: `tesseract --version`と必要言語一覧を確認し、画像処理を行わない。
    Then: ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。
    """
    assert tesseract_connectivity_gate.available is True
    assert tesseract_connectivity_gate.version
