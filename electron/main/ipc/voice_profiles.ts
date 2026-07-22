/**
 * electron/main/ipc/voice_profiles.ts — 公開契約:
 * voice-profile:create/list/get/update/archive handlers.
 *
 * Contract: docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md(14節)
 * Spec: docs/db/06-voice-profiles-table.md
 *
 * `voice-profile:*`は、Projectに紐づくVoiceProfile(DB正本)のCRUDであり、
 * `voice:list-engines`(VOICEVOX engine自体のspeaker/style列挙)とは別concept
 * (混同しないこと)。DBスキーマ・業務ルール(name重複禁止、status遷移、Project
 * 所属検証等)はPython側(script/services/voice_profiles.py)にのみ存在させ、
 * ここではcamelCase(TS)<->snake_case(Python)の変換とhandler登録だけを行う。
 */

const ALLOWED_STATUSES = new Set(["draft", "approved", "archived"]);

export interface VoiceProfileSummary {
  readonly voiceProfileId: string;
  readonly projectId: string;
  readonly name: string;
  readonly engine: string;
  readonly speakerId: string;
  readonly styleId?: string;
  readonly status: string;
  readonly speedScale: number;
  readonly pitchScale: number;
  readonly intonationScale: number;
  readonly volumeScale: number;
  readonly sentencePauseMs: number;
  readonly paragraphPauseMs: number;
  readonly sectionPauseMs: number;
  readonly chapterPauseMs: number;
  readonly settingsJson: string;
  readonly updatedAt?: string;
}

export interface CreateVoiceProfileInput {
  readonly projectId: string;
  readonly name: string;
  readonly engine: string;
  readonly speakerId: string;
  readonly styleId?: string;
  readonly speedScale?: number;
  readonly pitchScale?: number;
  readonly intonationScale?: number;
  readonly volumeScale?: number;
  readonly sentencePauseMs?: number;
  readonly paragraphPauseMs?: number;
  readonly sectionPauseMs?: number;
  readonly chapterPauseMs?: number;
  readonly settingsJson?: string;
}

export interface UpdateVoiceProfileInput {
  readonly voiceProfileId: string;
  readonly name?: string;
  readonly engine?: string;
  readonly speakerId?: string;
  readonly styleId?: string;
  readonly speedScale?: number;
  readonly pitchScale?: number;
  readonly intonationScale?: number;
  readonly volumeScale?: number;
  readonly sentencePauseMs?: number;
  readonly paragraphPauseMs?: number;
  readonly sectionPauseMs?: number;
  readonly chapterPauseMs?: number;
  readonly settingsJson?: string;
  readonly status?: string;
}

export interface VoiceProfileServiceLike {
  create(input: CreateVoiceProfileInput): Promise<VoiceProfileSummary>;
  list(projectId: string): Promise<readonly VoiceProfileSummary[]>;
  get(voiceProfileId: string): Promise<VoiceProfileSummary>;
  update(input: UpdateVoiceProfileInput): Promise<VoiceProfileSummary>;
  archive(voiceProfileId: string): Promise<VoiceProfileSummary>;
}

export class VoiceProfileValidationError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface IpcMainLike {
  handle(channel: string, listener: (event: unknown, ...args: unknown[]) => unknown): void;
}

export interface VoiceProfileIpcContext {
  readonly ipcMain: IpcMainLike;
  readonly voiceProfileService: VoiceProfileServiceLike;
}

function requireNonEmptyString(raw: unknown, fieldName: string): string {
  if (typeof raw !== "string" || !raw.trim()) {
    throw new VoiceProfileValidationError("validation_error", `${fieldName} is required`);
  }
  return raw.trim();
}

function optionalNumber(raw: unknown, fieldName: string): number | undefined {
  if (raw === undefined || raw === null) {
    return undefined;
  }
  if (typeof raw !== "number" || Number.isNaN(raw)) {
    throw new VoiceProfileValidationError("validation_error", `${fieldName} must be a number`);
  }
  return raw;
}

function optionalString(raw: unknown, fieldName: string): string | undefined {
  if (raw === undefined || raw === null) {
    return undefined;
  }
  if (typeof raw !== "string") {
    throw new VoiceProfileValidationError("validation_error", `${fieldName} must be a string`);
  }
  return raw;
}

function optionalNonEmptyString(raw: unknown): string | undefined {
  return typeof raw === "string" && raw.trim() ? raw.trim() : undefined;
}

function validateCreateInput(raw: unknown): CreateVoiceProfileInput {
  if (!raw || typeof raw !== "object") {
    throw new VoiceProfileValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;
  return {
    projectId: requireNonEmptyString(input.projectId, "projectId"),
    name: requireNonEmptyString(input.name, "name"),
    engine: requireNonEmptyString(input.engine, "engine"),
    speakerId: requireNonEmptyString(input.speakerId, "speakerId"),
    styleId: optionalNonEmptyString(input.styleId),
    speedScale: optionalNumber(input.speedScale, "speedScale"),
    pitchScale: optionalNumber(input.pitchScale, "pitchScale"),
    intonationScale: optionalNumber(input.intonationScale, "intonationScale"),
    volumeScale: optionalNumber(input.volumeScale, "volumeScale"),
    sentencePauseMs: optionalNumber(input.sentencePauseMs, "sentencePauseMs"),
    paragraphPauseMs: optionalNumber(input.paragraphPauseMs, "paragraphPauseMs"),
    sectionPauseMs: optionalNumber(input.sectionPauseMs, "sectionPauseMs"),
    chapterPauseMs: optionalNumber(input.chapterPauseMs, "chapterPauseMs"),
    settingsJson: optionalString(input.settingsJson, "settingsJson"),
  };
}

function validateUpdateInput(raw: unknown): UpdateVoiceProfileInput {
  if (!raw || typeof raw !== "object") {
    throw new VoiceProfileValidationError("validation_error", "input must be an object");
  }
  const input = raw as Record<string, unknown>;
  const status = input.status;
  if (status !== undefined && (typeof status !== "string" || !ALLOWED_STATUSES.has(status))) {
    throw new VoiceProfileValidationError("validation_error", `unknown status: ${String(status)}`);
  }
  return {
    voiceProfileId: requireNonEmptyString(input.voiceProfileId, "voiceProfileId"),
    name: optionalNonEmptyString(input.name),
    engine: optionalNonEmptyString(input.engine),
    speakerId: optionalNonEmptyString(input.speakerId),
    styleId: optionalNonEmptyString(input.styleId),
    speedScale: optionalNumber(input.speedScale, "speedScale"),
    pitchScale: optionalNumber(input.pitchScale, "pitchScale"),
    intonationScale: optionalNumber(input.intonationScale, "intonationScale"),
    volumeScale: optionalNumber(input.volumeScale, "volumeScale"),
    sentencePauseMs: optionalNumber(input.sentencePauseMs, "sentencePauseMs"),
    paragraphPauseMs: optionalNumber(input.paragraphPauseMs, "paragraphPauseMs"),
    sectionPauseMs: optionalNumber(input.sectionPauseMs, "sectionPauseMs"),
    chapterPauseMs: optionalNumber(input.chapterPauseMs, "chapterPauseMs"),
    settingsJson: optionalString(input.settingsJson, "settingsJson"),
    status: status as string | undefined,
  };
}

/** Project所属のVoiceProfile CRUDをvoiceProfileServiceへ委譲する。 */
export function registerVoiceProfileIpcHandlers(context: VoiceProfileIpcContext): void {
  if (!context) {
    throw new Error("context is required");
  }
  if (!context.ipcMain) {
    throw new Error("ipcMain is required");
  }
  if (!context.voiceProfileService) {
    throw new Error("voiceProfileService is required");
  }

  context.ipcMain.handle("voice-profile:create", async (_event: unknown, rawInput: unknown) => {
    const validated = validateCreateInput(rawInput);
    return context.voiceProfileService.create(validated);
  });

  context.ipcMain.handle("voice-profile:list", async (_event: unknown, rawProjectId: unknown) => {
    const projectId = requireNonEmptyString(rawProjectId, "projectId");
    return context.voiceProfileService.list(projectId);
  });

  context.ipcMain.handle("voice-profile:get", async (_event: unknown, rawVoiceProfileId: unknown) => {
    const voiceProfileId = requireNonEmptyString(rawVoiceProfileId, "voiceProfileId");
    return context.voiceProfileService.get(voiceProfileId);
  });

  context.ipcMain.handle("voice-profile:update", async (_event: unknown, rawInput: unknown) => {
    const validated = validateUpdateInput(rawInput);
    return context.voiceProfileService.update(validated);
  });

  context.ipcMain.handle("voice-profile:archive", async (_event: unknown, rawVoiceProfileId: unknown) => {
    const voiceProfileId = requireNonEmptyString(rawVoiceProfileId, "voiceProfileId");
    return context.voiceProfileService.archive(voiceProfileId);
  });
}
