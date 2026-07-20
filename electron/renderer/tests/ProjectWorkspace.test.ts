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

  test("TC-UI-002-04: file dialog/drop [integration_mock/P1]", async () => {
    const registerSource = vi.fn().mockResolvedValue(undefined);
    const wrapper = mount(ProjectWorkspace, {
      props: {
        sources: [],
        approvals: [],
        registerSource,
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges: vi.fn(),
      },
    });

    await wrapper.get('[data-testid="media-type-select"]').setValue("pdf");

    const file = new File(["dummy"], "chapter01.pdf", { type: "application/pdf" });
    const dataTransfer = { files: [file] } as unknown as DataTransfer;
    await wrapper.get('[data-testid="drop-zone"]').trigger("drop", { dataTransfer });

    expect(registerSource).toHaveBeenCalledTimes(1);
    expect(registerSource).toHaveBeenCalledWith({ filePath: "chapter01.pdf", mediaType: "pdf" });
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
