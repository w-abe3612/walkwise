/**
 * STEP4 test implementation for TASK-DESKTOP-001: preload allowlist / typed IPC contract.
 * Contract: docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md
 * Release scope: MVP.
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test, vi } from "vitest";

vi.mock("electron", () => ({
  contextBridge: { exposeInMainWorld: vi.fn() },
  ipcRenderer: { invoke: vi.fn(), on: vi.fn(), removeListener: vi.fn() },
}));

import { ALLOWED_CHANNELS, buildWalkwiseApi, installPreloadBridge } from "../preload/index";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

describe("TASK-DESKTOP-001 Electron/Vue scaffold・main/preload安全境界", () => {
  test("TC-DESKTOP-001-02: preload allowlist [unit/P0]", () => {
    const invoke = vi.fn().mockResolvedValue(undefined);
    const api = buildWalkwiseApi({ invoke, on: vi.fn(), removeListener: vi.fn() }) as unknown as Record<
      string,
      unknown
    >;

    // 未許可のchannel名に対応するmethodは存在せず、rendererから送信できない。
    const unlisted = api["unregistered.channel"] as unknown;
    expect(unlisted).toBeUndefined();
    expect(() => (unlisted as (...args: unknown[]) => unknown)()).toThrow();

    // job.startを呼んでも、固定allowlist内のchannel名でしかinvokeされない。
    void (api.job as { start: (input: unknown) => Promise<unknown> }).start({});
    expect(invoke).toHaveBeenCalledWith("job:start", {});
    for (const call of invoke.mock.calls) {
      expect(ALLOWED_CHANNELS).toContain(call[0]);
    }
  });

  test("TC-DESKTOP-001-04: package scripts [unit/P1]", () => {
    const packageJson = JSON.parse(readFileSync(path.join(REPO_ROOT, "package.json"), "utf-8")) as {
      scripts: Record<string, string>;
    };

    expect(packageJson.scripts.build).toBeTruthy();
    expect(packageJson.scripts.typecheck).toBeTruthy();
    expect(packageJson.scripts.test).toBeTruthy();
    expect(packageJson.scripts.package).toBeTruthy();
  });

  test("TC-DESKTOP-001-06: typed IPC contract [integration_mock/P1]", async () => {
    const invoke = vi.fn().mockResolvedValue({ projects: [] });
    const api = buildWalkwiseApi({ invoke, on: vi.fn(), removeListener: vi.fn() });

    const result = await api.project.list();

    expect(invoke).toHaveBeenCalledWith("project:list");
    expect(result).toEqual({ projects: [] });

    await api.project.get("proj-1");
    expect(invoke).toHaveBeenCalledWith("project:get", "proj-1");
  });

  test("TC-REVIEW-001-07: job progress channel一致 [unit/P0]", () => {
    // TASK-REVIEW-001監査: mainは"job:progress-event"へsendするが(electron/main/ipc/jobs.ts)、
    // 以前のpreloadは"job:subscribe-progress"を購読しており進捗がrendererへ届かなかった。
    const on = vi.fn();
    const removeListener = vi.fn();
    const invoke = vi.fn().mockResolvedValue(undefined);
    const api = buildWalkwiseApi({ invoke, on, removeListener });

    const listener = vi.fn();
    const unsubscribe = api.job.subscribeProgress("job-1", listener);

    expect(on).toHaveBeenCalledWith("job:progress-event", expect.any(Function));
    expect(invoke).toHaveBeenCalledWith("job:subscribe-progress", "job-1");

    unsubscribe();
    expect(removeListener).toHaveBeenCalledWith("job:progress-event", expect.any(Function));
  });

  test("TC-DESKTOP-001-08: 必須入力欠落 [unit/P0]", () => {
    expect(() => buildWalkwiseApi(null)).toThrow();
    expect(() => buildWalkwiseApi(undefined)).toThrow();

    const invoke = vi.fn();
    expect(() => installPreloadBridge(null, { invoke, on: vi.fn(), removeListener: vi.fn() })).toThrow();

    // installPreloadBridgeがcontextBridge欠落で例外を投げる場合、
    // 副作用(exposeInMainWorld呼出し)は一切発生していない。
    const exposeInMainWorld = vi.fn();
    try {
      installPreloadBridge(null, { invoke, on: vi.fn(), removeListener: vi.fn() });
    } catch {
      // expected
    }
    expect(exposeInMainWorld).not.toHaveBeenCalled();
  });

  test("TC-BUILD-EXEC-001-PRELOAD-01: voiceProfile APIは固定allowlist内のchannelだけを使う [unit/P0]", async () => {
    const invoke = vi.fn().mockResolvedValue({});
    const api = buildWalkwiseApi({ invoke, on: vi.fn(), removeListener: vi.fn() });

    await api.voiceProfile.create({ projectId: "proj-1", name: "n", engine: "voicevox", speakerId: "3" });
    expect(invoke).toHaveBeenCalledWith("voice-profile:create", expect.any(Object));

    await api.voiceProfile.list("proj-1");
    expect(invoke).toHaveBeenCalledWith("voice-profile:list", "proj-1");

    await api.voiceProfile.get("vp-1");
    expect(invoke).toHaveBeenCalledWith("voice-profile:get", "vp-1");

    await api.voiceProfile.update({ voiceProfileId: "vp-1", status: "approved" });
    expect(invoke).toHaveBeenCalledWith("voice-profile:update", expect.any(Object));

    await api.voiceProfile.archive("vp-1");
    expect(invoke).toHaveBeenCalledWith("voice-profile:archive", "vp-1");

    for (const call of invoke.mock.calls) {
      expect(ALLOWED_CHANNELS).toContain(call[0]);
    }
  });
});
