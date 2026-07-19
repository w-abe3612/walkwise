---
spec_id: screens-01-project-list-and-create
title: "Project一覧・新規作成画面"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/03-project-plan-schema.md
  - ../db/01-projects-table.md
---

# Project一覧・新規作成画面

## 1. 目的

Project(作品)の一覧表示と新規作成を行う、アプリ起動後の最初の画面。

## 2. route / window内navigation ID

`navigation_id: projects-list`(既定表示)。新規作成は同画面内のモーダルまたは
インライン展開とし、別routeへは遷移しない。

## 3. 表示項目

- Project一覧: 名前、`planning_stage`、最終更新日時
- 一覧が0件の場合の案内(6節参照)

## 4. 入力項目(新規作成)

| 項目 | 型 | 必須 |
|---|---|---|
| `title` | 文字列 | 必須 |
| `domain` | 文字列(自由入力) | 必須 |
| `purpose` | 複数行文字列 | 必須 |
| `usage_purpose` | 選択式(既定値`personal_learning`) | 必須 |
| `target_audience.description` | 文字列 | 必須 |
| `source_strategy` | 複数選択 | 1件以上必須 |

## 5. 操作

- 新規Project作成
- 既存Projectを開く(`02-project-workspace-and-source-import.md`へ遷移)

## 6. Electron mainへ要求するIPC

- `project:list`
- `project:create`

## 7. 状態

| 状態 | 表示 |
|---|---|
| empty | 「最初のプロジェクトを作成」への導線を強調表示 |
| loading | 一覧取得中のskeleton表示 |
| success | 一覧表示 |
| error | 取得失敗時の要約メッセージ+再試行ボタン |
| disabled | 必須入力未完了時、新規作成の確定ボタンをdisabledにする |

## 8. validation

必須項目(4節)がすべて入力され、`source_strategy`が1件以上選択されるまで、
作成確定ボタンをdisabledにする。

## 9. キーボード操作

フォーム項目はTabで順次移動できる。作成確定ボタンはEnterで実行できる。

## 10. 破壊操作の確認

本画面に破壊操作はない(削除・archiveは`02`のProject詳細側で扱う)。

## 11. 関連DB table

`docs/db/01-projects-table.md`

## 12. 関連する承認済み仕様

- `docs/specifications/03-project-plan-schema.md`
- `docs/specifications/19-application-scope-and-mvp.md`

## 13. MVP対象外

- Project複製・archive操作(本画面では提供しない)
- 検索・フィルタ機能
