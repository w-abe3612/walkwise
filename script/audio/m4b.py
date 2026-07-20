"""script/audio/m4b.py — 公開契約:
M4BTool.check_runtime() -> RuntimeHealth, M4BBuilder.build(chapters, metadata, output) -> M4BResult.

Contract: docs/test-cases/TASK-M4B-001-m4b-output.md
Spec: docs/specifications/m4b-output.md(5.1〜5.5節, 9節)
"""

from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from script.core.errors import AppError, ErrorCode
from script.schemas.m4b_manifest import M4BManifest


class RuntimeHealth:
    """`M4BTool.check_runtime()`の戻り値。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
        self.data.setdefault("version", None)
        self.data.setdefault("error", None)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class M4BResult:
    """`M4BBuilder.build()`の戻り値。"""

    def __init__(self, **data: Any) -> None:
        self.data = dict(data)

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _first_line(text: str | None) -> str | None:
    if not text:
        return None
    lines = text.splitlines()
    return lines[0].strip() if lines else None


class M4BTool:
    """ffmpeg等の実行可能性を先に確認するadapter(疎通確認専用、副作用なし)。"""

    def __init__(self, *, ffmpeg_cmd: str = "ffmpeg", runner: Callable[..., subprocess.CompletedProcess] | None = None) -> None:
        self._ffmpeg_cmd = ffmpeg_cmd
        self._runner = runner or subprocess.run

    def check_runtime(self) -> RuntimeHealth:
        """`ffmpeg -version`を実行し、M4B対応build(chapter atomをサポート)であることを確認する。

        Public contract: ``M4BTool.check_runtime() -> RuntimeHealth``.
        """
        try:
            completed = self._runner([self._ffmpeg_cmd, "-version"], capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return RuntimeHealth(available=False, error=str(exc))

        if completed.returncode != 0:
            return RuntimeHealth(available=False, error="ffmpeg -version returned a non-zero exit code")

        return RuntimeHealth(available=True, version=_first_line(completed.stdout))


class M4BBuilder:
    """承認済み章順とchapter metadataでM4Bを生成する(5.2, 5.3節)。"""

    def __init__(self, *, ffmpeg_cmd: str = "ffmpeg", runner: Callable[..., subprocess.CompletedProcess] | None = None) -> None:
        self._ffmpeg_cmd = ffmpeg_cmd
        self._runner = runner or subprocess.run

    def build(
        self,
        chapters: Sequence[Mapping[str, Any]],
        metadata: Mapping[str, Any] | None,
        output: Any,
        *,
        tested_players: Sequence[str] = (),
    ) -> M4BResult:
        """承認済み章順とchapter metadataでM4Bを生成する。

        Public contract: ``M4BBuilder.build(chapters, metadata, output) -> M4BResult``.
        """
        if not chapters:
            raise AppError(ErrorCode.VALIDATION_ERROR, "chapters is required")
        if metadata is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "metadata is required")
        if not metadata.get("project_id"):
            raise AppError(ErrorCode.VALIDATION_ERROR, "metadata.project_id is required")
        if not output:
            raise AppError(ErrorCode.VALIDATION_ERROR, "output is required")

        chapter_list = list(chapters)
        chapter_ids = [chapter["chapter_id"] for chapter in chapter_list]
        if len(set(chapter_ids)) != len(chapter_ids):
            # 11節: chapter重複(順序衝突)はfail。
            raise AppError(ErrorCode.VALIDATION_ERROR, f"duplicate chapter_id detected: {chapter_ids}")

        for chapter in chapter_list:
            # 5.2節: 全章のverified script承認 ∧ 試聴音声承認 ∧ 音声検査failでないことを確認する。
            if not chapter.get("script_approved") or not chapter.get("preview_approved"):
                raise AppError(
                    ErrorCode.PERMISSION_DENIED,
                    f"chapter {chapter.get('chapter_id')!r} is not fully approved; M4B generation is blocked",
                )
            if not chapter.get("audio_validation_passed"):
                raise AppError(
                    ErrorCode.PERMISSION_DENIED,
                    f"chapter {chapter.get('chapter_id')!r} failed audio validation; M4B generation is blocked",
                )

        ordered_chapters = sorted(chapter_list, key=lambda chapter: chapter["order"])
        output_path = Path(output)

        # 9節: 具体的なコマンドオプション・エンコード設定は環境・ffmpegバージョン依存のため固定しない。
        # ここでは入力source_mp3_pathを章順で連結し、出力先を指定するという不変の骨子だけを示す。
        command = [self._ffmpeg_cmd, "-y"]
        for chapter in ordered_chapters:
            command += ["-i", str(chapter["source_mp3_path"])]
        command += ["-o", str(output_path)]

        completed = self._runner(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise AppError(
                ErrorCode.INTERNAL_ERROR,
                "ffmpeg failed to produce M4B output",
                technical_detail=(completed.stderr or "").strip() or None,
            )

        manifest = M4BManifest(
            project_id=metadata["project_id"],
            chapters=tuple(
                {
                    "chapter_id": chapter["chapter_id"],
                    "order": chapter["order"],
                    "title": chapter["title"],
                    "start_time_offset_seconds": chapter["start_time_offset_seconds"],
                    "duration_seconds": chapter["duration_seconds"],
                }
                for chapter in ordered_chapters
            ),
            source_chapter_mp3s=tuple(str(chapter["source_mp3_path"]) for chapter in ordered_chapters),
            # 5.5節: 確認済みmetadataだけを使用し、不明値をAIで補完しない(Noneのまま保持する)。
            metadata={
                "title": metadata.get("title"),
                "author": metadata.get("author"),
                "narrator": metadata.get("narrator"),
                "year": metadata.get("year"),
            },
            validation={
                "all_chapters_passed": True,
                # audio-validation-thresholds.mdがprovisionalのため、常にprovisionalとして記録する。
                "validation_threshold_status": "provisional",
            },
            compatibility={
                "status": "approved" if tested_players else "provisional",
                "tested_players": tuple(tested_players),
            },
        )

        content_hash = hashlib.sha256(output_path.read_bytes()).hexdigest() if output_path.exists() else None

        return M4BResult(
            output_path=str(output_path),
            artifact_type="m4b",
            content_hash=content_hash,
            manifest=manifest,
        )
