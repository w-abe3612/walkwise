---
task_id: SPEC-APP-018
task_type: specification_drafting
status: ready
order: 38
title: "草案のレビュー・仕様昇格手順"
depends_on:
  - SPEC-APP-017
output: "docs/spec-proposals/generated-specifications/app-management/17-specification-promotion-plan.md"
---

# 草案のレビュー・仕様昇格手順

## 1. 目的

今回の草案をどのように検証・レビューし、承認済み仕様へ昇格し、その後に実装タスクへ変換するかを具体化する。

## 共通安全規則

- 本タスクは**仕様草案の作成**であり、実装ではない。
- `script/`、`tests/`、依存パッケージ、`Dockerfile`、`docker-compose.yml`を変更しない。
- パッケージをインストールしない。
- Webサーバー、DB、VOICEVOX、COEIROINK、ブラウザを起動しない。
- `docs/specifications/`の承認済み仕様を正本として扱う。
- 草案は`docs/spec-proposals/generated-specifications/app-management/`へ出力する。
- 草案の`status`は`review`、`provisional`、`blocked`のいずれかとし、`approved`にしない。
- 人間の承認なしに`docs/specifications/`へ移動しない。
- 既存ファイルを削除しない。
- 根拠不足は推測で確定せず、`evidence_gap`または`human_review_required`として残す。
- 技術選定は少なくとも3案を比較し、採用案・不採用案・判断条件を記録する。
- 既存のファイル正本を無断でDB正本へ変更しない。
- 著作権、録音許可、個人情報の法的判断を代行しない。
- 外部情報を調査する場合は公式ドキュメントを優先し、参照日を記録する。
- Markdown、YAML、JSON、Mermaidの構文を可能な範囲で検査する。

## 2. 調査・決定する質問

1. 一括昇格か分割昇格か。
2. どの草案を先に承認するか。
3. 技術選定にPoCが必要か。
4. DB schemaを承認する前に何を検証するか。
5. 昇格時にどのINDEX/READMEを更新するか。
6. 草案をいつ削除・archiveするか。

## 3. 初期推奨回答

- 分割昇格を推奨する。
- 順序候補は製品範囲→用語→architecture→persistence→DB→workflow→UI/API→個別flow→security/test。
- 技術stackとJob方式は小規模PoC結果を承認条件候補にする。
- approved後だけ`TASK-APP-*`実装タスクを作る。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- status transition
- 昇格順序
- 各仕様の承認条件
- PoC計画
- 人間review checklist
- 差分・リンク検査
- README/INDEX更新
- 旧草案archive
- 実装タスク生成規則
- rollback

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
