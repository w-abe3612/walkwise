---
spec_id: screens-02-project-workspace-and-source-import
title: "Projectワークスペース・素材登録画面"
status: approved
version: "1.1"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/07-approval-workflow.md
  - ../specifications/image-material-ingestion.md
  - ../specifications/pdf-direct-text-extraction.md
  - ../specifications/ocr-and-scanned-pdf.md
  - ../db/02-sources-table.md
---

# Projectワークスペース・素材登録画面

## 1. 目的

単一Projectの詳細確認、Source(素材)登録、4段階承認の確認を行う中心画面。

## 2. route / window内navigation ID

`navigation_id: project-workspace/:project_id`

## 3. 表示項目

- Project基本情報(title、domain、planning_stage)
- Source一覧(種類、状態)
- 承認状態バッジ(資料・カリキュラム/企画/検証済み原稿/試聴音声)

## 4. 入力項目

- 登録するSourceファイル(text/pdf/image、`19-application-scope-and-mvp.md` 5.3節のMVP範囲)

## 5. 操作

- Sourceをファイル選択で登録する(text/pdf/image)
- PDF直接抽出・OCR Jobを開始する(登録時に自動的にキューへ投入する)
- 承認一覧を確認する、承認/差し戻しを実行する
- `03-build-settings.md`へ遷移する

## 6. Electron mainへ要求するIPC

- `source:register`
- `approval:list`
- `approval:approve`
- `approval:request-changes`

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

## 8. validation

登録ファイルの`media_type`がMVP対象(text/pdf/image)であることを、
選択時にElectron main側で検証する。対象外の形式は登録前にエラー表示する。

## 9. キーボード操作

Source一覧・承認一覧はキーボードで上下移動・選択できる。

## 10. 破壊操作の確認

- 差し戻し操作は、理由入力(必須)を伴う確認ステップを経てから確定する。
- Source削除機能はMVPでは提供しない(誤削除リスクを避けるため)。

## 11. 関連DB table

- `docs/db/02-sources-table.md`
- `docs/db/01-projects-table.md`

## 12. 関連する承認済み仕様

- `docs/specifications/07-approval-workflow.md`
- `docs/specifications/image-material-ingestion.md`
- `docs/specifications/19-application-scope-and-mvp.md`

## 13. MVP対象外

- Kindle操作・Kindleキャプチャの起動導線(製品の恒久的対象外。`19-application-scope-and-mvp.md`参照)
- 動画・録音音声の登録導線(製品の恒久的対象外)
- EPUB入力(post-MVP。本画面の入力形式選択には表示しない)
- 原稿の詳細編集(確認・承認のみ)
- 一括承認

外部で用意されたPNG/JPEG/TIFF等の画像ファイルは、取得元をKindle固有方式として
識別せず、一般的な画像素材(`acquisition_method: existing_image_file`)として
登録できる。
