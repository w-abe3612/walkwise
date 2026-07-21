/**
 * electron/main/worker_service_adapters.ts — 公開契約: create*Adapter(deps) factories.
 *
 * TASK-REVIEW-001: 各`*ServiceLike`(ProjectServiceLike等、electron/main/ipc/*.ts)を、
 * `script/worker/commands.py`が実装する実handlerへ委譲するWorkerManager経由のadapterとして
 * 実装する。DBスキーマ・業務ルールはPython側(script/services/*)にのみ存在させ、ここでは
 * camelCase(TS)<->snake_case(Python)の変換とWorkerManager.request呼び出しだけを行う
 * (新しい業務ロジックは追加しない)。
 *
 * Contract: docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md(3.4節)
 * Spec: docs/specifications/21-electron-python-worker-interface.md
 */

import { randomUUID } from "node:crypto";

import type { WorkerManager } from "./worker_manager";
import type { CreateProjectInput, ProjectServiceLike, ProjectSummary } from "./ipc/projects";
import type { RegisterSourceInput, SourceServiceLike, SourceSummary } from "./ipc/sources";
import type { ApprovalServiceLike, ApprovalSummary, ApproveInput, RequestChangesInput } from "./ipc/approvals";
import type {
  ApprovalGateCheckerLike,
  BuildRequestSummary,
  BuildServiceLike,
  CreateBuildRequestInput,
  JobSummary as BuildJobSummary,
} from "./ipc/builds";
import type { JobServiceLike, JobStatus, JobSummary, ProgressEvent } from "./ipc/jobs";
import type { ArtifactServiceLike, ArtifactSummary } from "./ipc/artifacts";
import type { EngineHealth, ListEnginesResult, PreviewInput, PreviewResult, SpeakerOption, VoiceServiceLike } from "./ipc/voice";
import type {
  CreateVoiceProfileInput,
  UpdateVoiceProfileInput,
  VoiceProfileServiceLike,
  VoiceProfileSummary,
} from "./ipc/voice_profiles";

type Raw = Record<string, unknown>;

async function workerResult(manager: WorkerManager, jobType: string, parameters: Raw = {}): Promise<Raw> {
  const outcome = await manager.request(jobType, parameters);
  const result = outcome.terminalEvent.result;
  return (result as Raw | undefined) ?? {};
}

function toProjectSummary(raw: Raw): ProjectSummary {
  return {
    projectId: raw.project_id as string,
    title: raw.title as string,
    planningStage: raw.planning_stage as string,
    updatedAt: raw.updated_at as string,
  };
}

function toSourceSummary(raw: Raw): SourceSummary {
  return {
    sourceId: raw.source_id as string,
    projectId: raw.project_id as string,
    mediaType: raw.media_type as string,
    status: raw.status as string,
  };
}

function toApprovalSummary(raw: Raw): ApprovalSummary {
  return {
    gate: raw.gate as string,
    status: raw.status as string,
    comment: (raw.comment as string | null) ?? undefined,
  };
}

function toBuildRequestSummary(raw: Raw): BuildRequestSummary {
  return {
    buildRequestId: raw.build_request_id as string,
    projectId: raw.project_id as string,
    outputFormats: raw.output_formats as readonly string[],
    voiceProfileId: (raw.voice_profile_id as string | null) ?? undefined,
  };
}

function toJobSummary(raw: Raw): JobSummary & BuildJobSummary {
  return {
    jobId: raw.job_id as string,
    buildRequestId: raw.build_request_id as string,
    jobType: (raw.job_type as string) ?? "build",
    status: raw.status as JobStatus,
    progressCurrent: (raw.progress_current as number | null) ?? undefined,
    progressTotal: (raw.progress_total as number | null) ?? undefined,
    lastMessage: (raw.last_message as string | null) ?? undefined,
    stale: raw.last_message === "stale_job_detected_on_startup",
  };
}

function toVoiceProfileSummary(raw: Raw): VoiceProfileSummary {
  return {
    voiceProfileId: raw.voice_profile_id as string,
    projectId: raw.project_id as string,
    name: raw.name as string,
    engine: raw.engine as string,
    speakerId: raw.speaker_id as string,
    styleId: (raw.style_id as string | null) ?? undefined,
    status: raw.status as string,
    speedScale: raw.speed_scale as number,
    pitchScale: raw.pitch_scale as number,
    intonationScale: raw.intonation_scale as number,
    volumeScale: raw.volume_scale as number,
  };
}

function toArtifactSummary(raw: Raw): ArtifactSummary {
  return {
    artifactId: raw.artifact_id as string,
    artifactType: raw.artifact_type as string,
    versionNumber: raw.version_number as number,
    filePath: raw.file_path as string,
    createdAt: raw.created_at as string,
    jobId: raw.job_id as string,
  };
}

export function createProjectServiceAdapter(manager: WorkerManager): ProjectServiceLike {
  return {
    async list(): Promise<readonly ProjectSummary[]> {
      const result = await workerResult(manager, "project.list");
      return (result.projects as Raw[]).map(toProjectSummary);
    },
    async create(input: CreateProjectInput): Promise<ProjectSummary> {
      const result = await workerResult(manager, "project.create", {
        project_id: randomUUID(),
        title: input.title,
        domain: input.domain,
        purpose: input.purpose,
        usage_purpose: input.usagePurpose,
      });
      return toProjectSummary(result.project as Raw);
    },
    async get(projectId: string): Promise<ProjectSummary> {
      const result = await workerResult(manager, "project.get", { project_id: projectId });
      return toProjectSummary(result.project as Raw);
    },
  };
}

export function createSourceServiceAdapter(manager: WorkerManager): SourceServiceLike {
  return {
    async register(input: RegisterSourceInput): Promise<SourceSummary> {
      const result = await workerResult(manager, "source.register", {
        project_id: input.projectId,
        source_path: input.filePath,
        media_type: input.mediaType,
      });
      return toSourceSummary(result.source as Raw);
    },
    async list(projectId: string): Promise<readonly SourceSummary[]> {
      const result = await workerResult(manager, "source.list", { project_id: projectId });
      return (result.sources as Raw[]).map(toSourceSummary);
    },
    async retry(sourceId: string): Promise<SourceSummary> {
      const result = await workerResult(manager, "source.retry", { source_id: sourceId });
      return toSourceSummary(result.source as Raw);
    },
  };
}

export function createApprovalServiceAdapter(manager: WorkerManager): ApprovalServiceLike {
  return {
    async list(projectId: string): Promise<readonly ApprovalSummary[]> {
      const result = await workerResult(manager, "approval.list", { project_id: projectId });
      return (result.approvals as Raw[]).map(toApprovalSummary);
    },
    async approve(input: ApproveInput): Promise<ApprovalSummary> {
      const result = await workerResult(manager, "approval.approve", {
        project_id: input.projectId,
        gate: input.gate,
        approved_by: input.approvedBy,
      });
      return toApprovalSummary(result);
    },
    async requestChanges(input: RequestChangesInput): Promise<ApprovalSummary> {
      const result = await workerResult(manager, "approval.request_changes", {
        project_id: input.projectId,
        gate: input.gate,
        reason: input.reason,
      });
      return toApprovalSummary(result);
    },
  };
}

export function createBuildServiceAdapter(manager: WorkerManager): BuildServiceLike {
  return {
    async createBuildRequest(input: CreateBuildRequestInput): Promise<BuildRequestSummary> {
      const result = await workerResult(manager, "build_request.create", {
        project_id: input.projectId,
        output_formats: input.outputFormats,
        voice_profile_id: input.voiceProfileId,
      });
      return toBuildRequestSummary(result.build_request as Raw);
    },
    async startJob(buildRequestId: string): Promise<BuildJobSummary> {
      const result = await workerResult(manager, "job.start", { build_request_id: buildRequestId });
      return toJobSummary(result.job as Raw);
    },
  };
}

/**
 * builds.tsのjob:start handlerが、Job作成前に確認する承認gate checker。
 * 実判定はPython側(script/worker/commands.pyの`build_request.approval_gate_satisfied`、
 * ApprovalServiceを使うfail-closedな判定)に委譲する。ここでの実装を省略/rubber-stamp化
 * すると、未承認buildを止める層が`job.start`内部のfail-closed判定だけになり、Electron
 * main側での早期拒否(承認導線の提示)ができなくなるため、必ず実判定を経由させる。
 */
export function createApprovalGateCheckerAdapter(manager: WorkerManager): ApprovalGateCheckerLike {
  return {
    async isSatisfied(buildRequestId: string): Promise<boolean> {
      const result = await workerResult(manager, "build_request.approval_gate_satisfied", {
        build_request_id: buildRequestId,
      });
      return result.satisfied === true;
    },
  };
}

const JOB_PROGRESS_POLL_INTERVAL_MS = 500;
const TERMINAL_JOB_STATUSES: ReadonlySet<JobStatus> = new Set(["succeeded", "failed", "cancelled"]);

export function createJobServiceAdapter(manager: WorkerManager): JobServiceLike {
  return {
    async list(projectId: string): Promise<readonly JobSummary[]> {
      const result = await workerResult(manager, "job.list", { project_id: projectId });
      return (result.jobs as Raw[]).map(toJobSummary);
    },
    async get(jobId: string): Promise<JobSummary> {
      const result = await workerResult(manager, "job.get", { job_id: jobId });
      return toJobSummary(result.job as Raw);
    },
    /**
     * `script/worker/commands.py`のJob実行はqueued/running状態遷移のみを管理し、
     * 実際のbuild pipeline(章単位の進捗emit)はまだ接続されていないため、ここでは
     * `job:get`を定期polling(500ms間隔)して状態変化をProgressEventとして配信する
     * (真のpush型progressではない、既知の制約。docs/notes/implementation_assumptions.md参照)。
     */
    subscribeProgress(jobId: string, listener: (event: ProgressEvent) => void): () => void {
      let stopped = false;
      let lastSignature = "";

      const poll = async (): Promise<void> => {
        if (stopped) return;
        try {
          const job = await this.get(jobId);
          const signature = `${job.status}:${job.progressCurrent ?? -1}:${job.progressTotal ?? -1}`;
          if (signature !== lastSignature) {
            lastSignature = signature;
            listener({
              jobId,
              current: job.progressCurrent ?? 0,
              total: job.progressTotal ?? 0,
              message: job.lastMessage,
            });
          }
          if (TERMINAL_JOB_STATUSES.has(job.status)) {
            stopped = true;
            return;
          }
        } catch {
          // job.getの失敗はpollingを止めるだけにし、unsubscribe呼び出し側へ例外を投げない。
          stopped = true;
          return;
        }
        if (!stopped) {
          timer = setTimeout(() => void poll(), JOB_PROGRESS_POLL_INTERVAL_MS);
        }
      };

      let timer: ReturnType<typeof setTimeout> = setTimeout(() => void poll(), 0);

      return () => {
        stopped = true;
        clearTimeout(timer);
      };
    },
    async cancel(jobId: string): Promise<JobSummary> {
      const result = await workerResult(manager, "job.cancel", { job_id: jobId });
      return toJobSummary(result.job as Raw);
    },
    async retry(parentJobId: string): Promise<JobSummary> {
      const result = await workerResult(manager, "job.retry", { parent_job_id: parentJobId });
      return toJobSummary(result.job as Raw);
    },
  };
}

export interface ShellLike {
  showItemInFolder(fullPath: string): void;
}

export function createArtifactServiceAdapter(
  manager: WorkerManager,
  dataRoot: string,
  shell: ShellLike,
): ArtifactServiceLike {
  return {
    async list(projectId: string): Promise<readonly ArtifactSummary[]> {
      const result = await workerResult(manager, "artifact.list", { project_id: projectId });
      return (result.artifacts as Raw[]).map(toArtifactSummary);
    },
    async openFolder(artifactId: string): Promise<void> {
      const result = await workerResult(manager, "artifact.get", { artifact_id: artifactId });
      const artifact = result.artifact as Raw;
      const absolutePath = `${dataRoot}/${artifact.project_id as string}/${artifact.file_path as string}`;
      shell.showItemInFolder(absolutePath);
    },
  };
}

export function createVoiceServiceAdapter(manager: WorkerManager): VoiceServiceLike {
  async function listEngines(): Promise<ListEnginesResult> {
    const result = await workerResult(manager, "voice.list_engines");
    return result as unknown as ListEnginesResult;
  }

  return {
    async checkHealth(): Promise<EngineHealth> {
      const result = await listEngines();
      return result.health;
    },
    async listSpeakers(): Promise<readonly SpeakerOption[]> {
      const result = await listEngines();
      return result.speakers;
    },
    async preview(input: PreviewInput): Promise<PreviewResult> {
      const result = await workerResult(manager, "voice.preview", {
        speaker_id: input.speakerId,
        text: input.text,
        speed_scale: input.speedScale,
      });
      return { previewId: result.previewId as string, outputPath: result.outputPath as string };
    },
  };
}

/**
 * `voice_profile.*`(Projectに紐づくDB正本VoiceProfileのCRUD)を委譲する。
 * `voice.list_engines`(VOICEVOX engine自体のspeaker/style列挙)とは別concept。
 */
export function createVoiceProfileServiceAdapter(manager: WorkerManager): VoiceProfileServiceLike {
  return {
    async create(input: CreateVoiceProfileInput): Promise<VoiceProfileSummary> {
      const result = await workerResult(manager, "voice_profile.create", {
        project_id: input.projectId,
        name: input.name,
        engine: input.engine,
        speaker_id: input.speakerId,
        style_id: input.styleId,
        speed_scale: input.speedScale,
        pitch_scale: input.pitchScale,
        intonation_scale: input.intonationScale,
        volume_scale: input.volumeScale,
      });
      return toVoiceProfileSummary(result.voice_profile as Raw);
    },
    async list(projectId: string): Promise<readonly VoiceProfileSummary[]> {
      const result = await workerResult(manager, "voice_profile.list", { project_id: projectId });
      return (result.voice_profiles as Raw[]).map(toVoiceProfileSummary);
    },
    async get(voiceProfileId: string): Promise<VoiceProfileSummary> {
      const result = await workerResult(manager, "voice_profile.get", { voice_profile_id: voiceProfileId });
      return toVoiceProfileSummary(result.voice_profile as Raw);
    },
    async update(input: UpdateVoiceProfileInput): Promise<VoiceProfileSummary> {
      const result = await workerResult(manager, "voice_profile.update", {
        voice_profile_id: input.voiceProfileId,
        name: input.name,
        speed_scale: input.speedScale,
        pitch_scale: input.pitchScale,
        intonation_scale: input.intonationScale,
        volume_scale: input.volumeScale,
        status: input.status,
      });
      return toVoiceProfileSummary(result.voice_profile as Raw);
    },
    async archive(voiceProfileId: string): Promise<VoiceProfileSummary> {
      const result = await workerResult(manager, "voice_profile.archive", { voice_profile_id: voiceProfileId });
      return toVoiceProfileSummary(result.voice_profile as Raw);
    },
  };
}
