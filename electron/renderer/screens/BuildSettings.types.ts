/**
 * electron/renderer/screens/BuildSettings.types.ts — BuildSettings.vueの型定義。
 *
 * `.vue`ファイルはplain tscからnamed exportを認識されないため
 * (詳細は`ProjectWorkspace.types.ts`と同じ理由)、型のみ独立ファイルへ切り出す。
 */

export type OutputFormat = "mp3" | "text";

export interface EngineHealthView {
  readonly available: boolean;
  readonly detail?: string;
}

export interface SpeakerOptionView {
  readonly speakerId: string;
  readonly displayName: string;
}
