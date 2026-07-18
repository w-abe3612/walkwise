---
task_id: SPEC-APP-004
task_type: specification_drafting
status: ready
order: 24
title: "フロント画面・情報設計・操作導線"
depends_on:
  - SPEC-APP-002
  - SPEC-APP-003
output: "docs/spec-proposals/generated-specifications/app-management/03-frontend-information-architecture.md"
---

# フロント画面・情報設計・操作導線

## 1. 目的

管理画面のページ構成、navigation、フォーム、一覧、詳細、確認画面を草案化する。

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

1. 必要な画面は何か。
2. 新規作成をwizardにするか。
3. Project一覧とJob一覧をどう分けるか。
4. 素材・原稿・承認・出力をどこで確認するか。
5. 危険操作の確認方法は何か。
6. アクセシビリティとキーボード操作はどうするか。

## 3. 初期推奨回答

- 最低限、Dashboard、Project作成、Project詳細、素材、出力設定、声、Job、成果物、設定・診断を提案する。
- 新規作成は保存可能な段階式wizardを候補にする。
- 処理中でも画面reloadで状態が復元できる設計にする。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 画面一覧
- navigation map
- 主要wireframeを文章またはMermaidで表現
- フォーム項目
- empty/loading/error/disabled状態
- 破壊操作
- スマホ対応の要否
- MVP画面と後続画面

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
