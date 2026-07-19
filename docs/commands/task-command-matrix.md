---
document_type: task_command_matrix
status: review
version: "1.0"
last_updated: "2026-07-19"
---

# タスク・コマンド対応表

| 順序 | Task | Scope | Command documents | Test files |
|---:|---|---|---|---|
| 101 | `TASK-DEV-001` Pythonパッケージ・pytest収集基盤 | MVP | [testing.md](testing.md) | `tests/test_test_environment_contract.py` |
| 102 | `TASK-ENV-001` Docker開発・テスト実行環境 | MVP | [environment.md](environment.md), [testing.md](testing.md) | `tests/test_container_contract.py` |
| 103 | `TASK-CORE-001` 設定・共通エラー・ログ契約 | MVP | [configuration.md](configuration.md), [testing.md](testing.md) | `tests/test_core_config.py`<br>`tests/test_core_errors.py`<br>`tests/test_core_logging.py` |
| 105 | `TASK-FILE-001` ローカルファイル永続化・Project配置・atomic write | MVP | [storage.md](storage.md), [testing.md](testing.md) | `tests/test_persistence_paths.py`<br>`tests/test_atomic_file_write.py`<br>`tests/test_project_locking.py` |
| 106 | `TASK-DOMAIN-001` ドメインモデルと列挙値 | MVP | [data-validation.md](data-validation.md), [testing.md](testing.md) | `tests/test_domain_models.py`<br>`tests/test_domain_validation.py` |
| 107 | `TASK-DB-001` SQLite接続・migration runner・初期schema | MVP | [database.md](database.md), [testing.md](testing.md) | `tests/test_database_connection.py`<br>`tests/test_migration_runner.py`<br>`tests/test_initial_schema.py` |
| 109 | `TASK-PROJECT-001` Project作成・一覧・取得サービス | MVP | [projects.md](projects.md), [testing.md](testing.md) | `tests/test_project_service.py`<br>`tests/test_project_plan_schema.py` |
| 110 | `TASK-SOURCE-001` Source登録・状態管理サービス | MVP | [sources.md](sources.md), [testing.md](testing.md) | `tests/test_source_service.py`<br>`tests/test_source_status_transitions.py` |
| 111 | `TASK-RIGHTS-001` 権利・ライセンス・配布gate | MVP | [rights.md](rights.md), [testing.md](testing.md) | `tests/test_rights_gate.py`<br>`tests/test_credit_manifest.py` |
| 112 | `TASK-BUILD-001` Build Request作成サービス | MVP | [builds.md](builds.md), [testing.md](testing.md) | `tests/test_build_request_service.py` |
| 113 | `TASK-JOB-001` Job状態遷移・FIFO・再試行・stale復旧 | MVP | [jobs.md](jobs.md), [testing.md](testing.md) | `tests/test_job_lifecycle.py`<br>`tests/test_job_queue.py`<br>`tests/test_stale_job_recovery.py` |
| 114 | `TASK-ARTIFACT-001` Artifact登録・version管理 | MVP | [artifacts.md](artifacts.md), [testing.md](testing.md) | `tests/test_artifact_service.py` |
| 115 | `TASK-APPROVAL-001` 4段階承認・差し戻し・無効化 | MVP | [approvals.md](approvals.md), [testing.md](testing.md) | `tests/test_approval_workflow.py`<br>`tests/test_approval_invalidation.py` |
| 116 | `TASK-INGEST-001` 資料入力orchestrator・テキスト入力 | MVP | [source-processing.md](source-processing.md), [testing.md](testing.md) | `tests/test_material_input_orchestrator.py`<br>`tests/test_text_ingestion.py` |
| 117 | `TASK-IMAGE-001` 画像群登録・順序・manifest | MVP | [images.md](images.md), [testing.md](testing.md) | `tests/test_image_ingestion.py`<br>`tests/test_image_manifest.py` |
| 119 | `TASK-PDF-001` PDF直接テキスト抽出 | MVP | [pdf.md](pdf.md), [testing.md](testing.md) | `tests/test_pdf_direct_extraction.py`<br>`tests/test_pdf_extraction_fallback.py` |
| 120 | `TASK-OCR-001` OCR・スキャンPDF処理 | MVP | [ocr.md](ocr.md), [testing.md](testing.md) | `tests/test_ocr_client.py`<br>`tests/test_ocr_pipeline.py` |
| 123 | `TASK-EPUB-001` EPUBテキスト抽出 | post-MVP | [epub.md](epub.md), [testing.md](testing.md) | `tests/test_epub_extraction.py` |
| 124 | `TASK-AI-001` AI共通契約・Gemini adapter | MVP | [ai.md](ai.md), [testing.md](testing.md) | `tests/test_ai_client_contract.py`<br>`tests/test_gemini_client.py` |
| 127 | `TASK-CURRICULUM-001` topic map・curriculum・章仕様生成 | MVP | [content-generation.md](content-generation.md), [testing.md](testing.md) | `tests/test_curriculum_pipeline.py`<br>`tests/test_chapter_spec_schema.py` |
| 128 | `TASK-SCRIPT-001` 原稿segment・章初稿生成 | MVP | [content-generation.md](content-generation.md), [testing.md](testing.md) | `tests/test_script_schema.py`<br>`tests/test_draft_generation.py` |
| 129 | `TASK-CLAIM-001` 技術的主張・出典対応・fact check | MVP | [fact-checking.md](fact-checking.md), [testing.md](testing.md) | `tests/test_claims_pipeline.py`<br>`tests/test_claim_validation.py` |
| 130 | `TASK-PROFILE-001` Character・Voice profile読込と選択 | MVP | [profiles.md](profiles.md), [testing.md](testing.md) | `tests/test_character_profiles.py`<br>`tests/test_voice_profiles.py` |
| 131 | `TASK-NARRATION-001` 分かりやすさ・音声向け・character変換・最終意味検証 | MVP | [content-generation.md](content-generation.md), [testing.md](testing.md) | `tests/test_narration_transformations.py`<br>`tests/test_verified_script_pipeline.py` |
| 132 | `TASK-PIPELINE-001` 変更影響判定・部分再生成計画 | MVP | [regeneration.md](regeneration.md), [testing.md](testing.md) | `tests/test_impact_analysis.py`<br>`tests/test_regeneration_plan.py` |
| 133 | `TASK-TTS-001` TTS共通Protocol・registry・エラー契約 | MVP | [tts.md](tts.md), [testing.md](testing.md) | `tests/test_tts_client_contract.py`<br>`tests/test_tts_registry.py` |
| 134 | `TASK-VOICEVOX-001` VOICEVOX adapter・話者一覧・合成 | MVP | [tts.md](tts.md), [testing.md](testing.md) | `tests/test_voicevox_client.py`<br>`tests/test_voicevox_adapter.py` |
| 135 | `TASK-AUDIO-001` 試聴・segment TTS・WAV cache | MVP | [tts.md](tts.md), [testing.md](testing.md) | `tests/test_audio_synthesis.py`<br>`tests/test_audio_cache.py`<br>`tests/test_audio_preview.py` |
| 138 | `TASK-M4B-001` M4B出力 | post-MVP | [m4b.md](m4b.md), [testing.md](testing.md) | `tests/test_m4b_output.py` |
| 139 | `TASK-ASR-001` ASRによる原稿・音声照合 | post-MVP | [asr.md](asr.md), [testing.md](testing.md) | `tests/test_asr_verification.py` |
| 140 | `TASK-COEIR-001` COEIROINK adapter | blocked | [tts.md](tts.md), [testing.md](testing.md) | `tests/test_coeiroink_client.py`<br>`tests/test_coeiroink_adapter.py` |
| 141 | `TASK-WORKER-001` Python worker request dispatch・JSON Lines event | MVP | [worker.md](worker.md), [testing.md](testing.md) | `tests/test_worker_protocol.py`<br>`tests/test_worker_dispatch.py` |
| 143 | `TASK-DESKTOP-001` Electron/Vue scaffold・main/preload安全境界 | MVP | [desktop.md](desktop.md), [testing.md](testing.md) | `electron/tests/main_security.test.ts`<br>`electron/tests/preload_contract.test.ts` |
| 145 | `TASK-UI-001` Project一覧・新規作成画面 | MVP | [desktop.md](desktop.md), [ui.md](ui.md), [testing.md](testing.md) | `electron/tests/project_ipc.test.ts`<br>`electron/renderer/tests/ProjectList.test.ts` |
| 151 | `TASK-MIGRATION-001` 旧形式・既存client互換adapter | MVP | [migration.md](migration.md), [testing.md](testing.md) | `tests/test_legacy_migration.py`<br>`tests/test_legacy_input_priority.py` |
| 152 | `TASK-E2E-001` サンプル1章fixture・仕様間受入検証 | MVP | [end-to-end.md](end-to-end.md), [testing.md](testing.md) | `tests/integration/test_sample_book_e2e.py` |
| 153 | `TASK-RELEASE-001` Windows package・runtime同梱・license/privacy/backup | MVP | [packaging.md](packaging.md), [backup-restore.md](backup-restore.md), [testing.md](testing.md) | `electron/tests/packaging_contract.test.ts`<br>`tests/test_backup_restore.py`<br>`tests/test_license_manifest.py` |
| 104 | `TASK-CORE-002` 共通ID・canonical hash・YAML/JSON入出力 | MVP | [data-validation.md](data-validation.md), [testing.md](testing.md) | `tests/test_identifiers.py`<br>`tests/test_hashing.py`<br>`tests/test_serialization.py` |
| 108 | `TASK-DB-002` Repository・transaction境界 | MVP | [database.md](database.md), [testing.md](testing.md) | `tests/test_repositories.py`<br>`tests/test_unit_of_work.py` |
| 118 | `TASK-IMAGE-002` 画像前処理・品質flag・見開き分割 | MVP | [images.md](images.md), [testing.md](testing.md) | `tests/test_image_preprocessing.py`<br>`tests/test_image_quality_flags.py` |
| 121 | `TASK-SOURCE-002` 資料正規化・chunk・index・manifest | MVP | [source-processing.md](source-processing.md), [testing.md](testing.md) | `tests/test_source_normalization.py`<br>`tests/test_source_chunking.py`<br>`tests/test_source_manifest.py` |
| 125 | `TASK-AI-002` AIモデルrouting・cache・費用・予算停止 | MVP | [ai.md](ai.md), [testing.md](testing.md) | `tests/test_ai_routing.py`<br>`tests/test_ai_cache.py`<br>`tests/test_ai_budget.py` |
| 136 | `TASK-AUDIO-002` 音声自動検査・provisional閾値 | MVP | [audio-validation.md](audio-validation.md), [testing.md](testing.md) | `tests/test_audio_validation.py`<br>`tests/test_audio_thresholds.py` |
| 142 | `TASK-WORKER-002` Python worker cancel・timeout・異常終了復旧 | MVP | [worker.md](worker.md), [testing.md](testing.md) | `tests/test_worker_cancellation.py`<br>`tests/test_worker_runtime_failures.py` |
| 144 | `TASK-DESKTOP-002` Electron起動時data/DB/worker bootstrap | MVP | [desktop.md](desktop.md), [database.md](database.md), [testing.md](testing.md) | `electron/tests/bootstrap.test.ts`<br>`electron/tests/worker_manager.test.ts` |
| 146 | `TASK-UI-002` Project workspace・Source登録/レビュー・承認UI | MVP | [ui.md](ui.md), [testing.md](testing.md) | `electron/tests/source_approval_ipc.test.ts`<br>`electron/renderer/tests/ProjectWorkspace.test.ts` |
| 154 | `TASK-RELEASE-002` 性能・耐障害・最終release受入 | MVP | [performance.md](performance.md), [release.md](release.md), [testing.md](testing.md) | `tests/performance/test_large_sources.py`<br>`tests/resilience/test_failure_recovery.py` |
| 122 | `TASK-SOURCE-003` 資料レビュー・修正差分・再処理 | MVP | [source-review.md](source-review.md), [testing.md](testing.md) | `tests/test_source_review_service.py` |
| 126 | `TASK-AI-003` source summary・topic index・coverage map | MVP | [content-generation.md](content-generation.md), [testing.md](testing.md) | `tests/test_source_analysis_pipeline.py`<br>`tests/test_coverage_map.py` |
| 137 | `TASK-AUDIO-003` 章MP3・text成果物・manifest・Build orchestration | MVP | [builds.md](builds.md), [audio-packaging.md](audio-packaging.md), [testing.md](testing.md) | `tests/test_audio_packaging.py`<br>`tests/test_build_pipeline.py`<br>`tests/test_production_manifest.py` |
| 147 | `TASK-UI-003` 出力・声設定・試聴画面 | MVP | [ui.md](ui.md), [tts.md](tts.md), [testing.md](testing.md) | `electron/tests/build_voice_ipc.test.ts`<br>`electron/renderer/tests/BuildSettings.test.ts` |
| 150 | `TASK-DESKTOP-003` Desktop最短end-to-end導線 | MVP | [end-to-end.md](end-to-end.md), [testing.md](testing.md) | `tests/integration/test_mvp_flow.py`<br>`electron/tests/e2e/mvp-flow.test.ts` |
| 148 | `TASK-UI-004` Job進捗・cancel/retry・成果物画面 | MVP | [ui.md](ui.md), [testing.md](testing.md) | `electron/tests/job_artifact_ipc.test.ts`<br>`electron/renderer/tests/JobsAndArtifacts.test.ts` |
| 149 | `TASK-UI-005` Renderer共通state・navigation・error・アクセシビリティ | MVP | [ui.md](ui.md), [testing.md](testing.md) | `electron/renderer/tests/navigation.test.ts`<br>`electron/renderer/tests/accessibility.test.ts` |
