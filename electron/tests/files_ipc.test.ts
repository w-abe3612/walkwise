/**
 * Tests for TASK-REVIEW-001 P0 fix: safe main-process file picker.
 *
 * Contract: docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md(2.6, 3.6節)
 *
 * Before this fix, ProjectWorkspace.vue sent the browser `File.name` (not a real filesystem
 * path) as `filePath`, so main/Worker could never actually read the selected file. This module
 * is the only sanctioned way a real, validated absolute path reaches the Renderer: main opens
 * a native `dialog.showOpenDialog()` and validates the result (extension allowlist, existence,
 * regular file, no symlink, no UNC path, no path-traversal segment) before returning it.
 */

import { mkdtempSync, mkdirSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import {
  FileValidationError,
  registerFileDialogIpcHandlers,
  validateSourceFilePath,
  type DialogLike,
  type IpcMainLike,
} from "../main/ipc/files";

function fakeIpcMain(): { ipcMain: IpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain: IpcMainLike = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

describe("TASK-REVIEW-001 安全なfile picker (electron/main/ipc/files.ts)", () => {
  let scratchRoot: string;

  beforeEach(() => {
    scratchRoot = mkdtempSync(path.join(tmpdir(), "walkwise-files-ipc-"));
  });

  afterEach(() => {
    rmSync(scratchRoot, { recursive: true, force: true });
  });

  test("validateSourceFilePath accepts a real, allowed-extension regular file", () => {
    const filePath = path.join(scratchRoot, "chapter01.pdf");
    writeFileSync(filePath, "fake-pdf-bytes");

    const result = validateSourceFilePath(filePath);
    expect(result).toEqual({ filePath, mediaType: "pdf" });
  });

  test("validateSourceFilePath rejects unsupported extensions", () => {
    const filePath = path.join(scratchRoot, "movie.mp4");
    writeFileSync(filePath, "fake-video-bytes");

    expect(() => validateSourceFilePath(filePath)).toThrow(FileValidationError);
    expect(() => validateSourceFilePath(filePath)).toThrow(/unsupported file extension/);
  });

  test("validateSourceFilePath rejects a path that does not exist", () => {
    const filePath = path.join(scratchRoot, "does-not-exist.txt");
    expect(() => validateSourceFilePath(filePath)).toThrow(/does not exist/);
  });

  test("validateSourceFilePath rejects directories", () => {
    const dirPath = path.join(scratchRoot, "a-directory.txt");
    mkdirSync(dirPath);
    expect(() => validateSourceFilePath(dirPath)).toThrow(/not a regular file/);
  });

  test("validateSourceFilePath rejects symbolic links", () => {
    const realFile = path.join(scratchRoot, "real.txt");
    writeFileSync(realFile, "content");
    const linkPath = path.join(scratchRoot, "link.txt");
    symlinkSync(realFile, linkPath);

    expect(() => validateSourceFilePath(linkPath)).toThrow(/symbolic links/);
  });

  test("validateSourceFilePath rejects UNC paths and path-traversal segments", () => {
    expect(() => validateSourceFilePath("\\\\fileserver\\share\\chapter01.pdf")).toThrow(/UNC/);
    expect(() => validateSourceFilePath(`${scratchRoot}${path.sep}..${path.sep}escaped.txt`)).toThrow(/traversal/);
  });

  test("validateSourceFilePath rejects relative paths", () => {
    expect(() => validateSourceFilePath("relative/chapter01.txt")).toThrow(/absolute/);
  });

  test("registerFileDialogIpcHandlers returns null when the user cancels the dialog", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const dialog: DialogLike = { showOpenDialog: vi.fn().mockResolvedValue({ canceled: true, filePaths: [] }) };
    registerFileDialogIpcHandlers({ ipcMain, dialog });

    const result = await handlers.get("dialog:select-source-file")!({});
    expect(result).toBeNull();
  });

  test("registerFileDialogIpcHandlers validates the selected path before returning it to the renderer", async () => {
    const filePath = path.join(scratchRoot, "chapter01.txt");
    writeFileSync(filePath, "本文");

    const { ipcMain, handlers } = fakeIpcMain();
    const dialog: DialogLike = {
      showOpenDialog: vi.fn().mockResolvedValue({ canceled: false, filePaths: [filePath] }),
    };
    registerFileDialogIpcHandlers({ ipcMain, dialog });

    const result = await handlers.get("dialog:select-source-file")!({});
    expect(result).toEqual({ filePath, mediaType: "text" });
  });

  test("registerFileDialogIpcHandlers propagates validation failure for a disallowed selection", async () => {
    const filePath = path.join(scratchRoot, "movie.mp4");
    writeFileSync(filePath, "fake-video-bytes");

    const { ipcMain, handlers } = fakeIpcMain();
    const dialog: DialogLike = {
      showOpenDialog: vi.fn().mockResolvedValue({ canceled: false, filePaths: [filePath] }),
    };
    registerFileDialogIpcHandlers({ ipcMain, dialog });

    await expect(handlers.get("dialog:select-source-file")!({})).rejects.toThrow(/unsupported file extension/);
  });

  test("必須入力欠落: ipcMain/dialogがないと登録できない [unit/P0]", () => {
    const { ipcMain } = fakeIpcMain();
    expect(() => registerFileDialogIpcHandlers(undefined as never)).toThrow();
    expect(() => registerFileDialogIpcHandlers({ ipcMain, dialog: undefined as never })).toThrow();
    expect(ipcMain.handle).not.toHaveBeenCalled();
  });
});
