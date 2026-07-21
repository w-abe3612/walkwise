/**
 * Tests for TASK-BUILD-EXEC-001 §14: voice-profile:create/list/get/update/archive IPC handlers.
 * Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(14節)
 */

import { describe, expect, test, vi } from "vitest";

import {
  registerVoiceProfileIpcHandlers,
  type IpcMainLike,
  type VoiceProfileServiceLike,
  type VoiceProfileSummary,
} from "../main/ipc/voice_profiles";

function fakeIpcMain(): { ipcMain: IpcMainLike; handlers: Map<string, (...args: unknown[]) => unknown> } {
  const handlers = new Map<string, (...args: unknown[]) => unknown>();
  const ipcMain: IpcMainLike = {
    handle: vi.fn((channel: string, listener: (...args: unknown[]) => unknown) => {
      handlers.set(channel, listener);
    }),
  };
  return { ipcMain, handlers };
}

const SAMPLE: VoiceProfileSummary = {
  voiceProfileId: "vp-1",
  projectId: "proj-1",
  name: "ナレーター1",
  engine: "voicevox",
  speakerId: "3",
  status: "draft",
  speedScale: 1.0,
  pitchScale: 0.0,
  intonationScale: 1.0,
  volumeScale: 1.0,
};

describe("TASK-BUILD-EXEC-001 voice-profile IPC handlers", () => {
  test("voice-profile:create validates required fields and delegates to the service", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const voiceProfileService: VoiceProfileServiceLike = {
      create: vi.fn().mockResolvedValue(SAMPLE),
      list: vi.fn(),
      get: vi.fn(),
      update: vi.fn(),
      archive: vi.fn(),
    };
    registerVoiceProfileIpcHandlers({ ipcMain, voiceProfileService });

    const createHandler = handlers.get("voice-profile:create")!;
    const result = await createHandler({}, { projectId: "proj-1", name: "ナレーター1", engine: "voicevox", speakerId: "3" });

    expect(voiceProfileService.create).toHaveBeenCalledWith(
      expect.objectContaining({ projectId: "proj-1", name: "ナレーター1", engine: "voicevox", speakerId: "3" }),
    );
    expect(result).toEqual(SAMPLE);

    await expect(createHandler({}, { name: "n" })).rejects.toThrow(/projectId is required/);
  });

  test("voice-profile:list/get delegate with the raw string argument", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const voiceProfileService: VoiceProfileServiceLike = {
      create: vi.fn(),
      list: vi.fn().mockResolvedValue([SAMPLE]),
      get: vi.fn().mockResolvedValue(SAMPLE),
      update: vi.fn(),
      archive: vi.fn(),
    };
    registerVoiceProfileIpcHandlers({ ipcMain, voiceProfileService });

    const listResult = await handlers.get("voice-profile:list")!({}, "proj-1");
    expect(voiceProfileService.list).toHaveBeenCalledWith("proj-1");
    expect(listResult).toEqual([SAMPLE]);

    const getResult = await handlers.get("voice-profile:get")!({}, "vp-1");
    expect(voiceProfileService.get).toHaveBeenCalledWith("vp-1");
    expect(getResult).toEqual(SAMPLE);
  });

  test("voice-profile:update rejects unknown status values before calling the service", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const voiceProfileService: VoiceProfileServiceLike = {
      create: vi.fn(),
      list: vi.fn(),
      get: vi.fn(),
      update: vi.fn().mockResolvedValue({ ...SAMPLE, status: "approved" }),
      archive: vi.fn(),
    };
    registerVoiceProfileIpcHandlers({ ipcMain, voiceProfileService });

    const updateHandler = handlers.get("voice-profile:update")!;
    const result = await updateHandler({}, { voiceProfileId: "vp-1", status: "approved" });
    expect(result).toEqual({ ...SAMPLE, status: "approved" });

    await expect(updateHandler({}, { voiceProfileId: "vp-1", status: "not-a-real-status" })).rejects.toThrow(
      /unknown status/,
    );
    expect(voiceProfileService.update).toHaveBeenCalledTimes(1);
  });

  test("voice-profile:archive delegates to the service", async () => {
    const { ipcMain, handlers } = fakeIpcMain();
    const voiceProfileService: VoiceProfileServiceLike = {
      create: vi.fn(),
      list: vi.fn(),
      get: vi.fn(),
      update: vi.fn(),
      archive: vi.fn().mockResolvedValue({ ...SAMPLE, status: "archived" }),
    };
    registerVoiceProfileIpcHandlers({ ipcMain, voiceProfileService });

    const result = await handlers.get("voice-profile:archive")!({}, "vp-1");
    expect(voiceProfileService.archive).toHaveBeenCalledWith("vp-1");
    expect(result).toEqual({ ...SAMPLE, status: "archived" });
  });

  test("registration requires ipcMain and voiceProfileService (fail-closed on missing deps)", () => {
    const { ipcMain } = fakeIpcMain();
    expect(() => registerVoiceProfileIpcHandlers(undefined as never)).toThrow(/context is required/);
    expect(() => registerVoiceProfileIpcHandlers({ ipcMain, voiceProfileService: undefined as never })).toThrow(
      /voiceProfileService is required/,
    );
    expect(ipcMain.handle).not.toHaveBeenCalled();
  });
});
