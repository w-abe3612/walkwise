---
spec_id: screens-04-job-progress
title: "Job進捗画面"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - ../specifications/22-job-lifecycle-and-recovery.md
  - ../specifications/21-electron-python-worker-interface.md
  - ../db/04-jobs-table.md
---

# Job進捗画面

## 1. 目的

実行中・完了・失敗したJobの一覧と進捗を表示し、cancel・再試行を行う画面。

## 2. route / window内navigation ID

`navigation_id: project-workspace/:project_id/jobs`

## 3. 表示項目

- Job一覧: 種類、状態、進捗(`progress_current`/`progress_total`)、開始時刻
- 選択したJobの詳細: 直近メッセージ(`last_message`)、技術ログ(折りたたみ)

## 4. 入力項目

なし(操作のみ)。

## 5. 操作

- 実行中Jobのcancel
- 失敗Jobの再試行

## 6. Electron mainへ要求するIPC

- `job:get`
- `job:subscribe-progress`
- `job:cancel`
- `job:start`(再試行時、`parent_job_id`を伴う新規Job作成として)

## 7. 状態

| 状態 | 表示 |
|---|---|
| empty | Jobが1件もない場合、「まだ実行されたJobはありません」を表示 |
| loading | Job一覧取得中のskeleton表示 |
| success | Job一覧・進捗を表示 |
| error | Job詳細取得失敗時の要約メッセージ |
| disabled | 完了・失敗済みJobのcancelボタンはdisabledにする |

stale job検出(`22-job-lifecycle-and-recovery.md` 5.6節)によって`failed`へ
変更されたJobには、「前回異常終了しました」の注記を表示する。

## 8. validation

cancel操作は`running`または`queued`状態のJobにのみ許可する。再試行操作は
`failed`または`cancelled`状態のJobにのみ許可する。

## 9. キーボード操作

Job一覧はキーボードで上下移動・選択できる。

## 10. 破壊操作の確認

cancel操作は、実行中処理を中断する操作であるため、確認モーダルを表示してから
実行する。

## 11. 関連DB table

`docs/db/04-jobs-table.md`

## 12. 関連する承認済み仕様

- `docs/specifications/22-job-lifecycle-and-recovery.md`
- `docs/specifications/21-electron-python-worker-interface.md`

## 13. MVP対象外

- 並列Job実行の表示(同時実行数1のため、常に0または1件の`running`のみ)
- OS通知連携
