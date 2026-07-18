---
task_id: SPEC-APP-001
task_type: specification_drafting
status: ready
order: 21
title: "現状監査と製品用語の整理"
depends_on:
  []
output: "docs/spec-proposals/generated-specifications/app-management/00-current-state-and-terminology.md"
---

# 現状監査と製品用語の整理

## 1. 目的

現在のコマンド、設定JSON、ファイル保存、生成物、仕様体系を読み取り、管理画面とDB設計に使う共通用語を確定候補として整理する。

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

1. 現在の主要CLIと処理段階は何か。
2. 正本・派生物・cache・deliverableはどこか。
3. 製品内の「タスク」と開発用タスクをどう区別するか。
4. Project、Build Request、Job、Source、Artifactの境界は何か。
5. 既存ID体系を再利用できるか。

## 3. 初期推奨回答

- 製品内では「プロジェクト」「制作依頼」「処理ジョブ」を分離する。
- 既存ファイルを無断でDBへ移さず、現在の正本を明記する。
- 日本語UIラベルと内部英語名の対応表を作る。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 現状構成図
- 用語集
- 現在と将来の正本一覧
- 既存CLIから画面操作への対応表
- 衝突する名称の一覧

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
