/**
 * STEP4 test implementation for TASK-DESKTOP-002: migration failure / data root / python resolution /
 * required inputs / invariance / worker manager live smoke.
 * Contract: docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md
 * Release scope: MVP.
 */

import { spawn as nodeSpawn } from "node:child_process";
import { EventEmitter } from "node:events";
import { mkdtempSync, readFileSync, writeFileSync, copyFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test, vi } from "vitest";

import type { AppDatabaseHandle } from "../main/database";
import { bootstrapApplication, type BootstrapOptions } from "../main/bootstrap";
import { WorkerManager, resolvePythonExecutable, type ChildProcessLike } from "../main/worker_manager";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

function fakeChildProcess(): { child: ChildProcessLike; stdout: EventEmitter } {
  const stdout = new EventEmitter();
  const stderr = new EventEmitter();
  const emitter = new EventEmitter();
  const child = Object.assign(emitter, {
    stdin: { write: vi.fn(), end: vi.fn() },
    stdout,
    stderr,
    kill: vi.fn(),
  }) as unknown as ChildProcessLike;
  return { child, stdout };
}

function fakeDatabase(closeSpy: ReturnType<typeof vi.fn> = vi.fn()): AppDatabaseHandle {
  return { path: "/data/app.db", close: closeSpy };
}

function baseOptions(overrides: Partial<BootstrapOptions> = {}): BootstrapOptions {
  const { child } = fakeChildProcess();
  const spawn = vi.fn().mockReturnValue(child);
  const manager = new WorkerManager({ command: "python", spawn });
  return {
    dataRoot: "/data",
    openDatabase: vi.fn().mockResolvedValue(fakeDatabase()),
    runMigrations: vi.fn().mockResolvedValue(undefined),
    recoverStaleJobs: vi.fn().mockResolvedValue([]),
    createWorkerManager: vi.fn().mockReturnValue(manager),
    checkWorkerHealth: vi.fn().mockResolvedValue(undefined),
    ...overrides,
  };
}

describe("TASK-DESKTOP-002 Electron起動時data/DB/worker bootstrap", () => {
  test("TC-DESKTOP-002-02: migration失敗 [integration_mock/P0]", async () => {
    const dbCloseSpy = vi.fn().mockResolvedValue(undefined);
    const createWorkerManager = vi.fn();

    const options = baseOptions({
      openDatabase: vi.fn().mockResolvedValue(fakeDatabase(dbCloseSpy)),
      runMigrations: vi.fn().mockRejectedValue(new Error("schema mismatch")),
      createWorkerManager,
    });

    await expect(bootstrapApplication(options)).rejects.toThrow(/migration_failed/);

    expect(createWorkerManager).not.toHaveBeenCalled(); // workerを一切開始しない
    expect(dbCloseSpy).toHaveBeenCalled(); // 部分初期化状態を放置しない
  });

  test("TC-DESKTOP-002-04: appData配下root [unit/P1]", async () => {
    const ensureDataRoot = vi.fn().mockResolvedValue(undefined);
    const openDatabase = vi.fn().mockResolvedValue(fakeDatabase());

    const options = baseOptions({ dataRoot: "/home/user/.config/walkwise", ensureDataRoot, openDatabase });
    const context = await bootstrapApplication(options);

    expect(ensureDataRoot).toHaveBeenCalledWith("/home/user/.config/walkwise");
    expect(openDatabase).toHaveBeenCalledWith("/home/user/.config/walkwise/app.db");
    expect(context.dataRoot).toBe("/home/user/.config/walkwise");
  });

  test("TC-DESKTOP-002-06: Python executable解決 [unit/P1]", () => {
    expect(resolvePythonExecutable({ env: { WALKWISE_PYTHON_EXECUTABLE: "C:\\Python\\python.exe" }, platform: "win32" })).toBe(
      "C:\\Python\\python.exe",
    );
    expect(resolvePythonExecutable({ env: {}, platform: "win32" })).toBe("python");
    expect(resolvePythonExecutable({ env: {}, platform: "linux" })).toBe("python3");
    expect(resolvePythonExecutable({ env: { WALKWISE_PYTHON_EXECUTABLE: "  " }, platform: "linux" })).toBe("python3");
  });

  test("TC-DESKTOP-002-08: 必須入力欠落 [unit/P0]", async () => {
    const openDatabase = vi.fn();
    await expect(
      bootstrapApplication({ ...baseOptions(), dataRoot: "", openDatabase } as unknown as BootstrapOptions),
    ).rejects.toThrow();
    expect(openDatabase).not.toHaveBeenCalled(); // 副作用開始前に検証error

    expect(() => new WorkerManager({ command: "", spawn: vi.fn() })).toThrow();
    expect(() => new WorkerManager({ command: "python", spawn: undefined as never })).toThrow();
  });

  test("TC-DESKTOP-002-10: 入力・既存成果物の不変性 [unit/P0]", async () => {
    const tmpDir = mkdtempSync(path.join(tmpdir(), "walkwise-desktop-002-"));
    try {
      const dbPath = path.join(tmpDir, "app.db");
      const backupPath = path.join(tmpDir, "app.db.bak");
      writeFileSync(dbPath, "existing-good-db-bytes");
      const beforeBytes = readFileSync(dbPath);

      const options = baseOptions({
        dataRoot: tmpDir,
        backupDatabase: async (databasePath: string) => {
          copyFileSync(databasePath, backupPath);
        },
        runMigrations: vi.fn().mockRejectedValue(new Error("simulated migration failure")),
      });

      await expect(bootstrapApplication(options)).rejects.toThrow(/migration_failed/);

      expect(readFileSync(dbPath)).toEqual(beforeBytes); // 既存正常成果物は変化しない
      expect(readFileSync(backupPath)).toEqual(beforeBytes); // backupは正しく複製されている
    } finally {
      rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  const liveEnabled = process.env.WALKWISE_RUN_INTEGRATION_LIVE === "1";
  test.skipIf(!liveEnabled)(
    "TC-DESKTOP-002-12: Python worker subprocessの実機能テスト [integration_live/P1]",
    async () => {
      const pythonExecutable = resolvePythonExecutable({ env: process.env, platform: process.platform });
      const manager = new WorkerManager({
        command: pythonExecutable,
        args: ["-m", "script.worker.cli"],
        spawn: (command, args) =>
          nodeSpawn(command, args, { cwd: REPO_ROOT }) as unknown as ChildProcessLike,
      });

      manager.start();
      try {
        await expect(manager.request("health")).rejects.toThrow(/worker_request_failed/);
      } finally {
        manager.stop();
      }
    },
  );
});
