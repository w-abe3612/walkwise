from __future__ import annotations

from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
import shutil

# このファイルは dumps/dump_all_files.py に置く前提
DUMPS_DIR = Path(__file__).resolve().parent
BASE_DIR = DUMPS_DIR.parent
OUTPUT_DIR = DUMPS_DIR / "output"

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")
DUMP_FILENAME = f"audio_book_creation_dump_{TIMESTAMP}.txt"
TEMPLATE_FILENAME = "code_fix_prompt_template.txt"

DUMP_PATH = OUTPUT_DIR / DUMP_FILENAME
TEMPLATE_PATH = OUTPUT_DIR / TEMPLATE_FILENAME

SKIP_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    # TASK-REVIEW-001: build/cache生成物がsource dumpへ混入するのを防ぐ。
    ".pytest_cache",
    "dist",
    "build",
    "release",
    "coverage",
    "htmlcov",
    ".vite",
}

SKIP_FILE_NAMES = {
    ".DS_Store",
    ".env",
}

SKIP_GLOB_PATTERNS = {
    "*.png",
    "*.mp3",
    "*.wav",
    "*.pyc",
    # TASK-REVIEW-001: cache/log生成物を除外する。
    ".coverage",
    "*.log",
}

# dumps/output だけは再帰対象から除外する
SKIP_RELATIVE_PATH_PREFIXES = {
    "dumps/output",
}


def clear_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for child in output_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)


def is_skipped_relative_path(rel_str: str) -> bool:
    for prefix in SKIP_RELATIVE_PATH_PREFIXES:
        if rel_str == prefix or rel_str.startswith(prefix + "/"):
            return True
    return False


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    rel_str = rel.as_posix()

    if is_skipped_relative_path(rel_str):
        return True

    if any(part in SKIP_DIR_NAMES for part in rel.parts):
        return True

    if path.is_file() and path.name in SKIP_FILE_NAMES:
        return True

    for pattern in SKIP_GLOB_PATTERNS:
        if fnmatch(rel_str, pattern) or fnmatch(path.name, pattern):
            return True

    return False


def iter_paths(root: Path):
    for path in sorted(root.rglob("*")):
        if should_skip(path, root):
            continue
        yield path


def iter_files(root: Path):
    for path in iter_paths(root):
        if path.is_file():
            yield path


def dump_tree(root: Path) -> str:
    lines = [f"{root.name}/"]

    for path in iter_paths(root):
        rel = path.relative_to(root)
        indent = "    " * (len(rel.parts) - 1)
        suffix = "/" if path.is_dir() else ""
        lines.append(f"{indent}{rel.name}{suffix}")

    return "\n".join(lines)


def dump_path_list(root: Path) -> str:
    lines = [f"{root.name}/"]

    for path in iter_paths(root):
        rel = path.relative_to(root)
        rel_str = rel.as_posix()
        suffix = "/" if path.is_dir() else ""
        lines.append(f"{root.name}/{rel_str}{suffix}")

    return "\n".join(lines)


def dump_file(path: Path, root: Path) -> str:
    rel = path.relative_to(root)

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = "<binary or non-utf8 file>"
    except Exception as e:
        content = f"<read error: {e}>"

    return (
        f"\n{'=' * 80}\n"
        f"FILE: {rel.as_posix()}\n"
        f"{'=' * 80}\n"
        f"{content}\n"
    )


def build_template_text(dump_filename: str) -> str:
    return f"""下記の現在ソースコードを参照して、指定内容に沿ってソースコードを修正してください。

【現在のソースコード】
{dump_filename}

【前提】
- 現在のプロジェクト構成・既存コード・ファイル配置は、上記ダンプファイルの内容を正としてください。
- 修正対象ファイルが複数ある場合は、関連するファイルも含めて整合性が取れるように修正してください。
- 既存の処理意図はできるだけ維持してください。

【今回の修正依頼】
ここに、今回やりたい修正内容を書いてください。
例：
- dump_all_files.py の出力先を dumps/output に変更したい
- utility 配下へ移動したファイル構成に合わせて実行パスを直したい
- capture_ocr_tts.py に CLI 引数を追加したい

【修正時の必須ルール】
- 必要な範囲だけ修正してください。
- 修正後のコードは、そのままコピペで使える完成形で出力してください。
- 変更が複数ファイルにまたがる場合は、ファイルごとに分けて全文を出力してください。
- import、定数、パス、実行コマンドも必要に応じて修正してください。
- 実行方法が変わる場合は、最後に実行コマンド例も記載してください。
- 不明点があっても、現在の構成から最も自然な形で補完して修正してください。
- 可能なら、既存コードの問題点や注意点も簡潔に補足してください。

◆記載
下記の依頼文を、意味を変えずに、より明確で実行しやすい表現へ整形してください。

【出力ルール】
1. 修正後の依頼文は、全文をコードブロックに入れて出力してください。
2. 修正内容の説明もあわせて記載してください。
3. 修正内容は、必ず以下の形式で示してください。
4. ダウンロード形式にはせず、このチャット上にそのまま表示してください。
5. トリプルバッククォートはコードブロックの開始と終了を示すためのもので、コードブロック文中の出力には含めないでください。

// 削除
----------------------
（削除した表現）
----------------------

// 追加
+++++++++++++++++++++++
（追加した表現）
+++++++++++++++++++++++

【出力してほしい内容】
1. 修正後のソースコード全文
2. 修正した理由
3. 実行コマンド
4. 変更点の差分を以下の形式で記載

// 削除
----------------------
（削除した表現）
----------------------

// 追加
+++++++++++++++++++++++
（追加した表現）
+++++++++++++++++++++++
"""


def main() -> None:
    clear_output_dir(OUTPUT_DIR)

    sections: list[str] = []
    sections.append("# FILE TREE\n")
    sections.append(dump_tree(BASE_DIR))
    sections.append("\n\n# PATH LIST\n")
    sections.append(dump_path_list(BASE_DIR))
    sections.append("\n\n# FILE CONTENTS\n")

    for file_path in iter_files(BASE_DIR):
        sections.append(dump_file(file_path, BASE_DIR))

    DUMP_PATH.write_text("".join(sections), encoding="utf-8")
    TEMPLATE_PATH.write_text(build_template_text(DUMP_PATH.name), encoding="utf-8")

    print(f"dump written to     : {DUMP_PATH}")
    print(f"template written to : {TEMPLATE_PATH}")


if __name__ == "__main__":
    main()
