---
document_type: command_index
status: review
version: "1.0"
last_updated: "2026-07-19"
---

# コマンド文書一覧

## 共通

- [README](README.md)
- [preflight](preflight.md)
- [外部疎通・実機能テスト](external-connectivity.md)
- [タスク・コマンド対応表](task-command-matrix.md)
- [最新ダンプの状態](CURRENT_STATE.md)

## 分野別

| 文書 | 目的 | 関連タスク |
|---|---|---|
| [ai.md](ai.md) | AI共通契約、Gemini adapter、routing、cache、budgetの検証 | `TASK-AI-001`, `TASK-AI-002` |
| [approvals.md](approvals.md) | 4段階承認、差し戻し、revision変更時の無効化検証 | `TASK-APPROVAL-001` |
| [artifacts.md](artifacts.md) | Artifact登録、追記専用version、一覧取得の検証 | `TASK-ARTIFACT-001` |
| [asr.md](asr.md) | ローカルASR runtimeと原稿・音声照合の検証 | `TASK-ASR-001` |
| [audio-packaging.md](audio-packaging.md) | 章MP3、verified text、production manifest、build orchestrationの検証 | `TASK-AUDIO-003` |
| [audio-validation.md](audio-validation.md) | 音声形式・測定・provisional閾値・判定の検証 | `TASK-AUDIO-002` |
| [backup-restore.md](backup-restore.md) | アプリデータ、SQLite、Project成果物のbackup/restore検証 | `TASK-RELEASE-001` |
| [builds.md](builds.md) | Build Requestと制作パイプラインの検証 | `TASK-BUILD-001`, `TASK-AUDIO-003` |
| [configuration.md](configuration.md) | 設定、共通error、秘密値除外、loggingの検証 | `TASK-CORE-001` |
| [content-generation.md](content-generation.md) | 資料分析、coverage、curriculum、原稿、narration変換の検証 | `TASK-AI-003`, `TASK-CURRICULUM-001`, `TASK-SCRIPT-001`, `TASK-NARRATION-001` |
| [data-validation.md](data-validation.md) | ID、hash、serialization、domain model、validationの検証 | `TASK-CORE-002`, `TASK-DOMAIN-001` |
| [database.md](database.md) | SQLite接続、migration、schema、repository、transactionの検証 | `TASK-DB-001`, `TASK-DB-002`, `TASK-DESKTOP-002` |
| [desktop.md](desktop.md) | Electron main/preload/renderer、bootstrap、安全なIPC境界の検証 | `TASK-DESKTOP-001`, `TASK-DESKTOP-002`, `TASK-UI-001` |
| [end-to-end.md](end-to-end.md) | mock中心のMVP導線とsample-book受入検証 | `TASK-DESKTOP-003`, `TASK-E2E-001` |
| [environment.md](environment.md) | Python/Docker/Node開発・テスト環境の検証 | `TASK-ENV-001` |
| [epub.md](epub.md) | post-MVPのEPUB抽出検証 | `TASK-EPUB-001` |
| [fact-checking.md](fact-checking.md) | claim、evidence、source参照、fact-checkingの検証 | `TASK-CLAIM-001` |
| [images.md](images.md) | 画像登録、順序manifest、前処理、品質flagの検証 | `TASK-IMAGE-001`, `TASK-IMAGE-002` |
| [jobs.md](jobs.md) | Job状態遷移、queue、cancel、retry、stale recoveryの検証 | `TASK-JOB-001` |
| [m4b.md](m4b.md) | post-MVPのM4B生成とffmpeg連携検証 | `TASK-M4B-001` |
| [migration.md](migration.md) | 旧形式の読込、優先順位、変換reportの検証 | `TASK-MIGRATION-001` |
| [ocr.md](ocr.md) | Tesseract疎通、OCR、スキャンPDF処理の検証 | `TASK-OCR-001` |
| [packaging.md](packaging.md) | Windows package、runtime、license、privacyの検証 | `TASK-RELEASE-001` |
| [pdf.md](pdf.md) | PDF直接抽出とOCR fallback判定の検証 | `TASK-PDF-001` |
| [performance.md](performance.md) | 大規模資料、障害注入、回復性の専用検証 | `TASK-RELEASE-002` |
| [profiles.md](profiles.md) | character/voice profile schemaと既定値境界の検証 | `TASK-PROFILE-001` |
| [projects.md](projects.md) | Project作成、plan YAML、一覧・取得の検証 | `TASK-PROJECT-001` |
| [regeneration.md](regeneration.md) | 依存impact分析と部分再生成計画の検証 | `TASK-PIPELINE-001` |
| [release.md](release.md) | MVP release acceptance、性能、回復性、配布前確認 | `TASK-RELEASE-002` |
| [rights.md](rights.md) | 権利、利用目的、配布gate、credit manifestの検証 | `TASK-RIGHTS-001` |
| [source-processing.md](source-processing.md) | text入力、正規化、chunk、source manifestの検証 | `TASK-INGEST-001`, `TASK-SOURCE-002` |
| [source-review.md](source-review.md) | 抽出結果の人間修正、revision、再承認要求の検証 | `TASK-SOURCE-003` |
| [sources.md](sources.md) | Source登録、immutable原本、状態遷移の検証 | `TASK-SOURCE-001` |
| [storage.md](storage.md) | Project配置、相対path、atomic write、lockの検証 | `TASK-FILE-001` |
| [testing.md](testing.md) | 全テスト層、収集、対象実行、全体実行、外部接続gateの正本 | `TASK-DEV-001`, `TASK-ENV-001`, `TASK-CORE-001`, `TASK-CORE-002`, `TASK-FILE-001`, `TASK-DOMAIN-001`, `TASK-DB-001`, `TASK-DB-002`, `TASK-PROJECT-001`, `TASK-SOURCE-001`, `TASK-RIGHTS-001`, `TASK-BUILD-001`, `TASK-JOB-001`, `TASK-ARTIFACT-001`, `TASK-APPROVAL-001`, `TASK-INGEST-001`, `TASK-IMAGE-001`, `TASK-IMAGE-002`, `TASK-PDF-001`, `TASK-OCR-001`, `TASK-SOURCE-002`, `TASK-SOURCE-003`, `TASK-EPUB-001`, `TASK-AI-001`, `TASK-AI-002`, `TASK-AI-003`, `TASK-CURRICULUM-001`, `TASK-SCRIPT-001`, `TASK-CLAIM-001`, `TASK-PROFILE-001`, `TASK-NARRATION-001`, `TASK-PIPELINE-001`, `TASK-TTS-001`, `TASK-VOICEVOX-001`, `TASK-AUDIO-001`, `TASK-AUDIO-002`, `TASK-AUDIO-003`, `TASK-M4B-001`, `TASK-ASR-001`, `TASK-COEIR-001`, `TASK-WORKER-001`, `TASK-WORKER-002`, `TASK-DESKTOP-001`, `TASK-DESKTOP-002`, `TASK-UI-001`, `TASK-UI-002`, `TASK-UI-003`, `TASK-UI-004`, `TASK-UI-005`, `TASK-DESKTOP-003`, `TASK-MIGRATION-001`, `TASK-E2E-001`, `TASK-RELEASE-001`, `TASK-RELEASE-002` |
| [tts.md](tts.md) | TTS共通契約、VOICEVOX、preview/cache、将来engine境界の検証 | `TASK-TTS-001`, `TASK-VOICEVOX-001`, `TASK-AUDIO-001`, `TASK-COEIR-001`, `TASK-UI-003` |
| [ui.md](ui.md) | 5画面、navigation、状態表示、accessibility、IPC連携の検証 | `TASK-UI-001`, `TASK-UI-002`, `TASK-UI-003`, `TASK-UI-004`, `TASK-UI-005` |
| [worker.md](worker.md) | Python worker JSON Lines、dispatch、cancel、timeout、recoveryの検証 | `TASK-WORKER-001`, `TASK-WORKER-002` |
