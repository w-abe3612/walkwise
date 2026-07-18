---
task_id: SPEC-APP-019
task_type: specification_drafting
status: ready
order: 39
title: "夜間成果の統合報告と次の作業順"
depends_on:
  - SPEC-APP-018
output: "docs/spec-proposals/generated-specifications/app-management/APP_MANAGEMENT_REVIEW_CHECKLIST.md"
---

# 夜間成果の統合報告と次の作業順

## 1. 目的

全成果を検査し、翌朝に利用者が短時間で判断できる報告、decision matrix、review checklistを作る。

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

1. どの案が推奨されたか。
2. 何が未確定か。
3. どの順番でレビューすればよいか。
4. すぐ実装してはいけない箇所は何か。
5. 最初の実装タスク候補は何か。

## 3. 初期推奨回答

- 10分で読めるexecutive summaryを作る。
- 推奨案と代替案の差を表にする。
- 実装タスクは候補一覧だけ作り、実装しない。
- git diff確認手順を報告する。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- `APP_MANAGEMENT_DECISION_MATRIX.md`
- `APP_MANAGEMENT_REVIEW_CHECKLIST.md`
- `docs/tasks/app-management-overnight-report.md`
- 生成物一覧
- 構文検査
- 変更禁止範囲のdiff
- 翌朝レビュー順
- 実装タスク候補

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
