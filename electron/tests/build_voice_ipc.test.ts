/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-003: text-only, VOICEVOX connectivity display,
 * preview delegation, MVP-excluded features, re-execution determinism.
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Release scope: MVP.
 *
 * TASK-VOICE-PROFILE-UI-001: BuildSettings.vueは旧来のVOICEVOX speaker/style直接選択
 * (`engineHealth`/`speakers`/`preview`)を削除し、Project単位のapproved VoiceProfileを
 * 選択するだけになった。この画面がmountするtestは新しいprops形状へ更新した
 * (`voice:list-engines`/`voice:preview`自体のIPC handler testは変更なし、
 * 別concept)。
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
    voiceProfiles: [],
    createBuildRequest: vi.fn(),
    startJob: vi.fn(),
    ...overrides,
  };
}

describe("TASK-UI-003 出力・声設定・試聴画面", () => {
  test("TC-UI-003-01: text-only [unit/P0]", async () => {
    const wrapper = mount(BuildSettings, { props: baseProps() });

    await wrapper.get('[data-testid="format-text"]').trigger("change");

    expect((wrapper.get('[data-testid="voice-profile-select"]').element as HTMLSelectElement).disabled).toBe(true);
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(false);
  });

  test("TC-UI-003-03: approved VoiceProfileが0件ならMP3を開始できない [integration_mock/P0]", async () => {
    const createBuildRequest = vi.fn();
    const startJob = vi.fn();
    const wrapper = mount(BuildSettings, {
      props: baseProps({
        voiceProfiles: [{ voiceProfileId: "vp-draft", name: "下書き中", status: "draft" }],
        createBuildRequest,
        startJob,
      }),
    });

    await wrapper.get('[data-testid="format-mp3"]').trigger("change");

    // draftはapproved一覧に出ないため選択できず、送信もdisabledのまま
    expect(wrapper.find('option[value="vp-draft"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="voice-profile-none-available"]').exists()).toBe(true);
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(true);
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
      props: baseProps({ voiceProfiles: [{ voiceProfileId: "vp-1", name: "ナレーター1", status: "approved" }] }),
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
    // approvalGateChecker だけが欠落していれば登録自体が失敗し、handlerは1つも登録されない
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
