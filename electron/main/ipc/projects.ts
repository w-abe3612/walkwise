/**
 * electron/main/ipc/projects.ts — 公開契約: registerProjectIpcHandlers(context).
 *
 * Contract: docs/test-cases/TASK-UI-001-project-list-and-create-screen.md
 * Spec: docs/screens/01-project-list-and-create.md,
 *       docs/specifications/20-electron-desktop-architecture.md(5.6節)
 */

export interface ProjectSummary {
  readonly projectId: string;
  readonly title: string;
  readonly planningStage: string;
  readonly updatedAt: string;
}

export interface CreateProjectInput {
  readonly title: string;
  readonly domain: string;
  readonly purpose: string;
  readonly usagePurpose: string;
  readonly targetAudienceDescription: string;
  readonly sourceStrategy: readonly string[];
}

export interface ProjectServiceLike {
  list(): Promise<readonly ProjectSummary[]>;
  create(input: CreateProjectInput): Promise<ProjectSummary>;
}

export class ProjectValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface ProjectIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly projectService: ProjectServiceLike;
}

const REQUIRED_STRING_FIELDS = [
  "title",
  "domain",
  "purpose",
  "usagePurpose",
  "targetAudienceDescription",
] as const;

function validateCreateProjectInput(raw: unknown): CreateProjectInput {
  if (!raw || typeof raw !== "object") {
    throw new ProjectValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;

  for (const field of REQUIRED_STRING_FIELDS) {
    const value = input[field];
    if (typeof value !== "string" || !value.trim()) {
      throw new ProjectValidationError("validation_error", `${field} is required`);
    }
  }

  const sourceStrategy = input.sourceStrategy;
  if (!Array.isArray(sourceStrategy) || sourceStrategy.length === 0) {
    throw new ProjectValidationError("validation_error", "sourceStrategy requires at least one selection");
  }
  if (!sourceStrategy.every((entry) => typeof entry === "string" && entry.trim().length > 0)) {
    throw new ProjectValidationError("validation_error", "sourceStrategy entries must be non-empty strings");
  }

  return {
    title: (input.title as string).trim(),
    domain: (input.domain as string).trim(),
    purpose: (input.purpose as string).trim(),
    usagePurpose: (input.usagePurpose as string).trim(),
    targetAudienceDescription: (input.targetAudienceDescription as string).trim(),
    sourceStrategy: sourceStrategy as readonly string[],
  };
}

/** project:list/createをschema検証してserviceへ委譲する。 */
export function registerProjectIpcHandlers(context: ProjectIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.projectService) {
    throw new Error("projectService is required");
  }

  context.ipcMain.handle("project:list", async () => {
    const projects = await context.projectService.list();
    return { projects };
  });

  context.ipcMain.handle("project:create", async (_event: unknown, rawInput: unknown) => {
    const validated = validateCreateProjectInput(rawInput);
    return context.projectService.create(validated);
  });
}
