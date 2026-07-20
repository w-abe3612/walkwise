/**
 * electron/main/ipc/sources.ts — 公開契約: source:register handlers.
 *
 * Contract: docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md
 * Spec: docs/screens/02-project-workspace-and-source-import.md(4, 8節)
 */

export interface SourceSummary {
  readonly sourceId: string;
  readonly projectId: string;
  readonly mediaType: string;
  readonly status: string;
}

export interface RegisterSourceInput {
  readonly projectId: string;
  readonly filePath: string;
  readonly mediaType: string;
}

export interface SourceServiceLike {
  register(input: RegisterSourceInput): Promise<SourceSummary>;
  list(projectId: string): Promise<readonly SourceSummary[]>;
  retry(sourceId: string): Promise<SourceSummary>;
}

export class SourceValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface SourceIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly sourceService: SourceServiceLike;
}

/** 02-project-workspace-and-source-import.md 13節: MVP対象外形式(epub/kindle/video等)は登録できない。 */
const ALLOWED_MEDIA_TYPES = new Set(["text", "pdf", "image"]);

function validateRegisterSourceInput(raw: unknown): RegisterSourceInput {
  if (!raw || typeof raw !== "object") {
    throw new SourceValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;

  if (typeof input.projectId !== "string" || !input.projectId.trim()) {
    throw new SourceValidationError("validation_error", "projectId is required");
  }
  if (typeof input.filePath !== "string" || !input.filePath.trim()) {
    throw new SourceValidationError("validation_error", "filePath is required");
  }
  if (typeof input.mediaType !== "string" || !ALLOWED_MEDIA_TYPES.has(input.mediaType)) {
    throw new SourceValidationError("unsupported_media_type", `unsupported media_type: ${String(input.mediaType)}`);
  }

  return {
    projectId: input.projectId.trim(),
    filePath: input.filePath.trim(),
    mediaType: input.mediaType,
  };
}

/** path/media typeをmainで再検証しSource serviceへ委譲する。 */
export function registerSourceIpcHandlers(context: SourceIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.sourceService) {
    throw new Error("sourceService is required");
  }

  context.ipcMain.handle("source:register", async (_event: unknown, rawInput: unknown) => {
    const validated = validateRegisterSourceInput(rawInput);
    return context.sourceService.register(validated);
  });

  context.ipcMain.handle("source:list", async (_event: unknown, rawProjectId: unknown) => {
    if (typeof rawProjectId !== "string" || !rawProjectId.trim()) {
      throw new SourceValidationError("validation_error", "projectId is required");
    }
    const sources = await context.sourceService.list(rawProjectId.trim());
    return { sources };
  });

  context.ipcMain.handle("source:retry", async (_event: unknown, rawSourceId: unknown) => {
    if (typeof rawSourceId !== "string" || !rawSourceId.trim()) {
      throw new SourceValidationError("validation_error", "sourceId is required");
    }
    return context.sourceService.retry(rawSourceId.trim());
  });
}
