---
spec_id: screens-03-build-settings
title: "出力・声設定画面"
status: approved
version: "1.1"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/09-voice-profile-schema.md
  - ../db/03-build-requests-table.md
---

# 出力・声設定画面

## 1. 目的

出力形式とVOICEVOXの声・パラメータを選択し、Build Request(制作依頼)を
作成して本番Jobを起動する画面。

## 2. route / window内navigation ID

`navigation_id: project-workspace/:project_id/build-settings`

## 3. 表示項目

- VOICEVOX engine接続状態(health check結果)
- 選択可能なspeaker/style一覧

## 4. 入力項目

| 項目 | 型 | 必須 |
|---|---|---|
| 出力形式 | チェックボックス(MP3、テキスト) | 1件以上必須。複数選択可 |
| speaker/style | 選択式 | MP3を選択した場合のみ必須。テキストのみの場合は任意またはdisabled |
| speed等の音声parameter | スライダー(`09-voice-profile-schema.md`の`speed_scale`等の最小項目) | 任意(既定値あり)。MP3未選択時はdisabled |

## 5. 操作

- speaker/styleと音声parameterで試聴する(MP3選択時)
- Build Requestを作成し、本番Jobを起動する(「制作開始」)

## 6. Electron mainへ要求するIPC

- `voice:list-engines`
- `voice:preview`
- `build-request:create`(`output_formats_json`と、MP3選択時のみ`voice_profile_id`を渡す。`docs/db/03-build-requests-table.md`と一致させる)
- `job:start`

## 7. 状態

| 状態 | 表示 |
|---|---|
| empty | 該当なし(常に出力形式・音声選択フォームを表示) |
| loading | engine接続確認中のスピナー表示 |
| success | 選択可能なspeaker/style一覧を表示 |
| error | VOICEVOX未接続時、「VOICEVOX Engineに接続できません」を表示 |
| disabled | MP3未選択の間、speaker/style・音声parameterをdisabledにする |

EPUB、COEIROINK、M4Bは、`19-application-scope-and-mvp.md`のMVP対象外方針
(MVP対象外機能を画面に表示しない)に従い、本画面へ選択肢として一切表示しない。
disabledの選択肢として大量に列挙する表示は行わない。

## 8. validation

- 出力形式が1件以上選択されるまで「制作開始」ボタンをdisabledにする。
- 出力形式に`mp3`が含まれる場合、speaker/styleが選択されるまで「制作開始」ボタンを
  disabledにする。
- 出力形式が`text`のみの場合、speaker/style未選択でも「制作開始」を実行できる。
- 承認ゲート未充足の場合、「制作開始」実行時にIPCエラー
  (`approval_gate_not_satisfied`)を受け、画面はエラーメッセージと承認画面への
  導線を表示する。

## 9. キーボード操作

speaker一覧はキーボードで選択できる。スライダーは矢印キーで調整できる。

## 10. 破壊操作の確認

「制作開始」は既存Artifactを上書きしない新規Jobとして実行されるため、
確認ステップは必須にしないが、承認ゲート未充足時のエラー表示によって
誤起動を防止する。

## 11. 関連DB table

- `docs/db/03-build-requests-table.md`

## 12. 関連する承認済み仕様

- `docs/specifications/09-voice-profile-schema.md`
- `docs/specifications/22-job-lifecycle-and-recovery.md`

## 13. MVP対象外

- EPUB、COEIROINK、M4Bの選択肢(disabled表示すら行わず、画面に表示しない)
- 出力プロファイルの保存・複製
- 章・segment単位の声の上書き(Project既定のみ)
