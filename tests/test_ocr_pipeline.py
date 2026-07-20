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
from PIL import Image, ImageDraw

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


def _healthy_runner(recognize_stdout: str):
    def runner(args):
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        return _completed(stdout=recognize_stdout)

    return runner


@pytest.mark.unit
def test_tc_ocr_001_02(tmp_path: Path) -> None:
    """TC-OCR-001-02 — 高リスク要素

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: unit
    Given: table/code/math/figure候補page
    When: pipeline処理
    Then: review_required flagを付け自動確定しない
    """
    image = tmp_path / "table.png"
    image.write_bytes(b"fake")

    client = OcrClient(tesseract_cmd="tesseract", runner=_healthy_runner(_tsv([("A|B", 99)])))
    pipeline = OcrPipeline(client)

    manifest = pipeline.process_pages(
        [OcrPageRequest(image_path=str(image), options=OcrOptions(), high_risk_hint="table")],
        context={},
    )

    outcome = manifest.pages[0]
    assert outcome.status == "success"
    assert outcome.review_required is True
    assert "high_risk_table" in outcome.review_reasons
    # 高リスク要素は自動確定されない: OcrPageOutcomeに「確定済み」を意味するfieldは存在せず、
    # review_requiredが常にTrueであることのみが確定状態を表す。
    assert not hasattr(outcome, "auto_confirmed")


@pytest.mark.integration_mock
def test_tc_ocr_001_04(tmp_path: Path) -> None:
    """TC-OCR-001-04 — Tesseract subprocess/adapter境界

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: integration_mock
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「Tesseract subprocess/adapter境界」を実行する
    Then: 「Tesseract subprocess/adapter境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    image = tmp_path / "page.png"
    image.write_bytes(b"fake")

    calls: list[list[str]] = []

    def runner(args):
        calls.append(list(args))
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        return _completed(stdout=_tsv([("boundary", 90)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    pipeline = OcrPipeline(client)

    manifest = pipeline.process_pages(
        [OcrPageRequest(image_path=str(image), options=OcrOptions())],
        context={},
    )

    assert manifest.pages[0].result.text == "boundary"
    # OcrPipelineはsubprocessを直接呼ばず、OcrClient(adapter)経由でのみ呼び出す。
    assert any(str(image) in call for call in calls)


@pytest.mark.unit
def test_tc_ocr_001_06(tmp_path: Path) -> None:
    """TC-OCR-001-06 — confidence

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `OcrClient.check_runtime() -> RuntimeHealth`を通じて「confidence」を実行する
    Then: 「confidence」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    high_conf_image = tmp_path / "high.png"
    high_conf_image.write_bytes(b"fake")
    low_conf_image = tmp_path / "low.png"
    low_conf_image.write_bytes(b"fake")

    def runner(args):
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        if str(high_conf_image) in args:
            return _completed(stdout=_tsv([("confident", 95)]))
        return _completed(stdout=_tsv([("unsure", 20)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    pipeline = OcrPipeline(client)

    manifest = pipeline.process_pages(
        [
            OcrPageRequest(image_path=str(high_conf_image), options=OcrOptions()),
            OcrPageRequest(image_path=str(low_conf_image), options=OcrOptions()),
        ],
        context={},
    )

    high_outcome, low_outcome = manifest.pages
    assert high_outcome.result.confidence == pytest.approx(0.95)
    assert high_outcome.review_required is False

    assert low_outcome.result.confidence == pytest.approx(0.20)
    assert low_outcome.review_required is True
    assert "low_confidence" in low_outcome.review_reasons


@pytest.mark.unit
def test_tc_ocr_001_08(tmp_path: Path) -> None:
    """TC-OCR-001-08 — 必須入力欠落

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `OcrClient.check_runtime() -> RuntimeHealth`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    with pytest.raises(AppError) as excinfo_client:
        OcrPipeline(client=None)
    assert excinfo_client.value.code is ErrorCode.VALIDATION_ERROR

    client = OcrClient(tesseract_cmd="tesseract", runner=_healthy_runner(_tsv([("x", 90)])))
    pipeline = OcrPipeline(client)

    with pytest.raises(AppError) as excinfo_empty:
        pipeline.process_pages([], context={})
    assert excinfo_empty.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_missing_path:
        OcrPageRequest(image_path="", options=OcrOptions())
    assert excinfo_missing_path.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_missing_options:
        OcrPageRequest(image_path=str(tmp_path / "x.png"), options=None)
    assert excinfo_missing_options.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.unit
def test_tc_ocr_001_10(tmp_path: Path) -> None:
    """TC-OCR-001-10 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    good = tmp_path / "good.png"
    good.write_bytes(b"good-bytes")
    good_bytes_before = good.read_bytes()

    bad = tmp_path / "bad.png"
    bad.write_bytes(b"bad-bytes")

    def runner(args):
        if "--version" in args:
            return _completed(stdout="tesseract 5.3.0\n")
        if "--list-langs" in args:
            return _completed(stdout="List of available languages\njpn\neng\n")
        if str(bad) in args:
            return _completed(returncode=1, stderr="boom")
        return _completed(stdout=_tsv([("kept", 90)]))

    client = OcrClient(tesseract_cmd="tesseract", runner=runner)
    pipeline = OcrPipeline(client)

    manifest = pipeline.process_pages(
        [
            OcrPageRequest(image_path=str(good), options=OcrOptions()),
            OcrPageRequest(image_path=str(bad), options=OcrOptions()),
        ],
        context={},
    )

    assert manifest.pages[0].status == "success"
    assert manifest.pages[1].status == "failed"
    assert good.read_bytes() == good_bytes_before
    assert bad.read_bytes() == b"bad-bytes"


@pytest.mark.integration_live
def test_tc_ocr_001_12(tesseract_connectivity_gate, tmp_path: Path) -> None:
    """TC-OCR-001-12 — Tesseract runtimeの実機能テスト

    Contract: docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md
    Priority: P1
    Layer: integration_live
    Given: `tesseract_connectivity_gate`が成功済み
    When: 疎通成功後、1行だけの固定fixture画像をOCRし、期待語を含むpage resultを確認する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    assert tesseract_connectivity_gate.available is True

    image_path = tmp_path / "fixture_line.png"
    image = Image.new("RGB", (300, 60), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 15), "WALKWISE", fill="black")
    image.save(image_path, format="PNG")

    client = OcrClient()
    result = client.recognize(image_path, OcrOptions(language_mode="eng"))

    assert "WALKWISE" in result.text.upper()
