"""Test suite for TASK-RELEASE-001: Windows package・runtime同梱・license/privacy/backup.

Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
Cases in this file: TC-RELEASE-001-03, 06, 09, 12.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from script.audio.measurements import AudioMeasurementAdapter
from script.source_processing.ocr.client import OcrClient

pytestmark = pytest.mark.mvp

RELEASE_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "resources" / "release-manifest.json"


def _load_release_manifest() -> dict:
    return json.loads(RELEASE_MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.mark.static
def test_tc_release_001_03() -> None:
    """TC-RELEASE-001-03 — license manifest: third-party licenseと同梱/非同梱を正しく列挙する。"""
    manifest = _load_release_manifest()

    licenses = manifest["third_party_licenses"]
    assert len(licenses) >= 5
    names = {entry["name"] for entry in licenses}
    assert "Electron" in names
    assert "VOICEVOX Engine" in names
    assert "ffmpeg" in names
    assert "Tesseract OCR" in names

    for entry in licenses:
        assert entry["name"]
        assert entry["license"]
        assert isinstance(entry["bundled"], bool)

    bundled_names = {entry["name"] for entry in licenses if entry["bundled"]}
    not_bundled_names = {entry["name"] for entry in licenses if not entry["bundled"]}
    # Electron/Vueはelectron packageへ実際に同梱される。
    assert "Electron" in bundled_names
    # COEIROINK/VOICEVOXは対象外(4節)として明示的に非同梱。
    assert "VOICEVOX Engine" in not_bundled_names
    assert "COEIROINK" in not_bundled_names


@pytest.mark.unit
def test_tc_release_001_06() -> None:
    """TC-RELEASE-001-06 — ffmpeg/Tesseract存在確認: license manifestの非同梱宣言と、
    実際のruntime存在確認(TASK-AUDIO-002/TASK-OCR-001の既存adapterを再利用)を両立させる。
    """
    manifest = _load_release_manifest()
    licenses_by_name = {entry["name"]: entry for entry in manifest["third_party_licenses"]}
    assert licenses_by_name["ffmpeg"]["bundled"] is False
    assert licenses_by_name["Tesseract OCR"]["bundled"] is False

    def fake_runner_available(args, **kwargs):
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=f"{args[0]} version 1.0.0\n", stderr="")

    def fake_runner_unavailable(args, **kwargs):
        raise FileNotFoundError(f"{args[0]} not found")

    audio_adapter = AudioMeasurementAdapter(ffmpeg_cmd="ffmpeg", ffprobe_cmd="ffprobe", runner=fake_runner_available)
    audio_result = audio_adapter.check_runtime()
    assert audio_result.available is True

    ocr_client = OcrClient(tesseract_cmd="tesseract", runner=fake_runner_unavailable)
    ocr_health = ocr_client.check_runtime()
    assert ocr_health.available is False
    assert "not found" in ocr_health.error


@pytest.mark.unit
def test_tc_release_001_09() -> None:
    """TC-RELEASE-001-09 — 再実行時の決定性: 同じ入力を2回読んでも同じ論理結果を返す。"""
    first = _load_release_manifest()
    second = _load_release_manifest()
    assert first == second


@pytest.mark.integration_live
def test_tc_release_001_12(release_runtime_connectivity_gate) -> None:
    """TC-RELEASE-001-12 — 配布runtime群の実機能テスト

    Contract: docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md
    Priority: P1
    Layer: integration_live
    Given: `release_runtime_connectivity_gate`が成功済み
    When: 全runtime疎通成功後、最小backup/restore・最小worker起動・最小media probeを実行する。
    Then: 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。
    """
    import os

    from script.maintenance.backup import create_backup, restore_backup

    assert release_runtime_connectivity_gate["available"] is True

    tmp_root = Path(pytest.importorskip("tempfile").mkdtemp())
    data_root = tmp_root / "data_root"
    data_root.mkdir()
    (data_root / "app.db").write_bytes(b"live-smoke-data")

    manifest = create_backup(data_root, tmp_root / "backups")
    restore_result = restore_backup(tmp_root / "backups" / manifest.generation_id, tmp_root / "restored")
    assert restore_result.fully_restored is True

    python_executable = os.environ.get("WALKWISE_PYTHON_EXECUTABLE")
    if python_executable:
        completed = subprocess.run(
            [python_executable, "-m", "script.worker.cli"],
            input='{"job_id": "release-live-smoke-1", "job_type": "__unknown__", "parameters": {}}\n',
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert completed.returncode == 1
        last_line = [line for line in completed.stdout.splitlines() if line.strip()][-1]
        event = json.loads(last_line)
        assert event["event"] == "error"

    ffmpeg_cmd = os.environ.get("FFMPEG_PATH")
    ffprobe_cmd = os.environ.get("FFPROBE_PATH")
    if ffmpeg_cmd and ffprobe_cmd:
        media_probe = AudioMeasurementAdapter(ffmpeg_cmd=ffmpeg_cmd, ffprobe_cmd=ffprobe_cmd).check_runtime()
        assert media_probe.available is True
