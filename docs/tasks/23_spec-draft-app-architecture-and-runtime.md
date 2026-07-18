---
task_id: SPEC-APP-003
task_type: specification_drafting
status: ready
order: 23
title: "アプリケーション構成・技術スタック・起動方式"
depends_on:
  - SPEC-APP-001
  - SPEC-APP-002
output: "docs/spec-proposals/generated-specifications/app-management/02-architecture-and-runtime.md"
---

# アプリケーション構成・技術スタック・起動方式

## 1. 目的

フロント、Python処理、DB、ローカルTTS、ファイルシステムを接続する構成案を比較し、一コマンド起動の草案を作る。

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

1. SPA、サーバーレンダリング、デスクトップ包装のどれが適切か。
2. 既存Pythonコードをどうapplication service化するか。
3. 一コマンド起動とブラウザ自動表示をどう実現するか。
4. WindowsホストとDockerをどう扱うか。
5. ジョブ処理を同一process、subprocess、workerのどれにするか。
6. 開発・配布・更新方法は何か。

## 3. 初期推奨回答

- FastAPI等Python backend＋Vue 3系SPA案を有力候補として比較するが決め打ちしない。
- ローカルHTTPはloopback限定を初期案とする。
- 起動launcherがDB migration、port選択、health確認、browser openを順に行う案を検討する。
- TTSエンジンは外部ローカルserviceとしてadapter越しに扱う。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- 3案以上の比較表
- 推奨構成図
- process境界
- 起動・終了sequence
- port競合時の動作
- Windows/Docker構成
- 開発用と利用者用コマンド案
- 採用判断条件

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
