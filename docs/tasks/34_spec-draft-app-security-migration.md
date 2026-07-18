---
task_id: SPEC-APP-014
task_type: specification_drafting
status: ready
order: 34
title: "セキュリティ・権利・バックアップ・移行"
depends_on:
  - SPEC-APP-006
  - SPEC-APP-007
  - SPEC-APP-009
  - SPEC-APP-014
output: "docs/spec-proposals/generated-specifications/app-management/13-security-backup-migration.md"
---

# セキュリティ・権利・バックアップ・移行

## 1. 目的

ローカル管理画面とDB導入で増えるpath操作、file upload、個人情報、backup、schema migration、既存data移行の危険を整理する。

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

1. loopback外から接続可能にするか。
2. 任意path・path traversalをどう防ぐか。
3. secret/API keyをどこに置くか。
4. DBとファイルをどう整合backupするか。
5. 既存data/libraryをどうimportするか。
6. rollbackとrepairはどうするか。

## 3. 初期推奨回答

- 初期は127.0.0.1限定、認証なしは単一利用者ローカル条件付きとする。
- allowed root外への書込みを禁止する。
- secretをDB平文へ保存しない。
- DB＋files＋manifestを同一backup generationとして扱う。
- dry-run migrationと検証reportを必須にする。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- threat model
- path policy
- secret management
- backup/restore
- DB migration
- legacy import
- rollback
- privacy/rights
- 故障注入ケース

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
