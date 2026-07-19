---
document_type: claude_code_execution_order
status: review
version: "1.0"
last_updated: "2026-07-19"
---

# 実装順序と依存関係

数字順は依存関係を満たす。並列化は、相互依存がなく変更ファイルが重複しない場合だけ人間承認のうえで行う。

## 0. 開発基盤

101. [`TASK-DEV-001`](TASK-DEV-001-repository-and-test-baseline.md) — Pythonパッケージ・pytest収集基盤（依存: なし）
102. [`TASK-ENV-001`](TASK-ENV-001-docker-development-and-test-environment.md) — Docker開発・テスト実行環境（依存: `TASK-DEV-001`）
103. [`TASK-CORE-001`](TASK-CORE-001-configuration-errors-and-logging.md) — 設定・共通エラー・ログ契約（依存: `TASK-DEV-001`）
104. [`TASK-CORE-002`](TASK-CORE-002-identifiers-hashing-and-structured-files.md) — 共通ID・canonical hash・YAML/JSON入出力（依存: `TASK-DEV-001`, `TASK-CORE-001`）
105. [`TASK-FILE-001`](TASK-FILE-001-local-file-persistence-and-project-layout.md) — ローカルファイル永続化・Project配置・atomic write（依存: `TASK-CORE-001`, `TASK-CORE-002`）
106. [`TASK-DOMAIN-001`](TASK-DOMAIN-001-domain-entities-and-validation.md) — ドメインモデルと列挙値（依存: `TASK-CORE-002`）

## 1. 永続化と業務サービス

107. [`TASK-DB-001`](TASK-DB-001-sqlite-migrations-and-initial-schema.md) — SQLite接続・migration runner・初期schema（依存: `TASK-ENV-001`, `TASK-FILE-001`, `TASK-DOMAIN-001`）
108. [`TASK-DB-002`](TASK-DB-002-repositories-and-unit-of-work.md) — Repository・transaction境界（依存: `TASK-DB-001`）
109. [`TASK-PROJECT-001`](TASK-PROJECT-001-project-application-service.md) — Project作成・一覧・取得サービス（依存: `TASK-DB-002`, `TASK-FILE-001`）
110. [`TASK-SOURCE-001`](TASK-SOURCE-001-source-metadata-service.md) — Source登録・状態管理サービス（依存: `TASK-DB-002`, `TASK-FILE-001`, `TASK-PROJECT-001`）
111. [`TASK-RIGHTS-001`](TASK-RIGHTS-001-rights-license-and-distribution-gate.md) — 権利・ライセンス・配布gate（依存: `TASK-SOURCE-001`）
112. [`TASK-BUILD-001`](TASK-BUILD-001-build-request-service.md) — Build Request作成サービス（依存: `TASK-DB-002`, `TASK-PROJECT-001`）
113. [`TASK-JOB-001`](TASK-JOB-001-job-lifecycle-queue-and-recovery.md) — Job状態遷移・FIFO・再試行・stale復旧（依存: `TASK-BUILD-001`, `TASK-DB-002`）
114. [`TASK-ARTIFACT-001`](TASK-ARTIFACT-001-artifact-registry-and-versioning.md) — Artifact登録・version管理（依存: `TASK-JOB-001`, `TASK-FILE-001`, `TASK-DB-002`）
115. [`TASK-APPROVAL-001`](TASK-APPROVAL-001-approval-workflow-and-invalidation.md) — 4段階承認・差し戻し・無効化（依存: `TASK-PROJECT-001`, `TASK-SOURCE-001`, `TASK-FILE-001`）

## 2. 資料入力

116. [`TASK-INGEST-001`](TASK-INGEST-001-material-input-orchestrator-and-text.md) — 資料入力orchestrator・テキスト入力（依存: `TASK-SOURCE-001`, `TASK-RIGHTS-001`, `TASK-JOB-001`）
117. [`TASK-IMAGE-001`](TASK-IMAGE-001-image-material-registration-and-manifest.md) — 画像群登録・順序・manifest（依存: `TASK-INGEST-001`）
118. [`TASK-IMAGE-002`](TASK-IMAGE-002-image-preprocessing-and-quality-review.md) — 画像前処理・品質flag・見開き分割（依存: `TASK-IMAGE-001`）
119. [`TASK-PDF-001`](TASK-PDF-001-pdf-direct-text-extraction.md) — PDF直接テキスト抽出（依存: `TASK-INGEST-001`）
120. [`TASK-OCR-001`](TASK-OCR-001-ocr-and-scanned-pdf-processing.md) — OCR・スキャンPDF処理（依存: `TASK-IMAGE-002`, `TASK-PDF-001`）
121. [`TASK-SOURCE-002`](TASK-SOURCE-002-source-normalization-chunking-and-index.md) — 資料正規化・chunk・index・manifest（依存: `TASK-INGEST-001`, `TASK-PDF-001`, `TASK-OCR-001`）
122. [`TASK-SOURCE-003`](TASK-SOURCE-003-source-review-and-manual-correction.md) — 資料レビュー・修正差分・再処理（依存: `TASK-SOURCE-002`, `TASK-SOURCE-001`）
123. [`TASK-EPUB-001`](TASK-EPUB-001-epub-text-extraction.md) — EPUBテキスト抽出（依存: `TASK-INGEST-001`, `TASK-SOURCE-002`） — **MVP後まで保留**

## 3. 教材生成AI

124. [`TASK-AI-001`](TASK-AI-001-ai-client-contract-and-gemini-adapter.md) — AI共通契約・Gemini adapter（依存: `TASK-CORE-001`, `TASK-CORE-002`）
125. [`TASK-AI-002`](TASK-AI-002-ai-routing-cost-cache-and-budget.md) — AIモデルrouting・cache・費用・予算停止（依存: `TASK-AI-001`, `TASK-SOURCE-002`）
126. [`TASK-AI-003`](TASK-AI-003-source-analysis-and-coverage.md) — source summary・topic index・coverage map（依存: `TASK-AI-002`, `TASK-SOURCE-002`）
127. [`TASK-CURRICULUM-001`](TASK-CURRICULUM-001-curriculum-and-chapter-spec-generation.md) — topic map・curriculum・章仕様生成（依存: `TASK-AI-003`, `TASK-APPROVAL-001`）
128. [`TASK-SCRIPT-001`](TASK-SCRIPT-001-script-segments-and-draft-generation.md) — 原稿segment・章初稿生成（依存: `TASK-CURRICULUM-001`, `TASK-AI-002`）
129. [`TASK-CLAIM-001`](TASK-CLAIM-001-claims-evidence-and-fact-checking.md) — 技術的主張・出典対応・fact check（依存: `TASK-SCRIPT-001`, `TASK-AI-002`, `TASK-SOURCE-002`）
130. [`TASK-PROFILE-001`](TASK-PROFILE-001-character-and-voice-profiles.md) — Character・Voice profile読込と選択（依存: `TASK-CORE-002`）
131. [`TASK-NARRATION-001`](TASK-NARRATION-001-narration-transformations-and-verified-script.md) — 分かりやすさ・音声向け・character変換・最終意味検証（依存: `TASK-CLAIM-001`, `TASK-PROFILE-001`, `TASK-APPROVAL-001`）
132. [`TASK-PIPELINE-001`](TASK-PIPELINE-001-dependency-impact-and-partial-regeneration.md) — 変更影響判定・部分再生成計画（依存: `TASK-NARRATION-001`, `TASK-APPROVAL-001`, `TASK-ARTIFACT-001`）

## 4. TTSと成果物

133. [`TASK-TTS-001`](TASK-TTS-001-tts-client-interface-and-registry.md) — TTS共通Protocol・registry・エラー契約（依存: `TASK-PROFILE-001`, `TASK-CORE-001`）
134. [`TASK-VOICEVOX-001`](TASK-VOICEVOX-001-voicevox-client-adapter.md) — VOICEVOX adapter・話者一覧・合成（依存: `TASK-TTS-001`）
135. [`TASK-AUDIO-001`](TASK-AUDIO-001-preview-and-segment-tts-cache.md) — 試聴・segment TTS・WAV cache（依存: `TASK-VOICEVOX-001`, `TASK-NARRATION-001`, `TASK-PIPELINE-001`）
136. [`TASK-AUDIO-002`](TASK-AUDIO-002-audio-validation.md) — 音声自動検査・provisional閾値（依存: `TASK-AUDIO-001`）
137. [`TASK-AUDIO-003`](TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md) — 章MP3・text成果物・manifest・Build orchestration（依存: `TASK-AUDIO-002`, `TASK-ARTIFACT-001`, `TASK-JOB-001`, `TASK-BUILD-001`）
138. [`TASK-M4B-001`](TASK-M4B-001-m4b-output.md) — M4B出力（依存: `TASK-AUDIO-003`） — **MVP後まで保留**
139. [`TASK-ASR-001`](TASK-ASR-001-asr-script-audio-verification.md) — ASRによる原稿・音声照合（依存: `TASK-AUDIO-003`） — **MVP後まで保留**
140. [`TASK-COEIR-001`](TASK-COEIR-001-coeiroink-client-adapter.md) — COEIROINK adapter（依存: `TASK-TTS-001`, `TASK-PROFILE-001`） — **blocked解除まで実行禁止**

## 5. Workerとデスクトップ

141. [`TASK-WORKER-001`](TASK-WORKER-001-python-worker-request-and-event-protocol.md) — Python worker request dispatch・JSON Lines event（依存: `TASK-JOB-001`, `TASK-AUDIO-003`, `TASK-AI-003`）
142. [`TASK-WORKER-002`](TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md) — Python worker cancel・timeout・異常終了復旧（依存: `TASK-WORKER-001`, `TASK-JOB-001`）
143. [`TASK-DESKTOP-001`](TASK-DESKTOP-001-electron-vue-scaffold-and-ipc-security.md) — Electron/Vue scaffold・main/preload安全境界（依存: `TASK-ENV-001`）
144. [`TASK-DESKTOP-002`](TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md) — Electron起動時data/DB/worker bootstrap（依存: `TASK-DESKTOP-001`, `TASK-DB-001`, `TASK-WORKER-002`）
145. [`TASK-UI-001`](TASK-UI-001-project-list-and-create-screen.md) — Project一覧・新規作成画面（依存: `TASK-DESKTOP-002`, `TASK-PROJECT-001`）
146. [`TASK-UI-002`](TASK-UI-002-source-workspace-review-and-approval.md) — Project workspace・Source登録/レビュー・承認UI（依存: `TASK-DESKTOP-002`, `TASK-SOURCE-003`, `TASK-APPROVAL-001`）
147. [`TASK-UI-003`](TASK-UI-003-build-settings-and-voice-preview-screen.md) — 出力・声設定・試聴画面（依存: `TASK-DESKTOP-002`, `TASK-BUILD-001`, `TASK-AUDIO-001`）
148. [`TASK-UI-004`](TASK-UI-004-job-progress-and-artifacts-screens.md) — Job進捗・cancel/retry・成果物画面（依存: `TASK-DESKTOP-002`, `TASK-JOB-001`, `TASK-ARTIFACT-001`）
149. [`TASK-UI-005`](TASK-UI-005-renderer-state-routing-errors-and-accessibility.md) — Renderer共通state・navigation・error・アクセシビリティ（依存: `TASK-UI-001`, `TASK-UI-002`, `TASK-UI-003`, `TASK-UI-004`）
150. [`TASK-DESKTOP-003`](TASK-DESKTOP-003-desktop-end-to-end-integration.md) — Desktop最短end-to-end導線（依存: `TASK-UI-005`, `TASK-WORKER-002`, `TASK-AUDIO-003`）

## 6. 移行・品質・配布

151. [`TASK-MIGRATION-001`](TASK-MIGRATION-001-legacy-format-and-client-adapters.md) — 旧形式・既存client互換adapter（依存: `TASK-CORE-002`, `TASK-SCRIPT-001`, `TASK-VOICEVOX-001`）
152. [`TASK-E2E-001`](TASK-E2E-001-sample-book-fixtures-and-acceptance.md) — サンプル1章fixture・仕様間受入検証（依存: `TASK-DESKTOP-003`, `TASK-MIGRATION-001`）
153. [`TASK-RELEASE-001`](TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md) — Windows package・runtime同梱・license/privacy/backup（依存: `TASK-DESKTOP-003`, `TASK-ENV-001`, `TASK-RIGHTS-001`）
154. [`TASK-RELEASE-002`](TASK-RELEASE-002-performance-resilience-and-release-acceptance.md) — 性能・耐障害・最終release受入（依存: `TASK-E2E-001`, `TASK-RELEASE-001`）
