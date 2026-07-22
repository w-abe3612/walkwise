/**
 * electron/renderer/voiceProfileErrors.ts — 公開契約: mapVoiceProfileErrorMessage(error).
 *
 * TASK-VOICE-PROFILE-UI-001 17節: backendの安定したerror code(WorkerManagerが
 * `worker_request_failed: <message>`の形でErrorへ載せる。`electron/main/worker_manager.ts`
 * 参照)を、利用者向けの日本語messageへ変換する。ProjectWorkspace.vue/BuildSettings.vueの
 * 両方から共有し、同じmappingを重複実装しない。
 */

const ERROR_MESSAGES: readonly (readonly [string, string])[] = [
  ["voice_profile_required", "MP3を作成するには音声設定を選択してください。"],
  ["voice_profile_not_approved", "この音声設定はまだ利用可能になっていません。"],
  ["voice_profile_archived", "この音声設定はアーカイブ済みです。"],
  ["voice_profile_project_mismatch", "別のプロジェクトの音声設定は使用できません。"],
  ["voice_profile_not_found", "音声設定が見つかりません。"],
  // backendの実際の重複エラーcodeは`conflict`(script/persistence/repositories.py::map_integrity_error)。
  // `voice_profile_name_conflict`という別名でも一致するようにしておく。
  ["voice_profile_name_conflict", "同じ名前の音声設定が既にあります。"],
  ["conflict", "同じ名前の音声設定が既にあります。"],
  ["voice_profile_invalid", "入力内容を確認してください。"],
  ["approval_gate_not_satisfied", "承認が完了していません。承認画面を確認してください。"],
];

const FALLBACK_MESSAGE = "操作に失敗しました。もう一度お試しください。";

/** backendのerror messageから既知のcodeを探し、利用者向け日本語messageへ変換する。 */
export function mapVoiceProfileErrorMessage(error: unknown): string {
  const raw = error instanceof Error ? error.message : String(error ?? "");
  for (const [code, message] of ERROR_MESSAGES) {
    if (raw.includes(code)) {
      return message;
    }
  }
  return FALLBACK_MESSAGE;
}
