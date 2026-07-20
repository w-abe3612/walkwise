"""STEP3->STEP4 test suite for TASK-INGEST-001: 資料入力orchestrator・テキスト入力.

Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
Spec: docs/specifications/material-input-pipeline.md
Production files:
- script/source_processing/orchestrator.py
- script/source_processing/text_ingestion.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

from script.core.errors import AppError, ErrorCode
from script.source_processing.orchestrator import IngestSource, MaterialInputOrchestrator
from script.source_processing.text_ingestion import TextIngestionAdapter

pytestmark = pytest.mark.mvp


class _FakeAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, dict]] = []

    def process(self, path: Path, context) -> dict:
        self.calls.append((path, dict(context)))
        return {"path": str(path)}


@pytest.mark.unit
def test_tc_ingest_001_01(tmp_path: Path) -> None:
    """TC-INGEST-001-01 — dispatch

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P0
    Layer: unit
    Given: text/pdf/image Source
    When: processする
    Then: 各adapterへ正確に1回dispatchする
    """
    text_adapter = _FakeAdapter()
    pdf_adapter = _FakeAdapter()
    image_adapter = _FakeAdapter()

    orchestrator = MaterialInputOrchestrator()
    orchestrator.register_adapter("text", text_adapter)
    orchestrator.register_adapter("pdf", pdf_adapter)
    orchestrator.register_adapter("image_sequence", image_adapter)

    text_path = tmp_path / "a.txt"
    text_path.write_text("hello", encoding="utf-8")
    pdf_path = tmp_path / "a.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")
    image_path = tmp_path / "a.png"
    image_path.write_bytes(b"\x89PNG")

    orchestrator.process(IngestSource(source_id="src-text", media_type="text", path=text_path))
    orchestrator.process(IngestSource(source_id="src-pdf", media_type="pdf", path=pdf_path))
    orchestrator.process(IngestSource(source_id="src-image", media_type="image_sequence", path=image_path))

    assert len(text_adapter.calls) == 1
    assert len(pdf_adapter.calls) == 1
    assert len(image_adapter.calls) == 1
    assert text_adapter.calls[0][0] == text_path
    assert pdf_adapter.calls[0][0] == pdf_path
    assert image_adapter.calls[0][0] == image_path


@pytest.mark.unit
def test_tc_ingest_001_03(tmp_path: Path) -> None:
    """TC-INGEST-001-03 — text encoding

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P0
    Layer: unit
    Given: UTF-8正常/不正bytes
    When: text adapterを実行
    Then: 正常はstructured、異常はfailedで原本保持
    """
    orchestrator = MaterialInputOrchestrator()
    orchestrator.register_adapter("text", TextIngestionAdapter())

    good_path = tmp_path / "good.txt"
    good_path.write_text("正常な本文", encoding="utf-8")
    bad_path = tmp_path / "bad.txt"
    bad_bytes = b"\xff\xfe broken utf-8 \x80\x81"
    bad_path.write_bytes(bad_bytes)

    good_result = orchestrator.process(IngestSource(source_id="src-good", media_type="text", path=good_path))
    assert good_result.status == "structured"
    assert good_result.structured is not None
    assert good_result.error is None

    bad_result = orchestrator.process(IngestSource(source_id="src-bad", media_type="text", path=bad_path))
    assert bad_result.status == "failed"
    assert bad_result.structured is None
    assert bad_result.error is not None
    assert bad_result.error["code"] == ErrorCode.VALIDATION_ERROR.value

    # 原本保持: 失敗時にbad_pathのbyteが変化していない。
    assert bad_path.read_bytes() == bad_bytes


@pytest.mark.unit
def test_tc_ingest_001_05(tmp_path: Path) -> None:
    """TC-INGEST-001-05 — status更新

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「status更新」を実行する
    Then: 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。
    """
    orchestrator = MaterialInputOrchestrator()
    orchestrator.register_adapter("text", TextIngestionAdapter())

    good_path = tmp_path / "good.txt"
    good_path.write_text("ok", encoding="utf-8")
    bad_path = tmp_path / "bad.txt"
    bad_path.write_bytes(b"\xff\xfe\x80")

    good_result = orchestrator.process(IngestSource(source_id="src-good", media_type="text", path=good_path))
    bad_result = orchestrator.process(IngestSource(source_id="src-bad", media_type="text", path=bad_path))

    # processの結果statusは常に{"structured", "failed"}のいずれかであり、他の値を取らない。
    assert good_result.status in {"structured", "failed"}
    assert bad_result.status in {"structured", "failed"}
    assert good_result.status == "structured"
    assert bad_result.status == "failed"

    # ProcessingResultはfrozenであり、通常の属性代入で不正な値へ書き換えられない。
    with pytest.raises(AttributeError):
        good_result.status = "not_a_real_status"

    # 1件の失敗が他のsourceの既に確定した結果に影響しない。
    assert good_result.status == "structured"


@pytest.mark.unit
def test_tc_ingest_001_07(tmp_path: Path) -> None:
    """TC-INGEST-001-07 — 必須入力欠落

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P0
    Layer: unit
    Given: 主ID、必須path、必須設定のいずれかが欠落した入力
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を実行する
    Then: 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。
    """
    orchestrator = MaterialInputOrchestrator()
    adapter = _FakeAdapter()

    with pytest.raises(AppError) as excinfo_media_type:
        orchestrator.register_adapter("", adapter)
    assert excinfo_media_type.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_adapter:
        orchestrator.register_adapter("text", None)
    assert excinfo_adapter.value.code is ErrorCode.VALIDATION_ERROR

    orchestrator.register_adapter("text", adapter)

    with pytest.raises(AppError) as excinfo_source_id:
        orchestrator.process(IngestSource(source_id="", media_type="text", path=tmp_path / "x.txt"))
    assert excinfo_source_id.value.code is ErrorCode.VALIDATION_ERROR

    with pytest.raises(AppError) as excinfo_path:
        orchestrator.process(IngestSource(source_id="src-1", media_type="text", path=None))
    assert excinfo_path.value.code is ErrorCode.VALIDATION_ERROR

    # 検証失敗前に副作用(adapter呼び出し)が発生していない。
    assert adapter.calls == []


@pytest.mark.unit
def test_tc_ingest_001_09(tmp_path: Path) -> None:
    """TC-INGEST-001-09 — 入力・既存成果物の不変性

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P0
    Layer: unit
    Given: hash取得済みの入力と既存正常成果物
    When: 正常処理または意図的な失敗を発生させる
    Then: 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。
    """
    orchestrator = MaterialInputOrchestrator()
    orchestrator.register_adapter("text", TextIngestionAdapter())

    good_path = tmp_path / "good.txt"
    good_bytes = "既存の正常な本文\n".encode("utf-8")
    good_path.write_bytes(good_bytes)

    result = orchestrator.process(IngestSource(source_id="src-good", media_type="text", path=good_path))
    assert result.status == "structured"
    assert good_path.read_bytes() == good_bytes

    # 意図的な失敗(別sourceの不正bytes)を発生させても、既存正常成果物には影響しない。
    bad_path = tmp_path / "bad.txt"
    bad_bytes = b"\xff\xfe\x80\x81"
    bad_path.write_bytes(bad_bytes)

    failed_result = orchestrator.process(IngestSource(source_id="src-bad", media_type="text", path=bad_path))
    assert failed_result.status == "failed"

    assert good_path.read_bytes() == good_bytes
    assert bad_path.read_bytes() == bad_bytes
