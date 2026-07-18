---
task_id: SPEC-APP-006
task_type: specification_drafting
status: ready
order: 26
title: "ファイルとDBの永続化責務"
depends_on:
  - SPEC-APP-001
  - SPEC-APP-003
  - SPEC-APP-005
output: "docs/spec-proposals/generated-specifications/app-management/05-persistence-strategy.md"
---

# ファイルとDBの永続化責務

## 1. 目的

既存ファイル正本と新DBの境界を比較し、DBへ保存するもの、ファイルへ残すもの、同期・再構築方法を草案化する。

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

1. DBの目的は何か。
2. メタデータ正本をDBへ移すか。
3. 原素材・テキスト・音声・manifestをどこに置くか。
4. SQLiteとPostgreSQLの判断基準は何か。
5. DBを消失した際に再構築できるか。
6. atomic writeとtransactionをどう連携するか。

## 3. 初期推奨回答

- 単一利用者MVPはSQLiteを第一候補にする。
- 大型binaryとimmutable原素材はファイルに置く。
- DBにはProject、Source metadata、Build Request、Job、Artifact index、approval、settingsを候補にする。
- 既存YAML/JSONとの二重正本を避ける。
- import/export可能なportable manifestを残す。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 3永続化案の比較
- 正本マトリクス
- DB transactionとfile atomic writeの整合方式
- 再構築・repair方針
- backup単位
- 同時実行
- DB migration方針
- 採用前提

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
