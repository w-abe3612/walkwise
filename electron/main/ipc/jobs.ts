/**
 * electron/main/ipc/jobs.ts — 公開契約: job:get/subscribe/cancel handlers.
 *
 * Contract: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
 * Spec: docs/screens/04-job-progress.md(7, 8節),
 *       docs/specifications/22-job-lifecycle-and-recovery.md
 *
 * `job:start`(再試行payload `{parentJobId}`)は、`electron/main/ipc/builds.ts`の
 * `job:start`(新規Job起動payload)と同一channel名を共有するため、本モジュールでは
 * 登録しない(TASK-RELEASE-002でIPC channel重複を解消。詳細は
 * docs/notes/implementation_assumptions.md参照)。`registerBuildIpcHandlers`へ
 * `jobService`を注入することで、同一ipcMain上で両payload形状を1つのhandlerが処理する。
 */

export type JobStatus = "queued" | "running" | "succeeded" | "failed" | "cancel_requested" | "cancelled";

export interface JobSummary {
  readonly jobId: string;
  readonly buildRequestId: string;
  readonly jobType: string;
  readonly status: JobStatus;
  readonly progressCurrent?: number;
  readonly progressTotal?: number;
  readonly lastMessage?: string;
  /** 22-job-lifecycle-and-recovery.md 5.6節: stale job検出でfailedになった場合true。 */
  readonly stale?: boolean;
}

export interface ProgressEvent {
  readonly jobId: string;
  readonly current: number;
  readonly total: number;
  readonly message?: string;
}

export interface JobServiceLike {
  list(projectId: string): Promise<readonly JobSummary[]>;
  get(jobId: string): Promise<JobSummary>;
  subscribeProgress(jobId: string, listener: (event: ProgressEvent) => void): () => void;
  cancel(jobId: string): Promise<JobSummary>;
  /** 失敗Jobを上書きせず、parent_job_idを保持した新規Jobとして再試行する(5.4節)。 */
  retry(parentJobId: string): Promise<JobSummary>;
}

export class JobValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainInvokeEventLike {
  readonly sender: { send(channel: string, ...args: unknown[]): void };
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: IpcMainInvokeEventLike, ...args: unknown[]) => unknown): void;
}

export interface JobIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly jobService: JobServiceLike;
}

/** 04-job-progress.md 8節: cancelはqueued/runningのみ許可する。 */
const CANCELLABLE_STATUSES = new Set<JobStatus>(["queued", "running"]);
/** 04-job-progress.md 8節: 再試行はfailed/cancelledのみ許可する。
 * `job:start`(再試行payload)を発行する`electron/main/ipc/builds.ts`からも
 * 同じ判定を再利用するため公開する(TASK-RELEASE-002で解消したjob:start重複登録の一部)。 */
export const RETRYABLE_STATUSES = new Set<JobStatus>(["failed", "cancelled"]);

function requireJobId(raw: unknown): string {
  if (typeof raw !== "string" || !raw.trim()) {
    throw new JobValidationError("validation_error", "jobId is required");
  }
  return raw.trim();
}

/** 合法状態だけを操作し進捗eventを購読配信する。 */
export function registerJobIpcHandlers(context: JobIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.jobService) {
    throw new Error("jobService is required");
  }

  context.ipcMain.handle("job:list", async (_event, rawProjectId: unknown) => {
    if (typeof rawProjectId !== "string" || !rawProjectId.trim()) {
      throw new JobValidationError("validation_error", "projectId is required");
    }
    const jobs = await context.jobService.list(rawProjectId.trim());
    return { jobs };
  });

  context.ipcMain.handle("job:get", async (_event, rawJobId: unknown) => {
    const jobId = requireJobId(rawJobId);
    return context.jobService.get(jobId);
  });

  context.ipcMain.handle("job:subscribe-progress", (event, rawJobId: unknown) => {
    const jobId = requireJobId(rawJobId);
    return context.jobService.subscribeProgress(jobId, (progress) => {
      event.sender.send("job:progress-event", progress);
    });
  });

  context.ipcMain.handle("job:cancel", async (_event, rawJobId: unknown) => {
    const jobId = requireJobId(rawJobId);
    const job = await context.jobService.get(jobId);
    if (!CANCELLABLE_STATUSES.has(job.status)) {
      // 不正遷移: 永続状態を一切変更せず安定errorで停止する。
      throw new JobValidationError("invalid_job_transition", `job ${jobId} is not cancellable from status ${job.status}`);
    }
    return context.jobService.cancel(jobId);
  });
}
