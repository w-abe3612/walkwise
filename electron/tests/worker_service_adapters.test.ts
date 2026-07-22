/**
 * Tests for TASK-REVIEW-001 P0 fix: Electron *ServiceLike adapters wired to the
 * Python Worker subprocess (previously no such wiring existed at all — every
 * *ServiceLike in electron/main/ipc/*.ts had zero real implementations).
 *
 * A fake child process echoes scripted JSON Lines responses so these tests exercise
 * the real WorkerManager request/response plumbing and the adapters' camelCase<->
 * snake_case mapping, without spawning a real Python subprocess.
 */

import { EventEmitter } from "node:events";
import { describe, expect, test, vi } from "vitest";

import type { ChildProcessLike } from "../main/worker_manager";
import { WorkerManager } from "../main/worker_manager";
import {
  createApprovalGateCheckerAdapter,
  createApprovalServiceAdapter,
  createArtifactServiceAdapter,
  createBuildServiceAdapter,
  createJobServiceAdapter,
  createProjectServiceAdapter,
  createSourceServiceAdapter,
  createVoiceProfileServiceAdapter,
  createVoiceServiceAdapter,
  type ShellLike,
} from "../main/worker_service_adapters";

type Responder = (parameters: Record<string, unknown>) => Record<string, unknown> | { errorCode: string; errorMessage: string };

function fakeWorkerManager(responders: Record<string, Responder>): WorkerManager {
  const stdout = new EventEmitter();
  const stderr = new EventEmitter();

  function handleLine(line: string): void {
    const request = JSON.parse(line) as { job_id: string; job_type: string; parameters: Record<string, unknown> };
    const responder = responders[request.job_type];
    if (!responder) {
      stdout.emit("data", `${JSON.stringify({ event: "started", job_id: request.job_id })}\n`);
      stdout.emit(
        "data",
        `${JSON.stringify({ event: "error", job_id: request.job_id, code: "unknown_job_type", message: request.job_type })}\n`,
      );
      return;
    }
    const outcome = responder(request.parameters);
    stdout.emit("data", `${JSON.stringify({ event: "started", job_id: request.job_id })}\n`);
    if ("errorCode" in outcome) {
      stdout.emit(
        "data",
        `${JSON.stringify({ event: "error", job_id: request.job_id, code: outcome.errorCode, message: outcome.errorMessage })}\n`,
      );
      return;
    }
    stdout.emit("data", `${JSON.stringify({ event: "completed", job_id: request.job_id, result: outcome })}\n`);
  }

  const emitter = new EventEmitter();
  const child = Object.assign(emitter, {
    stdin: { write: (chunk: string) => chunk.split("\n").filter((l) => l.trim()).forEach(handleLine) },
    stdout,
    stderr,
    kill: vi.fn(),
  }) as unknown as ChildProcessLike;

  const manager = new WorkerManager({ command: "python", spawn: () => child });
  manager.start();
  return manager;
}

describe("TASK-REVIEW-001 Worker service adapters", () => {
  test("project adapter maps camelCase<->snake_case through project.list/create/get", async () => {
    const manager = fakeWorkerManager({
      "project.list": () => ({
        projects: [{ project_id: "p1", title: "t", planning_stage: "registered", updated_at: "2026-07-20T00:00:00Z" }],
      }),
      "project.create": (params) => ({
        project: {
          project_id: "p2",
          title: params.title,
          planning_stage: "registered",
          updated_at: "2026-07-20T00:00:00Z",
        },
      }),
      "project.get": () => ({
        project: { project_id: "p1", title: "t", planning_stage: "registered", updated_at: "2026-07-20T00:00:00Z" },
      }),
    });
    const adapter = createProjectServiceAdapter(manager);

    const list = await adapter.list();
    expect(list).toEqual([{ projectId: "p1", title: "t", planningStage: "registered", updatedAt: "2026-07-20T00:00:00Z" }]);

    const created = await adapter.create({
      title: "新規",
      domain: "d",
      purpose: "p",
      usagePurpose: "personal_learning",
      targetAudienceDescription: "x",
      sourceStrategy: ["upload_files"],
    });
    expect(created.projectId).toBe("p2");
    expect(created.title).toBe("新規");

    const got = await adapter.get("p1");
    expect(got.projectId).toBe("p1");
  });

  test("source adapter maps register/list/retry", async () => {
    const manager = fakeWorkerManager({
      "source.register": (params) => ({
        source: {
          source_id: "s1",
          project_id: params.project_id,
          media_type: params.media_type,
          status: "ready",
        },
      }),
      "source.list": () => ({
        sources: [{ source_id: "s1", project_id: "p1", media_type: "text", status: "ready" }],
      }),
      "source.retry": (params) => ({
        source: { source_id: params.source_id, project_id: "p1", media_type: "image", status: "registered" },
      }),
    });
    const adapter = createSourceServiceAdapter(manager);

    const registered = await adapter.register({ projectId: "p1", filePath: "/tmp/a.txt", mediaType: "text" });
    expect(registered).toEqual({ sourceId: "s1", projectId: "p1", mediaType: "text", status: "ready" });

    const list = await adapter.list("p1");
    expect(list).toHaveLength(1);

    const retried = await adapter.retry("s1");
    expect(retried.status).toBe("registered");
  });

  test("approval gate checker adapter is fail-closed via build_request.approval_gate_satisfied", async () => {
    const manager = fakeWorkerManager({
      "build_request.approval_gate_satisfied": (params) => ({ satisfied: params.build_request_id === "br-approved" }),
    });
    const checker = createApprovalGateCheckerAdapter(manager);

    expect(await checker.isSatisfied("br-approved")).toBe(true);
    expect(await checker.isSatisfied("br-other")).toBe(false);
  });

  test("build + job adapters map build_request.create/job.start/job.get/job.cancel/job.retry", async () => {
    const manager = fakeWorkerManager({
      "build_request.create": (params) => ({
        build_request: {
          build_request_id: "br1",
          project_id: params.project_id,
          output_formats: params.output_formats,
          voice_profile_id: params.voice_profile_id ?? null,
        },
      }),
      "job.start": () => ({
        job: { job_id: "j1", build_request_id: "br1", job_type: "build", status: "running" },
      }),
      "job.get": () => ({
        job: {
          job_id: "j1",
          build_request_id: "br1",
          job_type: "build",
          status: "running",
          progress_current: 2,
          progress_total: 5,
          last_message: "章2を処理中",
        },
      }),
      "job.cancel": () => ({
        job: { job_id: "j1", build_request_id: "br1", job_type: "build", status: "cancel_requested" },
      }),
      "job.retry": () => ({
        job: { job_id: "j2", build_request_id: "br1", job_type: "build", status: "queued" },
      }),
    });
    const buildAdapter = createBuildServiceAdapter(manager);
    const jobAdapter = createJobServiceAdapter(manager);

    const buildRequest = await buildAdapter.createBuildRequest({ projectId: "p1", outputFormats: ["text"] });
    expect(buildRequest.buildRequestId).toBe("br1");

    const started = await buildAdapter.startJob("br1");
    expect(started.status).toBe("running");

    const job = await jobAdapter.get("j1");
    expect(job).toMatchObject({ jobId: "j1", progressCurrent: 2, progressTotal: 5, lastMessage: "章2を処理中" });

    const cancelled = await jobAdapter.cancel("j1");
    expect(cancelled.status).toBe("cancel_requested");

    const retried = await jobAdapter.retry("j1");
    expect(retried.jobId).toBe("j2");
  });

  test("job progress polling adapter stops once a terminal status is observed", async () => {
    let callCount = 0;
    const manager = fakeWorkerManager({
      "job.get": () => {
        callCount += 1;
        const status = callCount < 3 ? "running" : "succeeded";
        return {
          job: {
            job_id: "j1",
            build_request_id: "br1",
            job_type: "build",
            status,
            progress_current: callCount,
            progress_total: 3,
          },
        };
      },
    });
    const jobAdapter = createJobServiceAdapter(manager);

    const events: unknown[] = [];
    await new Promise<void>((resolve) => {
      const unsubscribe = jobAdapter.subscribeProgress("j1", (event) => {
        events.push(event);
        if (events.length >= 3) {
          unsubscribe();
          resolve();
        }
      });
    });

    expect(events.length).toBeGreaterThanOrEqual(3);
  });

  test("artifact adapter resolves the absolute path and opens it via shell", async () => {
    const manager = fakeWorkerManager({
      "artifact.list": () => ({
        artifacts: [
          {
            artifact_id: "a1",
            job_id: "j1",
            project_id: "p1",
            artifact_type: "mp3_chapter",
            file_path: "audio/ch01.mp3",
            version_number: 1,
            created_at: "2026-07-20T00:00:00Z",
          },
        ],
      }),
      "artifact.get": () => ({
        artifact: {
          artifact_id: "a1",
          project_id: "p1",
          file_path: "audio/ch01.mp3",
        },
      }),
    });
    const showItemInFolder = vi.fn();
    const shell: ShellLike = { showItemInFolder };
    const adapter = createArtifactServiceAdapter(manager, "/data", shell);

    const list = await adapter.list("p1");
    expect(list).toEqual([
      { artifactId: "a1", artifactType: "mp3_chapter", versionNumber: 1, filePath: "audio/ch01.mp3", createdAt: "2026-07-20T00:00:00Z", jobId: "j1" },
    ]);

    await adapter.openFolder("a1");
    expect(showItemInFolder).toHaveBeenCalledWith("/data/p1/audio/ch01.mp3");
  });

  test("voice adapter maps voice.list_engines/preview", async () => {
    const manager = fakeWorkerManager({
      "voice.list_engines": () => ({
        health: { engine: "voicevox", available: true, detail: null },
        speakers: [{ speakerId: "3", displayName: "四国めたん", styleIds: ["3"] }],
      }),
      "voice.preview": () => ({ previewId: "prev-1", outputPath: "previews/prev-1.wav" }),
    });
    const adapter = createVoiceServiceAdapter(manager);

    const health = await adapter.checkHealth();
    expect(health.available).toBe(true);

    const speakers = await adapter.listSpeakers();
    expect(speakers).toHaveLength(1);

    const preview = await adapter.preview({ speakerId: "3", text: "サンプル" });
    expect(preview.previewId).toBe("prev-1");
  });

  test("approval adapter maps approval.list/approve/request_changes", async () => {
    const manager = fakeWorkerManager({
      "approval.list": () => ({ approvals: [{ gate: "planning", status: "draft", comment: null }] }),
      "approval.approve": (params) => ({ gate: params.gate, status: "approved", comment: null }),
      "approval.request_changes": (params) => ({ gate: params.gate, status: "changes_requested", comment: params.reason }),
    });
    const adapter = createApprovalServiceAdapter(manager);

    const list = await adapter.list("p1");
    expect(list).toEqual([{ gate: "planning", status: "draft", comment: undefined }]);

    const approved = await adapter.approve({ projectId: "p1", gate: "planning", approvedBy: "reviewer" });
    expect(approved.status).toBe("approved");

    const changes = await adapter.requestChanges({ projectId: "p1", gate: "planning", reason: "修正してください" });
    expect(changes.comment).toBe("修正してください");
  });

  test("voice profile adapter maps voice_profile.create/list/get/update/archive", async () => {
    const record = (overrides: Record<string, unknown> = {}) => ({
      voice_profile_id: "vp-1",
      project_id: "proj-1",
      name: "ナレーター1",
      engine: "voicevox",
      speaker_id: "3",
      style_id: null,
      status: "draft",
      speed_scale: 1.0,
      pitch_scale: 0.0,
      intonation_scale: 1.0,
      volume_scale: 1.0,
      sentence_pause_ms: 250,
      paragraph_pause_ms: 600,
      section_pause_ms: 1000,
      chapter_pause_ms: 1500,
      settings_json: "{}",
      updated_at: "2026-07-22T00:00:00+09:00",
      ...overrides,
    });

    const manager = fakeWorkerManager({
      "voice_profile.create": (params) => ({
        voice_profile: record({
          project_id: params.project_id, name: params.name, paragraph_pause_ms: params.paragraph_pause_ms,
        }),
      }),
      "voice_profile.list": () => ({ voice_profiles: [record()] }),
      "voice_profile.get": () => ({ voice_profile: record() }),
      "voice_profile.update": (params) => ({
        voice_profile: record({ status: "approved", speaker_id: params.speaker_id ?? "3" }),
      }),
      "voice_profile.archive": () => ({ voice_profile: record({ status: "archived" }) }),
    });
    const adapter = createVoiceProfileServiceAdapter(manager);

    const created = await adapter.create({
      projectId: "proj-1", name: "ナレーター1", engine: "voicevox", speakerId: "3", paragraphPauseMs: 800,
    });
    expect(created.voiceProfileId).toBe("vp-1");
    expect(created.name).toBe("ナレーター1");
    expect(created.paragraphPauseMs).toBe(800);
    expect(created.settingsJson).toBe("{}");

    const list = await adapter.list("proj-1");
    expect(list).toHaveLength(1);
    expect(list[0].status).toBe("draft");
    expect(list[0].sentencePauseMs).toBe(250);

    const got = await adapter.get("vp-1");
    expect(got.speakerId).toBe("3");

    const updated = await adapter.update({ voiceProfileId: "vp-1", status: "approved", speakerId: "8" });
    expect(updated.status).toBe("approved");
    expect(updated.speakerId).toBe("8");

    const archived = await adapter.archive("vp-1");
    expect(archived.status).toBe("archived");
  });
});
