/**
 * electron/main/app_entry.ts — 公開契約: run(overrides?): Promise<AppContext>(実Electron起動のcomposition root).
 *
 * TASK-REVIEW-001監査2.1節: `electron/main/index.ts`は`createMainWindow()`をexportするだけで、
 * `app.whenReady()`を実際に呼び出すコードがどこにも存在せず、`npm start`相当の実行手段がなかった。
 * 本fileが、data root確保→(backup)→DB open/migration→stale job recovery→Python Worker起動→
 * health確認→全IPC handler登録→BrowserWindow作成、という実際の起動処理をすべて行う唯一の
 * entrypointとなる。
 *
 * `electron/main/index.ts`の既存契約(`createMainWindow`)はそのまま維持し、ここから利用する
 * (main_security.test.ts等、`../main/index`をelectron mock環境でimportする既存testが、
 * 意図せず`app.whenReady()`を実行してしまわないよう、実行処理はこの別fileへ分離した)。
 *
 * DBスキーマ・業務ロジックはPython Worker側(script/persistence, script/services)にのみ
 * 存在させる設計とし(21-electron-python-worker-interface.md)、Electron mainはWorker
 * subprocessへの単一の常駐接続(WorkerManager)を介してのみDBを操作する。openDatabase/
 * runMigrations/recoverStaleJobsは、bootstrap.tsの既存契約上「DB操作を行う関数」として
 * 注入されるが、実体はすべて同じWorkerManager経由のrequestに委譲する。
 *
 * Spec: docs/specifications/20-electron-desktop-architecture.md,
 *       docs/specifications/21-electron-python-worker-interface.md,
 *       docs/specifications/17-local-data-persistence-policy.md(5.4, 5.5節)
 */

import { spawn as nodeSpawn } from "node:child_process";
import { existsSync } from "node:fs";
import { copyFile, mkdir } from "node:fs/promises";
import path from "node:path";

import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";

import type { AppContext } from "./bootstrap";
import { bootstrapApplication } from "./bootstrap";
import type { AppDatabaseHandle } from "./database";
import { createMainWindow } from "./index";
import { registerApprovalIpcHandlers } from "./ipc/approvals";
import { registerArtifactIpcHandlers } from "./ipc/artifacts";
import { registerBuildIpcHandlers } from "./ipc/builds";
import { registerFileDialogIpcHandlers } from "./ipc/files";
import { registerJobIpcHandlers } from "./ipc/jobs";
import { registerProjectIpcHandlers } from "./ipc/projects";
import { registerSourceIpcHandlers } from "./ipc/sources";
import { registerVoiceIpcHandlers } from "./ipc/voice";
import { resolvePythonExecutable, WorkerManager, type ChildProcessLike, type WorkerRequestResult } from "./worker_manager";
import {
  createApprovalGateCheckerAdapter,
  createApprovalServiceAdapter,
  createArtifactServiceAdapter,
  createBuildServiceAdapter,
  createJobServiceAdapter,
  createProjectServiceAdapter,
  createSourceServiceAdapter,
  createVoiceServiceAdapter,
} from "./worker_service_adapters";

export const REPO_ROOT = path.resolve(__dirname, "..", "..");

export interface AppEntryOverrides {
  readonly dataRoot?: string;
  readonly databaseFileName?: string;
  readonly createWindow?: (preloadPath: string, rendererEntry: string) => void;
  readonly preloadPath?: string;
  readonly rendererEntry?: string;
}

function extractResult(outcome: WorkerRequestResult): Record<string, unknown> {
  return (outcome.terminalEvent.result as Record<string, unknown> | undefined) ?? {};
}

/**
 * dataRoot/databaseFileNameからPython Worker subprocessを構築し、bootstrapApplicationの
 * openDatabase/runMigrations/recoverStaleJobs/createWorkerManagerをすべてこの1つの
 * WorkerManagerへ委譲する(21-electron-python-worker-interface.mdの単一常駐subprocess設計)。
 */
export async function runCompositionRoot(overrides: AppEntryOverrides = {}): Promise<AppContext> {
  const dataRoot = overrides.dataRoot ?? app.getPath("userData");
  const databaseFileName = overrides.databaseFileName ?? "app.db";
  const databasePath = `${dataRoot}/${databaseFileName}`;

  const pythonExecutable = resolvePythonExecutable({ env: process.env, platform: process.platform });
  const workerEnv = { ...process.env, WALKWISE_DB_PATH: databasePath };

  const workerManager = new WorkerManager({
    command: pythonExecutable,
    args: ["-m", "script.worker.cli"],
    spawn: (command: string, args: readonly string[]): ChildProcessLike =>
      nodeSpawn(command, [...args], { cwd: REPO_ROOT, env: workerEnv }) as unknown as ChildProcessLike,
    onStderr: (chunk: string) => {
      // 利用者向け画面にはこの内容を一切表示しない(技術ログ専用、21節5.4節)。
      console.error(`[worker] ${chunk}`);
    },
  });

  const context = await bootstrapApplication({
    dataRoot,
    databaseFileName,
    ensureDataRoot: async (root: string) => {
      await mkdir(root, { recursive: true });
    },
    backupDatabase: async (dbPath: string) => {
      // 17-local-data-persistence-policy.md 5.5節: migration前の自動backup。
      // DBの中身の解釈は一切行わない単純なbyte copyのため、Node側で直接行ってよい
      // (Worker起動前に必要な処理であり、Worker常駐接続の対象外)。
      if (existsSync(dbPath)) {
        await copyFile(dbPath, `${dbPath}.bak`);
      }
    },
    openDatabase: async (dbPath: string): Promise<AppDatabaseHandle> => {
      // 実DB接続はWorker subprocess側(script/persistence/database.py)にのみ存在する。
      // ここではpathを保持するだけの軽量handleを返す(closeはworkerManager.stop()に集約)。
      return { path: dbPath, close: async () => {} };
    },
    runMigrations: async () => {
      workerManager.start(); // 冪等: 既に起動済みなら何もしない
      await workerManager.request("db.migrate", {});
    },
    recoverStaleJobs: async (): Promise<readonly string[]> => {
      const outcome = await workerManager.request("job.recover_stale", {});
      const result = extractResult(outcome);
      return (result.recovered_job_ids as string[] | undefined) ?? [];
    },
    createWorkerManager: () => workerManager,
    checkWorkerHealth: async (manager) => {
      await manager.request("health", {});
    },
  });

  // bootstrapApplication自体はDB/Workerの後始末を保証するが(migration/health check失敗時)、
  // ここから先(IPC登録・BrowserWindow作成)で例外が起きた場合、bootstrap済みのcontextを
  // 呼び出し側へ一切返せなくなり、Workerがcleanupされずに残り続ける(TASK-REVIEW-001指摘の
  // 資源leak)。そのため、この区間で失敗したら必ずcontext.shutdown()してから再送出する。
  try {
    const projectService = createProjectServiceAdapter(workerManager);
    const sourceService = createSourceServiceAdapter(workerManager);
    const approvalService = createApprovalServiceAdapter(workerManager);
    const buildService = createBuildServiceAdapter(workerManager);
    const jobService = createJobServiceAdapter(workerManager);
    const artifactService = createArtifactServiceAdapter(workerManager, dataRoot, shell);
    const voiceService = createVoiceServiceAdapter(workerManager);
    const approvalGateChecker = createApprovalGateCheckerAdapter(workerManager);

    // すべてのIPC handlerを、実Electronの単一ipcMain上へ登録する(channel重複がないことは
    // electron/tests/app_entry.test.tsで検証する)。
    registerProjectIpcHandlers({ ipcMain, projectService });
    registerSourceIpcHandlers({ ipcMain, sourceService });
    registerApprovalIpcHandlers({ ipcMain, approvalService });
    registerBuildIpcHandlers({ ipcMain, buildService, approvalGateChecker, jobService });
    registerJobIpcHandlers({ ipcMain, jobService });
    registerArtifactIpcHandlers({ ipcMain, artifactService });
    registerVoiceIpcHandlers({ ipcMain, voiceService });
    registerFileDialogIpcHandlers({ ipcMain, dialog });

    const preloadPath = overrides.preloadPath ?? path.join(__dirname, "..", "preload", "index.js");
    const rendererEntry = overrides.rendererEntry ?? path.join(__dirname, "..", "renderer", "index.html");

    if (overrides.createWindow) {
      overrides.createWindow(preloadPath, rendererEntry);
    } else {
      createMainWindow({ preloadPath, rendererEntry });
    }
  } catch (error) {
    await context.shutdown();
    throw error;
  }

  return context;
}

let activeContext: AppContext | null = null;

async function shutdownAndQuit(): Promise<void> {
  if (activeContext) {
    await activeContext.shutdown();
    activeContext = null;
  }
}

/** 実Electronプロセスのentrypoint。`npm run start`/packaged appから呼び出される。 */
export async function main(): Promise<void> {
  await app.whenReady();

  try {
    activeContext = await runCompositionRoot();
  } catch (error) {
    // bootstrap失敗時、DB/Workerの後始末をした上でユーザーへ分かる形で終了する
    // (禁止事項: 起動失敗を隠してrelease readyと誤認させない)。
    console.error("[app_entry] bootstrap failed:", error);
    await shutdownAndQuit();
    app.exit(1);
    return;
  }

  app.on("window-all-closed", () => {
    void shutdownAndQuit().finally(() => {
      if (process.platform !== "darwin") {
        app.quit();
      }
    });
  });

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      void runCompositionRoot();
    }
  });

  app.on("before-quit", () => {
    void shutdownAndQuit();
  });
}
