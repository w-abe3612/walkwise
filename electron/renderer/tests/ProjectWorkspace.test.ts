/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-002: request-changes reason validation,
 * file registration via drop, retry-on-failed, required-input-missing at the IPC layer.
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import { registerApprovalIpcHandlers, type IpcMainLike, type ApprovalServiceLike } from "../../main/ipc/approvals";
import { registerSourceIpcHandlers, type SourceServiceLike } from "../../main/ipc/sources";
import ProjectWorkspace from "../screens/ProjectWorkspace.vue";
import type { SourceItem } from "../screens/ProjectWorkspace.types";

function fakeIpcMain(): { ipcMain: IpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain: IpcMainLike = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

/** TASK-VOICE-PROFILE-UI-001で追加した必須propsの既定値(この節のtestは音声設定の挙動を対象外とする)。 */
function voiceProfileTestProps() {
  return {
    voiceProfiles: [],
    voiceEngineHealth: null,
    voiceSpeakers: [],
    createVoiceProfile: vi.fn(),
    updateVoiceProfile: vi.fn(),
    approveVoiceProfile: vi.fn(),
    archiveVoiceProfile: vi.fn(),
  };
}

describe("TASK-UI-002 Project workspace・Source登録/レビュー・承認UI", () => {
  test("TC-UI-002-02: 差し戻し [unit/P0]", async () => {
    const requestChanges = vi.fn().mockResolvedValue(undefined);
    const wrapper = mount(ProjectWorkspace, {
      props: {
        sources: [],
        approvals: [{ gate: "materials_curriculum", status: "review_pending" }],
        registerSource: vi.fn(),
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges,
        selectSourceFile: vi.fn(),
        ...voiceProfileTestProps(),
      },
    });

    // 理由が空のまま差し戻しを試みると拒否され、IPCは呼ばれない
    await wrapper.get('[data-testid="request-changes-button-materials_curriculum"]').trigger("click");
    expect(requestChanges).not.toHaveBeenCalled();
    expect(wrapper.find('[data-testid="reason-error-materials_curriculum"]').exists()).toBe(true);

    // 理由を入力すればIPCが1回だけ呼ばれる
    await wrapper.get('[data-testid="reason-input-materials_curriculum"]').setValue("要出典追加");
    await wrapper.get('[data-testid="request-changes-button-materials_curriculum"]').trigger("click");
    expect(requestChanges).toHaveBeenCalledTimes(1);
    expect(requestChanges).toHaveBeenCalledWith("materials_curriculum", "要出典追加");
  });

  test("TC-UI-002-04: 安全なfile dialog選択 [integration_mock/P1]", async () => {
    // TASK-REVIEW-001 2.6節: file選択はmain process側のdialog.showOpenDialog()経由でのみ行い、
    // rendererはbrowser File.name等の任意path文字列を一切組み立てない。main側が検証済みの
    // 絶対pathを返した場合にのみregisterSourceが呼ばれる。
    const registerSource = vi.fn().mockResolvedValue(undefined);
    const selectSourceFile = vi.fn().mockResolvedValue({ filePath: "C:\\Users\\reader\\Documents\\chapter01.pdf", mediaType: "pdf" });
    const wrapper = mount(ProjectWorkspace, {
      props: {
        sources: [],
        approvals: [],
        registerSource,
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges: vi.fn(),
        selectSourceFile,
        ...voiceProfileTestProps(),
      },
    });

    await wrapper.get('[data-testid="select-file-button"]').trigger("click");
    await wrapper.vm.$nextTick();

    expect(selectSourceFile).toHaveBeenCalledTimes(1);
    expect(registerSource).toHaveBeenCalledTimes(1);
    expect(registerSource).toHaveBeenCalledWith({
      filePath: "C:\\Users\\reader\\Documents\\chapter01.pdf",
      mediaType: "pdf",
    });
  });

  test("TC-UI-002-04b: dialogがcancel(null)された場合はregisterSourceを呼ばない [unit/P1]", async () => {
    const registerSource = vi.fn();
    const selectSourceFile = vi.fn().mockResolvedValue(null);
    const wrapper = mount(ProjectWorkspace, {
      props: {
        sources: [],
        approvals: [],
        registerSource,
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges: vi.fn(),
        selectSourceFile,
        ...voiceProfileTestProps(),
      },
    });

    await wrapper.get('[data-testid="select-file-button"]').trigger("click");
    await wrapper.vm.$nextTick();

    expect(selectSourceFile).toHaveBeenCalledTimes(1);
    expect(registerSource).not.toHaveBeenCalled();
  });

  test("TC-UI-002-06: 再処理/修正/問題なし [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const sourceService: SourceServiceLike = {
      register: vi.fn().mockImplementation(async (input) => ({
        sourceId: "src-1",
        projectId: input.projectId,
        mediaType: input.mediaType,
        status: "registered",
      })),
      list: vi.fn().mockResolvedValue([]),
      retry: vi.fn().mockResolvedValue({
        sourceId: "src-1",
        projectId: "proj-1",
        mediaType: "pdf",
        status: "registered",
      }),
    };
    registerSourceIpcHandlers({ ipcMain, sourceService });
    const registerHandler = handlers.get("source:register")!;

    // 再処理: 失敗したSourceと同じfilePathで再登録すると新たな処理が開始される(冪等な再試行)
    await registerHandler({}, { projectId: "proj-1", filePath: "materials/broken.pdf", mediaType: "pdf" });
    await registerHandler({}, { projectId: "proj-1", filePath: "materials/broken.pdf", mediaType: "pdf" });
    expect(sourceService.register).toHaveBeenCalledTimes(2);

    // 修正: 未対応形式は「問題あり」として副作用前にvalidation errorになる
    await expect(
      registerHandler({}, { projectId: "proj-1", filePath: "materials/video.mp4", mediaType: "video" }),
    ).rejects.toThrow(/unsupported media_type/);
    expect(sourceService.register).toHaveBeenCalledTimes(2); // video分は呼ばれていない(問題なし側へは進まない)
  });

  test("TC-UI-002-08: 必須入力欠落 [unit/P0]", () => {
    const { ipcMain } = fakeIpcMain();

    expect(() => registerSourceIpcHandlers(undefined as never)).toThrow();
    expect(() => registerSourceIpcHandlers({ ipcMain, sourceService: undefined as never })).toThrow();
    expect(ipcMain.handle).not.toHaveBeenCalled();

    const approvalIpcMain = fakeIpcMain().ipcMain;
    expect(() => registerApprovalIpcHandlers(undefined as never)).toThrow();
    expect(() =>
      registerApprovalIpcHandlers({ ipcMain: approvalIpcMain, approvalService: undefined as never }),
    ).toThrow();
  });
});

describe("TASK-VOICE-PROFILE-UI-001 Project Workspaceの音声設定section", () => {
  const SPEAKERS = [{ speakerId: "3", displayName: "四国めたん", styleIds: ["0", "1"] }];

  function mountWorkspace(overrides: Record<string, unknown> = {}) {
    return mount(ProjectWorkspace, {
      props: {
        sources: [],
        approvals: [],
        registerSource: vi.fn(),
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges: vi.fn(),
        selectSourceFile: vi.fn(),
        ...voiceProfileTestProps(),
        voiceSpeakers: SPEAKERS,
        ...overrides,
      },
    });
  }

  test("VoiceProfile一覧を表示でき、statusが日本語表示され、speaker表示名を優先する", () => {
    const wrapper = mountWorkspace({
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "ナレーター1", engine: "voicevox", speakerId: "3", status: "approved", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });

    const item = wrapper.get('[data-testid="voice-profile-item"]');
    expect(item.get('[data-testid="voice-profile-name"]').text()).toBe("ナレーター1");
    expect(item.get('[data-testid="voice-profile-speaker"]').text()).toBe("四国めたん"); // IDではなく表示名
    expect(item.get('[data-testid="voice-profile-status"]').text()).toBe("利用可能"); // "approved"をそのまま見せない
  });

  test("0件時は追加を促す空状態を表示する", () => {
    const wrapper = mountWorkspace({ voiceProfiles: [] });
    expect(wrapper.get('[data-testid="voice-profile-empty"]').text()).toContain("音声設定がまだありません");
    expect(wrapper.find('[data-testid="voice-profile-draft-only"]').exists()).toBe(false);
  });

  test("draftしかない場合は承認を促す案内を表示する", () => {
    const wrapper = mountWorkspace({
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "n", engine: "voicevox", speakerId: "3", status: "draft", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });
    expect(wrapper.get('[data-testid="voice-profile-draft-only"]').text()).toContain("利用可能にする");
  });

  test("archivedしかない場合は新規追加を促す案内を表示する(元に戻す導線は出さない)", () => {
    const wrapper = mountWorkspace({
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "n", engine: "voicevox", speakerId: "3", status: "archived", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });
    expect(wrapper.get('[data-testid="voice-profile-archived-only"]').text()).toContain("新しい音声設定を追加してください");
    expect(wrapper.text()).not.toContain("元に戻す");
  });

  test("新規作成modalを開き、保存するとdraftとしてcreateVoiceProfileが呼ばれる(statusは送らない)", async () => {
    const createVoiceProfile = vi.fn().mockResolvedValue(undefined);
    const wrapper = mountWorkspace({ createVoiceProfile });

    await wrapper.get('[data-testid="voice-profile-add-button"]').trigger("click");
    const modal = wrapper.get('[data-testid="voice-profile-modal"]');
    expect(modal.attributes("role")).toBe("dialog");
    expect(modal.attributes("aria-modal")).toBe("true");

    await wrapper.get('[data-testid="voice-profile-name-input"]').setValue("新しい声");
    await wrapper.get('[data-testid="voice-profile-speaker-select"]').setValue("3");
    await wrapper.get('[data-testid="voice-profile-modal-save"]').trigger("click");
    await wrapper.vm.$nextTick();

    expect(createVoiceProfile).toHaveBeenCalledWith(
      expect.objectContaining({ name: "新しい声", speakerId: "3", engine: "voicevox" }),
    );
    const sentPayload = createVoiceProfile.mock.calls[0][0];
    expect(sentPayload.status).toBeUndefined(); // 作成はbackend側で常にdraft、UIからstatusは送らない
    expect(wrapper.find('[data-testid="voice-profile-modal"]').exists()).toBe(false); // 保存後は閉じる
  });

  test("編集modalを開いて保存しても、statusは送らない(承認済み方針: approved編集後もapprovedを維持)", async () => {
    const updateVoiceProfile = vi.fn().mockResolvedValue(undefined);
    const wrapper = mountWorkspace({
      updateVoiceProfile,
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "承認済みの声", engine: "voicevox", speakerId: "3", status: "approved", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });

    await wrapper.get('[data-testid="voice-profile-edit-button"]').trigger("click");
    expect((wrapper.get('[data-testid="voice-profile-name-input"]').element as HTMLInputElement).value).toBe("承認済みの声");

    await wrapper.get('[data-testid="voice-profile-name-input"]').setValue("名前変更後");
    await wrapper.get('[data-testid="voice-profile-modal-save"]').trigger("click");
    await wrapper.vm.$nextTick();

    expect(updateVoiceProfile).toHaveBeenCalledWith("vp-1", expect.objectContaining({ name: "名前変更後" }));
    const sentPayload = updateVoiceProfile.mock.calls[0][1];
    expect(sentPayload.status).toBeUndefined(); // approved維持: UIからstatus変更を送らない
  });

  test("draftの「利用可能にする」でapproveVoiceProfileが呼ばれる", async () => {
    const approveVoiceProfile = vi.fn().mockResolvedValue(undefined);
    const wrapper = mountWorkspace({
      approveVoiceProfile,
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "n", engine: "voicevox", speakerId: "3", status: "draft", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });

    await wrapper.get('[data-testid="voice-profile-approve-button"]').trigger("click");
    expect(approveVoiceProfile).toHaveBeenCalledWith("vp-1");
  });

  test("archiveは確認を経てから実行される(物理削除相当のUIは出さない)", async () => {
    const archiveVoiceProfile = vi.fn().mockResolvedValue(undefined);
    const wrapper = mountWorkspace({
      archiveVoiceProfile,
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "n", engine: "voicevox", speakerId: "3", status: "approved", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });

    await wrapper.get('[data-testid="voice-profile-archive-button"]').trigger("click");
    expect(archiveVoiceProfile).not.toHaveBeenCalled();
    expect(wrapper.get('[data-testid="voice-profile-archive-confirm"]').attributes("role")).toBe("alertdialog");

    await wrapper.get('[data-testid="voice-profile-archive-confirm-button"]').trigger("click");
    expect(archiveVoiceProfile).toHaveBeenCalledWith("vp-1");
  });

  test("archivedは編集不可(編集ボタンがdisabled)", () => {
    const wrapper = mountWorkspace({
      voiceProfiles: [
        { voiceProfileId: "vp-1", projectId: "p1", name: "n", engine: "voicevox", speakerId: "3", status: "archived", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });

    expect((wrapper.get('[data-testid="voice-profile-edit-button"]').element as HTMLButtonElement).disabled).toBe(true);
    expect(wrapper.find('[data-testid="voice-profile-approve-button"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="voice-profile-archive-button"]').exists()).toBe(false);
  });

  test("backendのerrorを利用者向け文言へ変換して表示する(内部codeをそのまま出さない)", async () => {
    const createVoiceProfile = vi.fn().mockRejectedValue(new Error("worker_request_failed: voice_profile_invalid: settings_json must be an object"));
    const wrapper = mountWorkspace({ createVoiceProfile });

    await wrapper.get('[data-testid="voice-profile-add-button"]').trigger("click");
    await wrapper.get('[data-testid="voice-profile-name-input"]').setValue("n");
    await wrapper.get('[data-testid="voice-profile-speaker-select"]').setValue("3");
    await wrapper.get('[data-testid="voice-profile-modal-save"]').trigger("click");
    await wrapper.vm.$nextTick();

    const errorText = wrapper.get('[data-testid="voice-profile-modal-error"]').text();
    expect(errorText).toBe("入力内容を確認してください。");
    expect(errorText).not.toContain("voice_profile_invalid");
    expect(wrapper.find('[data-testid="voice-profile-modal"]').exists()).toBe(true); // 失敗時はmodalを閉じない(入力保持)
  });

  test("Escapeキーでmodalを閉じられる", async () => {
    const wrapper = mountWorkspace();
    await wrapper.get('[data-testid="voice-profile-add-button"]').trigger("click");
    expect(wrapper.find('[data-testid="voice-profile-modal"]').exists()).toBe(true);

    await wrapper.get('[data-testid="voice-profile-modal"]').trigger("keydown", { key: "Escape" });
    expect(wrapper.find('[data-testid="voice-profile-modal"]').exists()).toBe(false);
  });

  test("別ProjectのProfileは表示しない(渡されたpropsだけを表示する。Project絞り込みはIPC/backend側で実施済み)", () => {
    const wrapper = mountWorkspace({
      voiceProfiles: [
        { voiceProfileId: "vp-own", projectId: "p1", name: "自分のProject", engine: "voicevox", speakerId: "3", status: "approved", speedScale: 1, pitchScale: 0, intonationScale: 1, volumeScale: 1, sentencePauseMs: 250, paragraphPauseMs: 600, sectionPauseMs: 1000, chapterPauseMs: 1500, settingsJson: "{}" },
      ],
    });

    const names = wrapper.findAll('[data-testid="voice-profile-name"]').map((n) => n.text());
    expect(names).toEqual(["自分のProject"]);
  });
});
