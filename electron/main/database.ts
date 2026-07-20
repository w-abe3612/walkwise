/**
 * electron/main/database.ts — 公開契約: openApplicationDatabase(path).
 *
 * Contract: docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md
 * Spec: docs/specifications/17-local-data-persistence-policy.md(5.1, 5.2節)
 */

export interface AppDatabaseHandle {
  readonly path: string;
  close(): Promise<void>;
}

export interface OpenDatabaseOptions {
  /** 実sqlite driverの選定は本タスクの対象外であり、呼び出し側が必ず注入する。 */
  readonly connectionFactory: (path: string) => AppDatabaseHandle;
}

/** rendererへ接続を渡さずmain内だけでDB handleを保持する。 */
export async function openApplicationDatabase(
  path: string,
  options: OpenDatabaseOptions,
): Promise<AppDatabaseHandle> {
  if (!path) {
    throw new Error("path is required");
  }
  if (!options) {
    throw new Error("options is required");
  }
  if (!options.connectionFactory) {
    throw new Error("connectionFactory is required");
  }

  return options.connectionFactory(path);
}
