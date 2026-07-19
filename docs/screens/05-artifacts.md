---
spec_id: screens-05-artifacts
title: "成果物画面"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - ../specifications/14-audio-packaging.md
  - ../db/05-artifacts-table.md
---

# 成果物画面

## 1. 目的

生成されたArtifact(MP3、テキスト)の一覧を表示し、フォルダを開く操作を提供する画面。

## 2. route / window内navigation ID

`navigation_id: project-workspace/:project_id/artifacts`

## 3. 表示項目

- Artifact一覧: 種類、version、生成日時、生成元Job

## 4. 入力項目

なし。

## 5. 操作

- フォルダを開く(OSのファイルエクスプローラで成果物の保存先を開く)
- 再生成(`03-build-settings.md`へ遷移し、新しいBuild Requestを作成する)

## 6. Electron mainへ要求するIPC

- `artifact:list`
- `artifact:open-folder`

## 7. 状態

| 状態 | 表示 |
|---|---|
| empty | Artifactが1件もない場合、「まだ成果物はありません」を表示 |
| loading | 一覧取得中のskeleton表示 |
| success | Artifact一覧を表示(同一`artifact_type`は最新versionを既定表示) |
| error | 一覧取得失敗時の要約メッセージ |
| disabled | 該当なし |

## 8. validation

該当なし(本画面は表示・フォルダを開く操作のみ)。

## 9. キーボード操作

Artifact一覧はキーボードで上下移動・選択できる。

## 10. 破壊操作の確認

本画面はArtifactの削除機能を提供しない(既存versionを上書きしない方針、
`docs/db/05-artifacts-table.md`)。破壊操作に該当する操作はない。

## 11. 関連DB table

`docs/db/05-artifacts-table.md`

## 12. 関連する承認済み仕様

`docs/specifications/14-audio-packaging.md`

## 13. MVP対象外

- 過去versionとの詳細な差分比較表示
- Artifactの直接削除
