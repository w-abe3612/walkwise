/**
 * @vitest-environment jsdom
 *
 * Tests for TASK-REVIEW-001 P0 fix: Renderer root (App.vue) wiring.
 *
 * Before this fix, `electron/renderer/main.ts` mounted an empty placeholder `<div>` — none of
 * the five completed screens (ProjectList/ProjectWorkspace/BuildSettings/JobsAndArtifacts) were
 * ever actually connected to navigation, shared loading/error state, or the real
 * `window.walkwise` API exposed by preload. This test mounts the real App.vue against a fake
 * `window.walkwise`, and drives it through the full Project -> Source -> Approval -> Build ->
 * Job -> Artifact flow via real navigation and DOM interaction (not by calling internal methods
 * directly), to prove the wiring is real end-to-end.
 */

import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, test, vi } from "vitest";

import App from "../App.vue";

function installFakeWalkwiseApi() {
  const api = {
    project: {
      list: vi.fn().mockResolvedValue({ projects: [{ projectId: "p1", title: "本のタイトル", planningStage: "registered", updatedAt: "2026-07-20T00:00:00Z" }] }),
      create: vi.fn(),
      get: vi.fn(),
    },
    source: {
      register: vi.fn().mockResolvedValue({ sourceId: "s1", projectId: "p1", mediaType: "text", status: "ready" }),
      list: vi.fn().mockResolvedValue({ sources: [{ sourceId: "s1", mediaType: "text", status: "ready" }] }),
      retry: vi.fn().mockResolvedValue({}),
    },
    approval: {
      list: vi.fn().mockResolvedValue([{ gate: "planning", status: "draft" }]),
      approve: vi.fn().mockResolvedValue({}),
      requestChanges: vi.fn().mockResolvedValue({}),
    },
    buildRequest: { create: vi.fn().mockResolvedValue({ buildRequestId: "br1" }) },
    job: {
      start: vi.fn().mockResolvedValue({ jobId: "j1", status: "running" }),
      list: vi.fn().mockResolvedValue({ jobs: [{ jobId: "j1", jobType: "build", status: "running" }] }),
      get: vi.fn(),
      subscribeProgress: vi.fn().mockReturnValue(() => {}),
      cancel: vi.fn().mockResolvedValue({}),
    },
    artifact: {
      list: vi.fn().mockResolvedValue({ artifacts: [] }),
      openFolder: vi.fn().mockResolvedValue({}),
    },
    voice: {
      listEngines: vi.fn().mockResolvedValue({ health: { engine: "voicevox", available: true }, speakers: [] }),
      preview: vi.fn(),
    },
    voiceProfile: {
      create: vi.fn().mockResolvedValue({ voiceProfileId: "vp-1", status: "draft" }),
      list: vi.fn().mockResolvedValue([]),
      get: vi.fn(),
      update: vi.fn().mockResolvedValue({ voiceProfileId: "vp-1", status: "approved" }),
      archive: vi.fn().mockResolvedValue({ voiceProfileId: "vp-1", status: "archived" }),
    },
    dialog: { selectSourceFile: vi.fn().mockResolvedValue({ filePath: "/abs/chapter01.txt", mediaType: "text" }) },
  };
  (globalThis as unknown as { walkwise: unknown }).walkwise = api;
  return api;
}

describe("TASK-REVIEW-001 Renderer root(App.vue)がProject->Source->Approval->Build->Job->Artifactを実際に結線する", () => {
  afterEach(() => {
    delete (globalThis as unknown as { walkwise?: unknown }).walkwise;
    vi.restoreAllMocks();
  });

  test("Project一覧から開く->workspaceでsource/approvalを実際にIPC経由で読み込む", async () => {
    const api = installFakeWalkwiseApi();
    const wrapper = mount(App);
    await flushPromises();

    expect(wrapper.get('[data-testid="project-list"]').text()).toContain("本のタイトル");

    await wrapper.get('[data-testid="open-project-button"]').trigger("click");
    await flushPromises();

    expect(api.source.list).toHaveBeenCalledWith("p1");
    expect(api.approval.list).toHaveBeenCalledWith("p1");
    expect(wrapper.get('[data-testid="source-list"]').text()).toContain("準備完了");
  });

  test("workspaceの安全なfile選択がdialog経由でregisterSourceへつながる", async () => {
    const api = installFakeWalkwiseApi();
    const wrapper = mount(App);
    await flushPromises();
    await wrapper.get('[data-testid="open-project-button"]').trigger("click");
    await flushPromises();

    await wrapper.get('[data-testid="select-file-button"]').trigger("click");
    await flushPromises();

    expect(api.dialog.selectSourceFile).toHaveBeenCalledTimes(1);
    expect(api.source.register).toHaveBeenCalledWith({
      projectId: "p1",
      filePath: "/abs/chapter01.txt",
      mediaType: "text",
    });
  });

  test("build-settingsへ遷移するとvoiceProfile.listがこのProject向けに呼ばれる", async () => {
    const api = installFakeWalkwiseApi();
    (api.voiceProfile.list as ReturnType<typeof vi.fn>).mockResolvedValue([
      { voiceProfileId: "vp-1", name: "ナレーター1", status: "approved" },
    ]);
    const wrapper = mount(App);
    await flushPromises();
    await wrapper.get('[data-testid="open-project-button"]').trigger("click");
    await flushPromises();

    await wrapper.get('[data-testid="nav-build-settings"]').trigger("click");
    await flushPromises();

    expect(api.voiceProfile.list).toHaveBeenCalledWith("p1");
    expect(wrapper.get('[data-testid="voice-profile-select"]').text()).toContain("ナレーター1");
  });

  test("jobsへ遷移するとjob.list/artifact.listが呼ばれ、cancelが実IPCへつながる", async () => {
    const api = installFakeWalkwiseApi();
    const wrapper = mount(App);
    await flushPromises();
    await wrapper.get('[data-testid="open-project-button"]').trigger("click");
    await flushPromises();

    await wrapper.get('[data-testid="nav-jobs"]').trigger("click");
    await flushPromises();

    expect(api.job.list).toHaveBeenCalledWith("p1");
    expect(api.artifact.list).toHaveBeenCalledWith("p1");

    await wrapper.get('[data-testid="cancel-button"]').trigger("click"); // 1回目: 確認dialog表示
    await wrapper.get('[data-testid="cancel-confirm-button"]').trigger("click");
    await flushPromises();

    expect(api.job.cancel).toHaveBeenCalledWith("j1");
  });

  test("API失敗時、日本語message付きerrorがAppShellのerror summaryへ表示される", async () => {
    const api = installFakeWalkwiseApi();
    api.source.list.mockRejectedValueOnce(new Error("Sourceを読み込めませんでした。"));
    const wrapper = mount(App, { attachTo: document.body });
    await flushPromises();
    await wrapper.get('[data-testid="open-project-button"]').trigger("click");
    await flushPromises();

    expect(wrapper.get('[data-testid="error-message"]').text()).toBe("Sourceを読み込めませんでした。");
    wrapper.unmount();
  });
});
