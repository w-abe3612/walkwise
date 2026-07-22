/**
 * electron/renderer/screens/BuildSettings.types.ts — BuildSettings.vueの型定義。
 *
 * `.vue`ファイルはplain tscからnamed exportを認識されないため
 * (詳細は`ProjectWorkspace.types.ts`と同じ理由)、型のみ独立ファイルへ切り出す。
 *
 * TASK-VOICE-PROFILE-UI-001: 旧来のVOICEVOX speaker/style直接選択(`EngineHealthView`/
 * `SpeakerOptionView`)は削除した。Build SettingsはこのProjectのapproved VoiceProfileを
 * 1件選択するだけになった(作成・編集・承認・archiveはProject Workspace側で行う)。
 */

export type OutputFormat = "mp3" | "text";

/** Build Settingsの選択肢用の最小view(approved以外もPropsとして受け取り、内部でfilterする)。 */
export interface VoiceProfileOptionView {
  readonly voiceProfileId: string;
  readonly name: string;
  readonly status: "draft" | "approved" | "archived";
}
