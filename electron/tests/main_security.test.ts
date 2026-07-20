/**
 * STEP4 test implementation for TASK-DESKTOP-001: main window security / renderer isolation.
 * Contract: docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md
 * Release scope: MVP.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test, vi } from "vitest";

vi.mock("electron", () => ({
  contextBridge: { exposeInMainWorld: vi.fn() },
  ipcRenderer: { invoke: vi.fn(), on: vi.fn(), removeListener: vi.fn() },
  BrowserWindow: class {
    constructor(public readonly options: unknown) {}
  },
}));

import { createMainWindow, type BrowserWindowLike } from "../main/index";
import { buildWalkwiseApi, installPreloadBridge } from "../preload/index";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RENDERER_ROOT = path.resolve(__dirname, "..", "renderer");

const FORBIDDEN_IMPORT_PATTERNS = [
  /from\s+["']node:fs["']/,
  /from\s+["']fs["']/,
  /require\(\s*["']fs["']\s*\)/,
  /from\s+["']node:child_process["']/,
  /from\s+["']child_process["']/,
  /require\(\s*["']child_process["']\s*\)/,
  /from\s+["']sqlite3["']/,
  /from\s+["']better-sqlite3["']/,
];

function listRendererSourceFiles(dir: string): string[] {
  const entries = readdirSync(dir);
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry);
    const stats = statSync(fullPath);
    if (stats.isDirectory()) {
      if (entry === "tests") continue; // testディレクトリ自体は対象外(production bundleではない)
      files.push(...listRendererSourceFiles(fullPath));
    } else if (entry.endsWith(".ts") || entry.endsWith(".vue")) {
      files.push(fullPath);
    }
  }
  return files;
}

describe("TASK-DESKTOP-001 Electron/Vue scaffold・main/preload安全境界", () => {
  test("TC-DESKTOP-001-01: webPreferences [static/P0]", () => {
    const captured: { webPreferences?: unknown } = {};
    const fakeWindow: BrowserWindowLike = { loadFile: vi.fn(), loadURL: vi.fn() };
    const factory = vi.fn((opts: { webPreferences: unknown }) => {
      captured.webPreferences = opts.webPreferences;
      return fakeWindow;
    });

    createMainWindow({
      preloadPath: "/preload/index.js",
      rendererEntry: "/renderer/index.html",
      browserWindowFactory: factory,
    });

    expect(captured.webPreferences).toEqual({
      preload: "/preload/index.js",
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    });
  });

  test("TC-DESKTOP-001-03: renderer isolation [static/P0]", () => {
    const files = listRendererSourceFiles(RENDERER_ROOT);
    expect(files.length).toBeGreaterThan(0);

    for (const file of files) {
      const content = readFileSync(file, "utf-8");
      for (const pattern of FORBIDDEN_IMPORT_PATTERNS) {
        expect(
          pattern.test(content),
          `${path.relative(RENDERER_ROOT, file)} must not import Node fs/child_process/sqlite directly`,
        ).toBe(false);
      }
    }
  });

  test("TC-DESKTOP-001-05: contextBridge [unit/P1]", () => {
    const exposeInMainWorld = vi.fn();
    const invoke = vi.fn().mockResolvedValue(undefined);
    const on = vi.fn();
    const removeListener = vi.fn();

    installPreloadBridge({ exposeInMainWorld }, { invoke, on, removeListener });

    expect(exposeInMainWorld).toHaveBeenCalledTimes(1);
    const [apiKey, api] = exposeInMainWorld.mock.calls[0] as [string, Record<string, unknown>];
    expect(apiKey).toBe("walkwise");
    expect(api).toHaveProperty("project");
    expect(api).toHaveProperty("job");
  });

  test("TC-DESKTOP-001-07: 任意IPC/FS/child_process非公開 [integration_mock/P1]", () => {
    const invoke = vi.fn().mockResolvedValue(undefined);
    const on = vi.fn();
    const removeListener = vi.fn();

    const api = buildWalkwiseApi({ invoke, on, removeListener }) as unknown as Record<string, unknown>;

    // 生のipcRenderer/fs/child_processはAPI上に一切公開されない。
    expect(api).not.toHaveProperty("ipcRenderer");
    expect(api).not.toHaveProperty("invoke");
    expect(api).not.toHaveProperty("send");
    expect(api).not.toHaveProperty("require");
    expect(api).not.toHaveProperty("fs");
    expect(api).not.toHaveProperty("childProcess");

    // 許可された固定method以外は存在しない(任意channel呼び出し不可)。
    const arbitrary = (api as Record<string, unknown>)["arbitrary:channel"];
    expect(arbitrary).toBeUndefined();
  });

  test("TC-DESKTOP-001-09: 再実行時の決定性 [unit/P1]", () => {
    const fakeWindowA: BrowserWindowLike = { loadFile: vi.fn(), loadURL: vi.fn() };
    const fakeWindowB: BrowserWindowLike = { loadFile: vi.fn(), loadURL: vi.fn() };
    const factory = vi.fn().mockReturnValueOnce(fakeWindowA).mockReturnValueOnce(fakeWindowB);

    const options = {
      preloadPath: "/preload/index.js",
      rendererEntry: "/renderer/index.html",
      browserWindowFactory: factory,
    };

    createMainWindow(options);
    createMainWindow(options);

    expect(factory).toHaveBeenCalledTimes(2);
    const [firstCallOptions] = factory.mock.calls[0] as [{ webPreferences: unknown }];
    const [secondCallOptions] = factory.mock.calls[1] as [{ webPreferences: unknown }];
    expect(firstCallOptions.webPreferences).toEqual(secondCallOptions.webPreferences);
  });
});
