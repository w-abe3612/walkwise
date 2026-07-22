/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-003 / TASK-VOICE-PROFILE-UI-001:
 * approved-only VoiceProfile selection, mp3/text output requirement, cleared-selection
 * handling, required-input-missing at the IPC layer.
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
        voiceProfiles: [{ voiceProfileId: "vp-1", name: "ナレーター1", status: "approved" }],
        createBuildRequest: vi.fn(),
        startJob: vi.fn(),
      },
    });

    await wrapper.get('[data-testid="format-mp3"]').trigger("change");
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(true);

    await wrapper.get('[data-testid="voice-profile-select"]').setValue("vp-1");
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(false);
  });

  test("TC-UI-003-04: draft/archivedは選択肢に出さない [unit/P1]", () => {
    const wrapper = mount(BuildSettings, {
      props: {
        voiceProfiles: [
          { voiceProfileId: "vp-approved", name: "承認済み", status: "approved" },
          { voiceProfileId: "vp-draft", name: "下書き", status: "draft" },
          { voiceProfileId: "vp-archived", name: "アーカイブ済み", status: "archived" },
        ],
        createBuildRequest: vi.fn(),
        startJob: vi.fn(),
      },
    });

    const options = wrapper.findAll('[data-testid="voice-profile-select"] option').map((o) => o.attributes("value"));
    expect(options).toContain("vp-approved");
    expect(options).not.toContain("vp-draft");
    expect(options).not.toContain("vp-archived");
  });

  test("TC-UI-003-06: approval gate error導線とvoice_profile_idの送信 [unit/P1]", async () => {
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

  test("TC-UI-003-06b: 実際のBuildSettings.vueがvoiceProfileIdとしてvoice_profile_idを送る(speaker_idではない) [unit/P0]", async () => {
    const createBuildRequest = vi.fn().mockResolvedValue({ buildRequestId: "br-1" });
    const startJob = vi.fn().mockResolvedValue({ jobId: "job-1" });
    const wrapper = mount(BuildSettings, {
      props: {
        voiceProfiles: [{ voiceProfileId: "vp-real-id", name: "ナレーター1", status: "approved" }],
        createBuildRequest,
        startJob,
      },
    });

    await wrapper.get('[data-testid="format-mp3"]').trigger("change");
    await wrapper.get('[data-testid="voice-profile-select"]').setValue("vp-real-id");
    await wrapper.get('[data-testid="submit-button"]').trigger("click");
    await wrapper.vm.$nextTick();

    expect(createBuildRequest).toHaveBeenCalledWith({
      outputFormats: ["mp3"],
      voiceProfileId: "vp-real-id",
    });
    expect(startJob).toHaveBeenCalledWith("br-1");
  });

  test("TC-UI-003-08: 必須入力欠落 [unit/P0]", () => {
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

  test("TC-VOICE-PROFILE-UI-001-01: 選択中Profileがapproved一覧から消えたら選択解除する [unit/P0]", async () => {
    const wrapper = mount(BuildSettings, {
      props: {
        voiceProfiles: [{ voiceProfileId: "vp-1", name: "ナレーター1", status: "approved" }],
        createBuildRequest: vi.fn(),
        startJob: vi.fn(),
      },
    });

    await wrapper.get('[data-testid="format-mp3"]').trigger("change");
    await wrapper.get('[data-testid="voice-profile-select"]').setValue("vp-1");
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(false);

    // vp-1がarchiveされ、approved一覧から消えた状況を模擬する。
    // `.vue`はenv.d.tsの`unknown` shim経由のため、`setProps`の型はVNode基底属性しか
    // 認識しない。実行時には正しく動作するため、この境界だけ`unknown`経由でcastする。
    const setProps = wrapper.setProps.bind(wrapper) as (props: Record<string, unknown>) => Promise<void>;
    await setProps({
      voiceProfiles: [{ voiceProfileId: "vp-1", name: "ナレーター1", status: "archived" as const }],
    });
    await wrapper.vm.$nextTick();

    expect((wrapper.get('[data-testid="voice-profile-select"]').element as HTMLSelectElement).value).toBe("");
    expect(wrapper.find('[data-testid="voice-profile-cleared-notice"]').exists()).toBe(true);
    expect((wrapper.get('[data-testid="submit-button"]').element as HTMLButtonElement).disabled).toBe(true);
  });

  test("TC-VOICE-PROFILE-UI-001-02: text-onlyはVoiceProfile未選択でもBuildできる [unit/P0]", async () => {
    const createBuildRequest = vi.fn().mockResolvedValue({ buildRequestId: "br-1" });
    const startJob = vi.fn();
    const wrapper = mount(BuildSettings, {
      props: { voiceProfiles: [], createBuildRequest, startJob },
    });

    await wrapper.get('[data-testid="format-text"]').trigger("change");
    await wrapper.get('[data-testid="submit-button"]').trigger("click");
    await wrapper.vm.$nextTick();

    expect(createBuildRequest).toHaveBeenCalledWith({ outputFormats: ["text"], voiceProfileId: undefined });
  });
});
