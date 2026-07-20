/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-003: mp3 speaker requirement, engine health/list,
 * approval-gate error path, required-input-missing at the IPC layer.
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import {
  registerBuildIpcHandlers,
  type ApprovalGateCheckerLike,
  type BuildServiceLike,
  type IpcMainLike as BuildIpcMainLike,
} from "../../main/ipc/builds";
import { registerVoiceIpcHandlers, type IpcMainLike as VoiceIpcMainLike, type VoiceServiceLike } from "../../main/ipc/voice";
import BuildSettings from "../screens/BuildSettings.vue";

function fakeIpcMain<T extends { handle: unknown }>(): {
  ipcMain: T;
  handlers: Map<string, (...args: unknown[]) => unknown>;
} {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  } as unknown as T;
  return { ipcMain, handlers };
}

describe("TASK-UI-003 出力・声設定・試聴画面", () => {
  test("TC-UI-003-02: mp3条件 [unit/P0]", async () => {
    const wrapper = mount(BuildSettings, {
      props: {
        engineHealth: { available: true },
        speakers: [{ speakerId: "1", displayName: "四国めたん" }],
        preview: vi.fn(),
        createBuildRequest: vi.fn(),
        startJob: vi.fn(),
      },
    });

    await wrapper.get('[data-testid="format-mp3"]').trigger("change");
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(true);

    await wrapper.get('[data-testid="speaker-select"]').setValue("1");
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(false);
  });

  test("TC-UI-003-04: engine health/list [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain<VoiceIpcMainLike>();
    const voiceService: VoiceServiceLike = {
      checkHealth: vi.fn().mockResolvedValue({ engine: "voicevox", available: false, detail: "unreachable" }),
      listSpeakers: vi.fn(),
      preview: vi.fn(),
    };
    registerVoiceIpcHandlers({ ipcMain, voiceService });

    const result = (await handlers.get("voice:list-engines")!({})) as { health: unknown; speakers: unknown[] };

    // engine未接続でも例外にせず、空一覧を正常結果として返す
    expect(result.speakers).toEqual([]);
    expect(voiceService.listSpeakers).not.toHaveBeenCalled();
  });

  test("TC-UI-003-06: approval gate error導線 [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain<BuildIpcMainLike>();
    const buildService: BuildServiceLike = {
      createBuildRequest: vi.fn(),
      startJob: vi.fn(),
    };
    const approvalGateChecker: ApprovalGateCheckerLike = { isSatisfied: vi.fn().mockResolvedValue(false) };
    registerBuildIpcHandlers({ ipcMain, buildService, approvalGateChecker });

    await expect(handlers.get("job:start")!({}, "br-1")).rejects.toThrow(/approval gate not satisfied/);
    expect(buildService.startJob).not.toHaveBeenCalled();

    (approvalGateChecker.isSatisfied as ReturnType<typeof vi.fn>).mockResolvedValue(true);
    (buildService.startJob as ReturnType<typeof vi.fn>).mockResolvedValue({
      jobId: "job-1",
      buildRequestId: "br-1",
      status: "queued",
    });
    await handlers.get("job:start")!({}, "br-1");
    expect(buildService.startJob).toHaveBeenCalledWith("br-1");
  });

  test("TC-UI-003-08: 必須入力欠落 [unit/P0]", () => {
    const { ipcMain: voiceIpcMain } = fakeIpcMain<VoiceIpcMainLike>();
    expect(() => registerVoiceIpcHandlers(undefined as never)).toThrow();
    expect(() => registerVoiceIpcHandlers({ ipcMain: voiceIpcMain, voiceService: undefined as never })).toThrow();
    expect(voiceIpcMain.handle).not.toHaveBeenCalled();

    const { ipcMain: buildIpcMain } = fakeIpcMain<BuildIpcMainLike>();
    expect(() => registerBuildIpcHandlers(undefined as never)).toThrow();
    expect(() =>
      registerBuildIpcHandlers({
        ipcMain: buildIpcMain,
        buildService: undefined as never,
        approvalGateChecker: undefined as never,
      }),
    ).toThrow();
    expect(buildIpcMain.handle).not.toHaveBeenCalled();
  });
});
