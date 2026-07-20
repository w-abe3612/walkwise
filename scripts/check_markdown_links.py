"""scripts/check_markdown_links.py — 公開契約: main() -> int(exit code).

TASK-REVIEW-001 7節: docs/tasks・docs/spec-proposals/taskの完了済みfile削除後、
削除済みpathへのMarkdown相対リンクが残っていないことを機械的に検証する。

対象: README.md, docs/**/*.md, release/**/*.md, tests/**/*.md
除外: 外部URL(http(s)://)、code fence内、`#anchor`のみのリンク、mailto:等。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET_GLOBS = (
    "README.md",
    "docs/**/*.md",
    "release/**/*.md",
    "tests/**/*.md",
)

# [text](path) 、code fence行・inline codeは事前に取り除いてから検出する。
_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
_CODE_FENCE_PATTERN = re.compile(r"^```")


def _strip_code_fences(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    in_fence = False
    for line in lines:
        if _CODE_FENCE_PATTERN.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        kept.append(line)
    return "\n".join(kept)


def _strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`]*`", "", text)


def _is_external_or_special(raw_target: str) -> bool:
    target = raw_target.strip()
    if not target:
        return True
    if target.startswith("#"):
        return True
    for prefix in ("http://", "https://", "mailto:", "data:"):
        if target.startswith(prefix):
            return True
    return False


def find_markdown_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in TARGET_GLOBS:
        files.update(REPO_ROOT.glob(pattern))
    return sorted(f for f in files if f.is_file())


def extract_links(markdown_text: str) -> list[str]:
    cleaned = _strip_code_fences(markdown_text)
    cleaned = _strip_inline_code(cleaned)
    return [match.group(1) for match in _LINK_PATTERN.finditer(cleaned)]


def resolve_target(markdown_file: Path, raw_target: str) -> Path:
    target = raw_target.strip()
    # `path#anchor` の anchor部分は対象外(fileの存在だけを検証する)。
    target = target.split("#", 1)[0]
    target = unquote(target)
    if not target:
        raise ValueError("empty target after stripping anchor")
    return (markdown_file.parent / target).resolve()


def check_file(markdown_file: Path) -> list[tuple[str, str]]:
    """戻り値: (raw_target, reason)のリスト(壊れているlinkだけ)。"""
    text = markdown_file.read_text(encoding="utf-8")
    broken: list[tuple[str, str]] = []
    for raw_target in extract_links(text):
        if _is_external_or_special(raw_target):
            continue
        try:
            resolved = resolve_target(markdown_file, raw_target)
        except ValueError:
            continue
        if not resolved.exists():
            broken.append((raw_target, f"resolved to missing path: {resolved}"))
    return broken


def main() -> int:
    files = find_markdown_files()
    total_links_checked = 0
    total_broken = 0
    for markdown_file in files:
        text = markdown_file.read_text(encoding="utf-8")
        links = [t for t in extract_links(text) if not _is_external_or_special(t)]
        total_links_checked += len(links)
        broken = check_file(markdown_file)
        if broken:
            total_broken += len(broken)
            rel = markdown_file.relative_to(REPO_ROOT)
            for raw_target, reason in broken:
                print(f"BROKEN LINK: {rel} -> {raw_target} ({reason})")

    print(f"\nchecked {len(files)} Markdown files, {total_links_checked} relative links, {total_broken} broken")
    return 1 if total_broken else 0


if __name__ == "__main__":
    sys.exit(main())
