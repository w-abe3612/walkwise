"""script/integration/mvp_flow.py — 公開契約: run_mvp_flow(dependencies) -> MvpFlowResult.

Contract: docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md
Spec: docs/specifications/19-application-scope-and-mvp.md,
      docs/specifications/audiobook-creation-pipeline.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from script.core.errors import AppError, ErrorCode


class WorkerRetryableError(RuntimeError):
    """run_workerがこの例外を送出した場合のみrun_mvp_flowは上限回数内で再試行する。"""


@dataclass(frozen=True)
class ProjectHandle:
    project_id: str

    def __post_init__(self) -> None:
        if not self.project_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "project_id is required")


@dataclass(frozen=True)
class SourceHandle:
    source_id: str

    def __post_init__(self) -> None:
        if not self.source_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "source_id is required")


@dataclass(frozen=True)
class BuildOutcome:
    build_request_id: str
    job_id: str
    artifacts: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.build_request_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "build_request_id is required")
        if not self.job_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "job_id is required")


@dataclass(frozen=True)
class MvpFlowDependencies:
    """Project作成からArtifactまでの各工程を注入するcallable群。

    実IPC/DB/file/workerとの結線は呼び出し側(実サービスまたはfake)が担い、
    本モジュールは工程の順序・承認gate・再試行上限だけを制御する。
    """

    create_project: Callable[[], ProjectHandle]
    register_source: Callable[[ProjectHandle], SourceHandle]
    approve_gates: Callable[[ProjectHandle], bool]
    run_worker: Callable[[], None]
    run_build: Callable[[ProjectHandle], BuildOutcome]
    max_worker_retries: int = 1


@dataclass(frozen=True)
class MvpFlowResult:
    project_id: str
    source_id: str
    build_request_id: str
    job_id: str
    artifacts: tuple[str, ...]
    worker_retry_count: int


_REQUIRED_DEPENDENCY_FIELDS = ("create_project", "register_source", "approve_gates", "run_worker", "run_build")


def run_mvp_flow(dependencies: MvpFlowDependencies) -> MvpFlowResult:
    """Project作成からArtifactまでの縦切りをmock依存で実行する。"""
    if dependencies is None:
        raise AppError(ErrorCode.VALIDATION_ERROR, "dependencies is required")
    for field_name in _REQUIRED_DEPENDENCY_FIELDS:
        if getattr(dependencies, field_name, None) is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, f"{field_name} is required")

    project = dependencies.create_project()
    source = dependencies.register_source(project)

    if not dependencies.approve_gates(project):
        # 承認gate未充足: worker/buildを一切開始しない。
        raise AppError(ErrorCode.PERMISSION_DENIED, "required approvals are not satisfied")

    retry_count = 0
    while True:
        try:
            dependencies.run_worker()
            break
        except WorkerRetryableError:
            retry_count += 1
            if retry_count > dependencies.max_worker_retries:
                raise

    outcome = dependencies.run_build(project)

    return MvpFlowResult(
        project_id=project.project_id,
        source_id=source.source_id,
        build_request_id=outcome.build_request_id,
        job_id=outcome.job_id,
        artifacts=outcome.artifacts,
        worker_retry_count=retry_count,
    )
