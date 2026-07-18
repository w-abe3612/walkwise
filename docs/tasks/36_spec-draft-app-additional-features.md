---
task_id: SPEC-APP-016
task_type: specification_drafting
status: ready
order: 36
title: "AIによる追加機能提案と優先順位"
depends_on:
  - SPEC-APP-002
  - SPEC-APP-004
  - SPEC-APP-008
  - SPEC-APP-009
  - SPEC-APP-010
  - SPEC-APP-011
  - SPEC-APP-012
  - SPEC-APP-013
  - SPEC-APP-014
  - SPEC-APP-015
output: "docs/spec-proposals/generated-specifications/app-management/15-additional-feature-proposals.md"
---

# AIによる追加機能提案と優先順位

## 1. 目的

利用者が列挙した機能以外に、実際のオーディオブック作成運用を安全・便利にする機能をAIが提案し、MVP、次期、将来へ分類する。

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

1. 不足している日常操作は何か。
2. 失敗対応・品質確認・コスト管理で何が必要か。
3. 素材・原稿・音声のpreviewに何が必要か。
4. 自動化しすぎると危険な操作は何か。
5. DBがあることで可能になる有用機能は何か。

## 3. 初期推奨回答

- 最低20案を出し、価値・実装量・危険・依存仕様で評価する。
- 候補例は複製、archive、差分再生成、承認待ち、素材順序編集、音声比較、出力履歴、容量診断、cost表示、検索、tag、template。
- 提案をすべてMVPへ入れない。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 20案以上
- MVP/次期/将来
- 価値・コスト・risk matrix
- 採用推奨Top5
- 不採用または保留理由
- 既存仕様との依存

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
