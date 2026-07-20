/**
 * electron/main/index.ts — 公開契約: createMainWindow(): BrowserWindow.
 *
 * Contract: docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md
 * Spec: docs/specifications/20-electron-desktop-architecture.md(5.4節)
 */

import { BrowserWindow } from "electron";

export interface BrowserWindowLike {
  loadFile(filePath: string): unknown;
  loadURL(url: string): unknown;
}

export interface SafeWebPreferences {
  readonly preload: string;
  readonly nodeIntegration: false;
  readonly contextIsolation: true;
  readonly sandbox: true;
}

export interface CreateMainWindowOptions {
  readonly preloadPath: string;
  readonly rendererEntry: string;
  readonly browserWindowFactory?: (options: { webPreferences: SafeWebPreferences }) => BrowserWindowLike;
}

function buildSafeWebPreferences(preloadPath: string): SafeWebPreferences {
  return {
    preload: preloadPath,
    nodeIntegration: false,
    contextIsolation: true,
    sandbox: true,
  };
}

function isHttpUrl(value: string): boolean {
  return /^https?:\/\//i.test(value);
}

/** 20-electron-desktop-architecture.md 5.4節の安全なwebPreferencesでmain windowを起動する。 */
export function createMainWindow(options: CreateMainWindowOptions): BrowserWindowLike {
  if (!options) {
    throw new Error("options is required");
  }
  if (!options.preloadPath) {
    throw new Error("preloadPath is required");
  }
  if (!options.rendererEntry) {
    throw new Error("rendererEntry is required");
  }

  const webPreferences = buildSafeWebPreferences(options.preloadPath);
  const factory =
    options.browserWindowFactory ??
    ((opts: { webPreferences: SafeWebPreferences }) =>
      new BrowserWindow(opts as ConstructorParameters<typeof BrowserWindow>[0]) as unknown as BrowserWindowLike);

  const window = factory({ webPreferences });

  if (isHttpUrl(options.rendererEntry)) {
    window.loadURL(options.rendererEntry);
  } else {
    window.loadFile(options.rendererEntry);
  }

  return window;
}
