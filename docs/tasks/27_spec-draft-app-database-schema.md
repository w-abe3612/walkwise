---
task_id: SPEC-APP-007
task_type: specification_drafting
status: ready
order: 27
title: "DB論理スキーマ・制約・履歴"
depends_on:
  - SPEC-APP-006
output: "docs/spec-proposals/generated-specifications/app-management/06-database-logical-schema.md"
---

# DB論理スキーマ・制約・履歴

## 1. 目的

選択候補の永続化方式を前提に、正規化しすぎず追跡性を保つ論理ERDと制約を作る。

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

1. 必要entityは何か。
2. Project、Source、Build Request、Job、Artifact、Voice Profile、Approvalをどう関連付けるか。
3. 履歴と現在値をどう扱うか。
4. soft delete、archive、version、optimistic lockは必要か。
5. 巨大本文をDBへ入れるか。

## 3. 初期推奨回答

- Project、Source、SourceRevision、BuildRequest、Job、JobEvent、Artifact、OutputProfile、VoiceProfileRef、ApprovalRecord、AppSettingを候補にする。
- 本文や音声本体はfile path＋hashを基本候補にする。
- 状態値は列挙とtransitionで制約する。
- 削除よりarchiveを初期既定とする。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- Mermaid ERD
- entity一覧
- PK/FK/unique/check/index
- 削除規則
- version規則
- path/hash列
- 監査列
- migration seed方針
- 最小DDLではなく論理schema

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
