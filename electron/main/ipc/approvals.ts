/**
 * electron/main/ipc/approvals.ts — 公開契約: approval:list/approve/request-changes handlers.
 *
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Spec: docs/specifications/07-approval-workflow.md,
 *       docs/screens/02-project-workspace-and-source-import.md(10節)
 */

export interface ApprovalSummary {
  readonly gate: string;
  readonly status: string;
  readonly comment?: string;
}

export interface ApproveInput {
  readonly projectId: string;
  readonly gate: string;
  readonly approvedBy: string;
}

export interface RequestChangesInput {
  readonly projectId: string;
  readonly gate: string;
  readonly reason: string;
}

export interface ApprovalServiceLike {
  list(projectId: string): Promise<readonly ApprovalSummary[]>;
  approve(input: ApproveInput): Promise<ApprovalSummary>;
  requestChanges(input: RequestChangesInput): Promise<ApprovalSummary>;
}

export class ApprovalValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface ApprovalIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly approvalService: ApprovalServiceLike;
}

function requireNonEmptyString(value: unknown, field: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new ApprovalValidationError("validation_error", `${field} is required`);
  }
  return value.trim();
}

function validateApproveInput(raw: unknown): ApproveInput {
  if (!raw || typeof raw !== "object") {
    throw new ApprovalValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;
  return {
    projectId: requireNonEmptyString(input.projectId, "projectId"),
    gate: requireNonEmptyString(input.gate, "gate"),
    approvedBy: requireNonEmptyString(input.approvedBy, "approvedBy"),
  };
}

function validateRequestChangesInput(raw: unknown): RequestChangesInput {
  if (!raw || typeof raw !== "object") {
    throw new ApprovalValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;
  return {
    projectId: requireNonEmptyString(input.projectId, "projectId"),
    gate: requireNonEmptyString(input.gate, "gate"),
    // 02-project-workspace-and-source-import.md 10節: 差し戻しは理由入力(必須)を伴う。
    reason: requireNonEmptyString(input.reason, "reason"),
  };
}

/** 差し戻し理由とgateを検証する。 */
export function registerApprovalIpcHandlers(context: ApprovalIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.approvalService) {
    throw new Error("approvalService is required");
  }

  context.ipcMain.handle("approval:list", async (_event: unknown, projectId: unknown) => {
    const validated = requireNonEmptyString(projectId, "projectId");
    return context.approvalService.list(validated);
  });

  context.ipcMain.handle("approval:approve", async (_event: unknown, rawInput: unknown) => {
    const validated = validateApproveInput(rawInput);
    return context.approvalService.approve(validated);
  });

  context.ipcMain.handle("approval:request-changes", async (_event: unknown, rawInput: unknown) => {
    const validated = validateRequestChangesInput(rawInput);
    return context.approvalService.requestChanges(validated);
  });
}
