---
status: draft
version: "2.0"
last_updated: "2026-07-20"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
---

# 実装準備タスク一覧

> 本一覧はSTEP1の正本である。`docs/tasks/`へ置くClaude Code実行タスク一覧ではない。
> 全MVPタスクのSTEP2〜STEP7と収集確認、人間承認が終わるまでClaude Codeの本実装を開始しない。

`TASK-REVIEW-001`(実行時統合とリポジトリ整理)の完了条件に従い、
実行完了済み53タスク(MVP対象50件 + post-MVP対象3件)分の個別STEP1提案書
(`101_....md`〜`154_....md`、`140`のCOEIROINK分を除く)を削除した。
各task_idの実装結果は[`docs/tasks/INDEX.md`](../../tasks/INDEX.md)と
[`docs/notes/progress.md`](../../notes/progress.md)を正本とする。

## 状態

- `draft`: STEP1で切り出し済み。後続準備は未完了。
- `blocked`: 外部証拠や仕様条件が不足し、値を推測して固定できない。

## 現役タスク

| 順序 | task_id | タイトル | phase | scope | status | task file |
|---:|---|---|---|---|---|---|
| 140 | `TASK-COEIR-001` | [COEIROINK adapter](140_task-coeir-001-coeiroink-client-adapter.md) | 4. TTSと成果物 | blocked | blocked | `140_task-coeir-001-coeiroink-client-adapter.md` |

## 削除済みタスク(参考、実装完了。順序101〜154、140を除く)

`TASK-DEV-001`, `TASK-ENV-001`, `TASK-CORE-001`, `TASK-CORE-002`, `TASK-FILE-001`,
`TASK-DOMAIN-001`, `TASK-DB-001`, `TASK-DB-002`, `TASK-PROJECT-001`, `TASK-SOURCE-001`,
`TASK-RIGHTS-001`, `TASK-BUILD-001`, `TASK-JOB-001`, `TASK-ARTIFACT-001`,
`TASK-APPROVAL-001`, `TASK-INGEST-001`, `TASK-IMAGE-001`, `TASK-IMAGE-002`,
`TASK-PDF-001`, `TASK-OCR-001`, `TASK-SOURCE-002`, `TASK-SOURCE-003`, `TASK-EPUB-001`,
`TASK-AI-001`, `TASK-AI-002`, `TASK-AI-003`, `TASK-CURRICULUM-001`, `TASK-SCRIPT-001`,
`TASK-CLAIM-001`, `TASK-PROFILE-001`, `TASK-NARRATION-001`, `TASK-PIPELINE-001`,
`TASK-TTS-001`, `TASK-VOICEVOX-001`, `TASK-AUDIO-001`, `TASK-AUDIO-002`,
`TASK-AUDIO-003`, `TASK-M4B-001`, `TASK-ASR-001`, `TASK-WORKER-001`, `TASK-WORKER-002`,
`TASK-DESKTOP-001`, `TASK-DESKTOP-002`, `TASK-UI-001`, `TASK-UI-002`, `TASK-UI-003`,
`TASK-UI-004`, `TASK-UI-005`, `TASK-DESKTOP-003`, `TASK-MIGRATION-001`, `TASK-E2E-001`,
`TASK-RELEASE-001`, `TASK-RELEASE-002`

## post-MVP・blocked(削除済み分含む、参考)

- `TASK-EPUB-001`: post-MVP、実装完了
- `TASK-M4B-001`: post-MVP、実装完了
- `TASK-ASR-001`: post-MVP、実装完了
- `TASK-COEIR-001`: blocked、現役(未実装のまま維持)

## STEP2への引継ぎ

各task fileの「STEP2で固定する契約」を元に、`docs/test-cases/`へ1 task 1文書で契約とGiven/When/Thenを作成する。
