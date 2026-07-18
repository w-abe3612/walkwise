---
task_id: SPEC-APP-017
task_type: specification_drafting
status: ready
order: 37
title: "フロント・DB管理の統合仕様草案"
depends_on:
  - SPEC-APP-002
  - SPEC-APP-003
  - SPEC-APP-004
  - SPEC-APP-005
  - SPEC-APP-006
  - SPEC-APP-007
  - SPEC-APP-008
  - SPEC-APP-009
  - SPEC-APP-010
  - SPEC-APP-011
  - SPEC-APP-012
  - SPEC-APP-013
  - SPEC-APP-014
  - SPEC-APP-015
  - SPEC-APP-016
output: "docs/spec-proposals/generated-specifications/app-management/16-integrated-application-proposal.md"
---

# フロント・DB管理の統合仕様草案

## 1. 目的

個別草案の矛盾を解消し、MVPとして一貫した管理アプリの統合草案を作る。

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

1. 推奨stackと永続化案は一貫しているか。
2. 画面、API、DB、Job状態が対応するか。
3. 既存仕様の承認gateと正本を壊していないか。
4. MVPで一冊を完成できるか。
5. 未決定事項をどの順で解消するか。

## 3. 初期推奨回答

- 統合草案は一つの推奨案を示すが、重要な代替案を残す。
- MVP sequenceを新規作成から成果物確認まで通す。
- 未確定機能はfeature flagまたはdisabled capabilityとして扱う案を示す。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 全体構成図
- MVP screen/API/entity対応表
- end-to-end sequence
- 正本一覧
- feature capability
- 非機能要件
- 未決定事項
- 人間判断順序
- 実装分割案

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
