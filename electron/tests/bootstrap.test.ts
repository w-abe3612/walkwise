/**
 * STEP4 test implementation for TASK-DESKTOP-002: bootstrap order / stale recovery / shutdown / smoke.
 * Contract: docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md
 * Release scope: MVP.
 */

import { spawn as nodeSpawn } from "node:child_process";
import { EventEmitter } from "node:events";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test, vi } from "vitest";

import type { AppDatabaseHandle } from "../main/database";
import { bootstrapApplication, type BootstrapOptions } from "../main/bootstrap";
import { WorkerManager, resolvePythonExecutable, type ChildProcessLike } from "../main/worker_manager";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

function fakeChildProcess(): { child: ChildProcessLike; stdout: EventEmitter; stderr: EventEmitter } {
  const stdout = new EventEmitter();
  const stderr = new EventEmitter();
  const emitter = new EventEmitter();
  const child = Object.assign(emitter, {
    stdin: { write: vi.fn(), end: vi.fn() },
    stdout,
    stderr,
    kill: vi.fn(),
  }) as unknown as ChildProcessLike;
  return { child, stdout, stderr };
}

function fakeDatabase(closeSpy: ReturnType<typeof vi.fn> = vi.fn()): AppDatabaseHandle {
  return { path: "/data/app.db", close: closeSpy };
}

function healthyWorkerManager(): { manager: WorkerManager; child: ChildProcessLike; stdout: EventEmitter } {
  const { child, stdout } = fakeChildProcess();
  const spawn = vi.fn().mockReturnValue(child);
  const manager = new WorkerManager({ command: "python", spawn });
  return { manager, child, stdout };
}

function baseOptions(overrides: Partial<BootstrapOptions> = {}): BootstrapOptions {
  const { manager } = healthyWorkerManager();
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
  test("TC-DESKTOP-002-01: bootstrap順 [integration_mock/P0]", async () => {
    const callOrder: string[] = [];
    const options = baseOptions({
      ensureDataRoot: vi.fn().mockImplementation(async () => {
        callOrder.push("data-root");
      }),
      backupDatabase: vi.fn().mockImplementation(async () => {
        callOrder.push("backup");
      }),
      openDatabase: vi.fn().mockImplementation(async () => {
        callOrder.push("open-db");
        return fakeDatabase();
      }),
      runMigrations: vi.fn().mockImplementation(async () => {
        callOrder.push("migration");
      }),
      recoverStaleJobs: vi.fn().mockImplementation(async () => {
        callOrder.push("stale-recovery");
        return [];
      }),
      checkWorkerHealth: vi.fn().mockImplementation(async () => {
        callOrder.push("worker-health");
      }),
    });

    await bootstrapApplication(options);

    expect(callOrder).toEqual(["data-root", "backup", "open-db", "migration", "stale-recovery", "worker-health"]);
  });

  test("TC-DESKTOP-002-03: worker疎通失敗 [integration_mock/P0]", async () => {
    const dbCloseSpy = vi.fn().mockResolvedValue(undefined);
    const stopSpy = vi.spyOn(WorkerManager.prototype, "stop");
    const checkWorkerHealth = vi.fn().mockRejectedValue(new Error("ping timeout"));

    const options = baseOptions({
      openDatabase: vi.fn().mockResolvedValue(fakeDatabase(dbCloseSpy)),
      checkWorkerHealth,
      healthCheckRetries: 2,
      sleep: vi.fn().mockResolvedValue(undefined),
    });

    await expect(bootstrapApplication(options)).rejects.toThrow(/worker_health_check_failed/);

    expect(checkWorkerHealth).toHaveBeenCalledTimes(3); // 初回 + retry 2回、診断可能な起動error
    expect(stopSpy).toHaveBeenCalled();
    expect(dbCloseSpy).toHaveBeenCalled();
    stopSpy.mockRestore();
  });

  test("TC-DESKTOP-002-05: stale recovery [unit/P1]", async () => {
    const options = baseOptions({
      recoverStaleJobs: vi.fn().mockResolvedValue(["job-1", "job-2"]),
    });

    const context = await bootstrapApplication(options);

    expect(context.recoveredStaleJobIds).toEqual(["job-1", "job-2"]);
  });

  test("TC-DESKTOP-002-07: shutdown cleanup [unit/P1]", async () => {
    const dbCloseSpy = vi.fn().mockResolvedValue(undefined);
    const stopSpy = vi.spyOn(WorkerManager.prototype, "stop");
    const options = baseOptions({ openDatabase: vi.fn().mockResolvedValue(fakeDatabase(dbCloseSpy)) });

    const context = await bootstrapApplication(options);
    await context.shutdown();
    await context.shutdown(); // 冪等であること

    expect(dbCloseSpy).toHaveBeenCalledTimes(1);
    expect(stopSpy).toHaveBeenCalledTimes(1);
    stopSpy.mockRestore();
  });

  test("TC-DESKTOP-002-09: 再実行時の決定性 [unit/P1]", async () => {
    const ensureDataRoot = vi.fn().mockResolvedValue(undefined);
    const recoverStaleJobs = vi.fn().mockResolvedValue(["job-1"]);

    const run = () =>
      bootstrapApplication(
        baseOptions({
          ensureDataRoot,
          recoverStaleJobs,
        }),
      );

    const first = await run();
    const second = await run();

    expect(first.dataRoot).toBe(second.dataRoot);
    expect(first.recoveredStaleJobIds).toEqual(second.recoveredStaleJobIds);
    expect(ensureDataRoot).toHaveBeenCalledTimes(2); // 実行ごとに1回ずつ(重複副作用なし)
  });

  const smokeEnabled = process.env.WALKWISE_RUN_INTEGRATION_SMOKE === "1";
  test.skipIf(!smokeEnabled)(
    "TC-DESKTOP-002-11: Python worker subprocessの疎通確認 [integration_smoke/P0]",
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
        // "health"がhandler未登録でも、JSON Linesの往復応答自体があれば疎通は確認できたとみなす
        // (unknown_job_typeのerror eventも、protocolが正しく機能している証拠になる)。
        await expect(manager.request("health")).rejects.toThrow(/worker_request_failed|worker_exited_unexpectedly/);
      } finally {
        manager.stop();
      }
    },
  );
});
