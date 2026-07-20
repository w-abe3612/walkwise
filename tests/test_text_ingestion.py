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
from script.source_processing.text_ingestion import StructuredSource, TextIngestionAdapter

pytestmark = pytest.mark.mvp


@pytest.mark.unit
def test_tc_ingest_001_02(tmp_path: Path) -> None:
    """TC-INGEST-001-02 — 未知media

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P0
    Layer: unit
    Given: epubまたはvideo
    When: processする
    Then: MVPではunsupported_media_typeで停止する
    """
    orchestrator = MaterialInputOrchestrator()
    orchestrator.register_adapter("text", TextIngestionAdapter())

    epub_path = tmp_path / "book.epub"
    epub_path.write_bytes(b"PK\x03\x04")
    video_path = tmp_path / "lecture.mp4"
    video_path.write_bytes(b"\x00\x00\x00\x18ftyp")

    with pytest.raises(AppError) as excinfo_epub:
        orchestrator.process(IngestSource(source_id="src-epub", media_type="epub", path=epub_path))
    assert excinfo_epub.value.code is ErrorCode.VALIDATION_ERROR
    assert "unsupported_media_type" in excinfo_epub.value.message

    with pytest.raises(AppError) as excinfo_video:
        orchestrator.process(IngestSource(source_id="src-video", media_type="video", path=video_path))
    assert excinfo_video.value.code is ErrorCode.VALIDATION_ERROR
    assert "unsupported_media_type" in excinfo_video.value.message

    # 未登録のmedia typeも同じerrorで停止する。
    with pytest.raises(AppError) as excinfo_unregistered:
        orchestrator.process(IngestSource(source_id="src-unknown", media_type="spreadsheet", path=epub_path))
    assert excinfo_unregistered.value.code is ErrorCode.VALIDATION_ERROR
    assert "unsupported_media_type" in excinfo_unregistered.value.message


@pytest.mark.unit
def test_tc_ingest_001_04(tmp_path: Path) -> None:
    """TC-INGEST-001-04 — original/extracted/normalized/structured handoff

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「original/extracted/normalized/structured handoff」を実行する
    Then: 「original/extracted/normalized/structured handoff」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。
    """
    path = tmp_path / "material.txt"
    path.write_bytes("行末に空白    \r\n次の行\r\n".encode("utf-8"))

    adapter = TextIngestionAdapter()
    result = adapter.process(path, {})

    assert isinstance(result, StructuredSource)
    assert result.original_path == str(path)
    assert result.extracted_text == "行末に空白    \r\n次の行\r\n"
    # normalized: 改行統一 + 行末空白除去。structuredはtext素材ではnormalizedと同じ内容。
    assert result.normalized_text == "行末に空白\n次の行\n"
    assert result.structured_text == result.normalized_text
    # 原本(original_path先のファイル)は変更されない。
    assert path.read_bytes().decode("utf-8") == "行末に空白    \r\n次の行\r\n"


@pytest.mark.unit
def test_tc_ingest_001_06(tmp_path: Path) -> None:
    """TC-INGEST-001-06 — Job進捗hook

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 承認済み仕様に適合する最小入力と、必要な依存をmockした状態
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を通じて「Job進捗hook」を実行する
    Then: current/totalとmessageを単調・順序どおりに通知し、完了後に進捗を逆行させない。
    """
    events: list[tuple[int, int, str]] = []

    def hook(current: int, total: int, message: str) -> None:
        events.append((current, total, message))

    orchestrator = MaterialInputOrchestrator(progress_hook=hook)
    orchestrator.register_adapter("text", TextIngestionAdapter())

    path = tmp_path / "material.txt"
    path.write_text("hello", encoding="utf-8")

    result = orchestrator.process(IngestSource(source_id="src-1", media_type="text", path=path))
    assert result.status == "structured"

    assert len(events) == 2
    currents = [event[0] for event in events]
    totals = {event[1] for event in events}
    assert currents == sorted(currents)
    assert currents[0] == 0
    assert currents[-1] == totals.pop()
    for _, _, message in events:
        assert isinstance(message, str) and message


@pytest.mark.unit
def test_tc_ingest_001_08(tmp_path: Path) -> None:
    """TC-INGEST-001-08 — 再実行時の決定性

    Contract: docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md
    Priority: P1
    Layer: unit
    Given: 同じ入力、同じ設定、同じ依存応答
    When: `MaterialInputOrchestrator.register_adapter(media_type, adapter) -> None`を2回実行する
    Then: 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。
    """
    path = tmp_path / "material.txt"
    path.write_text("同じ入力\n", encoding="utf-8")

    adapter = TextIngestionAdapter()
    first = adapter.process(path, {})
    second = adapter.process(path, {})

    assert first == second

    orchestrator_a = MaterialInputOrchestrator()
    orchestrator_a.register_adapter("text", TextIngestionAdapter())
    orchestrator_b = MaterialInputOrchestrator()
    orchestrator_b.register_adapter("text", TextIngestionAdapter())

    result_a = orchestrator_a.process(IngestSource(source_id="src-1", media_type="text", path=path))
    result_b = orchestrator_b.process(IngestSource(source_id="src-1", media_type="text", path=path))
    assert result_a == result_b
