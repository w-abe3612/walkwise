/**
 * @vitest-environment jsdom
 *
 * STEP4 test implementation for TASK-UI-002: source status display, excluded formats,
 * processing kickoff, approval-gate stability, re-execution determinism.
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Release scope: MVP.
 */

import { mount } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";

import type { ApprovalServiceLike } from "../main/ipc/approvals";
import { registerApprovalIpcHandlers, type IpcMainLike as ApprovalIpcMainLike } from "../main/ipc/approvals";
import type { SourceServiceLike, SourceSummary } from "../main/ipc/sources";
import { registerSourceIpcHandlers, type IpcMainLike as SourceIpcMainLike } from "../main/ipc/sources";
import ProjectWorkspace from "../renderer/screens/ProjectWorkspace.vue";
import type { SourceItem } from "../renderer/screens/ProjectWorkspace.types";

function fakeIpcMain(): { ipcMain: SourceIpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

function fakeSourceService(overrides: Partial<SourceServiceLike> = {}): SourceServiceLike {
  return {
    register: vi.fn().mockImplementation(async (input) => ({
      sourceId: "src-1",
      projectId: input.projectId,
      mediaType: input.mediaType,
      status: "registered",
    })),
    ...overrides,
  };
}

describe("TASK-UI-002 Project workspace・Source登録/レビュー・承認UI", () => {
  test("TC-UI-002-01: Source状態表示 [unit/P0]", () => {
    const sources: SourceItem[] = [
      { sourceId: "s1", mediaType: "text", status: "registered" },
      { sourceId: "s2", mediaType: "pdf", status: "processing" },
      { sourceId: "s3", mediaType: "image", status: "ready" },
      { sourceId: "s4", mediaType: "pdf", status: "review_required" },
      { sourceId: "s5", mediaType: "image", status: "failed" },
    ];

    const wrapper = mount(ProjectWorkspace, {
      props: {
        sources,
        approvals: [],
        registerSource: vi.fn(),
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges: vi.fn(),
      },
    });

    const text = wrapper.text();
    expect(text).toContain("登録済み・処理待ち");
    expect(text).toContain("抽出・OCR処理中");
    expect(text).toContain("準備完了");
    expect(text).toContain("要確認(低信頼・高リスク要素あり)");
    expect(text).toContain("抽出に失敗しました");

    // review_requiredにはreview導線、failedにはretry導線がある
    expect(wrapper.findAll('[data-testid="review-link"]')).toHaveLength(1);
    expect(wrapper.findAll('[data-testid="retry-button"]')).toHaveLength(1);
  });

  test("TC-UI-002-03: 対象外非表示 [unit/P0]", () => {
    const wrapper = mount(ProjectWorkspace, {
      props: {
        sources: [],
        approvals: [],
        registerSource: vi.fn(),
        retrySource: vi.fn(),
        approve: vi.fn(),
        requestChanges: vi.fn(),
      },
    });

    const options = wrapper.findAll('[data-testid="media-type-select"] option').map((o) => o.attributes("value"));
    expect(options).toEqual(["text", "pdf", "image"]);
    expect(options).not.toContain("epub");
    expect(options).not.toContain("kindle");
    expect(options).not.toContain("video");
    // disabledとしても表示しない(disabled optionが存在しないこと)
    expect(wrapper.findAll('option[disabled]')).toHaveLength(0);
  });

  test("TC-UI-002-05: 処理開始 [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const sourceService = fakeSourceService();
    registerSourceIpcHandlers({ ipcMain, sourceService });

    const registerHandler = handlers.get("source:register")!;
    const result = (await registerHandler(
      {},
      { projectId: "proj-1", filePath: "materials/ch01.pdf", mediaType: "pdf" },
    )) as SourceSummary;

    // text以外(pdf/image)は登録により処理(PDF直接抽出/OCR)が自動的に開始される前提でservice委譲される
    expect(sourceService.register).toHaveBeenCalledWith(
      expect.objectContaining({ projectId: "proj-1", mediaType: "pdf" }),
    );
    expect(result.status).toBe("registered");
  });

  test("TC-UI-002-07: approval badges [unit/P1]", async () => {
    const { ipcMain, handlers } = fakeIpcMain() as unknown as {
      ipcMain: ApprovalIpcMainLike;
      handlers: Map<string, (...args: unknown[]) => unknown>;
    };
    const approvalService: ApprovalServiceLike = {
      list: vi.fn().mockResolvedValue([
        { gate: "materials_curriculum", status: "approved" },
        { gate: "planning", status: "changes_requested" },
      ]),
      approve: vi.fn(),
      requestChanges: vi.fn(),
    };
    registerApprovalIpcHandlers({ ipcMain, approvalService });

    const listHandler = handlers.get("approval:list")!;
    const result = (await listHandler({}, "proj-1")) as ReadonlyArray<{ gate: string; status: string }>;

    expect(result).toHaveLength(2);
    // 未承認・changes_requestedのgateはそのまま安定した状態文字列として返る(後工程判断は呼び出し側の責務)
    expect(result.find((r) => r.gate === "planning")?.status).toBe("changes_requested");
    expect(approvalService.list).toHaveBeenCalledWith("proj-1");
  });

  test("TC-UI-002-09: 再実行時の決定性 [unit/P1]", async () => {
    const sourceService = fakeSourceService();

    const run = async () => {
      const { ipcMain, handlers } = fakeIpcMain();
      registerSourceIpcHandlers({ ipcMain, sourceService });
      const handler = handlers.get("source:register")!;
      return handler({}, { projectId: "proj-1", filePath: "materials/ch01.txt", mediaType: "text" });
    };

    const first = await run();
    const second = await run();

    expect(first).toEqual(second);
    expect(sourceService.register).toHaveBeenCalledTimes(2); // 実行ごとに1回ずつ
  });
});
