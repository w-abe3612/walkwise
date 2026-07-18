---
task_id: SPEC-APP-002
task_type: specification_drafting
status: ready
order: 22
title: "製品範囲・利用者導線・MVP"
depends_on:
  - SPEC-APP-001
output: "docs/spec-proposals/generated-specifications/app-management/01-product-scope-and-mvp.md"
---

# 製品範囲・利用者導線・MVP

## 1. 目的

ローカル管理アプリとしての目的、利用者、MVP、対象外を定め、利用者が一冊を完成させる導線を草案化する。

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

1. 誰が使う単一利用者アプリか。
2. 一冊作る最短導線は何か。
3. 新規作成時に必要な最小情報は何か。
4. 途中保存・再開・複製・削除・archiveは必要か。
5. どこまでをMVPに含めるか。

## 3. 初期推奨回答

- 初期は単一PC・単一利用者のローカルアプリとして比較する。
- MVPは新規プロジェクト、素材import、出力・声選択、実行、進捗、成果物確認までとする。
- 高度な編集、複数利用者、クラウド同期は後続候補にする。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- ペルソナ
- 主要ユースケース
- MVP/次期/対象外の表
- 正常導線
- 失敗・中断導線
- 画面から実行しない高リスク操作

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
