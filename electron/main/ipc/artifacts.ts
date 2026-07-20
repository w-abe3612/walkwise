/**
 * electron/main/ipc/artifacts.ts — 公開契約: artifact:list/open-folder handlers.
 *
 * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
 * Spec: docs/screens/05-artifacts.md
 */

export interface ArtifactSummary {
  readonly artifactId: string;
  readonly artifactType: string;
  readonly versionNumber: number;
  readonly filePath: string;
  readonly createdAt: string;
  readonly jobId: string;
}

export interface ListArtifactsResult {
  readonly artifacts: readonly ArtifactSummary[];
}

export interface ArtifactServiceLike {
  list(projectId: string): Promise<readonly ArtifactSummary[]>;
  openFolder(artifactId: string): Promise<void>;
}

export class ArtifactValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface ArtifactIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly artifactService: ArtifactServiceLike;
}

function assertRelativePath(path: string): void {
  const isAbsolute = path.startsWith("/") || path.startsWith("\\") || /^[a-zA-Z]:[\\/]/.test(path);
  if (isAbsolute || path.split(/[\\/]/).includes("..")) {
    throw new ArtifactValidationError("validation_error", `artifact path must be relative: ${path}`);
  }
}

function requireArtifactId(raw: unknown): string {
  if (typeof raw !== "string" || !raw.trim()) {
    throw new ArtifactValidationError("validation_error", "artifactId is required");
  }
  return raw.trim();
}

/** 相対pathを検証してOSへ委譲する。 */
export function registerArtifactIpcHandlers(context: ArtifactIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.artifactService) {
    throw new Error("artifactService is required");
  }

  context.ipcMain.handle("artifact:list", async (_event: unknown, rawProjectId: unknown): Promise<ListArtifactsResult> => {
    if (typeof rawProjectId !== "string" || !rawProjectId.trim()) {
      throw new ArtifactValidationError("validation_error", "projectId is required");
    }
    const artifacts = await context.artifactService.list(rawProjectId.trim());
    for (const artifact of artifacts) {
      assertRelativePath(artifact.filePath);
    }
    return { artifacts };
  });

  context.ipcMain.handle("artifact:open-folder", async (_event: unknown, rawArtifactId: unknown) => {
    const artifactId = requireArtifactId(rawArtifactId);
    await context.artifactService.openFolder(artifactId);
    return { opened: true };
  });
}
