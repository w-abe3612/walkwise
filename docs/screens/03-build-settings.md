---
spec_id: screens-03-build-settings
title: "出力・声設定画面"
status: approved
version: "1.2"
approved_at: "2026-07-19"
last_updated: "2026-07-22"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/09-voice-profile-schema.md
  - ../db/03-build-requests-table.md
  - ../db/06-voice-profiles-table.md
  - ../spec-proposals/build-settings-voice-profile-ui.md
---

# 出力・声設定画面

## 1. 目的

出力形式と、`02-project-workspace-and-source-import.md`で事前に作成・承認した
VoiceProfile(音声設定)を選択し、Build Request(制作依頼)を作成して本番Jobを
起動する画面。VoiceProfileの作成・編集・承認・archiveは本画面では行わない
(TASK-VOICE-PROFILE-UI-001、2026-07-22承認)。

## 2. route / window内navigation ID

`navigation_id: project-workspace/:project_id/build-settings`

## 3. 表示項目

- このProjectのapproved VoiceProfile一覧(選択肢)

## 4. 入力項目

| 項目 | 型 | 必須 |
|---|---|---|
| 出力形式 | チェックボックス(MP3、テキスト) | 1件以上必須。複数選択可 |
| 音声設定(VoiceProfile) | 選択式(このProjectのapproved VoiceProfileのみ) | MP3を選択した場合のみ必須。テキストのみの場合はdisabled(非表示にはしない) |

旧来のVOICEVOX speaker/style直接選択、speed等のparameterスライダーは本画面から
削除した(VoiceProfile作成・編集modal側[`02-project-workspace-and-source-import.md`]
でのみ扱う)。

## 5. 操作

- Build Requestを作成し、本番Jobを起動する(「制作開始」)

試聴機能(`voice:preview`)は、旧来のspeaker直接選択UIに紐づいていたため本画面からは
削除した。IPC自体(`voice:preview`)は変更していない。

## 6. Electron mainへ要求するIPC

- `voice-profile:list`(このProjectのVoiceProfile一覧を取得し、`approved`のみを
  選択肢とする。`voice:list-engines`は使用しない)
- `build-request:create`(`output_formats_json`と、MP3選択時のみ実際の
  `voice_profiles.voice_profile_id`を`voice_profile_id`として渡す。
  `docs/db/03-build-requests-table.md`と一致させる)
- `job:start`

## 7. 状態

| 状態 | 表示 |
|---|---|
| empty | 該当なし(常に出力形式・音声設定選択フォームを表示) |
| loading | VoiceProfile一覧取得中(既存の全画面共通skeletonに従う) |
| success | このProjectのapproved VoiceProfile一覧を選択肢として表示 |
| error | 選択中VoiceProfileが無効化された場合、「選択していた音声設定は現在利用できません。別の音声設定を選択してください。」を表示し選択を解除する |
| disabled | テキストのみ選択時、音声設定欄をdisabledのグレー表示にする(「音声を出力しないため使用しません」を併記) |

approved VoiceProfileが0件の場合、「利用可能な音声設定がありません。Project画面で
音声設定を追加し、「利用可能にする」を実行してください。」を表示する
(本画面から新規作成modalは開かない。Project Workspaceへの既存navigationを利用する)。

EPUB、COEIROINK、M4Bは、`19-application-scope-and-mvp.md`のMVP対象外方針
(MVP対象外機能を画面に表示しない)に従い、本画面へ選択肢として一切表示しない。
disabledの選択肢として大量に列挙する表示は行わない。

## 8. validation

- 出力形式が1件以上選択されるまで「制作開始」ボタンをdisabledにする。
- 出力形式に`mp3`が含まれる場合、approved VoiceProfileが選択されるまで
  「制作開始」ボタンをdisabledにする。
- 出力形式が`text`のみの場合、VoiceProfile未選択でも「制作開始」を実行できる
  (`voiceProfileId`は送らない)。
- 選択欄にはdraft/archivedのVoiceProfileを一切表示しない(approvedのみ)。
- 承認ゲート未充足の場合、「制作開始」実行時にIPCエラー
  (`approval_gate_not_satisfied`)を受け、画面はエラーメッセージと承認画面への
  導線を表示する。
- backendの安定したerror code(`voice_profile_required`/`voice_profile_not_approved`/
  `voice_profile_archived`/`voice_profile_project_mismatch`/`voice_profile_not_found`)は、
  利用者向け日本語messageへ変換して表示する(`02`と共有する変換表)。

## 9. キーボード操作

音声設定一覧はキーボードで選択できる。

## 10. 破壊操作の確認

「制作開始」は既存Artifactを上書きしない新規Jobとして実行されるため、
確認ステップは必須にしないが、承認ゲート未充足時のエラー表示によって
誤起動を防止する。

## 11. 関連DB table

- `docs/db/03-build-requests-table.md`
- `docs/db/06-voice-profiles-table.md`

## 12. 関連する承認済み仕様

- `docs/specifications/09-voice-profile-schema.md`
- `docs/specifications/22-job-lifecycle-and-recovery.md`
- `docs/spec-proposals/build-settings-voice-profile-ui.md`(2026-07-22承認)

## 13. MVP対象外

- EPUB、COEIROINK、M4Bの選択肢(disabled表示すら行わず、画面に表示しない)
- 出力プロファイルの保存・複製
- 章・segment単位の声の上書き(Project既定のみ)
- 本画面からのVoiceProfile新規作成・編集・承認・archive(`02`でのみ行う)
- 試聴機能(旧speaker直接選択UIとともに削除。IPC自体は維持)
