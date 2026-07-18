---
task_id: SPEC-APP-012
task_type: specification_drafting
status: ready
order: 32
title: "声・音声プロファイル・試聴選択"
depends_on:
  - SPEC-APP-004
  - SPEC-APP-008
output: "docs/spec-proposals/generated-specifications/app-management/11-voice-selection-and-preview.md"
---

# 声・音声プロファイル・試聴選択

## 1. 目的

VOICEVOX・COEIROINK等の声、style、速度、pitch等を画面で選択・試聴・保存する導線を草案化する。

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

1. engine、speaker、styleをどう列挙するか。
2. engine未起動時の表示は。
3. 試聴原稿とcacheはどうするか。
4. 推奨voiceと利用条件をどう表示するか。
5. Project既定と章・character上書きをどうするか。

## 3. 初期推奨回答

- 利用可能engineをhealth checkし、利用不可は理由付きdisabledにする。
- 共通試聴原稿と短いpreviewを用意する。
- 音声profileは既存schemaを参照し、DBにコピーせずversion参照を検討する。
- クレジット・利用条件を表示する。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- voice選択画面
- engine discovery
- profile hierarchy
- preview Job
- cache invalidation
- 利用条件
- 異常系
- MVPと後続

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
