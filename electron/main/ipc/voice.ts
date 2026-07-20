/**
 * electron/main/ipc/voice.ts — 公開契約: voice:list-engines/preview handlers.
 *
 * Contract: docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md
 * Spec: docs/screens/03-build-settings.md
 */

export interface EngineHealth {
  readonly engine: string;
  readonly available: boolean;
  readonly detail?: string;
}

export interface SpeakerOption {
  readonly speakerId: string;
  readonly displayName: string;
  readonly styleIds: readonly string[];
}

export interface ListEnginesResult {
  readonly health: EngineHealth;
  readonly speakers: readonly SpeakerOption[];
}

export interface PreviewInput {
  readonly speakerId: string;
  readonly text: string;
  readonly speedScale?: number;
}

export interface PreviewResult {
  readonly previewId: string;
  readonly outputPath: string;
}

export interface VoiceServiceLike {
  checkHealth(): Promise<EngineHealth>;
  listSpeakers(): Promise<readonly SpeakerOption[]>;
  preview(input: PreviewInput): Promise<PreviewResult>;
}

export class VoiceValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface VoiceIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly voiceService: VoiceServiceLike;
}

function validatePreviewInput(raw: unknown): PreviewInput {
  if (!raw || typeof raw !== "object") {
    throw new VoiceValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;
  if (typeof input.speakerId !== "string" || !input.speakerId.trim()) {
    throw new VoiceValidationError("validation_error", "speakerId is required");
  }
  if (typeof input.text !== "string" || !input.text.trim()) {
    throw new VoiceValidationError("validation_error", "text is required");
  }
  return {
    speakerId: input.speakerId.trim(),
    text: input.text,
    speedScale: typeof input.speedScale === "number" ? input.speedScale : undefined,
  };
}

/** VOICEVOX状態確認後に一覧・試聴を実行する。 */
export function registerVoiceIpcHandlers(context: VoiceIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.voiceService) {
    throw new Error("voiceService is required");
  }

  context.ipcMain.handle("voice:list-engines", async (): Promise<ListEnginesResult> => {
    const health = await context.voiceService.checkHealth();
    // engine未接続の場合は空一覧を返す(呼び出し側が「明確なerror」を表示する材料はhealthに含まれる)。
    const speakers = health.available ? await context.voiceService.listSpeakers() : [];
    return { health, speakers };
  });

  context.ipcMain.handle("voice:preview", async (_event: unknown, rawInput: unknown) => {
    const validated = validatePreviewInput(rawInput);
    return context.voiceService.preview(validated);
  });
}
