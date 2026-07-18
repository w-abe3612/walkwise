---
task_id: SPEC-APP-013
task_type: specification_drafting
status: ready
order: 33
title: "処理進捗・ログ・通知・中断復旧"
depends_on:
  - SPEC-APP-005
  - SPEC-APP-008
output: "docs/spec-proposals/generated-specifications/app-management/12-job-monitoring-and-recovery.md"
---

# 処理進捗・ログ・通知・中断復旧

## 1. 目的

長時間処理を画面から監視し、cancel、retry、resume、失敗原因、再実行範囲を扱う仕様を草案化する。

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

1. 進捗率を何から計算するか。
2. logをどこまで利用者へ見せるか。
3. browserを閉じてもJobは継続するか。
4. PC再起動後にresumeできるか。
5. 通知方式は何か。
6. 同時Job数はどう制限するか。

## 3. 初期推奨回答

- Jobは画面sessionから独立して継続する案を優先する。
- step、processed/total、current item、ETA不確実性を表示する。
- 利用者向け要約errorと技術logを分ける。
- MVPではapp内通知、OS通知は後続候補。

推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する。

## 4. 成果物へ必ず含めるもの

- progress model
- Job event
- ログlevelと保存期間
- cancel/retry/resume
- stale running Job復旧
- 同時実行制御
- 画面例
- 異常系

## 5. 人間レビュー項目

- 草案の採否と未決定事項

## 6. 完了条件

- 指定された出力ファイルが`review`、`provisional`、`blocked`のいずれかで存在する。
- 代替案、採用理由、未決定事項が記録されている。
- 既存承認済み仕様を変更していない。
- ソースコードを変更していない。
