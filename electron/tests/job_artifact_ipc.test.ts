/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-004: cancel confirmation, latest artifact display,
 * state-transition safety, technical detail collapse, re-execution determinism.
 * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import type { ArtifactServiceLike } from "../main/ipc/artifacts";
import { registerArtifactIpcHandlers, type IpcMainLike as ArtifactIpcMainLike } from "../main/ipc/artifacts";
import type { ApprovalGateCheckerLike, BuildServiceLike } from "../main/ipc/builds";
import { registerBuildIpcHandlers } from "../main/ipc/builds";
import type { IpcMainInvokeEventLike, JobServiceLike, JobSummary } from "../main/ipc/jobs";
import { registerJobIpcHandlers, type IpcMainLike as JobIpcMainLike } from "../main/ipc/jobs";
import JobsAndArtifacts from "../renderer/screens/JobsAndArtifacts.vue";
import type { ArtifactItem, JobItem } from "../renderer/screens/JobsAndArtifacts.types";

function fakeIpcMain<T extends { handle: unknown }>(): {
  ipcMain: T;
  handlers: Map<string, (event: unknown, ...args: unknown[]) => unknown>;
} {
  const handlers = new Map<string, (event: unknown, ...args: unknown[]) => unknown>();
  const ipcMain = {
    handle: vi.fn((channel: string, listener: (event: unknown, ...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  } as unknown as T;
  return { ipcMain, handlers };
}

function fakeJobService(overrides: Partial<JobServiceLike> = {}): JobServiceLike {
  return {
    get: vi.fn().mockResolvedValue({
      jobId: "job-1",
      buildRequestId: "br-1",
      jobType: "audio_packaging",
      status: "running",
    } satisfies JobSummary),
    subscribeProgress: vi.fn().mockReturnValue(() => {}),
    cancel: vi.fn().mockResolvedValue({
      jobId: "job-1",
      buildRequestId: "br-1",
      jobType: "audio_packaging",
      status: "cancel_requested",
    }),
    retry: vi.fn(),
    ...overrides,
  };
}

describe("TASK-UI-004 Job進捗・cancel/retry・成果物画面", () => {
  test("TC-UI-004-01: cancel確認 [unit/P0]", async () => {
    const cancelJob = vi.fn().mockResolvedValue(undefined);
    const job: JobItem = { jobId: "job-1", jobType: "audio_packaging", status: "running" };
    const wrapper = mount(JobsAndArtifacts, {
      props: { jobs: [job], artifacts: [], cancelJob, retryJob: vi.fn(), openFolder: vi.fn() },
    });

    // 1回目のクリックでは確認ダイアログを表示するだけでIPCは呼ばない
    await wrapper.get('[data-testid="cancel-button"]').trigger("click");
    expect(cancelJob).not.toHaveBeenCalled();
    expect(wrapper.find('[data-testid="cancel-confirm-dialog"]').exists()).toBe(true);

    // 確認後にだけIPCを呼ぶ
    await wrapper.get('[data-testid="cancel-confirm-button"]').trigger("click");
    expect(cancelJob).toHaveBeenCalledTimes(1);
    expect(cancelJob).toHaveBeenCalledWith("job-1");
  });

  test("TC-UI-004-03: 最新Artifact [unit/P0]", () => {
    const artifacts: ArtifactItem[] = [
      { artifactId: "a1", artifactType: "mp3_chapter", versionNumber: 1, createdAt: "2026-07-18T00:00:00+09:00" },
      { artifactId: "a2", artifactType: "mp3_chapter", versionNumber: 2, createdAt: "2026-07-19T00:00:00+09:00" },
      { artifactId: "a3", artifactType: "text_verified_script", versionNumber: 1, createdAt: "2026-07-18T00:00:00+09:00" },
    ];
    const wrapper = mount(JobsAndArtifacts, {
      props: { jobs: [], artifacts, cancelJob: vi.fn(), retryJob: vi.fn(), openFolder: vi.fn() },
    });

    const items = wrapper.findAll('[data-testid="artifact-item"]');
    expect(items).toHaveLength(2); // mp3_chapterは最新版(v2)のみ、text_verified_scriptは1件
    expect(wrapper.text()).toContain("mp3_chapter v2");
    expect(wrapper.text()).not.toContain("mp3_chapter v1");
    // 旧versionは破壊されず、propsの入力データとしてはそのまま残っている
    expect(artifacts.find((a) => a.artifactId === "a1")).toBeDefined();
  });

  test("TC-UI-004-05: job:get/subscribe/cancel/start retry [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain<JobIpcMainLike>();
    const jobService = fakeJobService();
    registerJobIpcHandlers({ ipcMain, jobService });
    // job:start(再試行payload)は electron/main/ipc/builds.ts が同一ipcMain上で処理する
    // (TASK-RELEASE-002でjob:start channel重複を解消、両モジュールが1つのipcMainを共有できることを確認する)。
    const buildService: BuildServiceLike = { createBuildRequest: vi.fn(), startJob: vi.fn() };
    const approvalGateChecker: ApprovalGateCheckerLike = { isSatisfied: vi.fn().mockResolvedValue(true) };
    registerBuildIpcHandlers({ ipcMain, buildService, approvalGateChecker, jobService });

    await handlers.get("job:get")!({}, "job-1");
    expect(jobService.get).toHaveBeenCalledWith("job-1");

    const fakeEvent: IpcMainInvokeEventLike = { sender: { send: vi.fn() } };
    handlers.get("job:subscribe-progress")!(fakeEvent, "job-1");
    const progressListener = (jobService.subscribeProgress as ReturnType<typeof vi.fn>).mock.calls[0][1] as (
      event: unknown,
    ) => void;
    progressListener({ jobId: "job-1", current: 1, total: 2 });
    expect(fakeEvent.sender.send).toHaveBeenCalledWith("job:progress-event", { jobId: "job-1", current: 1, total: 2 });

    await handlers.get("job:cancel")!({}, "job-1"); // status: running -> cancellable
    expect(jobService.cancel).toHaveBeenCalledWith("job-1");

    (jobService.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      jobId: "job-2",
      buildRequestId: "br-1",
      jobType: "audio_packaging",
      status: "failed",
    });
    (jobService.retry as ReturnType<typeof vi.fn>).mockResolvedValue({
      jobId: "job-3",
      buildRequestId: "br-1",
      jobType: "audio_packaging",
      status: "queued",
    });
    await handlers.get("job:start")!({}, { parentJobId: "job-2" });
    expect(jobService.retry).toHaveBeenCalledWith("job-2");
  });

  test("TC-UI-004-07: 技術detail折畳み [unit/P1]", () => {
    const job: JobItem = {
      jobId: "job-1",
      jobType: "audio_packaging",
      status: "failed",
      technicalDetail: "Traceback (most recent call last): ...",
    };
    const wrapper = mount(JobsAndArtifacts, {
      props: { jobs: [job], artifacts: [], cancelJob: vi.fn(), retryJob: vi.fn(), openFolder: vi.fn() },
    });

    const details = wrapper.get('[data-testid="technical-detail"]');
    expect(details.element.tagName.toLowerCase()).toBe("details");
    expect((details.element as HTMLDetailsElement).open).toBe(false); // 既定で折り畳まれている
    expect(details.text()).toContain("Traceback");
  });

  test("TC-UI-004-09: 再実行時の決定性 [unit/P1]", async () => {
    const jobService = fakeJobService();

    const run = async () => {
      const { ipcMain, handlers } = fakeIpcMain<JobIpcMainLike>();
      registerJobIpcHandlers({ ipcMain, jobService });
      return handlers.get("job:get")!({}, "job-1");
    };

    const first = await run();
    const second = await run();

    expect(first).toEqual(second);
    expect(jobService.get).toHaveBeenCalledTimes(2);
  });
});
