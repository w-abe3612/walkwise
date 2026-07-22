---
spec_id: screens-02-project-workspace-and-source-import
title: "Projectワークスペース・素材登録画面"
status: approved
version: "1.2"
approved_at: "2026-07-19"
last_updated: "2026-07-22"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/07-approval-workflow.md
  - ../specifications/image-material-ingestion.md
  - ../specifications/pdf-direct-text-extraction.md
  - ../specifications/ocr-and-scanned-pdf.md
  - ../db/02-sources-table.md
  - ../db/06-voice-profiles-table.md
  - ../spec-proposals/build-settings-voice-profile-ui.md
---

# Projectワークスペース・素材登録画面

## 1. 目的

単一Projectの詳細確認、Source(素材)登録、4段階承認の確認、および
VoiceProfile(音声設定)の作成・編集・承認・archiveを行う中心画面
(TASK-VOICE-PROFILE-UI-001、2026-07-22承認)。VoiceProfile自体のCRUDは
本画面でのみ行い、Build Settings画面ではapproved状態のVoiceProfileを
選択するだけにする(第6画面は追加しない)。

## 2. route / window内navigation ID

`navigation_id: project-workspace/:project_id`

## 3. 表示項目

- Project基本情報(title、domain、planning_stage)
- Source一覧(種類、状態)
- 承認状態バッジ(資料・カリキュラム/企画/検証済み原稿/試聴音声)
- 「音声設定」section(折り畳み可能、第6画面ではなく本画面内へ統合): VoiceProfile一覧
  (名前、engine、speaker/style表示名(取得できない場合のみID表示)、status(下書き/
  利用可能/アーカイブ済みの日本語表示)、更新日時)

## 4. 入力項目

- 登録するSourceファイル(text/pdf/image、`19-application-scope-and-mvp.md` 5.3節のMVP範囲)
- VoiceProfile作成・編集フォーム(modal): name(必須)、speaker(必須、`voice:list-engines`の
  候補から選択)、style(任意)、speed/pitch/intonation/volume(任意、既定値あり)、
  sentence/paragraph/section/chapter pause(任意、既定値あり)、settings_json(任意、JSON object)。
  engineはMVPでは`voicevox`固定でUI操作対象にしない。

## 5. 操作

- Sourceをファイル選択で登録する(text/pdf/image)
- PDF直接抽出・OCR Jobを開始する(登録時に自動的にキューへ投入する)
- 承認一覧を確認する、承認/差し戻しを実行する
- `03-build-settings.md`へ遷移する
- VoiceProfileを新規作成する(modal、常に`draft`として作成される)
- VoiceProfileを編集する(archived以外。承認済み(`approved`)を編集しても、
  editがstatusを変更しない限りapprovedのまま維持される)
- VoiceProfileを「利用可能にする」(draft→approved)
- VoiceProfileをarchiveする(確認を経てから実行、物理削除ではない。
  archived後の再編集・復元・archived解除は提供しない)

## 6. Electron mainへ要求するIPC

- `source:register`
- `approval:list`
- `approval:approve`
- `approval:request-changes`
- `voice-profile:create` / `voice-profile:list` / `voice-profile:get` /
  `voice-profile:update` / `voice-profile:archive`
- `voice:list-engines`(VoiceProfile作成・編集modal内のspeaker/style候補取得専用。
  Project単位のVoiceProfile一覧`voice-profile:list`とは別concept、混同しないこと)

## 7. 状態

| 状態 | 表示 |
|---|---|
| empty | Sourceが0件の場合、「素材を登録」への導線を表示 |
| loading | Source一覧・承認状態取得中のskeleton表示 |
| success | Source一覧・承認状態を表示 |
| error | 登録失敗時の要約メッセージ(利用者向け)+技術detail折りたたみ |
| disabled | 承認ゲート未充足の間、次段階(Build設定)への遷移ボタンは有効のままとするが、Job起動自体は`22-job-lifecycle-and-recovery.md`のゲート判定でIPCエラーとなる |

Sourceの`status`に応じて次を表示する(`docs/db/02-sources-table.md`と一致させる)。

| `status` | 表示 |
|---|---|
| `registered` | 「登録済み・処理待ち」 |
| `processing` | 「抽出・OCR処理中」 |
| `ready` | 「準備完了」 |
| `review_required` | 「要確認(低信頼・高リスク要素あり)」、確認画面への導線を表示 |
| `failed` | 「抽出に失敗しました」、再試行導線を表示 |

`text`のSourceは抽出処理を必要としないため、登録直後に`ready`となる。
`pdf`/`image`のSourceは、PDF直接抽出(`pdf-direct-text-extraction.md`)または
OCR(`ocr-and-scanned-pdf.md`)のJobが自動的に開始される。

VoiceProfileの`status`に応じて次を日本語表示する(内部値をそのまま見せない、
`docs/db/06-voice-profiles-table.md`と一致させる)。

| `status` | 表示 |
|---|---|
| `draft` | 「下書き」 |
| `approved` | 「利用可能」 |
| `archived` | 「アーカイブ済み」 |

VoiceProfile一覧が0件、draftのみ、archivedのみの場合、それぞれ次を表示する。

| 状況 | 表示 |
|---|---|
| 0件 | 「音声設定がまだありません。MP3を作成するには、音声設定を追加して利用可能にしてください。」+「音声設定を追加」ボタン |
| draftのみ(approved/archivedが0件) | 「利用可能な音声設定がありません。下書きの音声設定を確認し、「利用可能にする」を実行してください。」 |
| archivedのみ(approved/draftが0件) | 「利用可能な音声設定がありません。新しい音声設定を追加してください。」(元に戻す導線は表示しない) |
| VoiceProfile取得失敗 | 「音声設定を読み込めませんでした。もう一度お試しください。」(内部error codeは表示しない) |

## 8. validation

- 登録ファイルの`media_type`がMVP対象(text/pdf/image)であることを、
  選択時にElectron main側で検証する。対象外の形式は登録前にエラー表示する。
- VoiceProfile作成・編集: nameとspeakerは必須。settings_jsonを入力する場合はJSON
  object形式であることを保存前に検証する(配列・非JSON文字列は拒否)。
- backendの安定したerror code(`voice_profile_required`/`voice_profile_not_approved`/
  `voice_profile_archived`/`voice_profile_project_mismatch`/`voice_profile_not_found`/
  name重複の`conflict`)は、利用者向け日本語messageへ変換して表示する
  (`electron/renderer/voiceProfileErrors.ts`、本画面とBuild Settings画面で共有)。

## 9. キーボード操作

Source一覧・承認一覧・VoiceProfile一覧はキーボードで上下移動・選択できる。
VoiceProfile作成・編集modalはEscapeキーで閉じることができ、Tabキーはmodal内で
focusをtrapする(modal外へは移動しない)。modalを開いた時、最初の入力欄(name)へ
自動的にfocusが移動する。

## 10. 破壊操作の確認

- 差し戻し操作は、理由入力(必須)を伴う確認ステップを経てから確定する。
- Source削除機能はMVPでは提供しない(誤削除リスクを避けるため)。
- VoiceProfileのarchive操作は、実行前に確認(「この音声設定をアーカイブしますか?
  アーカイブ後は新しい音声作成には使用できません。」)を表示してから確定する。
  物理削除ではなく、archive後もPastのBuild実行履歴(manifest snapshot)からは
  引き続き参照できる。

## 11. 関連DB table

- `docs/db/02-sources-table.md`
- `docs/db/01-projects-table.md`
- `docs/db/06-voice-profiles-table.md`

## 12. 関連する承認済み仕様

- `docs/specifications/07-approval-workflow.md`
- `docs/specifications/image-material-ingestion.md`
- `docs/specifications/19-application-scope-and-mvp.md`
- `docs/spec-proposals/build-settings-voice-profile-ui.md`(2026-07-22承認、
  VoiceProfile UI検討の記録)

## 13. MVP対象外

- Kindle操作・Kindleキャプチャの起動導線(製品の恒久的対象外。`19-application-scope-and-mvp.md`参照)
- 動画・録音音声の登録導線(製品の恒久的対象外)
- EPUB入力(post-MVP。本画面の入力形式選択には表示しない)
- 原稿の詳細編集(確認・承認のみ)
- 一括承認
- VoiceProfileの複製機能
- 章・segment単位のVoiceProfile上書き(Project既定の1件のみ)
- approved VoiceProfile編集後にdraftへ戻す操作、archived解除操作
- VoiceProfile使用履歴の画面表示(どのBuild/Artifactがどのsnapshotを使ったかは
  production manifestに記録されるが、本画面では表示しない)

外部で用意されたPNG/JPEG/TIFF等の画像ファイルは、取得元をKindle固有方式として
識別せず、一般的な画像素材(`acquisition_method: existing_image_file`)として
登録できる。
