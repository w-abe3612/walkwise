/**
 * electron/preload/index.ts — 公開契約: window.walkwise API.
 *
 * Contract: docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md
 * Spec: docs/specifications/20-electron-desktop-architecture.md(5.3, 5.4, 5.6節)
 */

import { contextBridge, ipcRenderer } from "electron";

/** 20-electron-desktop-architecture.md 5.6節で固定されたIPCチャネル名の一覧。 */
export const ALLOWED_CHANNELS = [
  "project:list",
  "project:create",
  "project:get",
  "source:register",
  "approval:list",
  "approval:approve",
  "approval:request-changes",
  "build-request:create",
  "job:start",
  "job:get",
  "job:subscribe-progress",
  "job:cancel",
  "artifact:list",
  "artifact:open-folder",
  "voice:list-engines",
  "voice:preview",
] as const;

export type AllowedChannel = (typeof ALLOWED_CHANNELS)[number];

export interface IpcRendererLike {
  invoke(channel: AllowedChannel, ...args: readonly unknown[]): Promise<unknown>;
  on(channel: AllowedChannel, listener: (...args: readonly unknown[]) => void): void;
  removeListener(channel: AllowedChannel, listener: (...args: readonly unknown[]) => void): void;
}

export interface ContextBridgeLike {
  exposeInMainWorld(apiKey: string, api: unknown): void;
}

export interface WalkwiseApi {
  readonly project: {
    list(): Promise<unknown>;
    create(input: unknown): Promise<unknown>;
    get(projectId: string): Promise<unknown>;
  };
  readonly source: {
    register(input: unknown): Promise<unknown>;
  };
  readonly approval: {
    list(projectId: string): Promise<unknown>;
    approve(input: unknown): Promise<unknown>;
    requestChanges(input: unknown): Promise<unknown>;
  };
  readonly buildRequest: {
    create(input: unknown): Promise<unknown>;
  };
  readonly job: {
    start(input: unknown): Promise<unknown>;
    get(jobId: string): Promise<unknown>;
    subscribeProgress(jobId: string, listener: (event: unknown) => void): () => void;
    cancel(jobId: string): Promise<unknown>;
  };
  readonly artifact: {
    list(projectId: string): Promise<unknown>;
    openFolder(artifactId: string): Promise<unknown>;
  };
  readonly voice: {
    listEngines(): Promise<unknown>;
    preview(input: unknown): Promise<unknown>;
  };
}

function requireIpcRenderer(ipc: IpcRendererLike | null | undefined): IpcRendererLike {
  if (!ipc) {
    throw new Error("ipcRenderer is required to build the walkwise preload API");
  }
  return ipc;
}

/** 固定allowlistの範囲でだけ型付きIPC呼び出しを行うAPIを構築する(rendererへは本関数の戻り値だけを公開する)。 */
export function buildWalkwiseApi(ipc: IpcRendererLike | null | undefined): WalkwiseApi {
  const rendererIpc = requireIpcRenderer(ipc);

  return {
    project: {
      list: () => rendererIpc.invoke("project:list"),
      create: (input: unknown) => rendererIpc.invoke("project:create", input),
      get: (projectId: string) => rendererIpc.invoke("project:get", projectId),
    },
    source: {
      register: (input: unknown) => rendererIpc.invoke("source:register", input),
    },
    approval: {
      list: (projectId: string) => rendererIpc.invoke("approval:list", projectId),
      approve: (input: unknown) => rendererIpc.invoke("approval:approve", input),
      requestChanges: (input: unknown) => rendererIpc.invoke("approval:request-changes", input),
    },
    buildRequest: {
      create: (input: unknown) => rendererIpc.invoke("build-request:create", input),
    },
    job: {
      start: (input: unknown) => rendererIpc.invoke("job:start", input),
      get: (jobId: string) => rendererIpc.invoke("job:get", jobId),
      subscribeProgress: (jobId: string, listener: (event: unknown) => void) => {
        const wrapped = (...args: readonly unknown[]) => listener(args[0]);
        rendererIpc.on("job:subscribe-progress", wrapped);
        void rendererIpc.invoke("job:subscribe-progress", jobId);
        return () => rendererIpc.removeListener("job:subscribe-progress", wrapped);
      },
      cancel: (jobId: string) => rendererIpc.invoke("job:cancel", jobId),
    },
    artifact: {
      list: (projectId: string) => rendererIpc.invoke("artifact:list", projectId),
      openFolder: (artifactId: string) => rendererIpc.invoke("artifact:open-folder", artifactId),
    },
    voice: {
      listEngines: () => rendererIpc.invoke("voice:list-engines"),
      preview: (input: unknown) => rendererIpc.invoke("voice:preview", input),
    },
  };
}

/** contextBridge経由でwindow.walkwiseとしてAPIを公開する。 */
export function installPreloadBridge(
  bridge: ContextBridgeLike | null | undefined,
  ipc: IpcRendererLike | null | undefined,
): void {
  if (!bridge) {
    throw new Error("contextBridge is required to install the walkwise preload API");
  }
  const api = buildWalkwiseApi(ipc);
  bridge.exposeInMainWorld("walkwise", api);
}

// 実Electron preload実行時のみ自動的に公開する(vitest等のNode実行時は発火しない)。
if (typeof process !== "undefined" && process.versions?.electron) {
  installPreloadBridge(contextBridge, ipcRenderer);
}
