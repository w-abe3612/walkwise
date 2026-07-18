---
task_id: SPEC-APP-015
task_type: specification_drafting
status: ready
order: 35
title: "テスト戦略・受け入れ条件・運用診断"
depends_on:
  - SPEC-APP-003
  - SPEC-APP-004
  - SPEC-APP-005
  - SPEC-APP-006
  - SPEC-APP-008
output: "docs/spec-proposals/generated-specifications/app-management/14-testing-and-acceptance.md"
---

# テスト戦略・受け入れ条件・運用診断

## 1. 目的

フロント、API、DB、Job、filesystem、TTS連携をテスト先行で実装できる受け入れ条件へ落とす。

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

1. unit、integration、E2E、実機testをどう分けるか。
2. 外部TTSをmockするか。
3. DB migrationをどうtestするか。
4. 長時間Jobとcancelをどう再現するか。
5. Windowsの一コマンド起動をどう検証するか。

## 3. 初期推奨回答

- domain/serviceはunit、DB/filesystemはintegration、主要wizardはE2Eにする。
- VOICEVOX等はcontract testと実サービスsmokeを分離する。
- 一時directoryと一時SQLiteを使う。
- Playwright等は候補比較に留める。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- test pyramid
- acceptance scenario
- 主要TC-ID候補
- mock/fixture
- migration/backup test
- E2E対象
- 性能・容量
- diagnostics画面の受入条件

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
