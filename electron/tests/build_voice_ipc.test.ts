/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-003: text-only, VOICEVOX connectivity display,
 * preview delegation, MVP-excluded features, re-execution determinism.
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import { registerVoiceIpcHandlers, type IpcMainLike, type VoiceServiceLike } from "../main/ipc/voice";
import { registerBuildIpcHandlers, type BuildServiceLike } from "../main/ipc/builds";
import BuildSettings from "../renderer/screens/BuildSettings.vue";

function fakeIpcMain(): { ipcMain: IpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain: IpcMainLike = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

function baseProps(overrides: Record<string, unknown> = {}) {
  return {
    engineHealth: { available: true },
    speakers: [],
    preview: vi.fn(),
    createBuildRequest: vi.fn(),
    startJob: vi.fn(),
    ...overrides,
  };
}

describe("TASK-UI-003 出力・声設定・試聴画面", () => {
  test("TC-UI-003-01: text-only [unit/P0]", async () => {
    const wrapper = mount(BuildSettings, { props: baseProps() });

    await wrapper.get('[data-testid="format-text"]').trigger("change");

    expect((wrapper.get('[data-testid="speaker-select"]').element as HTMLSelectElement).disabled).toBe(true);
    expect((wrapper.get('[data-testid="speed-slider"]').element as HTMLInputElement).disabled).toBe(true);
    expect((wrapper.get('[data-testid="preview-button"]').element as HTMLButtonElement).disabled).toBe(true);
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(false);
  });

  test("TC-UI-003-03: VOICEVOX疎通 [integration_mock/P0]", async () => {
    const createBuildRequest = vi.fn();
    const startJob = vi.fn();
    const wrapper = mount(BuildSettings, {
      props: baseProps({ engineHealth: { available: false, detail: "connection refused" }, createBuildRequest, startJob }),
    });

    expect(wrapper.find('[data-testid="engine-error"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="engine-retry"]').exists()).toBe(true);
    // engine未接続の間はvoice controlsが常にdisabled(MP3を選んでも試聴・音声制御を使えない)
    await wrapper.get('[data-testid="format-mp3"]').trigger("change");
    expect((wrapper.get('[data-testid="speaker-select"]').element as HTMLSelectElement).disabled).toBe(true);
    expect(createBuildRequest).not.toHaveBeenCalled();
    expect(startJob).not.toHaveBeenCalled();
  });

  test("TC-UI-003-05: preview [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const voiceService: VoiceServiceLike = {
      checkHealth: vi.fn(),
      listSpeakers: vi.fn(),
      preview: vi.fn().mockResolvedValue({ previewId: "prev-1", outputPath: "preview/prev-1.wav" }),
    };
    registerVoiceIpcHandlers({ ipcMain, voiceService });

    const previewHandler = handlers.get("voice:preview")!;
    const result = await previewHandler({}, { speakerId: "1", text: "こんにちは" });

    expect(voiceService.preview).toHaveBeenCalledWith(expect.objectContaining({ speakerId: "1", text: "こんにちは" }));
    expect(result).toEqual({ previewId: "prev-1", outputPath: "preview/prev-1.wav" });
  });

  test("TC-UI-003-07: MVP外機能非表示 [unit/P1]", () => {
    const wrapper = mount(BuildSettings, {
      props: baseProps({ speakers: [{ speakerId: "1", displayName: "四国めたん" }] }),
    });

    const text = wrapper.text();
    expect(text).not.toContain("COEIROINK");
    expect(text).not.toContain("M4B");
    expect(text).not.toContain("EPUB");
    expect(wrapper.findAll('[data-testid="format-mp3"]')).toHaveLength(1);
    expect(wrapper.findAll('[data-testid="format-text"]')).toHaveLength(1);
    expect(wrapper.findAll('input[type="checkbox"]')).toHaveLength(2); // mp3/textのみ
  });

  test("TC-REVIEW-001-09: approvalGateChecker未注入はfail-closed(default-allowにならない) [unit/P0]", () => {
    // TASK-REVIEW-001 禁止事項: 承認gateのcheckerが注入されていない場合、
    // job:startをapproved扱いにしてはならない。buildServiceは正常に注入された状態でも、
    // approvalGateCheckerだけが欠落していれば登録自体が失敗し、handlerは1つも登録されない
    // (=job:startを一切呼び出せない、真にfail-closedな状態)。
    const { ipcMain } = fakeIpcMain();
    const buildService: BuildServiceLike = { createBuildRequest: vi.fn(), startJob: vi.fn() };

    expect(() =>
      registerBuildIpcHandlers({
        ipcMain,
        buildService,
        approvalGateChecker: undefined as never,
      }),
    ).toThrow(/approvalGateChecker is required/);
    expect(ipcMain.handle).not.toHaveBeenCalled();
  });

  test("TC-UI-003-09: 再実行時の決定性 [unit/P1]", async () => {
    const voiceService: VoiceServiceLike = {
      checkHealth: vi.fn().mockResolvedValue({ engine: "voicevox", available: true }),
      listSpeakers: vi.fn().mockResolvedValue([{ speakerId: "1", displayName: "四国めたん", styleIds: ["0"] }]),
      preview: vi.fn(),
    };

    const run = async () => {
      const { ipcMain, handlers } = fakeIpcMain();
      registerVoiceIpcHandlers({ ipcMain, voiceService });
      return handlers.get("voice:list-engines")!({});
    };

    const first = await run();
    const second = await run();

    expect(first).toEqual(second);
    expect(voiceService.checkHealth).toHaveBeenCalledTimes(2);
  });
});
