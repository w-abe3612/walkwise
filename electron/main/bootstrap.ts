/**
 * electron/main/bootstrap.ts — 公開契約: bootstrapApplication(): Promise<AppContext>.
 *
 * Contract: docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md
 * Spec: docs/specifications/17-local-data-persistence-policy.md(5.4, 5.5節),
 *       docs/specifications/20-electron-desktop-architecture.md,
 *       docs/specifications/22-job-lifecycle-and-recovery.md(5.6節)
 */

import type { AppDatabaseHandle } from "./database";
import { WorkerManager } from "./worker_manager";

export interface AppContext {
  readonly dataRoot: string;
  readonly database: AppDatabaseHandle;
  readonly workerManager: WorkerManager;
  readonly recoveredStaleJobIds: readonly string[];
  shutdown(): Promise<void>;
}

export interface BootstrapOptions {
  /** Electron `app.getPath('userData')`相当の解決済みdata root。 */
  readonly dataRoot: string;
  readonly databaseFileName?: string;
  /** data root配下に必要なディレクトリを作る(既定: 何もしないno-op、呼び出し側の責務)。 */
  readonly ensureDataRoot?: (root: string) => Promise<void>;
  /** migration適用前の自動backup(17-local-data-persistence-policy.md 5.5節)。 */
  readonly backupDatabase?: (databasePath: string) => Promise<void>;
  /** 実DB接続の確立(driver選定は本タスクの対象外、必須注入)。 */
  readonly openDatabase: (databasePath: string) => Promise<AppDatabaseHandle>;
  /** 未適用migrationの適用。失敗時はbootstrapApplication全体を失敗させる。 */
  readonly runMigrations: (db: AppDatabaseHandle) => Promise<void>;
  /** 22-job-lifecycle-and-recovery.md 5.6節: runningのまま残ったJobをfailedへ復旧する。 */
  readonly recoverStaleJobs: (db: AppDatabaseHandle) => Promise<readonly string[]>;
  readonly createWorkerManager: () => WorkerManager;
  /** worker health/ping確認。既定は`checkCommand`(既定"health")をrequestする。 */
  readonly checkWorkerHealth?: (manager: WorkerManager) => Promise<void>;
  readonly healthCheckRetries?: number;
  readonly sleep?: (ms: number) => Promise<void>;
}

function defaultSleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function defaultCheckWorkerHealth(manager: WorkerManager): Promise<void> {
  await manager.request("health");
}

/** data root→backup/migration→DB→worker healthの順で初期化する。 */
export async function bootstrapApplication(options: BootstrapOptions): Promise<AppContext> {
  if (!options) {
    throw new Error("options is required");
  }
  if (!options.dataRoot) {
    throw new Error("dataRoot is required");
  }
  if (!options.openDatabase) {
    throw new Error("openDatabase is required");
  }
  if (!options.runMigrations) {
    throw new Error("runMigrations is required");
  }
  if (!options.recoverStaleJobs) {
    throw new Error("recoverStaleJobs is required");
  }
  if (!options.createWorkerManager) {
    throw new Error("createWorkerManager is required");
  }

  const databaseFileName = options.databaseFileName ?? "app.db";
  const databasePath = `${options.dataRoot}/${databaseFileName}`;
  const sleep = options.sleep ?? defaultSleep;
  const checkWorkerHealth = options.checkWorkerHealth ?? defaultCheckWorkerHealth;
  const healthCheckRetries = options.healthCheckRetries ?? 2;

  // 1) data root
  if (options.ensureDataRoot) {
    await options.ensureDataRoot(options.dataRoot);
  }

  // 2) backup(migration前の自動backup、5.5節)
  if (options.backupDatabase) {
    await options.backupDatabase(databasePath);
  }

  // 3) DB open + migration。migration失敗時はwindowへ安全なerrorを返しworkerを開始しない。
  const database = await options.openDatabase(databasePath);
  try {
    await options.runMigrations(database);
  } catch (err) {
    await database.close();
    throw new Error(`migration_failed: ${err instanceof Error ? err.message : String(err)}`);
  }

  // 4) stale job recovery
  const recoveredStaleJobIds = await options.recoverStaleJobs(database);

  // 5) worker起動 + health確認(失敗時は再試行し、最終的に診断可能な起動errorにする)
  const workerManager = options.createWorkerManager();
  workerManager.start();

  let lastError: Error | null = null;
  let healthy = false;
  for (let attempt = 0; attempt <= healthCheckRetries; attempt += 1) {
    try {
      await checkWorkerHealth(workerManager);
      healthy = true;
      break;
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      if (attempt < healthCheckRetries) {
        await sleep(0);
      }
    }
  }

  if (!healthy) {
    workerManager.stop();
    await database.close();
    throw new Error(`worker_health_check_failed: ${lastError?.message ?? "unknown"}`);
  }

  let shutdownCalled = false;
  return {
    dataRoot: options.dataRoot,
    database,
    workerManager,
    recoveredStaleJobIds,
    async shutdown(): Promise<void> {
      if (shutdownCalled) {
        return; // shutdownは冪等
      }
      shutdownCalled = true;
      workerManager.stop();
      await database.close();
    },
  };
}
