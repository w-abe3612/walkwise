---
status: draft
version: "1.0"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
---

# 実装準備タスク一覧

> 本一覧はSTEP1の正本である。`docs/tasks/`へ置くClaude Code実行タスク一覧ではない。
> 全MVPタスクのSTEP2〜STEP7と収集確認、人間承認が終わるまでClaude Codeの本実装を開始しない。

## 状態

- `draft`: STEP1で切り出し済み。後続準備は未完了。
- `blocked`: 外部証拠や仕様条件が不足し、値を推測して固定できない。

## 一覧

| 順序 | task_id | タイトル | phase | scope | status | dependencies | task file |
|---:|---|---|---|---|---|---|---|
| 101 | `TASK-DEV-001` | [Pythonパッケージ・pytest収集基盤](101_task-dev-001-repository-and-test-baseline.md) | 0. 開発基盤 | MVP | draft | - | `101_task-dev-001-repository-and-test-baseline.md` |
| 102 | `TASK-ENV-001` | [Docker開発・テスト実行環境](102_task-env-001-docker-development-and-test-environment.md) | 0. 開発基盤 | MVP | draft | TASK-DEV-001 | `102_task-env-001-docker-development-and-test-environment.md` |
| 103 | `TASK-CORE-001` | [設定・共通エラー・ログ契約](103_task-core-001-configuration-errors-and-logging.md) | 0. 開発基盤 | MVP | draft | TASK-DEV-001 | `103_task-core-001-configuration-errors-and-logging.md` |
| 104 | `TASK-CORE-002` | [共通ID・canonical hash・YAML/JSON入出力](104_task-core-002-identifiers-hashing-and-structured-files.md) | 0. 開発基盤 | MVP | draft | TASK-DEV-001<br>TASK-CORE-001 | `104_task-core-002-identifiers-hashing-and-structured-files.md` |
| 105 | `TASK-FILE-001` | [ローカルファイル永続化・Project配置・atomic write](105_task-file-001-local-file-persistence-and-project-layout.md) | 0. 開発基盤 | MVP | draft | TASK-CORE-001<br>TASK-CORE-002 | `105_task-file-001-local-file-persistence-and-project-layout.md` |
| 106 | `TASK-DOMAIN-001` | [ドメインモデルと列挙値](106_task-domain-001-domain-entities-and-validation.md) | 0. 開発基盤 | MVP | draft | TASK-CORE-002 | `106_task-domain-001-domain-entities-and-validation.md` |
| 107 | `TASK-DB-001` | [SQLite接続・migration runner・初期schema](107_task-db-001-sqlite-migrations-and-initial-schema.md) | 1. 永続化と業務サービス | MVP | draft | TASK-ENV-001<br>TASK-FILE-001<br>TASK-DOMAIN-001 | `107_task-db-001-sqlite-migrations-and-initial-schema.md` |
| 108 | `TASK-DB-002` | [Repository・transaction境界](108_task-db-002-repositories-and-unit-of-work.md) | 1. 永続化と業務サービス | MVP | draft | TASK-DB-001 | `108_task-db-002-repositories-and-unit-of-work.md` |
| 109 | `TASK-PROJECT-001` | [Project作成・一覧・取得サービス](109_task-project-001-project-application-service.md) | 1. 永続化と業務サービス | MVP | draft | TASK-DB-002<br>TASK-FILE-001 | `109_task-project-001-project-application-service.md` |
| 110 | `TASK-SOURCE-001` | [Source登録・状態管理サービス](110_task-source-001-source-metadata-service.md) | 1. 永続化と業務サービス | MVP | draft | TASK-DB-002<br>TASK-FILE-001<br>TASK-PROJECT-001 | `110_task-source-001-source-metadata-service.md` |
| 111 | `TASK-RIGHTS-001` | [権利・ライセンス・配布gate](111_task-rights-001-rights-license-and-distribution-gate.md) | 1. 永続化と業務サービス | MVP | draft | TASK-SOURCE-001 | `111_task-rights-001-rights-license-and-distribution-gate.md` |
| 112 | `TASK-BUILD-001` | [Build Request作成サービス](112_task-build-001-build-request-service.md) | 1. 永続化と業務サービス | MVP | draft | TASK-DB-002<br>TASK-PROJECT-001 | `112_task-build-001-build-request-service.md` |
| 113 | `TASK-JOB-001` | [Job状態遷移・FIFO・再試行・stale復旧](113_task-job-001-job-lifecycle-queue-and-recovery.md) | 1. 永続化と業務サービス | MVP | draft | TASK-BUILD-001<br>TASK-DB-002 | `113_task-job-001-job-lifecycle-queue-and-recovery.md` |
| 114 | `TASK-ARTIFACT-001` | [Artifact登録・version管理](114_task-artifact-001-artifact-registry-and-versioning.md) | 1. 永続化と業務サービス | MVP | draft | TASK-JOB-001<br>TASK-FILE-001<br>TASK-DB-002 | `114_task-artifact-001-artifact-registry-and-versioning.md` |
| 115 | `TASK-APPROVAL-001` | [4段階承認・差し戻し・無効化](115_task-approval-001-approval-workflow-and-invalidation.md) | 1. 永続化と業務サービス | MVP | draft | TASK-PROJECT-001<br>TASK-SOURCE-001<br>TASK-FILE-001 | `115_task-approval-001-approval-workflow-and-invalidation.md` |
| 116 | `TASK-INGEST-001` | [資料入力orchestrator・テキスト入力](116_task-ingest-001-material-input-orchestrator-and-text.md) | 2. 資料入力 | MVP | draft | TASK-SOURCE-001<br>TASK-RIGHTS-001<br>TASK-JOB-001 | `116_task-ingest-001-material-input-orchestrator-and-text.md` |
| 117 | `TASK-IMAGE-001` | [画像群登録・順序・manifest](117_task-image-001-image-material-registration-and-manifest.md) | 2. 資料入力 | MVP | draft | TASK-INGEST-001 | `117_task-image-001-image-material-registration-and-manifest.md` |
| 118 | `TASK-IMAGE-002` | [画像前処理・品質flag・見開き分割](118_task-image-002-image-preprocessing-and-quality-review.md) | 2. 資料入力 | MVP | draft | TASK-IMAGE-001 | `118_task-image-002-image-preprocessing-and-quality-review.md` |
| 119 | `TASK-PDF-001` | [PDF直接テキスト抽出](119_task-pdf-001-pdf-direct-text-extraction.md) | 2. 資料入力 | MVP | draft | TASK-INGEST-001 | `119_task-pdf-001-pdf-direct-text-extraction.md` |
| 120 | `TASK-OCR-001` | [OCR・スキャンPDF処理](120_task-ocr-001-ocr-and-scanned-pdf-processing.md) | 2. 資料入力 | MVP | draft | TASK-IMAGE-002<br>TASK-PDF-001 | `120_task-ocr-001-ocr-and-scanned-pdf-processing.md` |
| 121 | `TASK-SOURCE-002` | [資料正規化・chunk・index・manifest](121_task-source-002-source-normalization-chunking-and-index.md) | 2. 資料入力 | MVP | draft | TASK-INGEST-001<br>TASK-PDF-001<br>TASK-OCR-001 | `121_task-source-002-source-normalization-chunking-and-index.md` |
| 122 | `TASK-SOURCE-003` | [資料レビュー・修正差分・再処理](122_task-source-003-source-review-and-manual-correction.md) | 2. 資料入力 | MVP | draft | TASK-SOURCE-002<br>TASK-SOURCE-001 | `122_task-source-003-source-review-and-manual-correction.md` |
| 123 | `TASK-EPUB-001` | [EPUBテキスト抽出](123_task-epub-001-epub-text-extraction.md) | 2. 資料入力 | post-MVP | draft | TASK-INGEST-001<br>TASK-SOURCE-002 | `123_task-epub-001-epub-text-extraction.md` |
| 124 | `TASK-AI-001` | [AI共通契約・Gemini adapter](124_task-ai-001-ai-client-contract-and-gemini-adapter.md) | 3. 教材生成AI | MVP | draft | TASK-CORE-001<br>TASK-CORE-002 | `124_task-ai-001-ai-client-contract-and-gemini-adapter.md` |
| 125 | `TASK-AI-002` | [AIモデルrouting・cache・費用・予算停止](125_task-ai-002-ai-routing-cost-cache-and-budget.md) | 3. 教材生成AI | MVP | draft | TASK-AI-001<br>TASK-SOURCE-002 | `125_task-ai-002-ai-routing-cost-cache-and-budget.md` |
| 126 | `TASK-AI-003` | [source summary・topic index・coverage map](126_task-ai-003-source-analysis-and-coverage.md) | 3. 教材生成AI | MVP | draft | TASK-AI-002<br>TASK-SOURCE-002 | `126_task-ai-003-source-analysis-and-coverage.md` |
| 127 | `TASK-CURRICULUM-001` | [topic map・curriculum・章仕様生成](127_task-curriculum-001-curriculum-and-chapter-spec-generation.md) | 3. 教材生成AI | MVP | draft | TASK-AI-003<br>TASK-APPROVAL-001 | `127_task-curriculum-001-curriculum-and-chapter-spec-generation.md` |
| 128 | `TASK-SCRIPT-001` | [原稿segment・章初稿生成](128_task-script-001-script-segments-and-draft-generation.md) | 3. 教材生成AI | MVP | draft | TASK-CURRICULUM-001<br>TASK-AI-002 | `128_task-script-001-script-segments-and-draft-generation.md` |
| 129 | `TASK-CLAIM-001` | [技術的主張・出典対応・fact check](129_task-claim-001-claims-evidence-and-fact-checking.md) | 3. 教材生成AI | MVP | draft | TASK-SCRIPT-001<br>TASK-AI-002<br>TASK-SOURCE-002 | `129_task-claim-001-claims-evidence-and-fact-checking.md` |
| 130 | `TASK-PROFILE-001` | [Character・Voice profile読込と選択](130_task-profile-001-character-and-voice-profiles.md) | 3. 教材生成AI | MVP | draft | TASK-CORE-002 | `130_task-profile-001-character-and-voice-profiles.md` |
| 131 | `TASK-NARRATION-001` | [分かりやすさ・音声向け・character変換・最終意味検証](131_task-narration-001-narration-transformations-and-verified-script.md) | 3. 教材生成AI | MVP | draft | TASK-CLAIM-001<br>TASK-PROFILE-001<br>TASK-APPROVAL-001 | `131_task-narration-001-narration-transformations-and-verified-script.md` |
| 132 | `TASK-PIPELINE-001` | [変更影響判定・部分再生成計画](132_task-pipeline-001-dependency-impact-and-partial-regeneration.md) | 3. 教材生成AI | MVP | draft | TASK-NARRATION-001<br>TASK-APPROVAL-001<br>TASK-ARTIFACT-001 | `132_task-pipeline-001-dependency-impact-and-partial-regeneration.md` |
| 133 | `TASK-TTS-001` | [TTS共通Protocol・registry・エラー契約](133_task-tts-001-tts-client-interface-and-registry.md) | 4. TTSと成果物 | MVP | draft | TASK-PROFILE-001<br>TASK-CORE-001 | `133_task-tts-001-tts-client-interface-and-registry.md` |
| 134 | `TASK-VOICEVOX-001` | [VOICEVOX adapter・話者一覧・合成](134_task-voicevox-001-voicevox-client-adapter.md) | 4. TTSと成果物 | MVP | draft | TASK-TTS-001 | `134_task-voicevox-001-voicevox-client-adapter.md` |
| 135 | `TASK-AUDIO-001` | [試聴・segment TTS・WAV cache](135_task-audio-001-preview-and-segment-tts-cache.md) | 4. TTSと成果物 | MVP | draft | TASK-VOICEVOX-001<br>TASK-NARRATION-001<br>TASK-PIPELINE-001 | `135_task-audio-001-preview-and-segment-tts-cache.md` |
| 136 | `TASK-AUDIO-002` | [音声自動検査・provisional閾値](136_task-audio-002-audio-validation.md) | 4. TTSと成果物 | MVP | draft | TASK-AUDIO-001 | `136_task-audio-002-audio-validation.md` |
| 137 | `TASK-AUDIO-003` | [章MP3・text成果物・manifest・Build orchestration](137_task-audio-003-chapter-packaging-manifests-and-build-orchestration.md) | 4. TTSと成果物 | MVP | draft | TASK-AUDIO-002<br>TASK-ARTIFACT-001<br>TASK-JOB-001<br>TASK-BUILD-001 | `137_task-audio-003-chapter-packaging-manifests-and-build-orchestration.md` |
| 138 | `TASK-M4B-001` | [M4B出力](138_task-m4b-001-m4b-output.md) | 4. TTSと成果物 | post-MVP | draft | TASK-AUDIO-003 | `138_task-m4b-001-m4b-output.md` |
| 139 | `TASK-ASR-001` | [ASRによる原稿・音声照合](139_task-asr-001-asr-script-audio-verification.md) | 4. TTSと成果物 | post-MVP | draft | TASK-AUDIO-003 | `139_task-asr-001-asr-script-audio-verification.md` |
| 140 | `TASK-COEIR-001` | [COEIROINK adapter](140_task-coeir-001-coeiroink-client-adapter.md) | 4. TTSと成果物 | blocked | blocked | TASK-TTS-001<br>TASK-PROFILE-001 | `140_task-coeir-001-coeiroink-client-adapter.md` |
| 141 | `TASK-WORKER-001` | [Python worker request dispatch・JSON Lines event](141_task-worker-001-python-worker-request-and-event-protocol.md) | 5. Workerとデスクトップ | MVP | draft | TASK-JOB-001<br>TASK-AUDIO-003<br>TASK-AI-003 | `141_task-worker-001-python-worker-request-and-event-protocol.md` |
| 142 | `TASK-WORKER-002` | [Python worker cancel・timeout・異常終了復旧](142_task-worker-002-python-worker-cancel-timeout-and-recovery.md) | 5. Workerとデスクトップ | MVP | draft | TASK-WORKER-001<br>TASK-JOB-001 | `142_task-worker-002-python-worker-cancel-timeout-and-recovery.md` |
| 143 | `TASK-DESKTOP-001` | [Electron/Vue scaffold・main/preload安全境界](143_task-desktop-001-electron-vue-scaffold-and-ipc-security.md) | 5. Workerとデスクトップ | MVP | draft | TASK-ENV-001 | `143_task-desktop-001-electron-vue-scaffold-and-ipc-security.md` |
| 144 | `TASK-DESKTOP-002` | [Electron起動時data/DB/worker bootstrap](144_task-desktop-002-electron-data-db-and-worker-bootstrap.md) | 5. Workerとデスクトップ | MVP | draft | TASK-DESKTOP-001<br>TASK-DB-001<br>TASK-WORKER-002 | `144_task-desktop-002-electron-data-db-and-worker-bootstrap.md` |
| 145 | `TASK-UI-001` | [Project一覧・新規作成画面](145_task-ui-001-project-list-and-create-screen.md) | 5. Workerとデスクトップ | MVP | draft | TASK-DESKTOP-002<br>TASK-PROJECT-001 | `145_task-ui-001-project-list-and-create-screen.md` |
| 146 | `TASK-UI-002` | [Project workspace・Source登録/レビュー・承認UI](146_task-ui-002-source-workspace-review-and-approval.md) | 5. Workerとデスクトップ | MVP | draft | TASK-DESKTOP-002<br>TASK-SOURCE-003<br>TASK-APPROVAL-001 | `146_task-ui-002-source-workspace-review-and-approval.md` |
| 147 | `TASK-UI-003` | [出力・声設定・試聴画面](147_task-ui-003-build-settings-and-voice-preview-screen.md) | 5. Workerとデスクトップ | MVP | draft | TASK-DESKTOP-002<br>TASK-BUILD-001<br>TASK-AUDIO-001 | `147_task-ui-003-build-settings-and-voice-preview-screen.md` |
| 148 | `TASK-UI-004` | [Job進捗・cancel/retry・成果物画面](148_task-ui-004-job-progress-and-artifacts-screens.md) | 5. Workerとデスクトップ | MVP | draft | TASK-DESKTOP-002<br>TASK-JOB-001<br>TASK-ARTIFACT-001 | `148_task-ui-004-job-progress-and-artifacts-screens.md` |
| 149 | `TASK-UI-005` | [Renderer共通state・navigation・error・アクセシビリティ](149_task-ui-005-renderer-state-routing-errors-and-accessibility.md) | 5. Workerとデスクトップ | MVP | draft | TASK-UI-001<br>TASK-UI-002<br>TASK-UI-003<br>TASK-UI-004 | `149_task-ui-005-renderer-state-routing-errors-and-accessibility.md` |
| 150 | `TASK-DESKTOP-003` | [Desktop最短end-to-end導線](150_task-desktop-003-desktop-end-to-end-integration.md) | 5. Workerとデスクトップ | MVP | draft | TASK-UI-005<br>TASK-WORKER-002<br>TASK-AUDIO-003 | `150_task-desktop-003-desktop-end-to-end-integration.md` |
| 151 | `TASK-MIGRATION-001` | [旧形式・既存client互換adapter](151_task-migration-001-legacy-format-and-client-adapters.md) | 6. 移行・品質・配布 | MVP | draft | TASK-CORE-002<br>TASK-SCRIPT-001<br>TASK-VOICEVOX-001 | `151_task-migration-001-legacy-format-and-client-adapters.md` |
| 152 | `TASK-E2E-001` | [サンプル1章fixture・仕様間受入検証](152_task-e2e-001-sample-book-fixtures-and-acceptance.md) | 6. 移行・品質・配布 | MVP | draft | TASK-DESKTOP-003<br>TASK-MIGRATION-001 | `152_task-e2e-001-sample-book-fixtures-and-acceptance.md` |
| 153 | `TASK-RELEASE-001` | [Windows package・runtime同梱・license/privacy/backup](153_task-release-001-windows-packaging-security-licenses-and-backup.md) | 6. 移行・品質・配布 | MVP | draft | TASK-DESKTOP-003<br>TASK-ENV-001<br>TASK-RIGHTS-001 | `153_task-release-001-windows-packaging-security-licenses-and-backup.md` |
| 154 | `TASK-RELEASE-002` | [性能・耐障害・最終release受入](154_task-release-002-performance-resilience-and-release-acceptance.md) | 6. 移行・品質・配布 | MVP | draft | TASK-E2E-001<br>TASK-RELEASE-001 | `154_task-release-002-performance-resilience-and-release-acceptance.md` |

## 実装開始順序

同じphase内でも`depends_on`を優先する。番号は推奨順であり、依存未完了taskを先に実装しない。

## post-MVP・blocked

- `TASK-EPUB-001`: post-MVP
- `TASK-M4B-001`: post-MVP
- `TASK-ASR-001`: post-MVP
- `TASK-COEIR-001`: blocked

## STEP2への引継ぎ

各task fileの「STEP2で固定する契約」を元に、`docs/test-cases/`へ1 task 1文書で契約とGiven/When/Thenを作成する。