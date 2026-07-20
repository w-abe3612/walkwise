"""Tests for TASK-REVIEW-001 §6: dump_all_files.py must not let build/cache
artifacts (dist, release, .pytest_cache, coverage, htmlcov, .vite, *.log,
.coverage) leak into the generated source dump.

Contract: docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md(6節)
Production file exercised: dumps/dump_all_files.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_MODULE_PATH = _REPO_ROOT / "dumps" / "dump_all_files.py"

pytestmark = pytest.mark.mvp


def _load_module():
    spec = importlib.util.spec_from_file_location("dump_all_files", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["dump_all_files"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_build_and_cache_artifacts_are_excluded(tmp_path: Path) -> None:
    """dist/build/release/.pytest_cache/coverage/htmlcov/.vite配下のfile、
    *.log、.coverageは、should_skip()によって常にskipされる。"""
    module = _load_module()

    root = tmp_path / "repo"
    root.mkdir()
    kept = root / "script" / "core.py"
    kept.parent.mkdir(parents=True)
    kept.write_text("x = 1\n", encoding="utf-8")

    skipped_paths = [
        root / "dist" / "main" / "electron_main.js",
        root / "release" / "win-unpacked" / "Walkwise.exe",
        root / ".pytest_cache" / "v" / "cache" / "nodeids",
        root / "coverage" / "lcov.info",
        root / "htmlcov" / "index.html",
        root / ".vite" / "manifest.json",
        root / "npm-debug.log",
        root / ".coverage",
    ]
    for path in skipped_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("artifact", encoding="utf-8")

    assert module.should_skip(kept, root) is False
    for path in skipped_paths:
        assert module.should_skip(path, root) is True, f"expected {path} to be skipped"


@pytest.mark.unit
def test_iter_files_never_yields_build_or_cache_artifacts(tmp_path: Path) -> None:
    """iter_files()自体の出力にも、build/cache生成物が一切含まれない(統合確認)。"""
    module = _load_module()

    root = tmp_path / "repo"
    (root / "script").mkdir(parents=True)
    (root / "script" / "core.py").write_text("x = 1\n", encoding="utf-8")
    (root / "dist" / "main").mkdir(parents=True)
    (root / "dist" / "main" / "electron_main.js").write_text("//", encoding="utf-8")
    (root / ".pytest_cache").mkdir()
    (root / ".pytest_cache" / "CACHEDIR.TAG").write_text("Signature", encoding="utf-8")

    files = list(module.iter_files(root))
    rel_paths = {f.relative_to(root).as_posix() for f in files}

    assert "script/core.py" in rel_paths
    assert not any(p.startswith("dist/") for p in rel_paths)
    assert not any(p.startswith(".pytest_cache/") for p in rel_paths)
