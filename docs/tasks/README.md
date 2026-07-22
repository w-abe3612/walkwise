---
document_type: claude_code_task_directory_guide
status: review
version: "1.1"
last_updated: "2026-07-22"
generated_from_dump: "audio_book_creation_dump_2026-07-19_180714.txt"
---

# Walkwise Claude Code実行タスク

`docs/tasks/`は、ChatGPTによる実装準備が完了した後、人間承認を経てClaude Codeへ渡す実行指示の正本である。

## 実行順

1. [CLAUDE_CODE_RULES.md](CLAUDE_CODE_RULES.md)を読む。
2. [EXECUTION_ORDER.md](EXECUTION_ORDER.md)の順序と依存関係を確認する。
3. 1回のClaude Code作業では原則1タスクだけを実行する。
4. テスト本実装→Red確認→source本実装→対象テスト→全体回帰→文書修正の順を守る。
5. MVP 50タスクを先に扱う。post-MVP 3タスクとblocked 1タスクは別承認まで実行しない。

## 現在の準備基準

- タスク契約: 54
- テストケース: 530
- 契約上のtest file: 109/109
- Python collection: 454
- 現在の通常実行: 431 xfailed / 23 skipped
- 外部接続: 0

この数値は空実装段階の基準であり、実装が進むにつれてxfailはpassへ移行する。
タスク完了報告では、開始時・終了時の両方を記録する。

## 古いコマンド文書

`docs/commands/`には、過去の「19件存在・90件欠落」状態を記録した文言が残っている。
STEP7では修正責任を各実装タスクへ割り当てた。

- 共通状態とmanifest: `TASK-DEV-001`
- 分野別文書: 最初にその文書を扱う関連タスク
- 個別文書では揮発性の存在注記を削除し、状態は`CURRENT_STATE.md`へ集約する

## 旧タスク

`16_image-material-ingestion.md`(superseded、`TASK-IMAGE-001`/`TASK-IMAGE-002`への
redirect専用文書)は、両taskとも完了したため`TASK-REVIEW-001`で削除した。

## 完了タスク文書の削除(TASK-REVIEW-001)

実行完了済み53タスク(MVP対象50件 + post-MVP対象3件)の個別task文書は、
`TASK-REVIEW-001`(実行時統合とリポジトリ整理)の完了条件に従い削除した。
上記「現在の準備基準」の数値(454収集・431 xfailed等)はSTEP3空実装段階の
開始時baselineとして意図的に固定された記述であり、削除後の現在の状態は
`docs/commands/CURRENT_STATE.md`を正本とする。

現在の現役task文書一覧(`TASK-COEIR-001`、`TASK-REVIEW-001`、および
`TASK-REVIEW-001`完了後に新規作成された`TASK-BUILD-EXEC-001`/
`TASK-VOICE-PROFILE-UI-001`)は[`INDEX.md`](INDEX.md)を正本とする。
