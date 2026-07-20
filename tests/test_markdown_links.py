"""Tests for TASK-REVIEW-001 §7: Markdown link integrity after docs/tasks and
docs/spec-proposals/task cleanup.

Contract: docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md(7節)
Production file exercised: scripts/check_markdown_links.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import check_markdown_links as link_checker  # noqa: E402

pytestmark = pytest.mark.mvp


@pytest.mark.static
def test_no_broken_relative_markdown_links() -> None:
    """README.md、docs/**/*.md、release/**/*.md、tests/**/*.mdに壊れた相対linkが0件であること。"""
    files = link_checker.find_markdown_files()
    assert files, "expected at least one Markdown file to check"

    all_broken: list[str] = []
    for markdown_file in files:
        broken = link_checker.check_file(markdown_file)
        for raw_target, reason in broken:
            rel = markdown_file.relative_to(_REPO_ROOT)
            all_broken.append(f"{rel} -> {raw_target} ({reason})")

    assert not all_broken, "broken relative Markdown links found:\n" + "\n".join(all_broken)


@pytest.mark.static
def test_link_checker_detects_a_genuinely_broken_link(tmp_path: Path) -> None:
    """検証scriptが実際に壊れたlinkを検出できることを、合成fileで確認する(検査自体の健全性)。"""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    sample = docs_dir / "sample.md"
    sample.write_text("[missing](./does-not-exist.md)\n[external](https://example.com)\n", encoding="utf-8")

    broken = link_checker.check_file(sample)
    assert len(broken) == 1
    assert broken[0][0] == "./does-not-exist.md"


@pytest.mark.unit
def test_no_dangling_references_to_deleted_task_and_proposal_paths() -> None:
    """docs/tasks/TASK-*・docs/spec-proposals/task/への参照が、削除済みfileを指していないこと
    (残す現役文書: TASK-COEIR-001、TASK-REVIEW-001、140_task-coeir-001-...md、index/readme類)。
    """
    import re

    allowed_patterns = (
        "TASK-COEIR-001",
        "TASK-REVIEW-001",
        "140_task-coeir-001",
        # 削除済み提案書への「旧〜、削除・吸収済み」という明示的な履歴説明としての言及
        # (実在するかのようなlinkではなく、どこへ吸収されたかを示す注記であるため許容する)。
        "2_file-persistence-operations.md",
        "3_voice-profile-default-values.md",
        "docs/spec-proposals/task/README.md",
        "docs/spec-proposals/task/INDEX.md",
        "docs/spec-proposals/task/IMPLEMENTATION_INDEX.md",
        "docs/spec-proposals/task/`",  # directory-name prose mentions, e.g. in README.md
        "docs/spec-proposals/task/\n",
    )

    pattern = re.compile(r"docs/tasks/TASK-[\w-]+\.md|docs/spec-proposals/task/[\w.-]+\.md")
    offenders: list[str] = []

    for markdown_file in link_checker.find_markdown_files():
        text = markdown_file.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            reference = match.group(0)
            if any(allowed in reference for allowed in allowed_patterns):
                continue
            # docs/notes/*.mdとdocs/tasks/STEP7_MANIFEST関連は完了履歴の記録として
            # 意図的に残しているため対象外(本testはdocs全体の"生きた"参照を検査する)。
            rel = markdown_file.relative_to(_REPO_ROOT).as_posix()
            if rel.startswith("docs/notes/"):
                continue
            offenders.append(f"{rel}: {reference}")

    assert not offenders, "dangling references to deleted task/proposal docs found:\n" + "\n".join(offenders)
