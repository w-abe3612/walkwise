---
task_id: SPEC-APP-005
task_type: specification_drafting
status: ready
order: 25
title: "バックエンドAPIとapplication service境界"
depends_on:
  - SPEC-APP-003
  - SPEC-APP-004
output: "docs/spec-proposals/generated-specifications/app-management/04-backend-api-and-service-boundary.md"
---

# バックエンドAPIとapplication service境界

## 1. 目的

フロントから既存Python処理を安全に呼び出すAPI、application service、domain service、adapter境界を定義する。

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

1. REST、RPC、WebSocket/SSEの使い分けは何か。
2. 長時間Jobの開始・監視・cancelはどうするか。
3. ファイル選択とpathをどう受け渡すか。
4. CLIとAPIが同じserviceを使えるか。
5. error codeと利用者向けmessageをどう分けるか。

## 3. 初期推奨回答

- CRUDはHTTP API、進捗はSSEまたはpollingを比較する。
- UIからshell command文字列を直接実行しない。
- 既存CLIの内部ロジックをserviceへ抽出し、CLIとAPIをadapter化する将来案にする。
- idempotency keyとjob IDを検討する。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- API一覧
- request/response例
- error schema
- service層責務
- CLI互換方針
- Job開始sequence
- cancel/retry契約
- path安全性

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
