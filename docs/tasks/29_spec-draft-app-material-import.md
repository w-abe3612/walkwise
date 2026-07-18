---
task_id: SPEC-APP-009
task_type: specification_drafting
status: ready
order: 29
title: "素材インポート画面と処理草案"
depends_on:
  - SPEC-APP-004
  - SPEC-APP-005
  - SPEC-APP-006
  - SPEC-APP-008
output: "docs/spec-proposals/generated-specifications/app-management/08-material-import-workflow.md"
---

# 素材インポート画面と処理草案

## 1. 目的

PDF、EPUB、画像、Kindle capture、既存text等の素材を画面から登録し、権利・品質・順序を確認する導線を草案化する。

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

1. drag and drop、file picker、directory importをどう扱うか。
2. 複数ファイルの順序をどう確認するか。
3. 種類を自動判定するか。
4. 権利・利用目的をいつ確認するか。
5. importをcopyするか参照するか。
6. 重複・破損・容量超過時はどうするか。

## 3. 初期推奨回答

- import前previewと確認を入れる。
- 原素材はimmutable copyを基本候補にし、参照モードは明示的advanced optionにする。
- 種類判定結果を利用者が修正できる。
- 権利・privacy statusを必須metadataとして扱う。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 対応素材表
- 画面導線
- import request例
- 順序編集
- duplicate/unsupported/corrupt異常系
- copy/reference比較
- rights review
- import Job分割

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
