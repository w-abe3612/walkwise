---
spec_id: screens-02-project-workspace-and-source-import
title: "Projectワークスペース・素材登録画面"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/07-approval-workflow.md
  - ../specifications/image-material-ingestion.md
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

- Sourceをファイル選択で登録する
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

Sourceの`status`が`registered`(処理待ち)の間、種類ごとに「処理待ち」表示を行う
(PDF・画像の抽出処理が未実装の場合、`19`5.3節の方針どおり)。

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

- Kindle画面キャプチャの起動導線(本体には含めない。`docs/spec-proposals/kindle-capture-separate-tool.md`参照)
- 原稿の詳細編集(確認・承認のみ)
- 一括承認
