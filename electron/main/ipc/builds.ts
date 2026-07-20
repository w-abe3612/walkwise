/**
 * electron/main/ipc/builds.ts — 公開契約: build-request:create/job:start handlers.
 *
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Spec: docs/screens/03-build-settings.md(4, 8節),
 *       docs/specifications/22-job-lifecycle-and-recovery.md(5.5節)
 *
 * `job:start`は2つのpayload形状を受け付ける(TASK-RELEASE-002で
 * `electron/main/ipc/jobs.ts`との channel重複を解消して統合した):
 * - `string`(buildRequestId): 新規Job起動。承認gate確認後`buildService.startJob`。
 * - `{ parentJobId: string }`: 失敗/取消済みJobの再試行。`jobService`が必要。
 *   `jobService`未注入の場合は再試行payloadを安定errorで拒否する
 *   (新規Job起動側の契約・挙動は変更しない)。
 */

import { RETRYABLE_STATUSES, type JobServiceLike } from "./jobs";

const ALLOWED_OUTPUT_FORMATS = new Set(["mp3", "text"]);

export interface BuildRequestSummary {
  readonly buildRequestId: string;
  readonly projectId: string;
  readonly outputFormats: readonly string[];
  readonly voiceProfileId?: string;
}

export interface CreateBuildRequestInput {
  readonly projectId: string;
  readonly outputFormats: readonly string[];
  readonly voiceProfileId?: string;
}

export interface JobSummary {
  readonly jobId: string;
  readonly buildRequestId: string;
  readonly status: string;
}

export interface BuildServiceLike {
  createBuildRequest(input: CreateBuildRequestInput): Promise<BuildRequestSummary>;
  startJob(buildRequestId: string): Promise<JobSummary>;
}

/** 22-job-lifecycle-and-recovery.md 5.5節: Job起動前に承認ゲートを確認する。 */
export interface ApprovalGateCheckerLike {
  isSatisfied(buildRequestId: string): Promise<boolean>;
}

export class BuildValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface BuildIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly buildService: BuildServiceLike;
  readonly approvalGateChecker: ApprovalGateCheckerLike;
  /** 再試行payload(`{parentJobId}`)を`job:start`で受け付ける場合に必要。省略時は再試行を拒否する。 */
  readonly jobService?: JobServiceLike;
}

function requireNonEmptyString(raw: unknown, fieldName: string): string {
  if (typeof raw !== "string" || !raw.trim()) {
    throw new BuildValidationError("validation_error", `${fieldName} is required`);
  }
  return raw.trim();
}

function validateCreateBuildRequestInput(raw: unknown): CreateBuildRequestInput {
  if (!raw || typeof raw !== "object") {
    throw new BuildValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;

  if (typeof input.projectId !== "string" || !input.projectId.trim()) {
    throw new BuildValidationError("validation_error", "projectId is required");
  }

  const outputFormats = input.outputFormats;
  if (!Array.isArray(outputFormats) || outputFormats.length === 0) {
    throw new BuildValidationError("validation_error", "outputFormats requires at least one selection");
  }
  if (!outputFormats.every((format) => typeof format === "string" && ALLOWED_OUTPUT_FORMATS.has(format))) {
    throw new BuildValidationError("validation_error", "outputFormats contains an unsupported format");
  }

  // 03-build-settings.md 4/8節: mp3を含む場合はvoice_profile_idが必須。
  if (outputFormats.includes("mp3")) {
    if (typeof input.voiceProfileId !== "string" || !input.voiceProfileId.trim()) {
      throw new BuildValidationError("validation_error", "voiceProfileId is required when mp3 is selected");
    }
  }

  return {
    projectId: input.projectId.trim(),
    outputFormats: [...outputFormats] as readonly string[],
    voiceProfileId: typeof input.voiceProfileId === "string" ? input.voiceProfileId.trim() : undefined,
  };
}

/** 出力形式とvoice条件、approval gateを検証する。 */
export function registerBuildIpcHandlers(context: BuildIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.buildService) {
    throw new Error("buildService is required");
  }
  if (!context.approvalGateChecker) {
    throw new Error("approvalGateChecker is required");
  }

  context.ipcMain.handle("build-request:create", async (_event: unknown, rawInput: unknown) => {
    const validated = validateCreateBuildRequestInput(rawInput);
    return context.buildService.createBuildRequest(validated);
  });

  context.ipcMain.handle("job:start", async (_event: unknown, rawInput: unknown) => {
    if (typeof rawInput === "string") {
      const buildRequestId = requireNonEmptyString(rawInput, "buildRequestId");

      const satisfied = await context.approvalGateChecker.isSatisfied(buildRequestId);
      if (!satisfied) {
        // 承認ゲート未充足: Jobを一切作成せず、画面が承認導線を表示できる安定errorにする。
        throw new BuildValidationError("approval_gate_not_satisfied", `approval gate not satisfied: ${buildRequestId}`);
      }

      return context.buildService.startJob(buildRequestId);
    }

    if (rawInput && typeof rawInput === "object" && "parentJobId" in rawInput) {
      if (!context.jobService) {
        throw new BuildValidationError("validation_error", "jobService is required to retry a job");
      }
      const parentJobId = requireNonEmptyString((rawInput as { parentJobId: unknown }).parentJobId, "parentJobId");
      const parentJob = await context.jobService.get(parentJobId);
      if (!RETRYABLE_STATUSES.has(parentJob.status)) {
        throw new BuildValidationError(
          "invalid_job_transition",
          `job ${parentJobId} is not retryable from status ${parentJob.status}`,
        );
      }
      return context.jobService.retry(parentJobId);
    }

    throw new BuildValidationError("validation_error", "job:start requires either a buildRequestId string or {parentJobId}");
  });
}
