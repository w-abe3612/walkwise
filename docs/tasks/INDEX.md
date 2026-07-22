---
document_type: claude_code_task_index
status: review
version: "2.1"
last_updated: "2026-07-22"
---

# Claude Code実行タスク一覧

`TASK-REVIEW-001`の完了条件に従い、実行完了済み53タスク(MVP対象50件 + post-MVP対象3件)の
個別task文書は削除した。各タスクの実装内容・確認結果は
[`docs/notes/progress.md`](../notes/progress.md)に完了時点の記録が残っており、
設計判断は[`docs/notes/implementation_assumptions.md`](../notes/implementation_assumptions.md)に、
実測値は[`docs/commands/CURRENT_STATE.md`](../commands/CURRENT_STATE.md)と
`docs/commands/STEP6_MANIFEST.json`に、それぞれ正本として残っている。
削除した54タスク分の元文書は、git履歴(`git log --all -- docs/tasks/`)から参照できる。

## 現役タスク文書

| タスク | タイトル | 状態 |
|---|---|---|
| [`TASK-COEIR-001`](TASK-COEIR-001-coeiroink-client-adapter.md) | COEIROINK adapter | **永久blocked** — 公式API世代・endpoint・話者識別子・利用条件が確認できるまで実装しない |
| [`TASK-REVIEW-001`](TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md) | 実行時統合とリポジトリ整理 | 実行中(人間承認による完了判定待ち。本file自体は人間承認前に削除しない) |
| [`TASK-BUILD-EXEC-001`](TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md) | Build実行パイプラインとVoiceProfile DB | 完了(2026-07-22。詳細は`docs/notes/progress.md`) |
| [`TASK-VOICE-PROFILE-UI-001`](TASK-VOICE-PROFILE-UI-001-project-voice-profile-management-and-build-selection.md) | Project VoiceProfile管理とBuild選択 | 完了(2026-07-22。詳細は`docs/notes/progress.md`) |

## 削除済みタスク(参考、実装完了)

0. 開発基盤: `TASK-DEV-001`, `TASK-ENV-001`, `TASK-CORE-001`, `TASK-CORE-002`,
   `TASK-FILE-001`, `TASK-DOMAIN-001`
1. 永続化と業務サービス: `TASK-DB-001`, `TASK-DB-002`, `TASK-PROJECT-001`,
   `TASK-SOURCE-001`, `TASK-RIGHTS-001`, `TASK-BUILD-001`, `TASK-JOB-001`,
   `TASK-ARTIFACT-001`, `TASK-APPROVAL-001`
2. 資料入力: `TASK-INGEST-001`, `TASK-IMAGE-001`, `TASK-IMAGE-002`, `TASK-PDF-001`,
   `TASK-OCR-001`, `TASK-SOURCE-002`, `TASK-SOURCE-003`, `TASK-EPUB-001`(post-MVP)
3. 教材生成AI: `TASK-AI-001`, `TASK-AI-002`, `TASK-AI-003`, `TASK-CURRICULUM-001`,
   `TASK-SCRIPT-001`, `TASK-CLAIM-001`, `TASK-PROFILE-001`, `TASK-NARRATION-001`,
   `TASK-PIPELINE-001`
4. TTSと成果物: `TASK-TTS-001`, `TASK-VOICEVOX-001`, `TASK-AUDIO-001`,
   `TASK-AUDIO-002`, `TASK-AUDIO-003`, `TASK-M4B-001`(post-MVP), `TASK-ASR-001`(post-MVP)
5. Workerとデスクトップ: `TASK-WORKER-001`, `TASK-WORKER-002`, `TASK-DESKTOP-001`,
   `TASK-DESKTOP-002`, `TASK-UI-001`, `TASK-UI-002`, `TASK-UI-003`, `TASK-UI-004`,
   `TASK-UI-005`, `TASK-DESKTOP-003`
6. 移行・品質・配布: `TASK-MIGRATION-001`, `TASK-E2E-001`, `TASK-RELEASE-001`,
   `TASK-RELEASE-002`

また、supersededな旧文書`16_image-material-ingestion.md`(`TASK-IMAGE-001`/
`TASK-IMAGE-002`が既に両方完了しているため、redirect先自体が不要になった)も削除した。
