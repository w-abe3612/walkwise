/**
 * electron/main/ipc/files.ts — 公開契約: dialog:select-source-file handler + validateSourceFilePath.
 *
 * TASK-REVIEW-001監査2.6節: 以前のProjectWorkspace.vueは、ブラウザの`File.name`
 * (拡張子付きファイル名のみで、実在するファイルシステムpathではない)をそのまま
 * `filePath`としてsource:registerへ送っており、main/Workerは対象ファイルを一度も
 * 実際に読めていなかった。本moduleは、rendererに任意path文字列を組み立てさせず、
 * 必ずmain process側の`dialog.showOpenDialog()`が返す絶対pathだけを許可し、
 * 拡張子・実在・通常ファイル(ディレクトリ/デバイス/symlinkでない)を検証する。
 *
 * `validateSourceFilePath`は、source:register handler(sources.ts)側でも同じ検証を
 * 再実行するために公開する(fail-closed: dialog経由かどうかに関わらず、main側は
 * 常に自分で検証してからWorkerへ委譲する。rendererが直接任意pathを送ってくる
 * 想定にも耐える多重防御)。
 *
 * Spec: docs/specifications/20-electron-desktop-architecture.md(5.8節),
 *       docs/screens/02-project-workspace-and-source-import.md(4, 13節)
 */

import { lstatSync } from "node:fs";
import path from "node:path";

const ALLOWED_EXTENSION_TO_MEDIA_TYPE: Record<string, string> = {
  ".txt": "text",
  ".md": "text",
  ".pdf": "pdf",
  ".jpg": "image",
  ".jpeg": "image",
  ".png": "image",
  ".tif": "image",
  ".tiff": "image",
};

export class FileValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

/**
 * 選択/入力されたpathを検証し、推定media typeとともに返す。
 * - 拡張子がMVP対象(text/pdf/image)であること
 * - 実在する通常ファイルであること(ディレクトリ/デバイスでない)
 * - symlinkでないこと(参照先を経由したproject外file読み出しを防ぐ)
 * - UNC path(`\\\\server\\share\\...`)でないこと(共有driveの想定外file読み出しを防ぐ)
 * - `..`によるpath traversal片(正規化前後の不一致)を含まないこと
 */
export function validateSourceFilePath(rawPath: string): { filePath: string; mediaType: string } {
  if (typeof rawPath !== "string" || !rawPath.trim()) {
    throw new FileValidationError("validation_error", "filePath is required");
  }
  const filePath = rawPath.trim();

  if (/^\\\\/.test(filePath) || /^\/\/[^/]/.test(filePath)) {
    throw new FileValidationError("validation_error", "UNC paths are not allowed");
  }
  // path.normalize()は".."を解決してしまうため、正規化前の生入力に対して判定する
  // (正規化後の絶対pathが安全な実在fileを指す場合でも、traversal片を含む入力自体を
  // 疑わしいものとしてfail-closedに拒否する)。
  if (filePath.split(/[\\/]/).includes("..")) {
    throw new FileValidationError("validation_error", "path traversal segments are not allowed");
  }

  const normalized = path.normalize(filePath);
  if (!path.isAbsolute(normalized)) {
    throw new FileValidationError("validation_error", "filePath must be an absolute path");
  }

  const extension = path.extname(normalized).toLowerCase();
  const mediaType = ALLOWED_EXTENSION_TO_MEDIA_TYPE[extension];
  if (!mediaType) {
    throw new FileValidationError("unsupported_media_type", `unsupported file extension: ${extension}`);
  }

  let stats;
  try {
    stats = lstatSync(normalized);
  } catch {
    throw new FileValidationError("not_found", `file does not exist: ${normalized}`);
  }
  if (stats.isSymbolicLink()) {
    throw new FileValidationError("validation_error", "symbolic links are not allowed as source files");
  }
  if (!stats.isFile()) {
    throw new FileValidationError("validation_error", `not a regular file: ${normalized}`);
  }

  return { filePath: normalized, mediaType };
}

export interface OpenDialogResultLike {
  readonly canceled: boolean;
  readonly filePaths: readonly string[];
}

export interface DialogLike {
  showOpenDialog(options: unknown): Promise<OpenDialogResultLike>;
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface FileDialogIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly dialog: DialogLike;
}

const OPEN_DIALOG_FILTERS = [
  { name: "対応済み素材", extensions: ["txt", "md", "pdf", "jpg", "jpeg", "png", "tif", "tiff"] },
];

/** rendererへは選択結果(検証済み絶対pathとmedia type)だけを返し、dialog自体はrendererから起動できない。 */
export function registerFileDialogIpcHandlers(context: FileDialogIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.dialog) {
    throw new Error("dialog is required");
  }

  context.ipcMain.handle("dialog:select-source-file", async () => {
    const result = await context.dialog.showOpenDialog({
      properties: ["openFile"],
      filters: OPEN_DIALOG_FILTERS,
    });
    if (result.canceled || result.filePaths.length === 0) {
      return null;
    }
    return validateSourceFilePath(result.filePaths[0]);
  });
}
