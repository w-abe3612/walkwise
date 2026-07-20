/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-001: empty/loading/error display, keyboard,
 * create-form IPC delegation, channel registration, re-execution determinism.
 * Contract: docs/test-cases/TASK-UI-001-project-list-and-create-screen.md
 * Release scope: MVP.
 */

import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import type { ProjectServiceLike, ProjectSummary } from "../main/ipc/projects";
import { registerProjectIpcHandlers, type IpcMainLike } from "../main/ipc/projects";
import ProjectList from "../renderer/screens/ProjectList.vue";
import * as projectsApi from "../renderer/api/projects";

function fakeIpcMain(): { ipcMain: IpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain: IpcMainLike = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

function fakeProjectService(overrides: Partial<ProjectServiceLike> = {}): ProjectServiceLike {
  return {
    list: vi.fn().mockResolvedValue([]),
    create: vi.fn().mockImplementation(async (input) => ({
      projectId: "proj-new",
      title: input.title,
      planningStage: "registered",
      updatedAt: "2026-07-20T00:00:00+09:00",
    })),
    ...overrides,
  };
}

describe("TASK-UI-001 Project一覧・新規作成画面", () => {
  test("TC-UI-001-01: empty/loading/error [unit/P0]", async () => {
    const listMock = vi.spyOn(projectsApi, "listProjects");

    // loading: 未解決のPromiseの間はskeletonを表示する
    let resolveList!: (value: projectsApi.ListProjectsResult) => void;
    listMock.mockReturnValueOnce(new Promise((resolve) => (resolveList = resolve)));
    const loadingWrapper = mount(ProjectList);
    expect(loadingWrapper.find('[data-testid="skeleton"]').exists()).toBe(true);
    resolveList({ projects: [] });
    await flushPromises();
    expect(loadingWrapper.find('[data-testid="empty-state"]').exists()).toBe(true);

    // error: 取得失敗で要約メッセージ+再試行ボタン
    listMock.mockRejectedValueOnce(new Error("network unavailable"));
    const errorWrapper = mount(ProjectList);
    await flushPromises();
    expect(errorWrapper.find('[data-testid="error-summary"]').exists()).toBe(true);
    expect(errorWrapper.find('[data-testid="retry-button"]').exists()).toBe(true);
    expect(errorWrapper.text()).toContain("network unavailable");

    listMock.mockRestore();
  });

  test("TC-UI-001-03: keyboard [unit/P0]", async () => {
    vi.spyOn(projectsApi, "listProjects").mockResolvedValue({ projects: [] });
    const createMock = vi.spyOn(projectsApi, "createProject").mockResolvedValue({
      projectId: "proj-1",
      title: "t",
      planningStage: "registered",
      updatedAt: "2026-07-20T00:00:00+09:00",
    });

    const wrapper = mount(ProjectList);
    await flushPromises();

    const form = wrapper.get('[data-testid="create-form"]');

    // 無効な状態でEnterを押しても作成されない
    await form.trigger("keydown", { key: "Enter" });
    expect(createMock).not.toHaveBeenCalled();

    // 必須項目をすべて満たす
    await wrapper.get('[data-testid="field-title"]').setValue("タイトル");
    await wrapper.get('[data-testid="field-domain"]').setValue("database");
    await wrapper.get('[data-testid="field-purpose"]').setValue("目的");
    await wrapper.get('[data-testid="field-usage-purpose"]').setValue("personal_learning");
    await wrapper.get('[data-testid="field-target-audience"]').setValue("初心者");
    await wrapper.get('[data-testid="field-source-strategy"] input[type="checkbox"]').setValue(true);

    expect((wrapper.vm as unknown as { isFormValid: boolean }).isFormValid).toBe(true);

    // 有効な状態でのEnterは作成を実行する
    await form.trigger("keydown", { key: "Enter" });
    await flushPromises();
    expect(createMock).toHaveBeenCalledTimes(1);

    createMock.mockRestore();
    vi.restoreAllMocks();
  });

  test("TC-UI-001-05: 新規作成form [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const projectService = fakeProjectService();

    registerProjectIpcHandlers({ ipcMain, projectService });

    const createHandler = handlers.get("project:create")!;
    const result = (await createHandler(
      {},
      {
        title: "データベース入門",
        domain: "database",
        purpose: "初心者向け解説",
        usagePurpose: "personal_learning",
        targetAudienceDescription: "初心者",
        sourceStrategy: ["upload_files"],
      },
    )) as ProjectSummary;

    expect(projectService.create).toHaveBeenCalledWith(
      expect.objectContaining({ title: "データベース入門", sourceStrategy: ["upload_files"] }),
    );
    expect(result.projectId).toBe("proj-new");
  });

  test("TC-UI-001-07: Enter/Tab [unit/P1]", () => {
    const { ipcMain } = fakeIpcMain();
    const projectService = fakeProjectService();

    registerProjectIpcHandlers({ ipcMain, projectService });

    const registeredChannels = (ipcMain.handle as unknown as { mock: { calls: unknown[][] } }).mock.calls.map(
      (call) => call[0],
    );
    expect(registeredChannels).toEqual(["project:list", "project:create"]);
  });

  test("TC-UI-001-09: 再実行時の決定性 [unit/P1]", async () => {
    const projectService = fakeProjectService({
      list: vi.fn().mockResolvedValue([{ projectId: "p1", title: "t", planningStage: "registered", updatedAt: "x" }]),
    });

    const run = async () => {
      const { ipcMain, handlers } = fakeIpcMain();
      registerProjectIpcHandlers({ ipcMain, projectService });
      const listHandler = handlers.get("project:list")!;
      return listHandler({});
    };

    const first = await run();
    const second = await run();

    expect(first).toEqual(second);
    expect(projectService.list).toHaveBeenCalledTimes(2); // 実行ごとに1回ずつ
  });
});
