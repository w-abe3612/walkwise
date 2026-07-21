/**
 * Tests for TASK-REVIEW-001 P0 fix: real Electron composition root.
 *
 * Before this fix, `electron/main/index.ts` only exported `createMainWindow()` — nothing in
 * the codebase ever called `app.whenReady()`, so there was no way to actually launch the app
 * (`npm start` had no real entrypoint). `electron/main/app_entry.ts` now performs the real
 * bootstrap: data root -> DB open/migration (via the Python Worker subprocess) -> stale job
 * recovery -> IPC registration on a single ipcMain -> BrowserWindow creation.
 *
 * This test fakes the "electron" module and the Python subprocess (via node:child_process'
 * spawn) so it can run the *real* runCompositionRoot() wiring without a display or a real
 * Python interpreter, while still proving every IPC handler is registered exactly once and
 * the full bootstrap sequence (including a real WorkerManager <-> fake subprocess round trip)
 * succeeds.
 */

import { EventEmitter } from "node:events";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

const registeredHandlers = new Map<string, (...args: unknown[]) => unknown>();
const createdWindows: unknown[] = [];
const appEventHandlers = new Map<string, Array<() => void>>();

vi.mock("electron", () => {
  return {
    app: {
      getPath: vi.fn().mockReturnValue("/fake/user-data"),
      whenReady: vi.fn().mockResolvedValue(undefined),
      on: vi.fn((event: string, handler: () => void) => {
        const handlers = appEventHandlers.get(event) ?? [];
        handlers.push(handler);
        appEventHandlers.set(event, handlers);
      }),
      quit: vi.fn(),
      exit: vi.fn(),
    },
    BrowserWindow: Object.assign(
      vi.fn().mockImplementation((options: unknown) => {
        const win = { options, loadFile: vi.fn(), loadURL: vi.fn() };
        createdWindows.push(win);
        return win;
      }),
      { getAllWindows: vi.fn().mockReturnValue([]) },
    ),
    ipcMain: {
      handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
        if (registeredHandlers.has(channel)) {
          throw new Error(`duplicate ipcMain.handle registration for channel: ${channel}`);
        }
        registeredHandlers.set(channel, listener);
      }),
    },
    shell: { showItemInFolder: vi.fn() },
    dialog: { showOpenDialog: vi.fn().mockResolvedValue({ canceled: true, filePaths: [] }) },
  };
});

type FakeResponder = (parameters: Record<string, unknown>) => Record<string, unknown>;

const RESPONDERS: Record<string, FakeResponder> = {
  health: () => ({ status: "ok" }),
  "db.migrate": () => ({ applied: [] }),
  "job.recover_stale": () => ({ recovered_job_ids: [] }),
};

vi.mock("node:child_process", () => {
  return {
    spawn: vi.fn(() => {
      const stdout = new EventEmitter();
      const stderr = new EventEmitter();
      const emitter = new EventEmitter();
      const child = Object.assign(emitter, {
        stdin: {
          write: (chunk: string) => {
            for (const line of chunk.split("\n")) {
              if (!line.trim()) continue;
              const request = JSON.parse(line) as { job_id: string; job_type: string };
              const responder = RESPONDERS[request.job_type];
              stdout.emit("data", `${JSON.stringify({ event: "started", job_id: request.job_id })}\n`);
              if (!responder) {
                stdout.emit(
                  "data",
                  `${JSON.stringify({ event: "error", job_id: request.job_id, code: "unknown_job_type", message: request.job_type })}\n`,
                );
                continue;
              }
              stdout.emit(
                "data",
                `${JSON.stringify({ event: "completed", job_id: request.job_id, result: responder({}) })}\n`,
              );
            }
          },
        },
        stdout,
        stderr,
        kill: vi.fn(),
      });
      return child;
    }),
  };
});

describe("TASK-REVIEW-001 Electron composition root (app_entry.ts)", () => {
  beforeEach(() => {
    registeredHandlers.clear();
    createdWindows.length = 0;
    appEventHandlers.clear();
    vi.resetModules();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test("runCompositionRoot bootstraps a real WorkerManager, registers every IPC channel exactly once, and creates a window", async () => {
    const { runCompositionRoot } = await import("../main/app_entry");

    const context = await runCompositionRoot({ dataRoot: "/fake/user-data" });

    const expectedChannels = [
      "project:list",
      "project:create",
      "project:get",
      "source:register",
      "source:list",
      "source:retry",
      "approval:list",
      "approval:approve",
      "approval:request-changes",
      "build-request:create",
      "job:start",
      "job:list",
      "job:get",
      "job:subscribe-progress",
      "job:cancel",
      "artifact:list",
      "artifact:open-folder",
      "voice:list-engines",
      "voice:preview",
      "voice-profile:create",
      "voice-profile:list",
      "voice-profile:get",
      "voice-profile:update",
      "voice-profile:archive",
      "dialog:select-source-file",
    ];
    for (const channel of expectedChannels) {
      expect(registeredHandlers.has(channel), `expected channel to be registered: ${channel}`).toBe(true);
    }
    expect(registeredHandlers.size).toBe(expectedChannels.length);

    expect(createdWindows).toHaveLength(1);
    expect(context.dataRoot).toBe("/fake/user-data");
    expect(context.recoveredStaleJobIds).toEqual([]);

    await context.shutdown();
  });

  test("bootstrap failure (worker subprocess exits immediately) does not register any IPC handler or create a window", async () => {
    const { spawn } = await import("node:child_process");
    (spawn as unknown as ReturnType<typeof vi.fn>).mockImplementationOnce(() => {
      const stdout = new EventEmitter();
      const stderr = new EventEmitter();
      const emitter = new EventEmitter();
      const child = Object.assign(emitter, { stdin: { write: vi.fn() }, stdout, stderr, kill: vi.fn() });
      // subprocessが起動直後に異常終了した状態を模擬する: 以降のrequest()は
      // 即座に"worker_not_running"で拒否され、30秒timeoutを待たずに失敗が確定する。
      queueMicrotask(() => emitter.emit("exit", 1));
      return child;
    });

    const { runCompositionRoot } = await import("../main/app_entry");

    // subprocessが起動直後に落ちるため、health確認まで到達せずmigration要求自体が失敗する
    // (bootstrapApplicationの契約どおり、DB/Workerを後始末した上でIPC登録前に停止する)。
    await expect(runCompositionRoot({ dataRoot: "/fake/user-data-2" })).rejects.toThrow(/migration_failed|worker_health_check_failed/);

    expect(registeredHandlers.size).toBe(0);
    expect(createdWindows).toHaveLength(0);
  });

  test("TC-REVIEW-001-10: window作成失敗時もbootstrap済みのWorker/DBを後始末する(資源leakしない)", async () => {
    const { spawn } = await import("node:child_process");
    let capturedChild: { kill: ReturnType<typeof vi.fn> } | null = null;
    (spawn as unknown as ReturnType<typeof vi.fn>).mockImplementationOnce(() => {
      const stdout = new EventEmitter();
      const stderr = new EventEmitter();
      const emitter = new EventEmitter();
      const child = Object.assign(emitter, {
        stdin: {
          write: (chunk: string) => {
            for (const line of chunk.split("\n")) {
              if (!line.trim()) continue;
              const request = JSON.parse(line) as { job_id: string; job_type: string };
              const responder = RESPONDERS[request.job_type];
              stdout.emit("data", `${JSON.stringify({ event: "started", job_id: request.job_id })}\n`);
              stdout.emit(
                "data",
                `${JSON.stringify({ event: "completed", job_id: request.job_id, result: responder ? responder({}) : {} })}\n`,
              );
            }
          },
        },
        stdout,
        stderr,
        kill: vi.fn(),
      });
      capturedChild = child;
      return child;
    });

    const { runCompositionRoot } = await import("../main/app_entry");

    await expect(
      runCompositionRoot({
        dataRoot: "/fake/user-data-3",
        createWindow: () => {
          throw new Error("simulated BrowserWindow construction failure");
        },
      }),
    ).rejects.toThrow(/simulated BrowserWindow construction failure/);

    // window作成失敗前にIPC handler自体は登録されるが(実装上の巻き戻しは行わない)、
    // 重要なのは起動したworker subprocessが確実にkillされ、放置されないこと
    // (main()側はこの例外を受けてapp.exit(1)し、プロセス全体を終了させる)。
    expect(capturedChild).not.toBeNull();
    expect(capturedChild!.kill).toHaveBeenCalled();
  });
});
