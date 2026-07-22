/**
 * electron/renderer/screens/ProjectWorkspace.types.ts — ProjectWorkspace.vueの型定義。
 *
 * `.vue`ファイルは`electron/env.d.ts`の汎用`declare module "*.vue"`shim経由でしか
 * plain `tsc`から型付けされず、named exportが認識されない(vue-tscでは可能だが
 * 本プロジェクトのtypecheck scriptはplain tscを使う)。そのため`<script setup>`側の
 * named export型をこの独立したplain `.ts`ファイルへ切り出し、componentとtestの
 * 両方がここから型をimportする。
 */

export interface SourceItem {
  readonly sourceId: string;
  readonly mediaType: string;
  readonly status: "registered" | "processing" | "ready" | "review_required" | "failed";
}

export interface ApprovalItem {
  readonly gate: string;
  readonly status: string;
}

/**
 * VoiceProfile関連の型(TASK-VOICE-PROFILE-UI-001)。
 *
 * `docs/db/06-voice-profiles-table.md`が定義するDB正本のcamelCase view。
 * `voice:list-engines`(VOICEVOX engine自体のspeaker/style列挙)とは別concept。
 */
export type VoiceProfileStatus = "draft" | "approved" | "archived";

export interface VoiceProfileItem {
  readonly voiceProfileId: string;
  readonly projectId: string;
  readonly name: string;
  readonly engine: string;
  readonly speakerId: string;
  readonly styleId?: string;
  readonly status: VoiceProfileStatus;
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

/** VoiceProfile作成・編集modal内のspeaker/style候補取得用(`voice:list-engines`由来)。 */
export interface VoiceEngineHealthView {
  readonly available: boolean;
  readonly detail?: string;
}

export interface VoiceSpeakerOptionView {
  readonly speakerId: string;
  readonly displayName: string;
  readonly styleIds: readonly string[];
}

export interface VoiceProfileFormInput {
  readonly name: string;
  readonly engine: string;
  readonly speakerId: string;
  readonly styleId?: string;
  readonly speedScale: number;
  readonly pitchScale: number;
  readonly intonationScale: number;
  readonly volumeScale: number;
  readonly sentencePauseMs: number;
  readonly paragraphPauseMs: number;
  readonly sectionPauseMs: number;
  readonly chapterPauseMs: number;
  readonly settingsJson: string;
}
