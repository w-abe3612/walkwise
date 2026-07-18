---
task_id: SPEC-APP-010
task_type: specification_drafting
status: ready
order: 30
title: "原稿・出典・承認・編集画面"
depends_on:
  - SPEC-APP-004
  - SPEC-APP-008
output: "docs/spec-proposals/generated-specifications/app-management/09-review-and-approval-workflow.md"
---

# 原稿・出典・承認・編集画面

## 1. 目的

OCR結果、正規化text、主張と出典、原稿、音声を人間が確認・差し戻し・承認する管理画面の範囲を草案化する。

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

1. MVPで編集画面をどこまで作るか。
2. 4段階承認をどう表示するか。
3. diffとversion履歴は必要か。
4. 一括承認を許すか。
5. AI生成箇所と人間編集をどう追跡するか。

## 3. 初期推奨回答

- MVPでも承認待ち一覧と個別確認を含める候補にする。
- 未検証主張を本番TTSへ進めない。
- 一括承認は条件付きか後続とする。
- 編集前後、編集者、日時、理由を追跡する。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 画面一覧
- approval gate
- 編集・diff
- 差し戻しreason
- 権限は単一利用者でも監査列を持つ案
- 未承認出力の隔離
- 異常系

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
