---
task_id: SPEC-APP-011
task_type: specification_drafting
status: ready
order: 31
title: "出力形式・出力プロファイル・成果物管理"
depends_on:
  - SPEC-APP-002
  - SPEC-APP-004
  - SPEC-APP-008
output: "docs/spec-proposals/generated-specifications/app-management/10-output-and-export-settings.md"
---

# 出力形式・出力プロファイル・成果物管理

## 1. 目的

MP3、テキスト、EPUBを中心に、出力選択、単位、品質、保存先、再生成、成果物一覧を草案化する。

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

1. 出力形式は複数同時選択か。
2. 章別・全文をどう選ぶか。
3. EPUBはどの仕様確定後に有効化するか。
4. 出力profileを保存・複製できるか。
5. 同名成果物のversionと上書きをどうするか。

## 3. 初期推奨回答

- 複数出力選択を可能にする。
- MP3、textをMVP候補、EPUBは仕様・実装状態によりdisabled表示可能にする。
- 成果物は上書きせずversionとmanifestを持つ。
- 出力先を画面から開ける。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- format capability表
- output profile schema案
- 画面項目
- disabled理由
- artifact一覧
- 再生成・download/open folder
- 上書き禁止
- 異常系

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
