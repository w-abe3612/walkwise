---
status: review
version: "1.0"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_163743.txt"
---

# STEP2 タスク契約書・テストケース一覧

- 契約書: **54件**
- テストケース: **530件**
- 共通外部疎通方針: [external-connectivity-policy.md](external-connectivity-policy.md)

## 0. 開発基盤

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-DEV-001` | Pythonパッケージ・pytest収集基盤 | MVP | review | 10 | [TASK-DEV-001-repository-and-test-baseline.md](TASK-DEV-001-repository-and-test-baseline.md) |
| `TASK-ENV-001` | Docker開発・テスト実行環境 | MVP | review | 9 | [TASK-ENV-001-docker-development-and-test-environment.md](TASK-ENV-001-docker-development-and-test-environment.md) |
| `TASK-CORE-001` | 設定・共通エラー・ログ契約 | MVP | review | 8 | [TASK-CORE-001-configuration-errors-and-logging.md](TASK-CORE-001-configuration-errors-and-logging.md) |
| `TASK-CORE-002` | 共通ID・canonical hash・YAML/JSON入出力 | MVP | review | 8 | [TASK-CORE-002-identifiers-hashing-and-structured-files.md](TASK-CORE-002-identifiers-hashing-and-structured-files.md) |
| `TASK-FILE-001` | ローカルファイル永続化・Project配置・atomic write | MVP | review | 9 | [TASK-FILE-001-local-file-persistence-and-project-layout.md](TASK-FILE-001-local-file-persistence-and-project-layout.md) |
| `TASK-DOMAIN-001` | ドメインモデルと列挙値 | MVP | review | 9 | [TASK-DOMAIN-001-domain-entities-and-validation.md](TASK-DOMAIN-001-domain-entities-and-validation.md) |

## 1. 永続化と業務サービス

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-DB-001` | SQLite接続・migration runner・初期schema | MVP | review | 10 | [TASK-DB-001-sqlite-migrations-and-initial-schema.md](TASK-DB-001-sqlite-migrations-and-initial-schema.md) |
| `TASK-DB-002` | Repository・transaction境界 | MVP | review | 8 | [TASK-DB-002-repositories-and-unit-of-work.md](TASK-DB-002-repositories-and-unit-of-work.md) |
| `TASK-PROJECT-001` | Project作成・一覧・取得サービス | MVP | review | 7 | [TASK-PROJECT-001-project-application-service.md](TASK-PROJECT-001-project-application-service.md) |
| `TASK-SOURCE-001` | Source登録・状態管理サービス | MVP | review | 8 | [TASK-SOURCE-001-source-metadata-service.md](TASK-SOURCE-001-source-metadata-service.md) |
| `TASK-RIGHTS-001` | 権利・ライセンス・配布gate | MVP | review | 10 | [TASK-RIGHTS-001-rights-license-and-distribution-gate.md](TASK-RIGHTS-001-rights-license-and-distribution-gate.md) |
| `TASK-BUILD-001` | Build Request作成サービス | MVP | review | 8 | [TASK-BUILD-001-build-request-service.md](TASK-BUILD-001-build-request-service.md) |
| `TASK-JOB-001` | Job状態遷移・FIFO・再試行・stale復旧 | MVP | review | 10 | [TASK-JOB-001-job-lifecycle-queue-and-recovery.md](TASK-JOB-001-job-lifecycle-queue-and-recovery.md) |
| `TASK-ARTIFACT-001` | Artifact登録・version管理 | MVP | review | 9 | [TASK-ARTIFACT-001-artifact-registry-and-versioning.md](TASK-ARTIFACT-001-artifact-registry-and-versioning.md) |
| `TASK-APPROVAL-001` | 4段階承認・差し戻し・無効化 | MVP | review | 10 | [TASK-APPROVAL-001-approval-workflow-and-invalidation.md](TASK-APPROVAL-001-approval-workflow-and-invalidation.md) |

## 2. 資料入力

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-INGEST-001` | 資料入力orchestrator・テキスト入力 | MVP | review | 9 | [TASK-INGEST-001-material-input-orchestrator-and-text.md](TASK-INGEST-001-material-input-orchestrator-and-text.md) |
| `TASK-IMAGE-001` | 画像群登録・順序・manifest | MVP | review | 10 | [TASK-IMAGE-001-image-material-registration-and-manifest.md](TASK-IMAGE-001-image-material-registration-and-manifest.md) |
| `TASK-IMAGE-002` | 画像前処理・品質flag・見開き分割 | MVP | review | 8 | [TASK-IMAGE-002-image-preprocessing-and-quality-review.md](TASK-IMAGE-002-image-preprocessing-and-quality-review.md) |
| `TASK-PDF-001` | PDF直接テキスト抽出 | MVP | review | 10 | [TASK-PDF-001-pdf-direct-text-extraction.md](TASK-PDF-001-pdf-direct-text-extraction.md) |
| `TASK-OCR-001` | OCR・スキャンPDF処理 | MVP | review | 12 | [TASK-OCR-001-ocr-and-scanned-pdf-processing.md](TASK-OCR-001-ocr-and-scanned-pdf-processing.md) |
| `TASK-SOURCE-002` | 資料正規化・chunk・index・manifest | MVP | review | 10 | [TASK-SOURCE-002-source-normalization-chunking-and-index.md](TASK-SOURCE-002-source-normalization-chunking-and-index.md) |
| `TASK-SOURCE-003` | 資料レビュー・修正差分・再処理 | MVP | review | 10 | [TASK-SOURCE-003-source-review-and-manual-correction.md](TASK-SOURCE-003-source-review-and-manual-correction.md) |
| `TASK-EPUB-001` | EPUBテキスト抽出 | post-MVP | review | 10 | [TASK-EPUB-001-epub-text-extraction.md](TASK-EPUB-001-epub-text-extraction.md) |

## 3. 教材生成AI

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-AI-001` | AI共通契約・Gemini adapter | MVP | review | 12 | [TASK-AI-001-ai-client-contract-and-gemini-adapter.md](TASK-AI-001-ai-client-contract-and-gemini-adapter.md) |
| `TASK-AI-002` | AIモデルrouting・cache・費用・予算停止 | MVP | review | 10 | [TASK-AI-002-ai-routing-cost-cache-and-budget.md](TASK-AI-002-ai-routing-cost-cache-and-budget.md) |
| `TASK-AI-003` | source summary・topic index・coverage map | MVP | review | 10 | [TASK-AI-003-source-analysis-and-coverage.md](TASK-AI-003-source-analysis-and-coverage.md) |
| `TASK-CURRICULUM-001` | topic map・curriculum・章仕様生成 | MVP | review | 10 | [TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md](TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md) |
| `TASK-SCRIPT-001` | 原稿segment・章初稿生成 | MVP | review | 9 | [TASK-SCRIPT-001-script-segments-and-draft-generation.md](TASK-SCRIPT-001-script-segments-and-draft-generation.md) |
| `TASK-CLAIM-001` | 技術的主張・出典対応・fact check | MVP | review | 10 | [TASK-CLAIM-001-claims-evidence-and-fact-checking.md](TASK-CLAIM-001-claims-evidence-and-fact-checking.md) |
| `TASK-PROFILE-001` | Character・Voice profile読込と選択 | MVP | review | 9 | [TASK-PROFILE-001-character-and-voice-profiles.md](TASK-PROFILE-001-character-and-voice-profiles.md) |
| `TASK-NARRATION-001` | 分かりやすさ・音声向け・character変換・最終意味検証 | MVP | review | 10 | [TASK-NARRATION-001-narration-transformations-and-verified-script.md](TASK-NARRATION-001-narration-transformations-and-verified-script.md) |
| `TASK-PIPELINE-001` | 変更影響判定・部分再生成計画 | MVP | review | 10 | [TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md](TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md) |

## 4. TTSと成果物

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-TTS-001` | TTS共通Protocol・registry・エラー契約 | MVP | review | 10 | [TASK-TTS-001-tts-client-interface-and-registry.md](TASK-TTS-001-tts-client-interface-and-registry.md) |
| `TASK-VOICEVOX-001` | VOICEVOX adapter・話者一覧・合成 | MVP | review | 12 | [TASK-VOICEVOX-001-voicevox-client-adapter.md](TASK-VOICEVOX-001-voicevox-client-adapter.md) |
| `TASK-AUDIO-001` | 試聴・segment TTS・WAV cache | MVP | review | 10 | [TASK-AUDIO-001-preview-and-segment-tts-cache.md](TASK-AUDIO-001-preview-and-segment-tts-cache.md) |
| `TASK-AUDIO-002` | 音声自動検査・provisional閾値 | MVP | review | 10 | [TASK-AUDIO-002-audio-validation.md](TASK-AUDIO-002-audio-validation.md) |
| `TASK-AUDIO-003` | 章MP3・text成果物・manifest・Build orchestration | MVP | review | 10 | [TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md](TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md) |
| `TASK-M4B-001` | M4B出力 | post-MVP | review | 10 | [TASK-M4B-001-m4b-output.md](TASK-M4B-001-m4b-output.md) |
| `TASK-ASR-001` | ASRによる原稿・音声照合 | post-MVP | review | 12 | [TASK-ASR-001-asr-script-audio-verification.md](TASK-ASR-001-asr-script-audio-verification.md) |
| `TASK-COEIR-001` | COEIROINK adapter | blocked | review | 12 | [TASK-COEIR-001-coeiroink-client-adapter.md](TASK-COEIR-001-coeiroink-client-adapter.md) |

## 5. Workerとデスクトップ

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-WORKER-001` | Python worker request dispatch・JSON Lines event | MVP | review | 10 | [TASK-WORKER-001-python-worker-request-and-event-protocol.md](TASK-WORKER-001-python-worker-request-and-event-protocol.md) |
| `TASK-WORKER-002` | Python worker cancel・timeout・異常終了復旧 | MVP | review | 10 | [TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md](TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md) |
| `TASK-DESKTOP-001` | Electron/Vue scaffold・main/preload安全境界 | MVP | review | 9 | [TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md](TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md) |
| `TASK-DESKTOP-002` | Electron起動時data/DB/worker bootstrap | MVP | review | 12 | [TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md](TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md) |
| `TASK-UI-001` | Project一覧・新規作成画面 | MVP | review | 9 | [TASK-UI-001-project-list-and-create-screen.md](TASK-UI-001-project-list-and-create-screen.md) |
| `TASK-UI-002` | Project workspace・Source登録/レビュー・承認UI | MVP | review | 9 | [TASK-UI-002-source-workspace-review-and-approval.md](TASK-UI-002-source-workspace-review-and-approval.md) |
| `TASK-UI-003` | 出力・声設定・試聴画面 | MVP | review | 9 | [TASK-UI-003-build-settings-and-voice-preview-screen.md](TASK-UI-003-build-settings-and-voice-preview-screen.md) |
| `TASK-UI-004` | Job進捗・cancel/retry・成果物画面 | MVP | review | 9 | [TASK-UI-004-job-progress-and-artifacts-screens.md](TASK-UI-004-job-progress-and-artifacts-screens.md) |
| `TASK-UI-005` | Renderer共通state・navigation・error・アクセシビリティ | MVP | review | 9 | [TASK-UI-005-renderer-state-routing-errors-and-accessibility.md](TASK-UI-005-renderer-state-routing-errors-and-accessibility.md) |
| `TASK-DESKTOP-003` | Desktop最短end-to-end導線 | MVP | review | 12 | [TASK-DESKTOP-003-desktop-end-to-end-integration.md](TASK-DESKTOP-003-desktop-end-to-end-integration.md) |

## 6. 移行・品質・配布

| Task ID | タイトル | scope | 状態 | case数 | 契約書 |
|---|---|---|---|---:|---|
| `TASK-MIGRATION-001` | 旧形式・既存client互換adapter | MVP | review | 10 | [TASK-MIGRATION-001-legacy-format-and-client-adapters.md](TASK-MIGRATION-001-legacy-format-and-client-adapters.md) |
| `TASK-E2E-001` | サンプル1章fixture・仕様間受入検証 | MVP | review | 12 | [TASK-E2E-001-sample-book-fixtures-and-acceptance.md](TASK-E2E-001-sample-book-fixtures-and-acceptance.md) |
| `TASK-RELEASE-001` | Windows package・runtime同梱・license/privacy/backup | MVP | review | 12 | [TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md](TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md) |
| `TASK-RELEASE-002` | 性能・耐障害・最終release受入 | MVP | review | 10 | [TASK-RELEASE-002-performance-resilience-and-release-acceptance.md](TASK-RELEASE-002-performance-resilience-and-release-acceptance.md) |

## 外部疎通対象

| Task | 対象 | 疎通fixture | 状態 |
|---|---|---|---|
| `TASK-AI-001` | Gemini API | `gemini_connectivity_gate` | review |
| `TASK-VOICEVOX-001` | VOICEVOX Engine API | `voicevox_connectivity_gate` | review |
| `TASK-COEIR-001` | COEIROINK API | `coeiroink_connectivity_gate` | blocked |
| `TASK-ASR-001` | ローカルWhisper互換runtime | `asr_connectivity_gate` | review |
| `TASK-OCR-001` | Tesseract runtime | `tesseract_connectivity_gate` | review |
| `TASK-AUDIO-002` | ffmpeg/ffprobe runtime | `ffmpeg_connectivity_gate` | review |
| `TASK-M4B-001` | ffmpeg runtime | `ffmpeg_connectivity_gate` | review |
| `TASK-RELEASE-001` | 配布runtime群 | `release_runtime_connectivity_gate` | review |
| `TASK-DESKTOP-002` | Python worker subprocess | `worker_connectivity_gate` | review |
| `TASK-DESKTOP-003` | Desktop統合runtime | `desktop_connectivity_gate` | review |
| `TASK-E2E-001` | 任意の実VOICEVOX | `voicevox_connectivity_gate` | review |
