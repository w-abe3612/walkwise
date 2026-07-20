---
document_type: claude_code_execution_order
status: review
version: "2.0"
last_updated: "2026-07-20"
---

# 実装順序と依存関係

`TASK-REVIEW-001`の完了条件に従い、実行完了済み53タスクの個別依存関係表は
削除した(全タスクの依存関係・実行順序の履歴は git履歴および
[`docs/notes/progress.md`](../notes/progress.md)を参照)。

## 現役タスク

- [`TASK-COEIR-001`](TASK-COEIR-001-coeiroink-client-adapter.md) — 永久blocked。
  依存: `TASK-TTS-001`(完了済み)、`TASK-PROFILE-001`(完了済み)。
  公式API世代・endpoint・話者識別子・利用条件が確認できるまで実行禁止。
- [`TASK-REVIEW-001`](TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md) —
  実行中。依存: 完了済み全53タスク(実行時統合対象のcomposition root・
  Worker registry・IPC adapter・Renderer root等はすべてそれらタスクの成果物を再利用する)。
