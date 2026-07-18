---
task_id: SPEC-APP-008
task_type: specification_drafting
status: ready
order: 28
title: "Project・制作依頼・Jobの状態遷移"
depends_on:
  - SPEC-APP-002
  - SPEC-APP-007
output: "docs/spec-proposals/generated-specifications/app-management/07-project-task-job-workflow.md"
---

# Project・制作依頼・Jobの状態遷移

## 1. 目的

利用者が作成する制作依頼と、内部処理Jobのstate machine、依存、再実行、承認gateを草案化する。

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

1. Project状態、Build Request状態、Job状態をどう分けるか。
2. 一つの制作依頼に何Jobあるか。
3. 失敗後にどこから再開するか。
4. 設定変更で何を無効化するか。
5. 承認待ちJobをどう表すか。
6. cancelとrollbackの意味は何か。

## 3. 初期推奨回答

- Projectは長寿命、Build Requestは一回の出力意図、Jobは実行履歴として分離する。
- Jobはqueued/running/succeeded/failed/cancel_requested/cancelled/blocked候補。
- 変更されたsegmentまたはsource以降だけをinvalidateする。
- 承認gateを迂回しない。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 各state machine
- transition表
- 再試行・再開
- 依存DAG
- 無効化規則
- cancelの保証範囲
- UI表示文言
- 異常例

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
