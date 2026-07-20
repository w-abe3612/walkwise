"""STEP4 test implementation for TASK-DESKTOP-003: Desktop最短end-to-end導線 (Python側).

Contract: docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md
Release scope: MVP
"""

from __future__ import annotations

import pytest

from script.integration.mvp_flow import (
    BuildOutcome,
    MvpFlowDependencies,
    ProjectHandle,
    SourceHandle,
    run_mvp_flow,
)

pytestmark = pytest.mark.mvp


@pytest.mark.e2e
def test_tc_desktop_003_01() -> None:
    """TC-DESKTOP-003-01 — 最短導線: Project→text Source→承認→text Artifactまで完了する。"""
    deps = MvpFlowDependencies(
        create_project=lambda: ProjectHandle(project_id="proj-1"),
        register_source=lambda project: SourceHandle(source_id="src-1"),
        approve_gates=lambda project: True,
        run_worker=lambda: None,
        run_build=lambda project: BuildOutcome(
            build_request_id="br-1", job_id="job-1", artifacts=("text-artifact-1",)
        ),
    )

    result = run_mvp_flow(deps)

    assert result.project_id == "proj-1"
    assert result.source_id == "src-1"
    assert result.build_request_id == "br-1"
    assert result.job_id == "job-1"
    assert result.artifacts == ("text-artifact-1",)


@pytest.mark.e2e
def test_tc_desktop_003_03() -> None:
    """TC-DESKTOP-003-03 — 再起動保持: 再起動を模擬しても同じProject/Job/Artifactを表示する。"""
    store: dict[str, object] = {}

    def _create_project() -> ProjectHandle:
        store.setdefault("project", ProjectHandle(project_id="proj-1"))
        return store["project"]  # type: ignore[return-value]

    def _register_source(project: ProjectHandle) -> SourceHandle:
        store.setdefault("source", SourceHandle(source_id="src-1"))
        return store["source"]  # type: ignore[return-value]

    def _run_build(project: ProjectHandle) -> BuildOutcome:
        store.setdefault(
            "build", BuildOutcome(build_request_id="br-1", job_id="job-1", artifacts=("text-artifact-1",))
        )
        return store["build"]  # type: ignore[return-value]

    def _make_deps() -> MvpFlowDependencies:
        return MvpFlowDependencies(
            create_project=_create_project,
            register_source=_register_source,
            approve_gates=lambda project: True,
            run_worker=lambda: None,
            run_build=_run_build,
        )

    first = run_mvp_flow(_make_deps())
    # アプリ再起動を模擬: 新しいdependencies(新closure)を同じ永続store経由で結び直す。
    second = run_mvp_flow(_make_deps())

    assert second.project_id == first.project_id
    assert second.source_id == first.source_id
    assert second.job_id == first.job_id
    assert second.artifacts == first.artifacts


@pytest.mark.unit
def test_tc_desktop_003_05() -> None:
    """TC-DESKTOP-003-05 — 正常導線: 各工程が1回ずつ決定的に呼ばれ、結果が完全に揃う。"""
    calls = {"create": 0, "register": 0, "approve": 0, "worker": 0, "build": 0}

    def _create_project() -> ProjectHandle:
        calls["create"] += 1
        return ProjectHandle(project_id="proj-1")

    def _register_source(project: ProjectHandle) -> SourceHandle:
        calls["register"] += 1
        return SourceHandle(source_id="src-1")

    def _approve(project: ProjectHandle) -> bool:
        calls["approve"] += 1
        return True

    def _run_worker() -> None:
        calls["worker"] += 1

    def _run_build(project: ProjectHandle) -> BuildOutcome:
        calls["build"] += 1
        return BuildOutcome(build_request_id="br-1", job_id="job-1", artifacts=("a1", "a2"))

    deps = MvpFlowDependencies(
        create_project=_create_project,
        register_source=_register_source,
        approve_gates=_approve,
        run_worker=_run_worker,
        run_build=_run_build,
    )

    result = run_mvp_flow(deps)

    assert calls == {"create": 1, "register": 1, "approve": 1, "worker": 1, "build": 1}
    assert result.worker_retry_count == 0
    assert result.artifacts == ("a1", "a2")  # 複数artifact


@pytest.mark.unit
def test_tc_desktop_003_07() -> None:
    """TC-DESKTOP-003-07 — 再起動後永続化: 既に永続化済みのProjectをそのまま参照できる。"""
    existing_project = ProjectHandle(project_id="proj-existing")

    deps = MvpFlowDependencies(
        create_project=lambda: existing_project,
        register_source=lambda project: SourceHandle(source_id="src-existing"),
        approve_gates=lambda project: True,
        run_worker=lambda: None,
        run_build=lambda project: BuildOutcome(
            build_request_id="br-existing", job_id="job-existing", artifacts=("a1",)
        ),
    )

    result = run_mvp_flow(deps)

    assert result.project_id == existing_project.project_id  # 新規作成せず既存を参照


@pytest.mark.unit
def test_tc_desktop_003_09() -> None:
    """TC-DESKTOP-003-09 — 再実行時の決定性: 同じ入力で2回実行しても重複外部呼出しが起きない。"""
    call_count = {"build": 0}

    def _run_build(project: ProjectHandle) -> BuildOutcome:
        call_count["build"] += 1
        return BuildOutcome(build_request_id="br-1", job_id=f"job-{call_count['build']}", artifacts=("a1",))

    def _make_deps() -> MvpFlowDependencies:
        return MvpFlowDependencies(
            create_project=lambda: ProjectHandle(project_id="proj-1"),
            register_source=lambda project: SourceHandle(source_id="src-1"),
            approve_gates=lambda project: True,
            run_worker=lambda: None,
            run_build=_run_build,
        )

    first = run_mvp_flow(_make_deps())
    second = run_mvp_flow(_make_deps())

    assert first.project_id == second.project_id
    assert first.source_id == second.source_id
    assert first.build_request_id == second.build_request_id
    assert call_count["build"] == 2  # 実行ごとに1回ずつ(重複外部呼出しなし)


@pytest.mark.integration_smoke
def test_tc_desktop_003_11(desktop_connectivity_gate: dict[str, object]) -> None:
    """TC-DESKTOP-003-11 — Desktop統合runtimeの疎通確認。"""
    assert desktop_connectivity_gate["available"] is True
