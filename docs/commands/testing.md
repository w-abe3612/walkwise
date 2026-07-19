---
document_type: command_reference
status: review
version: '1.1'
last_updated: '2026-07-19'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
current_state_verified: '2026-07-19'
related_tasks:
- TASK-DEV-001
- TASK-ENV-001
- TASK-CORE-001
- TASK-CORE-002
- TASK-FILE-001
- TASK-DOMAIN-001
- TASK-DB-001
- TASK-DB-002
- TASK-PROJECT-001
- TASK-SOURCE-001
- TASK-RIGHTS-001
- TASK-BUILD-001
- TASK-JOB-001
- TASK-ARTIFACT-001
- TASK-APPROVAL-001
- TASK-INGEST-001
- TASK-IMAGE-001
- TASK-IMAGE-002
- TASK-PDF-001
- TASK-OCR-001
- TASK-SOURCE-002
- TASK-SOURCE-003
- TASK-EPUB-001
- TASK-AI-001
- TASK-AI-002
- TASK-AI-003
- TASK-CURRICULUM-001
- TASK-SCRIPT-001
- TASK-CLAIM-001
- TASK-PROFILE-001
- TASK-NARRATION-001
- TASK-PIPELINE-001
- TASK-TTS-001
- TASK-VOICEVOX-001
- TASK-AUDIO-001
- TASK-AUDIO-002
- TASK-AUDIO-003
- TASK-M4B-001
- TASK-ASR-001
- TASK-COEIR-001
- TASK-WORKER-001
- TASK-WORKER-002
- TASK-DESKTOP-001
- TASK-DESKTOP-002
- TASK-UI-001
- TASK-UI-002
- TASK-UI-003
- TASK-UI-004
- TASK-UI-005
- TASK-DESKTOP-003
- TASK-MIGRATION-001
- TASK-E2E-001
- TASK-RELEASE-001
- TASK-RELEASE-002
release_scopes:
- MVP
- blocked
- post-MVP
---

# testing コマンド

## 1. 目的

全テスト層、収集、対象実行、全体実行、外部接続gateの正本に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-DEV-001` — Pythonパッケージ・pytest収集基盤（MVP）
  - 契約: `docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md`
- `TASK-ENV-001` — Docker開発・テスト実行環境（MVP）
  - 契約: `docs/test-cases/TASK-ENV-001-docker-development-and-test-environment.md`
- `TASK-CORE-001` — 設定・共通エラー・ログ契約（MVP）
  - 契約: `docs/test-cases/TASK-CORE-001-configuration-errors-and-logging.md`
- `TASK-CORE-002` — 共通ID・canonical hash・YAML/JSON入出力（MVP）
  - 契約: `docs/test-cases/TASK-CORE-002-identifiers-hashing-and-structured-files.md`
- `TASK-FILE-001` — ローカルファイル永続化・Project配置・atomic write（MVP）
  - 契約: `docs/test-cases/TASK-FILE-001-local-file-persistence-and-project-layout.md`
- `TASK-DOMAIN-001` — ドメインモデルと列挙値（MVP）
  - 契約: `docs/test-cases/TASK-DOMAIN-001-domain-entities-and-validation.md`
- `TASK-DB-001` — SQLite接続・migration runner・初期schema（MVP）
  - 契約: `docs/test-cases/TASK-DB-001-sqlite-migrations-and-initial-schema.md`
- `TASK-DB-002` — Repository・transaction境界（MVP）
  - 契約: `docs/test-cases/TASK-DB-002-repositories-and-unit-of-work.md`
- `TASK-PROJECT-001` — Project作成・一覧・取得サービス（MVP）
  - 契約: `docs/test-cases/TASK-PROJECT-001-project-application-service.md`
- `TASK-SOURCE-001` — Source登録・状態管理サービス（MVP）
  - 契約: `docs/test-cases/TASK-SOURCE-001-source-metadata-service.md`
- `TASK-RIGHTS-001` — 権利・ライセンス・配布gate（MVP）
  - 契約: `docs/test-cases/TASK-RIGHTS-001-rights-license-and-distribution-gate.md`
- `TASK-BUILD-001` — Build Request作成サービス（MVP）
  - 契約: `docs/test-cases/TASK-BUILD-001-build-request-service.md`
- `TASK-JOB-001` — Job状態遷移・FIFO・再試行・stale復旧（MVP）
  - 契約: `docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md`
- `TASK-ARTIFACT-001` — Artifact登録・version管理（MVP）
  - 契約: `docs/test-cases/TASK-ARTIFACT-001-artifact-registry-and-versioning.md`
- `TASK-APPROVAL-001` — 4段階承認・差し戻し・無効化（MVP）
  - 契約: `docs/test-cases/TASK-APPROVAL-001-approval-workflow-and-invalidation.md`
- `TASK-INGEST-001` — 資料入力orchestrator・テキスト入力（MVP）
  - 契約: `docs/test-cases/TASK-INGEST-001-material-input-orchestrator-and-text.md`
- `TASK-IMAGE-001` — 画像群登録・順序・manifest（MVP）
  - 契約: `docs/test-cases/TASK-IMAGE-001-image-material-registration-and-manifest.md`
- `TASK-IMAGE-002` — 画像前処理・品質flag・見開き分割（MVP）
  - 契約: `docs/test-cases/TASK-IMAGE-002-image-preprocessing-and-quality-review.md`
- `TASK-PDF-001` — PDF直接テキスト抽出（MVP）
  - 契約: `docs/test-cases/TASK-PDF-001-pdf-direct-text-extraction.md`
- `TASK-OCR-001` — OCR・スキャンPDF処理（MVP）
  - 契約: `docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md`
- `TASK-SOURCE-002` — 資料正規化・chunk・index・manifest（MVP）
  - 契約: `docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md`
- `TASK-SOURCE-003` — 資料レビュー・修正差分・再処理（MVP）
  - 契約: `docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md`
- `TASK-EPUB-001` — EPUBテキスト抽出（post-MVP）
  - 契約: `docs/test-cases/TASK-EPUB-001-epub-text-extraction.md`
- `TASK-AI-001` — AI共通契約・Gemini adapter（MVP）
  - 契約: `docs/test-cases/TASK-AI-001-ai-client-contract-and-gemini-adapter.md`
- `TASK-AI-002` — AIモデルrouting・cache・費用・予算停止（MVP）
  - 契約: `docs/test-cases/TASK-AI-002-ai-routing-cost-cache-and-budget.md`
- `TASK-AI-003` — source summary・topic index・coverage map（MVP）
  - 契約: `docs/test-cases/TASK-AI-003-source-analysis-and-coverage.md`
- `TASK-CURRICULUM-001` — topic map・curriculum・章仕様生成（MVP）
  - 契約: `docs/test-cases/TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md`
- `TASK-SCRIPT-001` — 原稿segment・章初稿生成（MVP）
  - 契約: `docs/test-cases/TASK-SCRIPT-001-script-segments-and-draft-generation.md`
- `TASK-CLAIM-001` — 技術的主張・出典対応・fact check（MVP）
  - 契約: `docs/test-cases/TASK-CLAIM-001-claims-evidence-and-fact-checking.md`
- `TASK-PROFILE-001` — Character・Voice profile読込と選択（MVP）
  - 契約: `docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md`
- `TASK-NARRATION-001` — 分かりやすさ・音声向け・character変換・最終意味検証（MVP）
  - 契約: `docs/test-cases/TASK-NARRATION-001-narration-transformations-and-verified-script.md`
- `TASK-PIPELINE-001` — 変更影響判定・部分再生成計画（MVP）
  - 契約: `docs/test-cases/TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md`
- `TASK-TTS-001` — TTS共通Protocol・registry・エラー契約（MVP）
  - 契約: `docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md`
- `TASK-VOICEVOX-001` — VOICEVOX adapter・話者一覧・合成（MVP）
  - 契約: `docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md`
- `TASK-AUDIO-001` — 試聴・segment TTS・WAV cache（MVP）
  - 契約: `docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md`
- `TASK-AUDIO-002` — 音声自動検査・provisional閾値（MVP）
  - 契約: `docs/test-cases/TASK-AUDIO-002-audio-validation.md`
- `TASK-AUDIO-003` — 章MP3・text成果物・manifest・Build orchestration（MVP）
  - 契約: `docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md`
- `TASK-M4B-001` — M4B出力（post-MVP）
  - 契約: `docs/test-cases/TASK-M4B-001-m4b-output.md`
- `TASK-ASR-001` — ASRによる原稿・音声照合（post-MVP）
  - 契約: `docs/test-cases/TASK-ASR-001-asr-script-audio-verification.md`
- `TASK-COEIR-001` — COEIROINK adapter（blocked）
  - 契約: `docs/test-cases/TASK-COEIR-001-coeiroink-client-adapter.md`
- `TASK-WORKER-001` — Python worker request dispatch・JSON Lines event（MVP）
  - 契約: `docs/test-cases/TASK-WORKER-001-python-worker-request-and-event-protocol.md`
- `TASK-WORKER-002` — Python worker cancel・timeout・異常終了復旧（MVP）
  - 契約: `docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md`
- `TASK-DESKTOP-001` — Electron/Vue scaffold・main/preload安全境界（MVP）
  - 契約: `docs/test-cases/TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md`
- `TASK-DESKTOP-002` — Electron起動時data/DB/worker bootstrap（MVP）
  - 契約: `docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md`
- `TASK-UI-001` — Project一覧・新規作成画面（MVP）
  - 契約: `docs/test-cases/TASK-UI-001-project-list-and-create-screen.md`
- `TASK-UI-002` — Project workspace・Source登録/レビュー・承認UI（MVP）
  - 契約: `docs/test-cases/TASK-UI-002-source-workspace-review-and-approval.md`
- `TASK-UI-003` — 出力・声設定・試聴画面（MVP）
  - 契約: `docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md`
- `TASK-UI-004` — Job進捗・cancel/retry・成果物画面（MVP）
  - 契約: `docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md`
- `TASK-UI-005` — Renderer共通state・navigation・error・アクセシビリティ（MVP）
  - 契約: `docs/test-cases/TASK-UI-005-renderer-state-routing-errors-and-accessibility.md`
- `TASK-DESKTOP-003` — Desktop最短end-to-end導線（MVP）
  - 契約: `docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md`
- `TASK-MIGRATION-001` — 旧形式・既存client互換adapter（MVP）
  - 契約: `docs/test-cases/TASK-MIGRATION-001-legacy-format-and-client-adapters.md`
- `TASK-E2E-001` — サンプル1章fixture・仕様間受入検証（MVP）
  - 契約: `docs/test-cases/TASK-E2E-001-sample-book-fixtures-and-acceptance.md`
- `TASK-RELEASE-001` — Windows package・runtime同梱・license/privacy/backup（MVP）
  - 契約: `docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md`
- `TASK-RELEASE-002` — 性能・耐障害・最終release受入（MVP）
  - 契約: `docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md`

## 3. 現在の収集状態

test fileの現在の存在件数・欠落件数・pytest collection実測値は
[`CURRENT_STATE.md`](CURRENT_STATE.md)を正本とする。本書は経路と実行方法だけを固定し、
揮発する存在件数・収集件数をここへ重複記載しない。

## 4. 実行前提

- リポジトリrootで実行する。
- 実行前に`git status --short`で既存変更を確認し、未コミット変更を破棄しない。
- 通常テストでは外部API、VOICEVOX、COEIROINK、Tesseract、ffmpeg、ASRへ接続しない。
- Pythonの正式な再現コマンドはDockerを基本とし、Electron/Vitestとローカルruntime疎通はhostで実行する。
- `docs/commands/preflight.md`のテストファイル存在確認が成功してから対象テストへ進む。

```powershell
git status --short
python --version
node --version
npm --version
```

## 5. 対象ファイル

各ファイルの現在の存在有無は[`CURRENT_STATE.md`](CURRENT_STATE.md)を正本とする。
本節はpathの正本のみを示す。

- `electron/renderer/tests/BuildSettings.test.ts`
- `electron/renderer/tests/JobsAndArtifacts.test.ts`
- `electron/renderer/tests/ProjectList.test.ts`
- `electron/renderer/tests/ProjectWorkspace.test.ts`
- `electron/renderer/tests/accessibility.test.ts`
- `electron/renderer/tests/navigation.test.ts`
- `electron/tests/bootstrap.test.ts`
- `electron/tests/build_voice_ipc.test.ts`
- `electron/tests/e2e/mvp-flow.test.ts`
- `electron/tests/job_artifact_ipc.test.ts`
- `electron/tests/main_security.test.ts`
- `electron/tests/packaging_contract.test.ts`
- `electron/tests/preload_contract.test.ts`
- `electron/tests/project_ipc.test.ts`
- `electron/tests/source_approval_ipc.test.ts`
- `electron/tests/worker_manager.test.ts`
- `tests/integration/test_mvp_flow.py`
- `tests/integration/test_sample_book_e2e.py`
- `tests/performance/test_large_sources.py`
- `tests/resilience/test_failure_recovery.py`
- `tests/test_ai_budget.py`
- `tests/test_ai_cache.py`
- `tests/test_ai_client_contract.py`
- `tests/test_ai_routing.py`
- `tests/test_approval_invalidation.py`
- `tests/test_approval_workflow.py`
- `tests/test_artifact_service.py`
- `tests/test_asr_verification.py`
- `tests/test_atomic_file_write.py`
- `tests/test_audio_cache.py`
- `tests/test_audio_packaging.py`
- `tests/test_audio_preview.py`
- `tests/test_audio_synthesis.py`
- `tests/test_audio_thresholds.py`
- `tests/test_audio_validation.py`
- `tests/test_backup_restore.py`
- `tests/test_build_pipeline.py`
- `tests/test_build_request_service.py`
- `tests/test_chapter_spec_schema.py`
- `tests/test_character_profiles.py`
- `tests/test_claim_validation.py`
- `tests/test_claims_pipeline.py`
- `tests/test_coeiroink_adapter.py`
- `tests/test_coeiroink_client.py`
- `tests/test_container_contract.py`
- `tests/test_core_config.py`
- `tests/test_core_errors.py`
- `tests/test_core_logging.py`
- `tests/test_coverage_map.py`
- `tests/test_credit_manifest.py`
- `tests/test_curriculum_pipeline.py`
- `tests/test_database_connection.py`
- `tests/test_domain_models.py`
- `tests/test_domain_validation.py`
- `tests/test_draft_generation.py`
- `tests/test_epub_extraction.py`
- `tests/test_gemini_client.py`
- `tests/test_hashing.py`
- `tests/test_identifiers.py`
- `tests/test_image_ingestion.py`
- `tests/test_image_manifest.py`
- `tests/test_image_preprocessing.py`
- `tests/test_image_quality_flags.py`
- `tests/test_impact_analysis.py`
- `tests/test_initial_schema.py`
- `tests/test_job_lifecycle.py`
- `tests/test_job_queue.py`
- `tests/test_legacy_input_priority.py`
- `tests/test_legacy_migration.py`
- `tests/test_license_manifest.py`
- `tests/test_m4b_output.py`
- `tests/test_material_input_orchestrator.py`
- `tests/test_migration_runner.py`
- `tests/test_narration_transformations.py`
- `tests/test_ocr_client.py`
- `tests/test_ocr_pipeline.py`
- `tests/test_pdf_direct_extraction.py`
- `tests/test_pdf_extraction_fallback.py`
- `tests/test_persistence_paths.py`
- `tests/test_production_manifest.py`
- `tests/test_project_locking.py`
- `tests/test_project_plan_schema.py`
- `tests/test_project_service.py`
- `tests/test_regeneration_plan.py`
- `tests/test_repositories.py`
- `tests/test_rights_gate.py`
- `tests/test_script_schema.py`
- `tests/test_serialization.py`
- `tests/test_source_analysis_pipeline.py`
- `tests/test_source_chunking.py`
- `tests/test_source_manifest.py`
- `tests/test_source_normalization.py`
- `tests/test_source_review_service.py`
- `tests/test_source_service.py`
- `tests/test_source_status_transitions.py`
- `tests/test_stale_job_recovery.py`
- `tests/test_test_environment_contract.py`
- `tests/test_text_ingestion.py`
- `tests/test_tts_client_contract.py`
- `tests/test_tts_registry.py`
- `tests/test_unit_of_work.py`
- `tests/test_verified_script_pipeline.py`
- `tests/test_voice_profiles.py`
- `tests/test_voicevox_adapter.py`
- `tests/test_voicevox_client.py`
- `tests/test_worker_cancellation.py`
- `tests/test_worker_dispatch.py`
- `tests/test_worker_protocol.py`
- `tests/test_worker_runtime_failures.py`

## 6. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/integration/test_mvp_flow.py tests/integration/test_sample_book_e2e.py tests/performance/test_large_sources.py tests/resilience/test_failure_recovery.py tests/test_ai_budget.py tests/test_ai_cache.py tests/test_ai_client_contract.py tests/test_ai_routing.py tests/test_approval_invalidation.py tests/test_approval_workflow.py tests/test_artifact_service.py tests/test_asr_verification.py tests/test_atomic_file_write.py tests/test_audio_cache.py tests/test_audio_packaging.py tests/test_audio_preview.py tests/test_audio_synthesis.py tests/test_audio_thresholds.py tests/test_audio_validation.py tests/test_backup_restore.py tests/test_build_pipeline.py tests/test_build_request_service.py tests/test_chapter_spec_schema.py tests/test_character_profiles.py tests/test_claim_validation.py tests/test_claims_pipeline.py tests/test_coeiroink_adapter.py tests/test_coeiroink_client.py tests/test_container_contract.py tests/test_core_config.py tests/test_core_errors.py tests/test_core_logging.py tests/test_coverage_map.py tests/test_credit_manifest.py tests/test_curriculum_pipeline.py tests/test_database_connection.py tests/test_domain_models.py tests/test_domain_validation.py tests/test_draft_generation.py tests/test_epub_extraction.py tests/test_gemini_client.py tests/test_hashing.py tests/test_identifiers.py tests/test_image_ingestion.py tests/test_image_manifest.py tests/test_image_preprocessing.py tests/test_image_quality_flags.py tests/test_impact_analysis.py tests/test_initial_schema.py tests/test_job_lifecycle.py tests/test_job_queue.py tests/test_legacy_input_priority.py tests/test_legacy_migration.py tests/test_license_manifest.py tests/test_m4b_output.py tests/test_material_input_orchestrator.py tests/test_migration_runner.py tests/test_narration_transformations.py tests/test_ocr_client.py tests/test_ocr_pipeline.py tests/test_pdf_direct_extraction.py tests/test_pdf_extraction_fallback.py tests/test_persistence_paths.py tests/test_production_manifest.py tests/test_project_locking.py tests/test_project_plan_schema.py tests/test_project_service.py tests/test_regeneration_plan.py tests/test_repositories.py tests/test_rights_gate.py tests/test_script_schema.py tests/test_serialization.py tests/test_source_analysis_pipeline.py tests/test_source_chunking.py tests/test_source_manifest.py tests/test_source_normalization.py tests/test_source_review_service.py tests/test_source_service.py tests/test_source_status_transitions.py tests/test_stale_job_recovery.py tests/test_test_environment_contract.py tests/test_text_ingestion.py tests/test_tts_client_contract.py tests/test_tts_registry.py tests/test_unit_of_work.py tests/test_verified_script_pipeline.py tests/test_voice_profiles.py tests/test_voicevox_adapter.py tests/test_voicevox_client.py tests/test_worker_cancellation.py tests/test_worker_dispatch.py tests/test_worker_protocol.py tests/test_worker_runtime_failures.py
```
```powershell
npm run typecheck
```
```powershell
npm test -- electron/renderer/tests/BuildSettings.test.ts electron/renderer/tests/JobsAndArtifacts.test.ts electron/renderer/tests/ProjectList.test.ts electron/renderer/tests/ProjectWorkspace.test.ts electron/renderer/tests/accessibility.test.ts electron/renderer/tests/navigation.test.ts electron/tests/bootstrap.test.ts electron/tests/build_voice_ipc.test.ts electron/tests/e2e/mvp-flow.test.ts electron/tests/job_artifact_ipc.test.ts electron/tests/main_security.test.ts electron/tests/packaging_contract.test.ts electron/tests/preload_contract.test.ts electron/tests/project_ipc.test.ts electron/tests/source_approval_ipc.test.ts electron/tests/worker_manager.test.ts
```

## 7. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/integration/test_mvp_flow.py tests/integration/test_sample_book_e2e.py tests/performance/test_large_sources.py tests/resilience/test_failure_recovery.py tests/test_ai_budget.py tests/test_ai_cache.py tests/test_ai_client_contract.py tests/test_ai_routing.py tests/test_approval_invalidation.py tests/test_approval_workflow.py tests/test_artifact_service.py tests/test_asr_verification.py tests/test_atomic_file_write.py tests/test_audio_cache.py tests/test_audio_packaging.py tests/test_audio_preview.py tests/test_audio_synthesis.py tests/test_audio_thresholds.py tests/test_audio_validation.py tests/test_backup_restore.py tests/test_build_pipeline.py tests/test_build_request_service.py tests/test_chapter_spec_schema.py tests/test_character_profiles.py tests/test_claim_validation.py tests/test_claims_pipeline.py tests/test_coeiroink_adapter.py tests/test_coeiroink_client.py tests/test_container_contract.py tests/test_core_config.py tests/test_core_errors.py tests/test_core_logging.py tests/test_coverage_map.py tests/test_credit_manifest.py tests/test_curriculum_pipeline.py tests/test_database_connection.py tests/test_domain_models.py tests/test_domain_validation.py tests/test_draft_generation.py tests/test_epub_extraction.py tests/test_gemini_client.py tests/test_hashing.py tests/test_identifiers.py tests/test_image_ingestion.py tests/test_image_manifest.py tests/test_image_preprocessing.py tests/test_image_quality_flags.py tests/test_impact_analysis.py tests/test_initial_schema.py tests/test_job_lifecycle.py tests/test_job_queue.py tests/test_legacy_input_priority.py tests/test_legacy_migration.py tests/test_license_manifest.py tests/test_m4b_output.py tests/test_material_input_orchestrator.py tests/test_migration_runner.py tests/test_narration_transformations.py tests/test_ocr_client.py tests/test_ocr_pipeline.py tests/test_pdf_direct_extraction.py tests/test_pdf_extraction_fallback.py tests/test_persistence_paths.py tests/test_production_manifest.py tests/test_project_locking.py tests/test_project_plan_schema.py tests/test_project_service.py tests/test_regeneration_plan.py tests/test_repositories.py tests/test_rights_gate.py tests/test_script_schema.py tests/test_serialization.py tests/test_source_analysis_pipeline.py tests/test_source_chunking.py tests/test_source_manifest.py tests/test_source_normalization.py tests/test_source_review_service.py tests/test_source_service.py tests/test_source_status_transitions.py tests/test_stale_job_recovery.py tests/test_test_environment_contract.py tests/test_text_ingestion.py tests/test_tts_client_contract.py tests/test_tts_registry.py tests/test_unit_of_work.py tests/test_verified_script_pipeline.py tests/test_voice_profiles.py tests/test_voicevox_adapter.py tests/test_voicevox_client.py tests/test_worker_cancellation.py tests/test_worker_dispatch.py tests/test_worker_protocol.py tests/test_worker_runtime_failures.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/integration/test_mvp_flow.py tests/integration/test_sample_book_e2e.py tests/performance/test_large_sources.py tests/resilience/test_failure_recovery.py tests/test_ai_budget.py tests/test_ai_cache.py tests/test_ai_client_contract.py tests/test_ai_routing.py tests/test_approval_invalidation.py tests/test_approval_workflow.py tests/test_artifact_service.py tests/test_asr_verification.py tests/test_atomic_file_write.py tests/test_audio_cache.py tests/test_audio_packaging.py tests/test_audio_preview.py tests/test_audio_synthesis.py tests/test_audio_thresholds.py tests/test_audio_validation.py tests/test_backup_restore.py tests/test_build_pipeline.py tests/test_build_request_service.py tests/test_chapter_spec_schema.py tests/test_character_profiles.py tests/test_claim_validation.py tests/test_claims_pipeline.py tests/test_coeiroink_adapter.py tests/test_coeiroink_client.py tests/test_container_contract.py tests/test_core_config.py tests/test_core_errors.py tests/test_core_logging.py tests/test_coverage_map.py tests/test_credit_manifest.py tests/test_curriculum_pipeline.py tests/test_database_connection.py tests/test_domain_models.py tests/test_domain_validation.py tests/test_draft_generation.py tests/test_epub_extraction.py tests/test_gemini_client.py tests/test_hashing.py tests/test_identifiers.py tests/test_image_ingestion.py tests/test_image_manifest.py tests/test_image_preprocessing.py tests/test_image_quality_flags.py tests/test_impact_analysis.py tests/test_initial_schema.py tests/test_job_lifecycle.py tests/test_job_queue.py tests/test_legacy_input_priority.py tests/test_legacy_migration.py tests/test_license_manifest.py tests/test_m4b_output.py tests/test_material_input_orchestrator.py tests/test_migration_runner.py tests/test_narration_transformations.py tests/test_ocr_client.py tests/test_ocr_pipeline.py tests/test_pdf_direct_extraction.py tests/test_pdf_extraction_fallback.py tests/test_persistence_paths.py tests/test_production_manifest.py tests/test_project_locking.py tests/test_project_plan_schema.py tests/test_project_service.py tests/test_regeneration_plan.py tests/test_repositories.py tests/test_rights_gate.py tests/test_script_schema.py tests/test_serialization.py tests/test_source_analysis_pipeline.py tests/test_source_chunking.py tests/test_source_manifest.py tests/test_source_normalization.py tests/test_source_review_service.py tests/test_source_service.py tests/test_source_status_transitions.py tests/test_stale_job_recovery.py tests/test_test_environment_contract.py tests/test_text_ingestion.py tests/test_tts_client_contract.py tests/test_tts_registry.py tests/test_unit_of_work.py tests/test_verified_script_pipeline.py tests/test_voice_profiles.py tests/test_voicevox_adapter.py tests/test_voicevox_client.py tests/test_worker_cancellation.py tests/test_worker_dispatch.py tests/test_worker_protocol.py tests/test_worker_runtime_failures.py
```
### Vitest
```powershell
npm test -- electron/renderer/tests/BuildSettings.test.ts electron/renderer/tests/JobsAndArtifacts.test.ts electron/renderer/tests/ProjectList.test.ts electron/renderer/tests/ProjectWorkspace.test.ts electron/renderer/tests/accessibility.test.ts electron/renderer/tests/navigation.test.ts electron/tests/bootstrap.test.ts electron/tests/build_voice_ipc.test.ts electron/tests/e2e/mvp-flow.test.ts electron/tests/job_artifact_ipc.test.ts electron/tests/main_security.test.ts electron/tests/packaging_contract.test.ts electron/tests/preload_contract.test.ts electron/tests/project_ipc.test.ts electron/tests/source_approval_ipc.test.ts electron/tests/worker_manager.test.ts
```

## 8. 補助・運用コマンド

### Python構文
```powershell
python -m compileall -q script tests
```
### Python collection
```powershell
python -m pytest --collect-only -q
```
### Python安全全体
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```
### TypeScript型検査
```powershell
npm run typecheck
```
### Vitest collection/実行
```powershell
npm test
```

## 9. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-OCR-001: Tesseract runtime

- connectivity fixture: `tesseract_connectivity_gate`
- 注意: 疎通は--versionと言語一覧。本テストは固定1行画像のみ。
- 必要設定: `TESSERACT_CMD`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_ocr_client.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_ocr_pipeline.py
```

### TASK-AI-001: Gemini API

- connectivity fixture: `gemini_connectivity_gate`
- 注意: 疎通ではmetadata/listのみ。本文生成はliveで極短文1回。
- 必要設定: `GEMINI_API_KEY`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_ai_client_contract.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_gemini_client.py
```

### TASK-VOICEVOX-001: VOICEVOX Engine API

- connectivity fixture: `voicevox_connectivity_gate`
- 注意: 疎通はGET /speakers。本テストは短文のaudio_query→synthesis。
- 必要設定: `VOICEVOX_URL`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_voicevox_client.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_voicevox_adapter.py
```

### TASK-AUDIO-002: ffmpeg/ffprobe runtime

- connectivity fixture: `ffmpeg_connectivity_gate`
- 注意: 疎通はversion確認。本テストは最小fixtureのprobe/measurement。
- 必要設定: `FFMPEG_PATH`, `FFPROBE_PATH`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_audio_validation.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_audio_validation.py
```

### TASK-M4B-001: ffmpeg runtime

- connectivity fixture: `ffmpeg_connectivity_gate`
- 注意: post-MVP。疎通後に最小M4B fixtureだけを生成。
- 必要設定: `FFMPEG_PATH`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_m4b_output.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_m4b_output.py
```

### TASK-ASR-001: ローカルWhisper互換runtime

- connectivity fixture: `asr_connectivity_gate`
- 注意: 疎通はruntime/model読込確認。本テストは数秒の固定WAV。cloud送信禁止。
- 必要設定: `WALKWISE_ASR_ENABLED`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_asr_verification.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_asr_verification.py
```

### TASK-COEIR-001: COEIROINK API

- connectivity fixture: `coeiroink_connectivity_gate`
- 注意: blocked。公式API世代・endpoint確認前はsmoke/liveを実行しない。
- **状態: blocked。公式仕様のevidence gapが解消するまでsmoke/liveコマンドを実行しない。**

### TASK-DESKTOP-002: Python worker subprocess

- connectivity fixture: `worker_connectivity_gate`
- 注意: 疎通はhealth/ping。Project作成などの副作用は行わない。
- 秘密環境変数: なし

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
npm test -- electron/tests/bootstrap.test.ts electron/tests/worker_manager.test.ts
```

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
npm test -- electron/tests/bootstrap.test.ts electron/tests/worker_manager.test.ts
```

### TASK-DESKTOP-003: Desktop統合runtime

- connectivity fixture: `desktop_connectivity_gate`
- 注意: 疎通は起動・preload・DB/worker health。本E2Eで初めてProjectを作成。
- 秘密環境変数: なし

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

### TASK-E2E-001: 任意の実VOICEVOX

- connectivity fixture: `voicevox_connectivity_gate`
- 注意: 通常受入はmock。実VOICEVOXは任意で、疎通後のみ。
- 必要設定: `VOICEVOX_URL`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/integration/test_sample_book_e2e.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/integration/test_sample_book_e2e.py
```

### TASK-RELEASE-001: 配布runtime群

- connectivity fixture: `release_runtime_connectivity_gate`
- 注意: package内のPython/ffmpeg等の存在と起動を確認。実利用者dataは使わない。
- 秘密環境変数: なし

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
npm test -- electron/tests/packaging_contract.test.ts
```

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
npm test -- electron/tests/packaging_contract.test.ts
```


## 10. 全体回帰

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```
```powershell
npm run typecheck
```
```powershell
npm test
```

## 11. 成功条件

- 対象test fileがすべて収集される。
- 未知marker、import error、TypeScript型errorがない。
- 通常テストが外部接続しない。
- STEP3空実装段階では、意図したstrict xfailまたはopt-in skipだけになる。
- Claude Code本実装後は、対象タスクのxfailを解除し、対象テストがpassする。
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない。

## 12. 停止条件

- 契約にあるtest fileが存在しない。
- 疎通確認を行わず実機能テストだけを直接実行しようとしている。
- API key、利用者データ、絶対pathなどの秘密・個人情報がログへ出る。
- `blocked`またはpost-MVPの未承認契約をMVPへ混入させる。
- 承認済み仕様と空実装signatureが矛盾する。

## 13. 実行記録

Claude Codeの完了報告には、少なくとも次を記録する。

```text
実行日時:
対象タスク:
実行コマンド:
収集件数:
pass / fail / xfail / skip:
外部疎通の有無:
外部疎通結果:
未解決事項:
```
