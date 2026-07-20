/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-004: retry eligibility, retry non-duplication,
 * stale note display, required-input-missing at the IPC layer.
 * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import { registerArtifactIpcHandlers, type IpcMainLike as ArtifactIpcMainLike } from "../../main/ipc/artifacts";
import type { ApprovalGateCheckerLike, BuildServiceLike } from "../../main/ipc/builds";
import { registerBuildIpcHandlers } from "../../main/ipc/builds";
import { registerJobIpcHandlers, type IpcMainLike as JobIpcMainLike, type JobServiceLike } from "../../main/ipc/jobs";
import JobsAndArtifacts from "../screens/JobsAndArtifacts.vue";
import type { JobItem } from "../screens/JobsAndArtifacts.types";

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

describe("TASK-UI-004 Job進捗・cancel/retry・成果物画面", () => {
  test("TC-UI-004-02: retry条件 [unit/P0]", () => {
    const jobs: JobItem[] = [
      { jobId: "j1", jobType: "audio_packaging", status: "failed" },
      { jobId: "j2", jobType: "audio_packaging", status: "cancelled" },
      { jobId: "j3", jobType: "audio_packaging", status: "running" },
      { jobId: "j4", jobType: "audio_packaging", status: "succeeded" },
    ];
    const wrapper = mount(JobsAndArtifacts, {
      props: { jobs, artifacts: [], cancelJob: vi.fn(), retryJob: vi.fn(), openFolder: vi.fn() },
    });

    const retryButtons = wrapper.findAll('[data-testid="retry-button"]');
    expect((retryButtons[0].element as HTMLButtonElement).disabled).toBe(false); // failed
    expect((retryButtons[1].element as HTMLButtonElement).disabled).toBe(false); // cancelled
    expect((retryButtons[2].element as HTMLButtonElement).disabled).toBe(true); // running
    expect((retryButtons[3].element as HTMLButtonElement).disabled).toBe(true); // succeeded
  });

  test("TC-UI-004-04: job:get/subscribe/cancel/start retry [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain<JobIpcMainLike>();
    const jobService: JobServiceLike = {
      list: vi.fn().mockResolvedValue([]),
      get: vi.fn().mockResolvedValue({ jobId: "job-1", buildRequestId: "br-1", jobType: "t", status: "running" }),
      subscribeProgress: vi.fn().mockReturnValue(() => {}),
      cancel: vi.fn(),
      retry: vi.fn().mockResolvedValue({ jobId: "job-2", buildRequestId: "br-1", jobType: "t", status: "queued" }),
    };
    registerJobIpcHandlers({ ipcMain, jobService });
    // job:start(再試行payload)は electron/main/ipc/builds.ts が同一ipcMain上で処理する
    // (TASK-RELEASE-002でjob:start channel重複を解消)。
    const buildService: BuildServiceLike = { createBuildRequest: vi.fn(), startJob: vi.fn() };
    const approvalGateChecker: ApprovalGateCheckerLike = { isSatisfied: vi.fn().mockResolvedValue(true) };
    registerBuildIpcHandlers({ ipcMain, buildService, approvalGateChecker, jobService });

    // 不正遷移(running状態のJobを再試行しようとする)は永続状態を変更しない
    await expect(handlers.get("job:start")!({}, { parentJobId: "job-1" })).rejects.toThrow(/not retryable/);
    expect(jobService.retry).not.toHaveBeenCalled();

    // failedからの再試行は1回だけ委譲され、同一requestで重複登録しない
    (jobService.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      jobId: "job-1",
      buildRequestId: "br-1",
      jobType: "t",
      status: "failed",
    });
    await handlers.get("job:start")!({}, { parentJobId: "job-1" });
    expect(jobService.retry).toHaveBeenCalledTimes(1);
    expect(jobService.retry).toHaveBeenCalledWith("job-1");
  });

  test("TC-UI-004-06: stale注記 [unit/P1]", () => {
    const staleJob: JobItem = { jobId: "j1", jobType: "audio_packaging", status: "failed", stale: true };
    const normalJob: JobItem = { jobId: "j2", jobType: "audio_packaging", status: "failed", stale: false };
    const wrapper = mount(JobsAndArtifacts, {
      props: { jobs: [staleJob, normalJob], artifacts: [], cancelJob: vi.fn(), retryJob: vi.fn(), openFolder: vi.fn() },
    });

    expect(wrapper.findAll('[data-testid="stale-note"]')).toHaveLength(1);
    expect(wrapper.text()).toContain("前回異常終了しました");
  });

  test("TC-UI-004-08: 必須入力欠落 [unit/P0]", () => {
    const { ipcMain: jobIpcMain } = fakeIpcMain<JobIpcMainLike>();
    expect(() => registerJobIpcHandlers(undefined as never)).toThrow();
    expect(() => registerJobIpcHandlers({ ipcMain: jobIpcMain, jobService: undefined as never })).toThrow();
    expect(jobIpcMain.handle).not.toHaveBeenCalled();

    const { ipcMain: artifactIpcMain } = fakeIpcMain<ArtifactIpcMainLike>();
    expect(() => registerArtifactIpcHandlers(undefined as never)).toThrow();
    expect(() =>
      registerArtifactIpcHandlers({ ipcMain: artifactIpcMain, artifactService: undefined as never }),
    ).toThrow();
    expect(artifactIpcMain.handle).not.toHaveBeenCalled();
  });
});
