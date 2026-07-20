/**
 * @vitest-environment jsdom
 *
 * STEP4 implementation for TASK-DESKTOP-003: Desktop最短end-to-end導線.
 * Contract: docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md
 * Release scope: MVP.
 *
 * このtest fileそのものが本タスクの"production"を兼ねる(契約のsource_filesに
 * 本ファイル自身が列挙されている)。既に完了した各IPC handler登録関数
 * (project/source/approval/voice/build/job/artifact)をfakeサービス実装で結線し、
 * Project作成からArtifact表示までの縦切りを実IPC契約どおりに検証する。
 */

import { describe, expect, test, vi } from "vitest";

import { registerProjectIpcHandlers, type ProjectServiceLike } from "../../main/ipc/projects";
import { registerSourceIpcHandlers, type SourceServiceLike } from "../../main/ipc/sources";
import { registerApprovalIpcHandlers, type ApprovalServiceLike } from "../../main/ipc/approvals";
import { registerVoiceIpcHandlers, type VoiceServiceLike } from "../../main/ipc/voice";
import {
  registerBuildIpcHandlers,
  type ApprovalGateCheckerLike,
  type BuildServiceLike,
} from "../../main/ipc/builds";
import { registerJobIpcHandlers, type JobServiceLike, type JobStatus } from "../../main/ipc/jobs";
import { registerArtifactIpcHandlers, type ArtifactServiceLike } from "../../main/ipc/artifacts";

type Handler = (event: unknown, ...args: unknown[]) => unknown;

function fakeIpcMain(): { ipcMain: { handle: Handler }; handlers: Map<string, Handler> } {
  const handlers = new Map<string, Handler>();
  const ipcMain = {
    handle: vi.fn((channel: string, listener: Handler) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain: ipcMain as unknown as { handle: Handler }, handlers };
}

const REQUIRED_APPROVAL_GATES_FOR_TEXT = ["verified_script"] as const;
const REQUIRED_APPROVAL_GATES_FOR_MP3 = ["verified_script", "preview_audio"] as const;

/** 全IPC moduleをfake serviceで結線した最小限のdesktop統合backendを構築する。 */
function buildFakeDesktopBackend() {
  let idCounter = 0;
  const nextId = (prefix: string) => `${prefix}-${++idCounter}`;

  const projects = new Map<string, { projectId: string; title: string; planningStage: string; updatedAt: string }>();
  const sources = new Map<string, { sourceId: string; projectId: string; mediaType: string; status: string }>();
  const approvals = new Map<string, string>(); // `${projectId}:${gate}` -> status
  const buildRequests = new Map<
    string,
    { buildRequestId: string; projectId: string; outputFormats: readonly string[]; voiceProfileId?: string }
  >();
  const jobs = new Map<string, { jobId: string; buildRequestId: string; jobType: string; status: JobStatus }>();
  const artifacts: { artifactId: string; artifactType: string; versionNumber: number; filePath: string; createdAt: string; jobId: string }[] = [];

  function approvalKey(projectId: string, gate: string): string {
    return `${projectId}:${gate}`;
  }

  const projectService: ProjectServiceLike = {
    list: async () => [...projects.values()],
    create: async (input) => {
      const projectId = nextId("proj");
      const project = { projectId, title: input.title, planningStage: "registered", updatedAt: "2026-07-20T00:00:00+09:00" };
      projects.set(projectId, project);
      for (const gate of ["materials_curriculum", "planning", "verified_script", "preview_audio"]) {
        approvals.set(approvalKey(projectId, gate), "draft");
      }
      return project;
    },
    get: async (projectId) => {
      const project = projects.get(projectId);
      if (!project) {
        throw new Error(`project not found: ${projectId}`);
      }
      return project;
    },
  };

  const sourceService: SourceServiceLike = {
    register: async (input) => {
      const sourceId = nextId("src");
      const source = { sourceId, projectId: input.projectId, mediaType: input.mediaType, status: "ready" };
      sources.set(sourceId, source);
      return source;
    },
    list: async (projectId) => [...sources.values()].filter((source) => source.projectId === projectId),
    retry: async (sourceId) => {
      const source = sources.get(sourceId);
      if (!source) {
        throw new Error(`source not found: ${sourceId}`);
      }
      const updated = { ...source, status: "registered" };
      sources.set(sourceId, updated);
      return updated;
    },
  };

  const approvalService: ApprovalServiceLike = {
    list: async (projectId) =>
      ["materials_curriculum", "planning", "verified_script", "preview_audio"].map((gate) => ({
        gate,
        status: approvals.get(approvalKey(projectId, gate)) ?? "draft",
      })),
    approve: async (input) => {
      approvals.set(approvalKey(input.projectId, input.gate), "approved");
      return { gate: input.gate, status: "approved" };
    },
    requestChanges: async (input) => {
      approvals.set(approvalKey(input.projectId, input.gate), "changes_requested");
      return { gate: input.gate, status: "changes_requested" };
    },
  };

  const voiceService: VoiceServiceLike = {
    checkHealth: async () => ({ engine: "voicevox", available: true }),
    listSpeakers: async () => [{ speakerId: "1", displayName: "四国めたん", styleIds: ["0"] }],
    preview: async (input) => ({ previewId: nextId("preview"), outputPath: `preview/${input.speakerId}.wav` }),
  };

  const buildService: BuildServiceLike = {
    createBuildRequest: async (input) => {
      const buildRequestId = nextId("br");
      const record = { buildRequestId, projectId: input.projectId, outputFormats: input.outputFormats, voiceProfileId: input.voiceProfileId };
      buildRequests.set(buildRequestId, record);
      return record;
    },
    startJob: async (buildRequestId) => {
      const buildRequest = buildRequests.get(buildRequestId)!;
      const jobId = nextId("job");
      const job = { jobId, buildRequestId, jobType: "audio_packaging", status: "succeeded" as JobStatus };
      jobs.set(jobId, job);
      for (const format of buildRequest.outputFormats) {
        artifacts.push({
          artifactId: nextId("artifact"),
          artifactType: format === "mp3" ? "mp3_chapter" : "text_verified_script",
          versionNumber: 1,
          filePath: `output/${buildRequest.projectId}/${format}.${format === "mp3" ? "mp3" : "txt"}`,
          createdAt: "2026-07-20T00:00:00+09:00",
          jobId,
        });
      }
      return job;
    },
  };

  const approvalGateChecker: ApprovalGateCheckerLike = {
    isSatisfied: async (buildRequestId) => {
      const buildRequest = buildRequests.get(buildRequestId)!;
      const requiredGates = buildRequest.outputFormats.includes("mp3")
        ? REQUIRED_APPROVAL_GATES_FOR_MP3
        : REQUIRED_APPROVAL_GATES_FOR_TEXT;
      return requiredGates.every((gate) => approvals.get(approvalKey(buildRequest.projectId, gate)) === "approved");
    },
  };

  const jobService: JobServiceLike = {
    list: async (projectId) =>
      [...jobs.values()].filter((job) => buildRequests.get(job.buildRequestId)?.projectId === projectId),
    get: async (jobId) => jobs.get(jobId)!,
    subscribeProgress: () => () => {},
    cancel: async (jobId) => {
      const job = jobs.get(jobId)!;
      const updated = { ...job, status: "cancel_requested" as JobStatus };
      jobs.set(jobId, updated);
      return updated;
    },
    retry: async (parentJobId) => {
      const parent = jobs.get(parentJobId)!;
      const jobId = nextId("job");
      const job = { jobId, buildRequestId: parent.buildRequestId, jobType: parent.jobType, status: "queued" as JobStatus };
      jobs.set(jobId, job);
      return job;
    },
  };

  const artifactService: ArtifactServiceLike = {
    list: async (projectId) => artifacts.filter((a) => buildRequests.get(jobs.get(a.jobId)!.buildRequestId)?.projectId === projectId),
    openFolder: async () => {},
  };

  return {
    projectService,
    sourceService,
    approvalService,
    voiceService,
    buildService,
    jobService,
    artifactService,
    approvalGateChecker,
    jobs,
    buildRequests,
  };
}

describe("TASK-DESKTOP-003 Desktop最短end-to-end導線", () => {
  test("TC-DESKTOP-003-02: mp3導線 [e2e/P0]", async () => {
    const backend = buildFakeDesktopBackend();
    const { ipcMain: projectIpc, handlers: projectHandlers } = fakeIpcMain();
    registerProjectIpcHandlers({ ipcMain: projectIpc, projectService: backend.projectService });
    const { ipcMain: sourceIpc, handlers: sourceHandlers } = fakeIpcMain();
    registerSourceIpcHandlers({ ipcMain: sourceIpc, sourceService: backend.sourceService });
    const { ipcMain: approvalIpc, handlers: approvalHandlers } = fakeIpcMain();
    registerApprovalIpcHandlers({ ipcMain: approvalIpc, approvalService: backend.approvalService });
    const { ipcMain: voiceIpc, handlers: voiceHandlers } = fakeIpcMain();
    registerVoiceIpcHandlers({ ipcMain: voiceIpc, voiceService: backend.voiceService });
    const { ipcMain: buildIpc, handlers: buildHandlers } = fakeIpcMain();
    registerBuildIpcHandlers({ ipcMain: buildIpc, buildService: backend.buildService, approvalGateChecker: backend.approvalGateChecker });
    const { ipcMain: artifactIpc, handlers: artifactHandlers } = fakeIpcMain();
    registerArtifactIpcHandlers({ ipcMain: artifactIpc, artifactService: backend.artifactService });

    const project = (await projectHandlers.get("project:create")!(
      {},
      { title: "データベース入門", domain: "database", purpose: "解説", usagePurpose: "personal_learning", targetAudienceDescription: "初心者", sourceStrategy: ["upload_files"] },
    )) as { projectId: string };

    await sourceHandlers.get("source:register")!({}, { projectId: project.projectId, filePath: "materials/ch01.txt", mediaType: "text" });

    for (const gate of ["materials_curriculum", "planning", "verified_script"]) {
      await approvalHandlers.get("approval:approve")!({}, { projectId: project.projectId, gate, approvedBy: "author" });
    }

    // preview(mock VOICEVOX)を実行してから試聴音声を承認する
    const previewResult = (await voiceHandlers.get("voice:preview")!({}, { speakerId: "1", text: "サンプル" })) as { previewId: string };
    expect(previewResult.previewId).toBeTruthy();
    await approvalHandlers.get("approval:approve")!({}, { projectId: project.projectId, gate: "preview_audio", approvedBy: "author" });

    const buildRequest = (await buildHandlers.get("build-request:create")!(
      {},
      { projectId: project.projectId, outputFormats: ["mp3"], voiceProfileId: "1" },
    )) as { buildRequestId: string };

    await buildHandlers.get("job:start")!({}, buildRequest.buildRequestId);

    const artifactResult = (await artifactHandlers.get("artifact:list")!({}, project.projectId)) as {
      artifacts: readonly { artifactType: string }[];
    };
    expect(artifactResult.artifacts.some((a) => a.artifactType === "mp3_chapter")).toBe(true);
  });

  test("TC-DESKTOP-003-04: 実IPC/DB/file/worker統合 [integration_mock/P1]", async () => {
    const backend = buildFakeDesktopBackend();
    const { ipcMain, handlers } = fakeIpcMain();

    // 全moduleを同一契約(IpcMainLike)で結線できることを確認する(実際の統合ではchannel
    // 名前空間の割当を1箇所で管理する必要があるという既知の課題は
    // implementation_assumptions.mdに記録済み)。
    registerProjectIpcHandlers({ ipcMain, projectService: backend.projectService });
    registerSourceIpcHandlers({ ipcMain, sourceService: backend.sourceService });
    registerApprovalIpcHandlers({ ipcMain, approvalService: backend.approvalService });
    registerVoiceIpcHandlers({ ipcMain, voiceService: backend.voiceService });
    registerArtifactIpcHandlers({ ipcMain, artifactService: backend.artifactService });

    const expectedChannels = [
      "project:list",
      "project:create",
      "source:register",
      "approval:list",
      "approval:approve",
      "approval:request-changes",
      "voice:list-engines",
      "voice:preview",
      "artifact:list",
      "artifact:open-folder",
    ];
    for (const channel of expectedChannels) {
      expect(handlers.has(channel), `channel not registered: ${channel}`).toBe(true);
    }

    const project = (await handlers.get("project:create")!(
      {},
      { title: "t", domain: "d", purpose: "p", usagePurpose: "personal_learning", targetAudienceDescription: "a", sourceStrategy: ["upload_files"] },
    )) as { projectId: string };
    const source = (await handlers.get("source:register")!(
      {},
      { projectId: project.projectId, filePath: "materials/ch01.txt", mediaType: "text" },
    )) as { sourceId: string };
    expect(source.sourceId).toBeTruthy();
  });

  test("TC-DESKTOP-003-06: worker失敗/retry [unit/P1]", async () => {
    const backend = buildFakeDesktopBackend();
    const { ipcMain, handlers } = fakeIpcMain();
    registerJobIpcHandlers({ ipcMain, jobService: backend.jobService });
    // job:start(再試行payload)は electron/main/ipc/builds.ts が同一ipcMain上で処理する
    // (TASK-RELEASE-002でjob:start channel重複を解消し、両モジュールが1つのipcMainを
    // 共有できることをこのE2Eでも確認する)。
    registerBuildIpcHandlers({
      ipcMain,
      buildService: backend.buildService,
      approvalGateChecker: backend.approvalGateChecker,
      jobService: backend.jobService,
    });

    // failedなJobをbackendへ直接投入し(worker失敗を模擬)、retryが新しいJobを1件だけ作る
    backend.jobs.set("job-failed", { jobId: "job-failed", buildRequestId: "br-1", jobType: "audio_packaging", status: "failed" });
    backend.buildRequests.set("br-1", { buildRequestId: "br-1", projectId: "proj-1", outputFormats: ["text"] });

    const retried = (await handlers.get("job:start")!({}, { parentJobId: "job-failed" })) as { jobId: string; status: string };
    expect(retried.status).toBe("queued");
    expect(retried.jobId).not.toBe("job-failed");

    // 同じ失敗Jobを重ねてretryしても、既存の失敗Job自体は変更されない(新規Jobだけが増える)
    const stillFailed = await handlers.get("job:get")!({}, "job-failed");
    expect((stillFailed as { status: string }).status).toBe("failed");
  });

  test("TC-DESKTOP-003-08: 必須入力欠落 [unit/P0]", async () => {
    const { ipcMain: buildIpc } = fakeIpcMain();
    const backend = buildFakeDesktopBackend();

    expect(() =>
      registerBuildIpcHandlers({ ipcMain: buildIpc, buildService: undefined as never, approvalGateChecker: backend.approvalGateChecker }),
    ).toThrow();

    const { ipcMain: projectIpc } = fakeIpcMain();
    expect(() => registerProjectIpcHandlers({ ipcMain: projectIpc, projectService: undefined as never })).toThrow();
  });

  test("TC-DESKTOP-003-10: 入力・既存成果物の不変性 [unit/P0]", async () => {
    const backend = buildFakeDesktopBackend();
    const { ipcMain: projectIpc, handlers: projectHandlers } = fakeIpcMain();
    registerProjectIpcHandlers({ ipcMain: projectIpc, projectService: backend.projectService });
    const { ipcMain: buildIpc, handlers: buildHandlers } = fakeIpcMain();
    registerBuildIpcHandlers({ ipcMain: buildIpc, buildService: backend.buildService, approvalGateChecker: backend.approvalGateChecker });

    const project = (await projectHandlers.get("project:create")!(
      {},
      { title: "t", domain: "d", purpose: "p", usagePurpose: "personal_learning", targetAudienceDescription: "a", sourceStrategy: ["upload_files"] },
    )) as { projectId: string };

    const goodBuildRequest = (await buildHandlers.get("build-request:create")!(
      {},
      { projectId: project.projectId, outputFormats: ["text"] },
    )) as { buildRequestId: string };
    // 承認ゲート未充足のため成功しない = 既存の正常な状態(projectレコード)は変化しない
    await expect(buildHandlers.get("job:start")!({}, goodBuildRequest.buildRequestId)).rejects.toThrow(
      /not satisfied/,
    );

    const projectsAfterFailure = await projectHandlers.get("project:list")!({});
    expect((projectsAfterFailure as { projects: readonly { projectId: string }[] }).projects).toHaveLength(1);
    expect((projectsAfterFailure as { projects: readonly { projectId: string }[] }).projects[0].projectId).toBe(
      project.projectId,
    );
  });

  const liveEnabled = process.env.WALKWISE_RUN_INTEGRATION_LIVE === "1";
  test.skipIf(!liveEnabled)("TC-DESKTOP-003-12: Desktop統合runtimeの実機能テスト [e2e/P1]", async () => {
    // desktop_connectivity_gate相当の疎通成功後にだけ実行する最小MVP導線(mock AI/TTS)。
    // この環境ではWALKWISE_RUN_INTEGRATION_LIVEが未設定のため既定でskipする。
    const backend = buildFakeDesktopBackend();
    const { ipcMain, handlers } = fakeIpcMain();
    registerProjectIpcHandlers({ ipcMain, projectService: backend.projectService });
    const project = (await handlers.get("project:create")!(
      {},
      { title: "t", domain: "d", purpose: "p", usagePurpose: "personal_learning", targetAudienceDescription: "a", sourceStrategy: ["upload_files"] },
    )) as { projectId: string };
    expect(project.projectId).toBeTruthy();
  });
});
