/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-001: create-disabled, list rendering,
 * required-field validation, required-input-missing at the IPC layer.
 * Contract: docs/test-cases/TASK-UI-001-project-list-and-create-screen.md
 * Release scope: MVP.
 */

import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import { registerProjectIpcHandlers, type IpcMainLike, type ProjectServiceLike } from "../../main/ipc/projects";
import ProjectList from "../screens/ProjectList.vue";
import * as projectsApi from "../api/projects";

function fakeIpcMain(): { ipcMain: IpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain: IpcMainLike = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

describe("TASK-UI-001 Project一覧・新規作成画面", () => {
  test("TC-UI-001-02: 作成disabled [unit/P0]", async () => {
    vi.spyOn(projectsApi, "listProjects").mockResolvedValue({ projects: [] });
    const wrapper = mount(ProjectList);
    await flushPromises();

    const submitButton = wrapper.get('[data-testid="submit-button"]');
    expect((submitButton.element as HTMLButtonElement).disabled).toBe(true);

    await wrapper.get('[data-testid="field-title"]').setValue("タイトル");
    await wrapper.get('[data-testid="field-domain"]').setValue("database");
    await wrapper.get('[data-testid="field-purpose"]').setValue("目的");
    await wrapper.get('[data-testid="field-usage-purpose"]').setValue("personal_learning");
    await wrapper.get('[data-testid="field-target-audience"]').setValue("初心者");
    // source_strategyが未選択の間はまだdisabled
    expect((submitButton.element as HTMLButtonElement).disabled).toBe(true);

    await wrapper.get('[data-testid="field-source-strategy"] input[type="checkbox"]').setValue(true);
    expect((submitButton.element as HTMLButtonElement).disabled).toBe(false);

    vi.restoreAllMocks();
  });

  test("TC-UI-001-04: 一覧 [unit/P1]", async () => {
    const projects = [
      { projectId: "p1", title: "本1", planningStage: "registered", updatedAt: "2026-07-18T00:00:00+09:00" },
      { projectId: "p2", title: "本2", planningStage: "curriculum_ready", updatedAt: "2026-07-19T00:00:00+09:00" },
    ];
    vi.spyOn(projectsApi, "listProjects").mockResolvedValue({ projects });

    const wrapper = mount(ProjectList);
    await flushPromises();

    const items = wrapper.findAll('[data-testid="project-item"]');
    expect(items).toHaveLength(2);
    expect(items[0].text()).toContain("本1");
    expect(items[1].text()).toContain("本2");

    vi.restoreAllMocks();

    // 空一覧も正常結果(empty state)として扱う
    vi.spyOn(projectsApi, "listProjects").mockResolvedValue({ projects: [] });
    const emptyWrapper = mount(ProjectList);
    await flushPromises();
    expect(emptyWrapper.find('[data-testid="empty-state"]').exists()).toBe(true);
    expect(emptyWrapper.find('[data-testid="error-summary"]').exists()).toBe(false);

    vi.restoreAllMocks();
  });

  test("TC-UI-001-06: 必須validation [unit/P1]", async () => {
    const { ipcMain } = fakeIpcMain();
    const projectService: ProjectServiceLike = {
      list: vi.fn().mockResolvedValue([]),
      create: vi.fn().mockResolvedValue({
        projectId: "proj-1",
        title: "t",
        planningStage: "registered",
        updatedAt: "x",
      }),
    };
    registerProjectIpcHandlers({ ipcMain, projectService });
    const createHandler = (ipcMain.handle as unknown as { mock: { calls: unknown[][] } }).mock.calls.find(
      (call) => call[0] === "project:create",
    )![1] as (event: unknown, input: unknown) => Promise<unknown>;

    // sourceStrategy欠落は副作用(service.create)前にvalidation errorになる
    await expect(
      createHandler(
        {},
        {
          title: "t",
          domain: "d",
          purpose: "p",
          usagePurpose: "personal_learning",
          targetAudienceDescription: "a",
          sourceStrategy: [],
        },
      ),
    ).rejects.toThrow(/validation_error|sourceStrategy/);
    expect(projectService.create).not.toHaveBeenCalled();

    // 正常値は受理する
    await createHandler(
      {},
      {
        title: "t",
        domain: "d",
        purpose: "p",
        usagePurpose: "personal_learning",
        targetAudienceDescription: "a",
        sourceStrategy: ["upload_files"],
      },
    );
    expect(projectService.create).toHaveBeenCalledTimes(1);
  });

  test("TC-UI-001-08: 必須入力欠落 [unit/P0]", () => {
    const { ipcMain } = fakeIpcMain();

    expect(() => registerProjectIpcHandlers(undefined as never)).toThrow();
    expect(() => registerProjectIpcHandlers({ ipcMain, projectService: undefined as never })).toThrow();
    expect(ipcMain.handle).not.toHaveBeenCalled(); // 副作用を開始する前に検証error
  });
});
