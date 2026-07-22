---
document_type: overnight_progress_log
status: in_progress
last_updated: "2026-07-22"
---

# 夜間自律実行 進捗ログ

開始時点: `TASK-DEV-001`は実装済み・pass済み(別セッションで完了)。
本ログはPhase単位で進捗を追記する。降順ではなく実行順に追記する。

## 開始時Repository状態

- 契約上のtest file: 109/109存在
- pytest collection: 454
- 完了タスク: TASK-DEV-001のみ(10/10 case pass)
- 残りタスク: 53件(STEP3/STEP4空実装のまま)

(以下、Phaseごとに追記)

## Phase1: 開発基盤・Core・DB

### TASK-ENV-001 完了

- 対象: `tests/test_container_contract.py`(9 case)
- Red確認: `.dockerignore`に`dumps`/`release`/`.pytest_cache`等が未登録、
  `docker-compose.yml`に`test-live` serviceが未定義の状態で2 failed(TC-02, TC-04)、
  7 passedを確認(production未実装起因、import/構文errorではない)。
- production実装: `docker-compose.yml`へ`test-live` service追加(host環境変数を
  `${VAR:-default}`で明示的にpass-through、既定は無効/空)。`.dockerignore`へ
  `dumps`, `audio_book_creation_dump_*.txt`, `release`, `.pytest_cache`を追加
  (repo rootに実在する`.env`と`dumps/`(4MB超のダンプ含む)がbuild contextへ
  入らないことを確認)。`Dockerfile`はコメント整理のみ(機能変更なし)。
- 対象テスト結果: 9 passed(`docker compose build test`実施、`docker compose run --rm test`で
  454件収集を実機確認)。
- 文書修正: `docs/commands/environment.md`(担当分)の揮発性欠落注記を除去。
- 備考: 初回`docker compose build`でDocker側の一時的なsnapshot取得エラーが発生したが、
  再実行で解消(production/testの契約とは無関係な環境側の一過性事象)。

### TASK-CORE-001 完了

- 対象: `tests/test_core_config.py`(3 case), `tests/test_core_errors.py`(3 case),
  `tests/test_core_logging.py`(2 case)
- Red確認: `python -m pytest -ra tests/test_core_config.py tests/test_core_errors.py
  tests/test_core_logging.py` → 8 failed(`AppConfig.load`未定義、`ErrorCode`の値未定義、
  `configure_logging`が`NotImplementedError`)。import/構文errorではない。
- production実装: `script/core/errors.py`(`ErrorCode` enum, `AppError.to_public_dict()`)、
  `script/core/config.py`(`AppConfig.load`優先順位解決+必須key検証)、
  `script/core/logging.py`(UTC ISO8601 timestamp、正規表現による秘密値redaction)。
  [[implementation_assumptions.md]]に3件の仮定を記録。
- 対象テスト結果: 8 passed。
- 文書修正: `docs/commands/configuration.md`(担当分)。

### TASK-CORE-002 完了

- 対象: `tests/test_identifiers.py`(3 case), `tests/test_hashing.py`(3 case),
  `tests/test_serialization.py`(2 case)
- Red確認: 8 failed(`canonical_sha256`/`validate_identifier`等が`NotImplementedError`、
  `load_yaml`/`dump_yaml`/`load_json`が引数0個のplaceholderで`TypeError`)。
- production実装: `script/core/identifiers.py`(`validate_identifier`,
  `normalize_unit_id`)、`script/core/hashing.py`(`canonical_sha256`: NFC正規化、
  CRLF→LF、key順ソート、除外key対応)、`script/core/serialization.py`
  (`load_yaml/load_json/dump_yaml/dump_json`、schema_version majorチェック+
  minor警告)。新規依存として`requirements.txt`へ`pyyaml==6.0.2`を追加し、
  host環境へも導入した。[[implementation_assumptions.md]]に4件の仮定を記録。
- 対象テスト結果: 8 passed。
- 文書修正: `docs/commands/data-validation.md`(担当分。domain側は
  `TASK-DOMAIN-001`で別途更新)。

### TASK-FILE-001 完了

- 対象: `tests/test_persistence_paths.py`(3 case), `tests/test_atomic_file_write.py`
  (3 case), `tests/test_project_locking.py`(3 case)
- Red確認: 9 failed(`atomic_write_bytes`/`copy_immutable`/`ProjectLock.acquire`が
  `NotImplementedError`、`ProjectPaths.for_root`が旧instance-method placeholderで
  `TypeError`)。
- production実装: `script/persistence/paths.py`(`ProjectPaths.for_root`
  classmethod化、`resolve_relative`/`to_relative_str`によるroot escape・絶対path
  拒否)、`script/persistence/files.py`(`atomic_write_bytes`: 同volume一時ファイル
  →`os.replace`、`.bak`backup、失敗時cleanup、`copy_immutable`: SHA-256付き
  immutableコピー)、`script/persistence/locking.py`(`ProjectLock.acquire`:
  `O_CREAT|O_EXCL`による排他lock)。[[implementation_assumptions.md]]に2件の
  仮定を記録。
- 対象テスト結果: 9 passed。
- 文書修正: `docs/commands/storage.md`(担当分)。

### TASK-DOMAIN-001 完了

- 対象: `tests/test_domain_models.py`(5 case), `tests/test_domain_validation.py`(4 case)
- Red確認: 9 failed(placeholder dataclassの`__init__`signature不一致による
  `AttributeError`/`TypeError`、`canonicalize_output_formats`等の`NotImplementedError`)。
- production実装: `script/domain/enums.py`(5 enum、docs/dbのcolumn定義に基づく
  列挙値)、`script/domain/validation.py`(`canonicalize_output_formats`:
  mp3→text canonical order、空/未知/重複拒否。`validate_build_request`:
  mp3時のvoice必須。非公開`_assert_relative_path`)、`script/domain/models.py`
  (frozen dataclass 5種、path系フィールドのrelative検証、BuildRequestの
  自動canonicalize)。[[implementation_assumptions.md]]に2件の仮定を記録。
- 対象テスト結果: 9 passed。
- 文書修正: `documentation_repair_ownership`は空(担当文書なし)。
  `docs/commands/data-validation.md`の域内記述(domain側)を実装状況に合わせて更新。

### TASK-DB-001 完了

- 対象: `tests/test_database_connection.py`(4 case), `tests/test_migration_runner.py`
  (3 case), `tests/test_initial_schema.py`(3 case)
- Red確認: 10 failed(`connect_database`/`MigrationRunner.apply_all`等が
  `NotImplementedError`)。
- production実装: `script/persistence/sql/0001_initial.sql`(schema_migrations +
  5製品ドメインテーブル、FK、CHECK、index)、`script/persistence/database.py`
  (`connect_database`: `PRAGMA foreign_keys=ON`、`sqlite3.Row` factory)、
  `script/persistence/migrations.py`(`MigrationRunner.apply_all`: 発見・順序検証・
  適用・checksum記録・任意backup、`verify_applied_checksums`: 改変検出)。
  [[implementation_assumptions.md]]に2件の仮定を記録。
- 対象テスト結果: 10 passed。
- 文書修正: `docs/commands/database.md`(担当分。repository側は`TASK-DB-002`で
  別途更新)。

### TASK-DB-002 完了

- 対象: `tests/test_repositories.py`(4 case), `tests/test_unit_of_work.py`(4 case)
- Red確認: placeholder `SqliteUnitOfWork.__init__(self, **data)`/`XxxRepository.__init__`
  が想定引数(`connection`)を受け付けずTypeErrorで8 failed。
- production実装: `script/persistence/repositories.py`(5 Repository:
  Project/Source/BuildRequest/Job/Artifactそれぞれinsert/find/list/update、
  Artifactのみupdateを拒否。`map_integrity_error`: FK/UNIQUE/CHECK違反の
  分類変換)、`script/persistence/unit_of_work.py`(`SqliteUnitOfWork`:
  5 Repositoryを共有接続へ束ね、`with`終了時にcommit、例外時rollback)。
  重複していた独自`AppError`定義を`script.core.errors.AppError`利用へ統一。
  [[implementation_assumptions.md]]に3件の仮定を記録。
- 対象テスト結果: 8 passed。
- 文書修正: `documentation_repair_ownership`は空。`docs/commands/database.md`の
  域内記述(repository側)を実装状況に合わせて更新。

## Phase1完了

`TASK-DEV-001`(別セッション)に加え、`TASK-ENV-001`, `TASK-CORE-001`,
`TASK-CORE-002`, `TASK-FILE-001`, `TASK-DOMAIN-001`, `TASK-DB-001`, `TASK-DB-002`の
7タスクを本セッションで実装完了。Phase1(開発基盤・Core・DB)は完了。

### Phase1全体回帰結果

- `python -m compileall -q script tests` → 成功
- `python -m pytest --collect-only -q` → 454件収集、未知marker警告なし
- `python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"`
  → **71 passed, 23 deselected, 360 xfailed**、failed/error 0
  (完了8タスク分のcase数合計: 10+9+8+8+9+9+10+8 = 71)
- `npm run typecheck` → 成功、error 0件
- `npm test -- --run` → 16 test files / 76 tests、すべてpassed
- 外部接続: 0
- NotImplementedError残数: Phase1対象ファイル(`script/core/*`, `script/persistence/*`,
  `script/domain/*`, `Dockerfile`, `docker-compose.yml`, `.dockerignore`)には残っていない。
- 完了タスク: 8 / 54。残タスク: 46。

## Phase2: Project・Source・Build・Job

### TASK-PROJECT-001 完了

- 対象: `tests/test_project_service.py`(4 case), `tests/test_project_plan_schema.py`(3 case)
- Red確認: `ProjectPlan`/`ProjectService`のplaceholderが`NotImplementedError`または
  signature不一致で7 failed。
- production実装: `script/schemas/project_plan.py`(`ProjectPlan.from_mapping/
  to_mapping/validate`: 必須15項目、planning_stage/source_strategy値検証、
  review_pending・approved時の章/learning_outcomes/4段階承認必須)、
  `script/services/projects.py`(`ProjectService.create/list_active/get`:
  Project root+plan file+DB行を1操作で作成、失敗時plan file cleanup、
  事前重複チェックで既存正常成果物を保護)。
  横断バグとして`script/core/serialization.py`の`dump_yaml/dump_json`に
  親ディレクトリ自動作成を追加(既存TASK-CORE-002テストでは検出されなかった
  欠陥、[[implementation_assumptions.md]]参照)。
- 対象テスト結果: 7 passed。全体回帰再実行で78 passed(regressionなし)を確認。
- 文書修正: `docs/commands/projects.md`(担当分)。

### TASK-SOURCE-001 完了

- 対象: `tests/test_source_service.py`(4 case), `tests/test_source_status_transitions.py`
  (4 case)
- Red確認: 8 failed(`SourceMetadata.from_file`/`SourceService.register`等が
  `NotImplementedError`)。
- production実装: `script/schemas/source_metadata.py`(`SourceMetadata.from_file`:
  拡張子からmedia_type推定、`ProjectPaths.resolve_relative`経由でroot escape拒否、
  SHA-256計算、text即readyそれ以外registered)、`script/services/sources.py`
  (`SourceService.register`: immutable copy+DB登録+重複hash検出、`transition`:
  遷移表に基づく合法遷移のみ許可、`list_for_project`: rowid順)。
  [[implementation_assumptions.md]]に3件の仮定を記録。
- 対象テスト結果: 8 passed。
- 文書修正: `docs/commands/sources.md`(担当分)。

### TASK-RIGHTS-001 完了

- 対象: `tests/test_rights_gate.py`(5 case), `tests/test_credit_manifest.py`(5 case)
- Red確認: 型(enum/dataclass shape)は保持しつつ`gate_decision`/`evaluate_*`/
  `build_credit_manifest`本体のみ`NotImplementedError`化した中間版で10 failed
  (`NotImplementedError`および検証欠如による`DID NOT RAISE`)を確認。
- production実装: `script/schemas/rights.py`(`RightsStatus`8値、`UsagePurpose`4値、
  5.3節ゲート表を全網羅、`RightsRecord.__post_init__`でverified_*系のhuman確認
  必須化)、`script/services/rights.py`(`evaluate_local_generation`/
  `evaluate_distribution`/`build_credit_manifest`: 決定的順序・重複排除・
  human確認済みcreditのみ出力)。[[implementation_assumptions.md]]に3件の
  仮定を記録。
- 対象テスト結果: 10 passed。
- 文書修正: `docs/commands/rights.md`(担当分)。

### TASK-BUILD-001 完了

- 対象: `tests/test_build_request_service.py`(8 case、単一file)
- Red確認: 8 failed(`BuildRequestService.create`/`serialize_output_formats`が
  `NotImplementedError`)。
- production実装: `script/services/build_requests.py`(`BuildRequestService.create`:
  `TASK-DOMAIN-001`の`canonicalize_output_formats`/`validate_build_request`を再利用し
  Project存在確認後にdraft保存、`serialize_output_formats`: 同じcanonicalize経由で
  JSON化)。
- 対象テスト結果: 8 passed。
- 文書修正: `docs/commands/builds.md`(担当分。audio側は`TASK-AUDIO-003`で別途更新)。

### TASK-JOB-001 完了

- 対象: `tests/test_job_lifecycle.py`(4 case), `tests/test_job_queue.py`(3 case),
  `tests/test_stale_job_recovery.py`(3 case)
- Red確認: 10 failed(`can_transition`/`JobService.*`が`NotImplementedError`)。
- production実装: `script/domain/job_state.py`(`can_transition`: 5.2節の状態遷移表
  +queued→cancel_requested拡張)、`script/services/jobs.py`(`enqueue`: 注入可能な
  approval_gate_check hook経由でgate確認、`start_next`: running不在時のみ
  最古queuedをrowid順で起動、`request_cancel`: cancel_requestedへの遷移、
  `retry`: parent_job_idチェーンで上限3回、`recover_stale`: is_process_alive hook
  経由でstale runningをfailed化)。[[implementation_assumptions.md]]に4件の
  仮定を記録(うち1件はTASK-APPROVAL-001との依存分離に関する重要な設計判断)。
- 対象テスト結果: 10 passed。
- 文書修正: `docs/commands/jobs.md`(担当分)。

### TASK-ARTIFACT-001 完了

- 対象: `tests/test_artifact_service.py`(9 case、単一file)
- Red確認: 9 failed(`ArtifactService.register/list_latest/list_versions`が
  `NotImplementedError`)。
- production実装: `script/services/artifacts.py`(`register`: file存在確認→
  Job/Project整合確認(job.build_request_id経由)→既存path上書き拒否→
  次version自動採番→`copy_immutable`でhash付きimmutable copy→DB追記、
  `list_latest`: type別最新version、`list_versions`: 降順一覧)。
  [[implementation_assumptions.md]]に3件の仮定を記録。
- 対象テスト結果: 9 passed。
- 文書修正: `docs/commands/artifacts.md`(担当分)。

### TASK-APPROVAL-001 完了

- 対象: `tests/test_approval_workflow.py`(TC-01,03,05,07,09の5 case),
  `tests/test_approval_invalidation.py`(TC-02,04,06,08,10の5 case)
- Red確認: 型(`ApprovalGate`/`ApprovalStatus`/dataclass shape)は保持しつつ
  `can_transition_approval`/`compute_bundle_hash`/`ApprovalTarget.__post_init__`/
  `ApprovalRecord.__post_init__`/`ChangeRequest.__post_init__`および
  `ApprovalService._transition/submit/approve/request_changes/
  invalidate_changed_targets/assert_gate`本体のみ`NotImplementedError`化した
  中間版で10 failed(全件`NotImplementedError`、import error・構文errorなし)を確認。
- production実装: `script/schemas/approvals.py`(`ApprovalGate`4値、
  `ApprovalStatus`7値、07節4節の状態遷移表を`_TRANSITIONS`で網羅、
  `ApprovalTarget`/`ApprovalRecord`/`ChangeRequest`の入力検証、
  `ApprovalBundle.from_mapping/to_mapping/empty/with_record`で
  4gate欠落拒否と決定的serialization、`compute_bundle_hash`はpath+file hash+
  順序を`canonical_sha256`で正規化)、`script/services/approvals.py`
  (`ApprovalService`はDBでなくfile正本`project/approvals.yaml`を
  `dump_yaml`/`load_yaml`で読み書き。`submit/approve/request_changes/
  mark_revised/resubmit/reject`は共通`_transition`経由で不正遷移を
  `AppError(CONFLICT)`拒否かつ失敗時ファイル未変更、`invalidate_changed_targets`
  は07節10節の変更種別→gateマッピングで承認済みgateのみinvalidated化、
  `assert_gate`は非approvedを`AppError(PERMISSION_DENIED)`で停止)。
  [[implementation_assumptions.md]]に3件の仮定を記録
  (承認をDBでなくfileを正本とする設計判断を含む)。
- 対象テスト結果: 10 passed。
- 文書修正: `docs/commands/approvals.md`(担当分)。

## Phase 2 完了

- 完了タスク: `TASK-PROJECT-001`, `TASK-SOURCE-001`, `TASK-RIGHTS-001`,
  `TASK-BUILD-001`, `TASK-JOB-001`, `TASK-ARTIFACT-001`, `TASK-APPROVAL-001`(7件)。
- Phase 2対象13 test file実測: 62 passed(想定63件ではなく実測62件が正)。
- Repository全体回帰実測(2026-07-20時点):
  - `python -m compileall -q script tests`: エラーなし。
  - `python -m pytest --collect-only -q`: 454 tests collected。
  - `python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"`:
    133 passed, 23 deselected, 298 xfailed(予期しないfailなし)。
  - `npm run typecheck`: エラーなし。
  - `npm test -- --run`: 16 test files / 76 tests passed
    (すべてPhase6/7未着手task向けの`test.fails`placeholderであり、
    本実装完了を意味しない)。
  - `docker compose build test`: 成功。
  - `docker compose run --rm test python -m pytest --collect-only -q`: 454 tests
    collected(host側と一致)。
- 累計完了タスク: 15/54(Phase1: 8件 + Phase2: 7件)。
- 累計完了Pythonケース: 133 passed。
- 次のPhase開始可否: 可。次はPhase 3の`TASK-INGEST-001`から開始する。

## Phase 3 進行中

### TASK-INGEST-001 完了

- 対象: `tests/test_material_input_orchestrator.py`(TC-01,03,05,07,09の5 case),
  `tests/test_text_ingestion.py`(TC-02,04,06,08の4 case)
- Red確認: 型(`IngestSource`/`ProcessingResult`/`StructuredSource`のdataclass shape)
  は保持しつつ`MaterialInputOrchestrator.register_adapter/process`および
  `TextIngestionAdapter.process`本体のみ`NotImplementedError`化した中間版で
  9 failed(全件`NotImplementedError`、import error・構文errorなし)を確認。
- production実装: `script/source_processing/orchestrator.py`
  (`MaterialInputOrchestrator`: media_type→adapter registryを保持し、
  `_PERMANENTLY_UNSUPPORTED_MEDIA_TYPES`(epub/video/audio_recording/
  kindle_capture)と未登録media typeの両方を同一の`unsupported_media_type`
  errorで拒否、`process`はadapter呼び出し前後で進捗hookを2回(0/1→1/1)通知し、
  adapterが`AppError`を送出した場合は原本を保持したまま`status="failed"`の
  `ProcessingResult`を返す)、`script/source_processing/text_ingestion.py`
  (`TextIngestionAdapter.process`: UTF-8 decode失敗を`AppError(VALIDATION_ERROR)`
  化し、改行統一+行末空白除去による最小限の`normalize`で
  original/extracted/normalized/structuredの4段階を`StructuredSource`として返す)。
  [[implementation_assumptions.md]]に3件の仮定を記録。
- 対象テスト結果: 9 passed。
- 全体回帰: 142 passed, 23 deselected, 289 xfailed(予期しないfailなし、
  Phase2完了時点の133から+9)。
- 文書修正: `docs/commands/source-processing.md`(担当分。`TASK-SOURCE-002`側の
  記述は未着手のため変更していない)。

### TASK-IMAGE-001 完了

- 対象: `tests/test_image_ingestion.py`(TC-01,03,05,07,09の5 case),
  `tests/test_image_manifest.py`(TC-02,04,06,08,10の5 case)
- Red確認: 型(`PageEntry`/`Locator`/`ImageManifest`/`ImageIngestionResult`の
  dataclass shape)は保持しつつ`ImageIngestionService.ingest`と
  `build_image_manifest`本体のみ`NotImplementedError`化した中間版で
  10 failed(全件`NotImplementedError`、import error・構文errorなし)を確認。
- production実装: `script/source_processing/images/manifest.py`
  (`Locator`/`PageEntry`/`ImageManifest`のdataclassと、`build_image_manifest`:
  `page_index`/`image_id`の重複を拒否しcanonical dict化(位置情報等の生値は
  含めない))、`script/source_processing/images/ingestion.py`
  (`ImageIngestionService(destination_dir)`: Pillowで形式検証(PNG/JPEG/TIFF)+
  `verify()`による壊れた画像検出を全件先に行い1件でも不正なら一切コピーしない
  two-phase設計、`explicit_order`は入力pathsの完全な順列であることを検証、
  natural sortのフォールバック時は`order_requires_human_preview`warningを
  付与、EXIF GPS(tag 34853)の有無だけを`exif_location_present`flagとして
  記録し実際の座標は一切保持・返却しない、原本への上書きは内容が同一なら
  冪等成功・異なれば`AppError(CONFLICT)`で拒否)。
  [[implementation_assumptions.md]]に4件の仮定を記録。
- 対象テスト結果: 10 passed。
- 全体回帰: 152 passed, 23 deselected, 279 xfailed(予期しないfailなし、
  TASK-INGEST-001完了時点の142から+10)。
- 文書修正: `docs/commands/images.md`(担当分。`TASK-IMAGE-002`側の記述は
  未着手のため変更していない)。

### TASK-IMAGE-002 完了

- 対象: `tests/test_image_preprocessing.py`(TC-01,03,05,07の4 case),
  `tests/test_image_quality_flags.py`(TC-02,04,06,08の4 case)
- Red確認: 型(`PreprocessOptions`/`PreprocessedPage`/`ImageQualityReport`の
  dataclass shape)は保持しつつ`ImagePreprocessor.process`/`split_spread`/
  `assess_image_quality`本体のみ`NotImplementedError`化した中間版で
  8 failed(全件`NotImplementedError`、import error・構文errorなし)を確認。
- production実装: `script/source_processing/images/preprocess.py`
  (`ImagePreprocessor(destination_dir).process(page, options)`:
  Pillowで回転/contrast補正を適用しPNG派生物として保存、原画像は
  処理前後でbyte比較して不変性を確認、派生物書込みは
  `TASK-IMAGE-001`と同型の「内容同一なら冪等成功・異なれば
  `AppError(CONFLICT)`」パターンを再利用、`split_spread(page)`:
  既存派生PNGを左右に等分割し`Locator`(`original_image_id`/`crop_x`等)で
  元座標対応を保持)、`script/source_processing/images/quality.py`
  (`assess_image_quality(page)`: グレースケール変換後のPillow
  `ImageStat.Stat`によるstddevでblank_candidateを検出(削除はしない)、
  低解像度候補も付随的に検出)。[[implementation_assumptions.md]]に
  3件の仮定を記録(`destination_dir`引数追加、two-phase不要な
  single-image処理、blur/skew/contrast閾値は仕様19節の未決定事項として
  blank/低解像度のみ実装)。
- 対象テスト結果: 8 passed。
- 全体回帰: 160 passed, 23 deselected, 271 xfailed(予期しないfailなし、
  TASK-IMAGE-001完了時点の152から+8)。
- 文書修正: なし(`documentation_repair_ownership`が空)。

### TASK-PDF-001 完了

- 対象: `tests/test_pdf_direct_extraction.py`(TC-01,03,05,07,09の5 case),
  `tests/test_pdf_extraction_fallback.py`(TC-02,04,06,08,10の5 case)
- 依存追加: `PyMuPDF==1.24.14`(未導入だったため`pip install`で追加)、
  `pypdf==6.10.2`(環境に既存だったversionをそのまま採用)を
  `requirements.txt`へ追記。契約が「PyMuPDF primary adapter」/
  「pypdf secondary adapter境界」を明示的に要求しており、実装に必須のため。
- Red確認: 型(`PdfPage`/`PdfExtractionReport`/`TextBlock`のdataclass shape)は
  保持しつつ`PdfTextExtractor.extract`/`should_fallback_to_ocr`本体のみ
  `NotImplementedError`化した中間版で10 failed(全件`NotImplementedError`、
  import error・構文errorなし)を確認。
- production実装: `script/source_processing/pdf/models.py`
  (`TextBlock`/`PdfPage`/`PdfExtractionReport`)、
  `script/source_processing/pdf/extract.py`(`PdfTextExtractor(extractor=
  "pymupdf"|"pypdf").extract(path)`: 開いた直後に`needs_pass`/`is_encrypted`
  (pypdfは`is_encrypted`)を検査しパスワード解除を一切試みず
  `unsupported_password_protected_pdf`で即時拒否、PyMuPDFは
  `page.get_text("blocks")`のbbox(y,x)でsortした簡易読み順、
  抽出前後で入力fileのbyte比較により不変性を保証、
  `should_fallback_to_ocr(page)`: 5.4節のprovisional閾値
  (printable_char_ratio<0.85 / duplicate_ratio>0.3 /
  抽出文字数<20)でOCR候補を判定)。[[implementation_assumptions.md]]に
  3件の仮定を記録(依存追加、`should_fallback_to_ocr`の引数を`report`でなく
  単一`page`とした解釈、read_order推定の簡易アルゴリズム)。
- 対象テスト結果: 10 passed。
- 全体回帰: 170 passed, 23 deselected, 261 xfailed(予期しないfailなし、
  TASK-IMAGE-002完了時点の160から+10)。
- 文書修正: `docs/commands/pdf.md`(担当分)。

### TASK-OCR-001 完了(external_gate、通常テストのみ確認済み)

- 対象: `tests/test_ocr_client.py`(TC-01,03,05,07,09の5 case + TC-11
  integration_smoke)、`tests/test_ocr_pipeline.py`(TC-02,04,06,08,10の
  5 case + TC-12 integration_live)。合計12 case中、外部接続なしの10 caseを
  本実装・確認、smoke/liveの2 caseは実装済みだがこの環境ではTesseract
  runtime未導入のため未確認(既定skip)。
- Red確認: 型(`RuntimeHealth`/`OcrOptions`/`OcrPageResult`/`OcrPageRequest`/
  `OcrPageOutcome`/`OcrManifest`のdataclass shape)は保持しつつ
  `OcrClient.check_runtime`/`recognize`/`OcrPipeline.process_pages`本体のみ
  `NotImplementedError`化した中間版で10 failed(全件`NotImplementedError`、
  import error・構文errorなし。integration_smoke/liveの2 caseは通常時は
  skip対象のためこのRed確認から除外)を確認。
- production実装: `script/source_processing/ocr/client.py`
  (`OcrClient(tesseract_cmd=None, runner=None)`: subprocess呼出しを
  injectable`runner`経由にしてmock可能にし、`check_runtime`は
  `--version`/`--list-langs`を副作用なく確認、`recognize`は
  `tesseract <image> stdout -l <lang> tsv`のTSV出力からtext/confidence
  (0.0-1.0)を再構成)、`script/source_processing/ocr/pipeline.py`
  (`OcrPipeline.process_pages`: 先にruntime確認を1回だけ行い不在なら
  全pageをfailed/review_required化してsubprocessを個別に試行しない、
  各pageの`recognize`失敗は`AppError`を捕捉して当該pageだけfailed化し
  他page結果を保持(失敗分離)、`high_risk_hint`(formula/code/table/
  figure)指定pageは信頼度に関わらず常に`review_required`)。
  [[implementation_assumptions.md]]に4件の仮定を記録(confidence閾値、
  high_risk_hintの表現方法、`tests/conftest.py`の
  `tesseract_connectivity_gate`を実装した点を含む)。
- 対象テスト結果(外部接続なし10件): 10 passed。smoke/live 2件は
  `WALKWISE_RUN_INTEGRATION_SMOKE`/`_LIVE`未設定のため既定どおりskip。
  `TESSERACT_CMD`未設定での`WALKWISE_RUN_INTEGRATION_SMOKE=1`実行も
  確認し、`tesseract_connectivity_gate`が秘密値を出さず
  `pytest.skip`することを確認した(設定確認段階の正しい挙動)。
- 全体回帰: 180 passed, 23 deselected, 251 xfailed(予期しないfailなし、
  TASK-PDF-001完了時点の170から+10)。
- 外部疎通実行: なし(この開発環境にTesseract未導入のため)。
- 文書修正: `docs/commands/ocr.md`(担当分)。

### TASK-SOURCE-002 完了

- 対象: `tests/test_source_normalization.py`(TC-01,04,07,10の4 case),
  `tests/test_source_chunking.py`(TC-02,05,08の3 case),
  `tests/test_source_manifest.py`(TC-03,06,09の3 case)
- Red確認: 型(`NormalizationRules`/`NormalizationResult`/`ChunkLocator`/
  `StructuredSourceInput`/`SourceChunk`のdataclass shape)は保持しつつ
  `normalize_text`/`chunk_structured_source`/`build_chunk_manifest`/
  `build_topic_index`本体のみ`NotImplementedError`化した中間版で10 failed
  (全件`NotImplementedError`、import error・構文errorなし)を確認。
- production実装: `script/source_processing/normalize.py`
  (`normalize_text`: NFKC Unicode正規化+改行統一+行末空白除去、
  2回以上出現する短い行(80文字以下)を反復header/footer候補として
  最初の1回以外を除去、`[n]: 本文`形式の行をfootnoteとして本文から分離、
  fenced code block(```...```)は正規化対象から除外し内容を一切変更
  しない(structured Markdown/YAML/JSON保護)、before/after hashと
  unified diffを返す)、`script/source_processing/chunking.py`
  (`chunk_structured_source`: 空行区切りで段落分割し、soft_limitを
  超える手前まで段落を貪欲に詰め、段落の途中では絶対に分割しない
  (意味境界優先)、typed locator(`ChunkLocator`)を全chunkへ伝播)、
  `script/source_processing/manifests.py`(`build_chunk_manifest`:
  chunk_id/orderの重複拒否、`build_topic_index`: chunk_manifestに
  存在しないchunk_idへの参照を拒否)。[[implementation_assumptions.md]]に
  2件の仮定を記録(「structured Markdown/YAML/JSON」「footnote分離」
  「繰返しheader/footer除去」の各TCタイトルが実際にはnormalize.py側の
  機能であるにもかかわらず、STEP3側のtest file割当がchunking.py/
  manifests.py側になっている点の解釈を含む)。
- 対象テスト結果: 10 passed。
- 全体回帰: 190 passed, 23 deselected, 241 xfailed(予期しないfailなし、
  TASK-OCR-001完了時点の180から+10)。
- 文書修正: なし(`documentation_repair_ownership`が空)。

### TASK-SOURCE-003 完了(Phase3最終タスク)

- 対象: `tests/test_source_review_service.py`(TC-01〜10の全10 case、単一file)
- Red確認: 型(`SourceReviewIssue`/`CorrectionPatch`/`ReviewDecision`/
  `SourceReviewLocator`/`ApplyCorrection`/`ReviewResult`/
  `ReprocessingRequest`のdataclass shape)は保持しつつ各`__post_init__`
  validationと`SourceReviewService.apply_correction`/`mark_resolved`/
  `require_reprocessing`本体のみ`NotImplementedError`化した中間版で
  10 failed(全件`NotImplementedError`、import error・構文errorなし)を確認。
- production実装: `script/schemas/source_review.py`(`ReviewIssueCategory`
  5値、`ReviewIssueStatus`4値(open/resolved/corrected/
  reprocessing_requested)、`SourceReviewLocator`は仕様どおり全項目任意、
  `SourceReviewIssue`/`CorrectionPatch`/`ReviewDecision`の必須field
  検証)、`script/services/source_review.py`(`SourceReviewService
  (destination_dir)`: `apply_correction`はraw/extractedをbyte比較で
  不変性確認しつつ`revision-NNNN.md`という新revisionへ修正後本文と
  diff・provenance(issue_id/corrected_by/corrected_at/before_hash/
  after_hash)を保存、`mark_resolved`/`require_reprocessing`は
  `open`からのみ遷移可能な状態遷移表で不正遷移を`AppError(CONFLICT)`
  拒否、`require_reprocessing`は理由必須で新Job候補
  (`ReprocessingRequest`)を返すのみで実際のJob起動・既存成果物削除は
  行わない)。[[implementation_assumptions.md]]に2件の仮定を記録
  (`mark_resolved`/`require_reprocessing`の状態遷移設計と、
  `apply_correction`のrevision命名規則)。
- 対象テスト結果: 10 passed。
- 全体回帰: 200 passed, 23 deselected, 231 xfailed(予期しないfailなし、
  TASK-SOURCE-002完了時点の190から+10)。
- 文書修正: `docs/commands/source-review.md`(担当分)。

## Phase 3 完了

- 完了タスク: `TASK-INGEST-001`, `TASK-IMAGE-001`, `TASK-IMAGE-002`,
  `TASK-PDF-001`, `TASK-OCR-001`, `TASK-SOURCE-002`, `TASK-SOURCE-003`
  (7件、Phase3の全タスク)。
- Phase3対象13 test file(`test_material_input_orchestrator.py`,
  `test_text_ingestion.py`, `test_image_ingestion.py`,
  `test_image_manifest.py`, `test_image_preprocessing.py`,
  `test_image_quality_flags.py`, `test_pdf_direct_extraction.py`,
  `test_pdf_extraction_fallback.py`, `test_ocr_client.py`(外部接続なし分),
  `test_ocr_pipeline.py`(外部接続なし分), `test_source_normalization.py`,
  `test_source_chunking.py`, `test_source_manifest.py`,
  `test_source_review_service.py`)実測: 67 passed(外部接続なし)、
  `TASK-OCR-001`のsmoke/live 2 caseは未確認(既定skip)。
- Repository全体回帰実測(2026-07-20時点):
  - `python -m compileall -q script tests`: エラーなし。
  - `python -m pytest --collect-only -q`: 454 tests collected(host/Docker一致)。
  - host: `python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"`:
    200 passed, 23 deselected, 231 xfailed(予期しないfailなし)。
  - `npm run typecheck`: エラーなし。
  - `npm test -- --run`: 16 test files / 76 tests passed(すべて
    Phase6/7未着手task向けの`test.fails`placeholder、本実装完了を意味しない)。
  - Docker: `docker compose build test`は成功したが、初回の
    `docker compose run --rm test python -m pytest ...`で
    `test_tc_pdf_001_01`が1件failした(下記参照、修正済み)。
  - Docker(修正後再実行): 193 passed, 7 skipped
    (`test_container_contract.py`のdocker CLI未検出skipのみ、コンテナ内
    実行のため想定どおり), 23 deselected, 231 xfailed。193+7=200で
    host側と合致。
  - 累計完了タスク: 21/54(Phase1: 8件 + Phase2: 7件 + Phase3: 7件全完了)。
  - 累計完了Pythonケース: 200 passed(うちTASK-OCR-001の2 caseは
    smoke/live未確認で上記には含まれず)。
- Docker回帰で発見した横断バグ: `_extract_with_pypdf`が、
  `cryptography`package未導入環境でAES暗号化PDFのmetadata検査時に
  `pypdf.errors.DependencyError`を「cannot open pdf」という誤った
  messageへ変換していた。`requirements.txt`へ`cryptography==47.0.0`を
  追加し、`DependencyError`専用のexcept節も追加して修正・再確認済み。
  詳細は[[implementation_assumptions.md]]を参照。
- 新規依存: `PyMuPDF==1.24.14`/`pypdf==6.10.2`/`cryptography==47.0.0`
  (`TASK-PDF-001`)。
- 未確認の外部runtime: Tesseract(`TASK-OCR-001`のTC-11/TC-12)。
  この開発環境には未導入。
- 次のPhase開始可否: 可。次はPhase 4(AI教材生成)の`TASK-AI-001`
  (Gemini依存、external_gate)から開始する。

## Phase 4 進行中

### TASK-AI-001 完了(external_gate、通常テストのみ確認済み)

- 対象: `tests/test_ai_client_contract.py`(TC-01,03,05,07,09の5 case +
  TC-11 integration_smoke)、`tests/test_gemini_client.py`(TC-02,04,06,08,10
  の5 case + TC-12 integration_live)。合計12 case中、外部接続なしの10 case
  を本実装・確認、smoke/liveの2 caseは実装済みだがこの環境に
  `GEMINI_API_KEY`が未設定のため未確認(既定skip)。
- 前提確認: `script/ai_clients/gemini/client.py`には既存の稼働中legacy実装
  (`call_gemini`/`load_prompt`/`render_prompt`/`split_text_into_chunks`等、
  `merged_text_fixer.py`/`mindmap_builder.py`が依存)がSTEP4スキャフォールドの
  上に存在していた。本タスクはこのlegacy実装を一切変更せず、その下に追記
  されていたSTEP4契約(`GeminiClient`/`ConnectivityResult`)だけを実装した。
  実装後に`from script.ai_clients.gemini.client import call_gemini, ...`が
  引き続き成功することを確認し、legacy消費者を壊していないことを確認した。
- Red確認: 型(dataclass shape)は保持しつつ`AIRequest`/`AIResult`の
  `__post_init__`、`make_json_response_validator`/
  `make_yaml_response_validator`、`AIClientRegistry.register`/`get`、
  `GeminiClient.check_connectivity`/`generate`本体のみ
  `NotImplementedError`化した中間版で10 failed(全件`NotImplementedError`、
  import error・構文errorなし。smoke/liveの2 caseは通常時skip対象のため
  このRed確認から除外)を確認。
- production実装: `script/ai_clients/base.py`(`AIClientError(AppError)`に
  `retryable: bool`を追加、`AIRequest`/`AIResult`/`AIUsage`、
  `make_json_response_validator`/`make_yaml_response_validator`という
  pluggableなresponse検証hook、`runtime_checkable`な`AIClient`Protocol)、
  `script/ai_clients/registry.py`(`AIClientRegistry.register/get`)、
  `script/ai_clients/gemini/client.py`(`GeminiClient`: 既存の
  `build_endpoint`/`extract_text_from_candidate`/`_is_retryable_status_code`/
  `_compute_retry_wait_sec`/`_summarize_response_error`を再利用し、
  429/5xxのみ上限内で再試行・400は即時error、timeoutは再試行せず安定error
  へ変換、`session_get`/`session_post`/`sleep`のDI hookで外部接続なしの
  決定的なmockテストを可能にした)。[[implementation_assumptions.md]]に
  2件の仮定を記録。
- 対象テスト結果(外部接続なし10件): 10 passed。smoke/live 2件は
  `WALKWISE_RUN_INTEGRATION_SMOKE`/`_LIVE`未設定のため既定どおりskip。
- 全体回帰: 210 passed, 23 deselected, 221 xfailed(予期しないfailなし、
  Phase3完了時点の200から+10)。
- 外部疎通実行: なし(`GEMINI_API_KEY`未設定のため)。
- 文書修正: `docs/commands/ai.md`(担当分。`TASK-AI-002`側の記述は
  未着手のため変更していない)。

### TASK-AI-002 完了

- 対象: `tests/test_ai_routing.py`(TC-01,04,07,10の4 case),
  `tests/test_ai_cache.py`(TC-02,05,08の3 case),
  `tests/test_ai_budget.py`(TC-03,06,09の3 case)
- Red確認: 型(`ModelPolicy`/`ModelSelection`/`AICacheKey`/`UsageEstimate`の
  dataclass shape)は保持しつつ`AIRouter.resolve`/`ModelPolicy.__post_init__`/
  `ModelPolicy.from_mapping`/`AICacheKey.__post_init__`/`AICache.get`/`put`/
  `BudgetGuard.assert_available`/`reserve`/`record`本体のみ
  `NotImplementedError`化した中間版で10 failed(全件`NotImplementedError`、
  import error・構文errorなし)を確認。
- production実装: `script/ai/routing.py`(`AIRouter.resolve(task_class,
  policy)`: `task_class`を論理層名(economy_structuring/
  standard_generation/high_assurance_review)として扱い、`env_override`>
  `policy`既定値の順でmodelを解決、`required_when_invoked`なtierで
  model未解決の場合はstandardへ黙って降格せず`AppError
  (EXTERNAL_UNAVAILABLE)`で停止)、`script/ai/cache.py`(`AICacheKey`
  (task_type/logical_tier/model/prompt_id/prompt_version/input_hash/
  schema_version)をhashable frozen dataclassとしてdictキーに直接使う
  `AICache.get/put`)、`script/ai/budget.py`(`BudgetGuard.reserve`は
  推測値(`UsageEstimate.is_measured=False`)による事前判定のみ行い
  `spent_usd`/`records`を変更しない、`record`は実測値を`spent_usd`へ
  反映し`records`へ保存、`assert_available`は残予算0を
  `AppError(PERMISSION_DENIED, "budget_exceeded: ...")`で拒否)。
  [[implementation_assumptions.md]]に2件の仮定を記録(`task_class`の
  解釈、reserve/recordの推測値・実測値分離設計)。
- 対象テスト結果: 10 passed。
- 全体回帰: 220 passed, 23 deselected, 211 xfailed(予期しないfailなし、
  TASK-AI-001完了時点の210から+10)。
- 文書修正: なし(`documentation_repair_ownership`が空)。

### TASK-AI-003 完了

- 対象: `tests/test_source_analysis_pipeline.py`(TC-01,03,05,07,09の5 case),
  `tests/test_coverage_map.py`(TC-02,04,06,08,10の5 case)
- Red確認: 型(`SourceChunkInput`/`RequiredTopic`/`SourceAnalysisBundle`/
  `SourceSummary`/`TopicIndex`/`TopicIndexEntry`/`CoverageEntry`/
  `CoverageMap`/`SourceRequirement`のdataclass shape)は保持しつつ
  `SourceAnalysisPipeline.run`/`analyze_gaps`本体のみ`NotImplementedError`
  化した中間版で10 failed(全件`NotImplementedError`、import error・
  構文errorなし)を確認。
- production実装: `script/schemas/source_analysis.py`
  (`CoverageStatus`5値、`CoverageEntry.__post_init__`が
  status=conflictのときnext_action必須を強制(黙った解決の禁止))、
  `script/pipelines/source_analysis.py`(`SourceAnalysisPipeline
  (ai_client, model="gemini-2.5-flash-lite")`: source summaryは
  対象source_idのchunkだけを本文に含めてAI(`AIClient.generate`経由、
  economy tier想定)へ渡す、topic indexは入力chunkの`topic_ids`
  hintから決定的に構築、coverage判定はrequired_topicsに対し
  chunk不在→missing、`conflicting=True`のchunkを含む→conflict
  (`human_review_required`、絶対に自動でcoveredへ降格しない)、
  それ以外→covered、`analyze_gaps`はcoverage_mapとtopic_indexから
  missing/conflict/partially_covered/duplicateを決定的に抽出)。
  [[implementation_assumptions.md]]に2件の仮定を記録
  (`conflicting`フラグによる矛盾hintの表現方法、topic index構築を
  AI呼出しなしで決定的に行う設計判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 230 passed, 23 deselected, 201 xfailed(予期しないfailなし、
  TASK-AI-002完了時点の220から+10)。
- 文書修正: `docs/commands/content-generation.md`(担当分。
  `TASK-CURRICULUM-001`/`TASK-SCRIPT-001`/`TASK-NARRATION-001`側の記述は
  未着手のため変更していない)。

### TASK-CURRICULUM-001 完了

- 対象: `tests/test_curriculum_pipeline.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_chapter_spec_schema.py`(TC-02,04,06,08,10の5 case)。
  `documentation_repair_ownership: []`のため文書更新は対象外。
- Red確認: dataclass shape(`TopicMap`/`TopicMapEntry`/`Curriculum`/
  `CurriculumChapter`/`ChapterSpec`/`RequiredTopicRef`/`CurriculumResult`の
  `__post_init__`型検証)は保持しつつ、`CurriculumPipeline.generate`と
  `ChapterSpec.validate`の本体のみ`NotImplementedError`化した中間版で
  9 failed/1 passed(全件import error・構文errorなし)を確認。TC-08
  (`必須入力欠落`)はdataclass `__post_init__`の型検証だけを対象にした
  testのため、この中間版でも1件passした(`TASK-AI-003`等これまでの
  タスクと同じ扱い: dataclassの構造的検証はSTEP4未実装スタブの対象外)。
- production実装: `script/schemas/curriculum.py`(`TopicMap`/
  `TopicMapEntry`/`Curriculum`/`CurriculumChapter`。`Curriculum`は
  `status="approved"`での直接構築を拒否し、人間承認前のdraft/
  review_pending状態でのみ生成される契約を型で強制)、
  `script/schemas/chapter_spec.py`(`ChapterSpec`。`known_topic_ids`/
  `known_source_ids`を呼び出し側から明示的に渡す設計とし、
  `validate()`は未知topic/source参照・`required_topics`重複・
  `explanation_order`の未知topic参照をerrorにし、
  `learning_outcomes`空はwarningとして戻り値に含めるだけで
  処理を継続する非致命扱い)、`script/pipelines/curriculum.py`
  (`CurriculumPipeline.generate(analysis, project_plan)`:
  `TASK-AI-003`の`SourceAnalysisBundle`/`CoverageStatus`を直接消費し、
  missing/conflictのtopicをcurriculumへ含めない(coverage反映)、
  AI呼出しは1回のみ・指定modelのまま実行(黙った降格をしない)、
  結果は常に`status="review_pending"`で返す)。
  [[implementation_assumptions.md]]に仮定を記録
  (`ChapterSpec`の`known_topic_ids`/`known_source_ids`を
  コンストラクタ引数として明示化した設計判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 240 passed, 23 deselected, 191 xfailed(予期しないfailなし、
  TASK-AI-003完了時点の230から+10)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-SCRIPT-001 完了

- 対象: `tests/test_script_schema.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_draft_generation.py`(TC-02,04,06,08の4 case)。
  `documentation_repair_ownership: []`のため文書更新は対象外。
- Red確認: dataclass shape(`SpeakerRef`/`SegmentPauses`/
  `GenerationProvenance`/`ScriptSegment`/`ScriptDocument`/
  `DraftChunkInput`の`__post_init__`型検証)は保持しつつ、
  `ScriptDocument.ordered_segments`/`DraftGenerationPipeline.generate`/
  `segment_legacy_text`の本体のみ`NotImplementedError`化した中間版で
  7 failed/2 passed(全件import error・構文errorなし)を確認。TC-07/
  TC-09はdataclass `__post_init__`の型検証だけを対象にしたtestのため、
  この中間版でも2件passした(これまでのタスクと同じ扱い)。
- production実装: `script/schemas/script.py`(`SpeakerRef`/
  `SegmentPauses`(負のpauseを拒否)/`GenerationProvenance`(prompt/input
  provenance)/`ScriptSegment`/`ScriptDocument`。segment_id/orderの
  重複はerror、`pending_claims`は実在するsegment_idだけを参照可能)、
  `script/pipelines/draft_generation.py`(`DraftGenerationPipeline
  .generate(chapter_spec, chunks)`: `chapter_spec.source_ids`に
  含まれるchunkだけを本文に含めてAIへ渡し、AI応答を`SOURCE_REFS:`/
  `TEXT:`形式で解析、応答が指定外source_idを含む場合は
  `pending_claims`へsegment_idを記録し黙って承認しない(review_status
  は常に`pending_review`)。`segment_legacy_text(text)`は段落単位で
  決定的にsegment化し、`provenance.legacy_input=True`を設定して
  常に未承認扱いにする)。
  [[implementation_assumptions.md]]に仮定を記録
  (claim_ref必須ルールを構造的に強制しなかった判断、AI応答の
  `SOURCE_REFS:`/`TEXT:`形式によるprompt/response契約の設計)。
- 対象テスト結果: 9 passed。
- 全体回帰: 249 passed, 23 deselected, 182 xfailed(予期しないfailなし、
  TASK-CURRICULUM-001完了時点の240から+9)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-CLAIM-001 完了

- 対象: `tests/test_claims_pipeline.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_claim_validation.py`(TC-02,04,06,08,10の5 case)。
  `documentation_repair_ownership: ["docs/commands/fact-checking.md"]`。
- Red確認: dataclass shape(`SourceLocator`/`SourceEvidence`/
  `ClaimConflict`/`Claim`/`FactCheckReport`の`__post_init__`型検証)は
  保持しつつ、`ClaimPipeline.extract`/`ClaimPipeline.verify`/
  `assert_script_claims_publishable`の本体のみ`NotImplementedError`化
  した中間版で10 failed(全件import error・構文errorなし)を確認。
  この中間版ではTC-08もfailした(dataclass検証だけでなく
  `pipeline.extract(None)`/`pipeline.verify((), ...)`も呼ぶため)。
- production実装: `script/schemas/claims.py`(`ClaimType`10種、
  `ClaimStatus`7種、`Claim.__post_init__`が`status=verified`のとき
  `verified_by_human=True`必須・事実系claim_typeなら`source_evidence`
  必須を強制(AI出力のみでのverified化を禁止)、`ClaimConflict`が
  資料間矛盾を表現)、`script/pipelines/claims.py`
  (`ClaimPipeline.extract(script)`: 非事実的segment_type
  (heading/transition/introduction/summary/question)を除く各segment
  についてAI(economy_structuring既定`gemini-2.5-flash-lite`)へ
  `CLAIM_TYPE:`/`STATEMENT:`形式で1件抽出させ、常にstatus=pendingで
  生成。`ClaimPipeline.verify(claims, sources)`: 存在しないsource_id
  参照はerror、conflict claimは黙って解決せず常に
  human_review_requiredへ(`TASK-AI-002`の`AIRouter`/`ModelPolicy`が
  設定されていれば高保証tier解決を試みるが、未設定/未解決でも
  human_review_requiredのまま停止しerrorにしない)、事実系claimは
  `verified_by_human`かつlocator付きevidenceがある場合のみverified、
  AI由来evidenceのみではhuman_review_required、evidence皆無は
  unsupported。`assert_script_claims_publishable(script, claims)`:
  verified/人間承認済みpartially_verified以外のclaimがあれば
  `ErrorCode.CONFLICT`で本番工程を遮断)。
  実装中、契約にない`FactCheckReport.unsupported_claim_ids()`
  helperを一度追加したが、どのtestからも呼ばれない未使用コードと
  気づき、Red確認前に削除した。
  [[implementation_assumptions.md]]に仮定を記録
  (claim ref必須ルールの非対象化に類似する事実系/非事実系の切り分け、
  AI応答の`CLAIM_TYPE:`/`STATEMENT:`形式によるprompt/response契約)。
- 対象テスト結果: 10 passed。
- 全体回帰: 259 passed, 23 deselected, 172 xfailed(予期しないfailなし、
  TASK-SCRIPT-001完了時点の249から+10)。
- 文書修正: `docs/commands/fact-checking.md`(担当分。
  `現在のダンプでは欠落`という揮発性注記を削除し、`CURRENT_STATE.md`
  参照へ置換。対象10 caseがすべてpassする旨を記録。
  `rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands/fact-checking.md`
  で該当なしを確認)。

### TASK-PROFILE-001 完了(Phase4最終タスク)

- 対象: `tests/test_character_profiles.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_voice_profiles.py`(TC-02,04,06,08の4 case)。
  `documentation_repair_ownership: ["docs/commands/profiles.md"]`。
- Red確認: dataclass shape(`CharacterProfile`/`VoiceProfile`/
  `EngineIdentity`/`VoiceSpeaker`/`VoiceParameters`/`VoicePauses`の
  `__post_init__`型検証)は保持しつつ、`CharacterProfileRepository
  .load`/`.select`、`VoiceProfileRepository.load`/`.select`/
  `.list_available`、`CharacterProfile.content_hash`/
  `VoiceProfile.content_hash`の本体のみ`NotImplementedError`化した
  中間版で9 failed(全件import error・構文errorなし)を確認。
- production実装: `script/schemas/profiles.py`(`CharacterProfile`:
  08-character-profile-schema.mdが状態名を定義しないため
  `CharacterProfileStatus`(candidate/approved/rejected)を最小追加、
  `content_hash()`で正規化内容からSHA-256を決定的に計算。
  `VoiceProfile`: 09-voice-profile-schema.md 4節の6状態
  `VoiceProfileStatus`、`status=approved`なら`engine_identity
  .engine_version`と`audition_approved=True`を必須にする
  (11節のerror規則)、`content_hash()`で同様にSHA-256計算)、
  `script/profiles/characters.py`(`CharacterProfileRepository
  .select`は`status=approved`以外を`PERMISSION_DENIED`で拒否)、
  `script/profiles/voices.py`(`VoiceProfileRepository.select`は
  `approved`/`approved_for_limited_use`以外を拒否、
  `list_available`はMVPでは`engine="voicevox"`かつ`approved`のみを
  返す(COEIROINKは`TASK-COEIR-001`が永久blockedのため対象外))。
  [[implementation_assumptions.md]]に仮定を記録
  (CharacterProfileの承認状態モデルを最小新設した判断、
  voice profileの状態語彙を09番(承認済み仕様)から採用し
  spec-proposal task 3の詳細な試聴段階語彙を採用しなかった判断)。
- 対象テスト結果: 9 passed。
- 全体回帰: 268 passed, 23 deselected, 163 xfailed(予期しないfailなし、
  TASK-CLAIM-001完了時点の259から+9)。
- 文書修正: `docs/commands/profiles.md`(担当分。
  `現在のダンプでは欠落`という揮発性注記を削除し、`CURRENT_STATE.md`
  参照へ置換。対象9 caseがすべてpassする旨と、話者別最終値確定/
  COEIROINK対象外の位置づけを記録。
  `rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands/profiles.md`
  で該当なしを確認)。

## Phase 4 完了

Phase4(教材生成AI)の7タスク(`TASK-AI-001`, `TASK-AI-002`,
`TASK-AI-003`, `TASK-CURRICULUM-001`, `TASK-SCRIPT-001`,
`TASK-CLAIM-001`, `TASK-PROFILE-001`)がすべて本実装・Red確認・
対象テスト・Phase全体回帰まで完了した。

- 累計完了タスク: 29/54(Phase1: 8件、Phase2: 7件、Phase3: 7件、
  Phase4: 7件)。
- 対象68 case(Phase4の7タスク合計、10+10+10+10+9+10+9)がすべてpass。
- 全体回帰: 268 passed, 23 deselected, 163 xfailed(Phase3完了時点の
  200から、Phase4の7タスク累計で+68)。
- 外部疎通: `TASK-OCR-001`(Tesseract)・`TASK-AI-001`(Gemini)は
  この環境でintegration_smoke/liveとも未確認のまま(既定skip、
  秘密値・runtimeが未提供のため)。Phase4の他タスクは外部接続不要。
- 文書更新: `docs/commands/ai.md`(`TASK-AI-001`)、
  `docs/commands/content-generation.md`(`TASK-AI-003`)、
  `docs/commands/fact-checking.md`(`TASK-CLAIM-001`)、
  `docs/commands/profiles.md`(`TASK-PROFILE-001`)を各タスクの
  担当分だけ修正。`TASK-AI-002`/`TASK-CURRICULUM-001`/
  `TASK-SCRIPT-001`は`documentation_repair_ownership`が空のため対象外。
- 未解決事項: なし(Phase4のタスクはすべて完了、次はPhase5)。
- 次: Phase5(TTS・Pipeline・Audio) — `TASK-NARRATION-001`から
  依存順に開始する。

## Phase 5 進行中

### TASK-NARRATION-001 完了

- 対象: `tests/test_narration_transformations.py`(TC-01,03,05,07,09の
  5 case)、`tests/test_verified_script_pipeline.py`(TC-02,04,06,08,10
  の5 case)。`documentation_repair_ownership: []`のため文書更新は対象外。
- Red確認: dataclass shape(`SemanticDifference`/`SemanticReviewResult`
  の型)は保持しつつ、`SemanticReview.compare`、`NarrationPipeline
  .simplify`/`.adapt_for_audio`/`.apply_character`、
  `build_verified_script`の本体のみ`NotImplementedError`化した中間版で
  10 failed(全件import error・構文errorなし)を確認。
- production実装: `script/pipelines/semantic_review.py`
  (`SemanticReview.compare(source, transformed)`: segment_idで対応
  付けたtext同士を比較し、数値token集合の差・否定語の出現有無差・
  条件語の出現有無差を決定的に検出、差異があればreview_required、
  なければpass。AI呼出しなしの決定的heuristic)、
  `script/pipelines/narration.py`(`NarrationPipeline.simplify`/
  `.adapt_for_audio`はAI(`AIClient.generate`)を用いて`TEXT:`形式で
  本文を受け取り、それぞれ新しい`ScriptDocument`(stage=
  simplified/audio_adapted)を生成。`adapt_for_audio`は`text`を
  変更せず`tts_text`だけを設定。`apply_character`はAI呼出しなしで
  `CharacterProfileRepository.select`により承認状態を検証し、
  `character_id`未指定は中立原稿として局所disable(textもspeakerも
  不変)、存在しないcharacter_idは`speaker_not_found`
  (`ErrorCode.NOT_FOUND`)、解決成功時はspeakerのcharacter_idだけを
  更新しtextは変更しない。`build_verified_script(transformed_script,
  source_script, claims, router, model_policy)`は
  `assert_script_claims_publishable`(`TASK-CLAIM-001`)で未検証claimを
  遮断→`SemanticReview.compare`で意味差を確認→`AIRouter.resolve`
  (`TASK-AI-002`)で`high_assurance_review` tierが未設定/未解決なら
  黙って降格せず停止→すべて通過した場合だけstage="verified"の
  `ScriptDocument`を返す)。
  [[implementation_assumptions.md]]に仮定を記録
  (`apply_character`をspeaker解決/gatingに限定しtextの語尾変換
  アルゴリズムは実装しなかった判断、`SemanticReview`をAI呼出しなしの
  決定的heuristicにした判断、`build_verified_script`の
  kwargs専用signature設計)。
- 対象テスト結果: 10 passed。
- 全体回帰: 278 passed, 23 deselected, 153 xfailed(予期しないfailなし、
  TASK-PROFILE-001完了時点の268から+10)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### 文書集計の不整合修正(`docs/commands/STEP6_MANIFEST.json`)

継続実行指示により、`STEP6_MANIFEST.json`の`verification`ブロックが
Phase 3完了時点(`230 passed, 201 xfailed`、Docker
`193 passed, 7 skipped, 231 xfailed`)のまま更新されていなかったことを
発見した。`CURRENT_STATE.md`は既にPhase4完了時点まで実測更新済みで
一致していたため、`STEP6_MANIFEST.json`側だけが古かった。

実測(2026-07-20、TASK-NARRATION-001完了時点)により次へ更新した。

- host pytest: 278 passed, 23 deselected, 153 xfailed
- Docker: `docker compose build test`成功、
  `docker compose run --rm test python -m pytest --collect-only -q`で
  454件収集(host一致)、
  `docker compose run --rm test python -m pytest -ra -m "..."`で
  271 passed, 7 skipped(`test_container_contract.py`のdocker CLI
  未検出skipのみ、コンテナ内実行のため想定どおり), 23 deselected,
  153 xfailed(271+7=278でhostと完全一致)
- TypeScript: `npm ci`成功(395 packages)、`npm run typecheck`成功
  (error 0件)
- Vitest: `npm test -- --run`で16 test files/76 tests、すべてpassed
  (すべて`test.fails`placeholderであり、Phase6/7で対象タスクごとに
  解除する。production完了を意味しない)
- 外部接続: 0件(実行なし)

以後、Phase終了時ごとに`STEP6_MANIFEST.json`の`verification`ブロックも
`CURRENT_STATE.md`と同時に実測更新する。

### TASK-PIPELINE-001 完了

- 対象: `tests/test_impact_analysis.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_regeneration_plan.py`(TC-02,04,06,08,10の5 case)。
  `documentation_repair_ownership: ["docs/commands/regeneration.md"]`。
- Red確認: dataclass shape(`Change`/`DependencyGraph`/`ImpactSet`/
  `CacheState`/`RegenerationStep`の`__post_init__`型検証)は保持
  しつつ、`ImpactAnalyzer.analyze`、`RegenerationPlanner.plan`、
  `RegenerationPlan.validate_no_unrelated_targets`の本体のみ
  `NotImplementedError`化した中間版で10 failed(全件import error・
  構文errorなし)を確認。
- production実装: `script/pipelines/impact.py`
  (`ChangeType`8種を`02-process-input-output.md`14節「再利用と部分
  再生成」表に基づき`TargetCategory`10種へ決定的に対応付け
  (`_REPROCESS_TARGETS`)、`ImpactAnalyzer.analyze(change, graph)`は
  `DependencyGraph`で未知のchapter_id/segment_idをNOT_FOUNDにし、
  `ImpactSet.content_hash`で正規化入力から決定的なSHA-256を計算)、
  `script/pipelines/regeneration.py`(`RegenerationPlanner
  .plan(impact_set, cache_state)`は対象categoryを
  `07-approval-workflow.md`の4承認地点
  (materials_curriculum/planning/verified_script/preview_audio)へ
  対応付け、該当承認が`approved`でなければ`PERMISSION_DENIED`で
  停止(MP3タグのみの変更はgate対象外、10節「原則として維持」)。
  `RegenerationPlan.validate_no_unrelated_targets()`はimpact_setが
  宣言した対象category以外のstepが紛れ込んでいないか検証)。
  [[implementation_assumptions.md]]に仮定を記録
  (承認地点とTargetCategoryの対応付け、segment/chapter/project単位の
  scope解決ルール)。
- 対象テスト結果: 10 passed。
- 全体回帰: 288 passed, 23 deselected, 143 xfailed(予期しないfailなし、
  TASK-NARRATION-001完了時点の278から+10)。
- 文書修正: `docs/commands/regeneration.md`(担当分。
  `現在のダンプでは欠落`という揮発性注記を削除し、`CURRENT_STATE.md`
  参照へ置換。対象10 caseがすべてpassする旨を記録。
  `rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands/regeneration.md`
  で該当なしを確認)。

### TASK-TTS-001 完了

- 対象: `tests/test_tts_client_contract.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_tts_registry.py`(TC-02,04,06,08,10の5 case)。
  `documentation_repair_ownership: ["docs/commands/tts.md"]`。
- Red確認: dataclass shape(`SynthesisParameters`/`SynthesisRequest`/
  `SynthesisResult`/`SpeakerInfo`/`EngineCapabilities`の
  `__post_init__`型検証)は保持しつつ、`MockTTSClient`の4method
  (`check_connectivity`/`get_capabilities`/`list_speakers`/
  `synthesize`)と`TTSClientRegistry.register`/`.get`の本体のみ
  `NotImplementedError`化した中間版で8 failed/2 passed(全件import
  error・構文errorなし)を確認。TC-03(独立したtest-local double)と
  TC-04(dataclassのみ)はこの中間版でも2件passした(これまでのタスクと
  同じ扱い)。
- production実装: `script/tts_clients/models.py`
  (`SynthesisRequest`/`SynthesisResult`/`SpeakerInfo`/
  `EngineCapabilities`。10-tts-client-common-interface.md 4〜6節の
  request/response/capabilities形式を型化)、
  `script/tts_clients/base.py`(`TTSErrorCode`(spec 7節の共通error
  13種+9節のunsupported_engine)、`TTSClientError(code,
  engine_detail)`、`TTSClient`(`@runtime_checkable` Protocol:
  `check_connectivity`/`get_capabilities`/`list_speakers`/
  `synthesize`)、`MockTTSClient`(扱う範囲の「mock client」相当。
  外部接続なしの決定的実装で、speaker_idでのみ解決し
  display_nameには依存しない))、`script/tts_clients/registry.py`
  (`TTSClientRegistry.register/get`。未登録engineは
  `TTSClientError(code=unsupported_engine)`)。
  [[implementation_assumptions.md]]に仮定を記録
  (STEP4スタブの`check_connectivity`命名を承認済み仕様の
  `health_check`より優先した判断、`get_capabilities`を
  Protocolへ追加した判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 298 passed, 23 deselected, 133 xfailed(予期しないfailなし、
  TASK-PIPELINE-001完了時点の288から+10)。
- 文書修正: `docs/commands/tts.md`(担当分。`TASK-TTS-001`の2test file
  について`現在のダンプでは欠落`を`本実装済み(10 case pass)`へ置換。
  他タスク(`TASK-VOICEVOX-001`/`TASK-AUDIO-001`/`TASK-COEIR-001`)分の
  記述は、それぞれ「未着手(STEP3のまま)」「blocked、実装しない」という
  正確な現状に置換したが、それらのタスク自体は実装していない。
  `rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands/tts.md`
  で該当なしを確認)。

### TASK-VOICEVOX-001 完了(external_gate、通常テストのみ確認済み)

- 対象: `tests/test_voicevox_client.py`(TC-01,03,05,07,09の5 case +
  TC-11 integration_smoke)、`tests/test_voicevox_adapter.py`
  (TC-02,04,06,08,10の5 case + TC-12 integration_live)。
  `documentation_repair_ownership: []`(担当分は`docs/commands/tts.md`
  だが本タスク自体は空リストのため文書更新は対象外)。
- Red確認: `VoicevoxHttpClient.check_connectivity`/`.list_speakers`/
  `.create_audio_query`/`.synthesize_wave`/`.merge_waves`、
  `VoicevoxAdapter.synthesize`の本体のみ`NotImplementedError`化した
  中間版で10 failed(全件import error・構文errorなし、TC-11/TC-12は
  integration_smoke/liveのため対象外)。既存legacy実装
  (`check_voicevox_running`/`create_audio_query`/`apply_voice_settings`
  /`synthesize_wave`/`merge_wav_bytes`/`split_text_for_voicevox`/
  `text_to_voicevox_wav`/`main`)は完全に無変更のまま維持。
- production実装: `script/tts_clients/voicevox/client.py`
  (`ConnectivityResult`、`VoicevoxHttpClient`が`TASK-TTS-001`の
  `TTSClient`契約へ適合: `check_connectivity`は`/speakers`の
  HTTP/JSON schemaを確認し、壊れたspeaker一覧は例外でなく
  `available=False`で返す(局所disable)。`list_speakers`は
  `/speakers`応答を共通`SpeakerInfo`(`speaker_id`=style ID文字列、
  表示名は別フィールド)へ変換。`create_audio_query`/
  `synthesize_wave`はtimeout/非音声応答/4xxを`TTSClientError`の
  該当codeへ変換。`merge_waves`は既存`merge_wav_bytes`を再利用し
  `VoicevoxClientError`を`TTSClientError(audio_format_mismatch)`へ
  変換)、`script/tts_clients/voicevox/adapter.py`
  (`VoicevoxAdapter.synthesize(request)`: 共通`SynthesisRequest`の
  parametersをVOICEVOXのspeedScale等へ適合、`split_text_for_voicevox`
  で分割、`merge_waves`で結合、結果WAVのframerate/channelsを
  `wave`標準ライブラリで読み取りSynthesisResultへ反映)。
  `tests/conftest.py`の`voicevox_connectivity_gate` placeholder
  fixtureも実装した(`TASK-OCR-001`/`TASK-AI-001`と同様の1対1専用
  fixture、`VOICEVOX_URL`未設定はskip、設定済みで疎通不能はfail)。
  [[implementation_assumptions.md]]に仮定を記録(STEP4スタブの
  module-level `list_speakers()`関数signatureを、`TTSClient`
  Protocolに適合させるためinstance methodへ変更した判断)。
- 対象テスト結果: 10 passed(TC-01〜10、外部接続なし)。
- 外部疎通: `TASK-VOICEVOX-001`のintegration_smoke(TC-11)/
  integration_live(TC-12)は、この環境に`VOICEVOX_URL`が設定されず
  実際のVOICEVOX Engineも起動していないため未確認のまま(既定skip)。
  `WALKWISE_RUN_INTEGRATION_SMOKE`/`WALKWISE_RUN_INTEGRATION_LIVE`を
  設定しても、`voicevox_connectivity_gate`が`require_environment`で
  安全にskipすることを確認した(秘密値・実接続なし)。
- 全体回帰: 308 passed, 23 deselected, 123 xfailed(予期しないfailなし、
  TASK-TTS-001完了時点の298から+10)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外。
  `tts.md`は`TASK-TTS-001`完了時にすでに本タスクの現状(未着手→
  今回で本実装済み)を先行して部分反映していたが、担当タスクとしての
  正式な更新責任は`TASK-TTS-001`にあり、本タスクでは再修正しない)。

### TASK-AUDIO-001 完了

- 対象: `tests/test_audio_synthesis.py`(TC-01,04,07,10の4 case)、
  `tests/test_audio_cache.py`(TC-02,05,08の3 case)、
  `tests/test_audio_preview.py`(TC-03,06,09の3 case)。
  `documentation_repair_ownership: []`のため文書更新は対象外。
- 横断変更: `script/tts_clients/models.py`の`SynthesisResult`へ
  `audio_bytes: bytes | None = None`を追加(既存フィールドは無変更、
  既定値ありの追加のみ)。`script/tts_clients/voicevox/adapter.py`の
  `VoicevoxAdapter.synthesize()`が結合済みWAV bytesを
  `audio_bytes`へ設定するよう1行追加。理由: 本タスクの扱う範囲に
  明記された「atomic output」を実装するには、合成済み音声の
  生bytesを受け取る手段が必須だが、`TASK-TTS-001`/
  `TASK-VOICEVOX-001`完了時点の`SynthesisResult`にはbytesを運ぶ
  フィールドがなかった。追加後、`TASK-TTS-001`(10 case)・
  `TASK-VOICEVOX-001`(10 case、外部接続なし分)を再実行し、
  全件pass・回帰なしを確認した。
- Red確認: dataclass shape(`AudioCacheKey`/`CachedAudio`/
  `SegmentAudioPart`/`SegmentAudio`/`PreviewRequest`/`PreviewAudio`の
  `__post_init__`型検証)は保持しつつ、`AudioCache.key`/`.get`/`.put`、
  `SegmentSynthesizer.synthesize`、`PreviewService.generate`の本体
  のみ`NotImplementedError`化した中間版で10 failed(全件import
  error・構文errorなし)を確認。
- production実装: `script/audio/cache.py`(`AudioCache.key()`は
  text/tts_text/voice_profile_id/voice_content_hash(revision込み)/
  engine_versionから決定的にSHA-256を計算、同一text・異なるrevisionで
  異なるkeyになる)、`script/audio/synthesis.py`
  (`SegmentSynthesizer.synthesize(script, profile)`: `script.stage
  != "verified"`を`PERMISSION_DENIED`で拒否(未承認script本番禁止)、
  `tts_text`優先でTTS入力を選択、300文字超は句読点優先の内部part
  (`<segment_id>-partNNN`)へ決定的に分割、cacheにhitしたsegmentは
  `TTSClient.synthesize`を一切呼ばない(部分再生成)、`audio_bytes`が
  ある場合は一時ファイル→`os.replace`のatomic writeで出力)、
  `script/audio/preview.py`(`PreviewService.generate(request)`:
  segment_audioのduration/sample_rateを検証してから合算し、
  (project_id, chapter_id)ごとの内部version counterで常に新しい
  `preview_id`/`output_path`を生成(既存を上書きしない))。
  [[implementation_assumptions.md]]に仮定を記録
  (`SynthesisResult.audio_bytes`追加の判断、内部part分割ロジックを
  VOICEVOX固有splitterを再利用せず本タスク専用に実装した判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 318 passed, 23 deselected, 113 xfailed(予期しないfailなし、
  TASK-VOICEVOX-001完了時点の308から+10)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-AUDIO-002 完了(external_gate、通常テストのみ確認済み)

- 対象: `tests/test_audio_validation.py`(TC-01,03,05,07の4 case +
  TC-09 integration_smoke)、`tests/test_audio_thresholds.py`
  (TC-02,04,06,08の4 case + TC-10 integration_live)。
  `documentation_repair_ownership: ["docs/commands/audio-validation.md"]`。
- Red確認: dataclass shape(`LoudnessThreshold`/`PeakThreshold`/
  `TextDurationRatioThreshold`/`ThresholdEvidence`/`AudioThresholdSet`/
  `RuntimeCheckResult`/`AudioMeasurement`/`ValidationIssue`/
  `ValidationReport`の`__post_init__`型検証)は保持しつつ、
  `AudioThresholds.load`/`.validate_approval`、
  `AudioMeasurementAdapter.check_runtime`/`.measure`、
  `AudioValidator.validate`の本体のみ`NotImplementedError`化した
  中間版で8 failed(全件import error・構文errorなし、TC-09/TC-10は
  integration_smoke/liveのため対象外)。
- production実装: `script/audio/thresholds.py`
  (`AudioThresholdSet`は13-audio-validation.md 5節/
  audio-validation-thresholds.md 5.3節の仮値をそのまま転記した既定値。
  `status="approved"`構築時、`evidence.measured=False`または
  `sample_count<minimum_required_speakers`(既定2)なら
  `__post_init__`で拒否(構造的二重防御)。`AudioThresholds
  .validate_approval()`が正式な昇格経路として同じ検証を行い、
  合格時のみ`status="approved"`のcopyを返す)、
  `script/audio/measurements.py`(`AudioMeasurementAdapter
  .check_runtime()`は`ffmpeg -version`/`ffprobe -version`を
  injectable runner経由で実行し起動可否だけ確認(外部ffmpeg
  adapter境界)。`.measure(path)`はPython標準`wave`モジュールで
  WAVのduration/sample_rate/channelsを読み、生PCMから
  peak_dbfs/silence_ratioを決定的に計算(ffmpeg不要、LUFS等の
  複雑な心理音響測定は対象外としNone許容)。ファイル欠落・0byte・
  RIFF/WAVEとして読めない場合はAppErrorを送出)、
  `script/audio/validation.py`(`AudioValidator.validate(path, text,
  thresholds)`は測定失敗を常にfail(warningへ格下げしない)、
  duration不足・大半無音もfail、clippingはreview_required、
  長い無音・文字数毎秒範囲外はwarningとし、fail>review_required>
  warning>passの優先順位で最終status決定(warning/review累積規則は
  保守的、より軽い判定が重い判定を隠さない))。
  `tests/conftest.py`の`ffmpeg_connectivity_gate` placeholder
  fixtureも実装した(`TASK-OCR-001`/`TASK-AI-001`/`TASK-VOICEVOX-001`
  と同様の1対1専用fixture、`FFMPEG_PATH`/`FFPROBE_PATH`未設定は
  skip、設定済みで起動不能はfail)。
  [[implementation_assumptions.md]]に仮定を記録(LUFS実測を実装せず
  Noneのまま許容した判断、approved昇格をdataclass構築時の防御と
  `validate_approval()`の二重チェックにした設計)。
- 対象テスト結果: 8 passed(TC-01〜08、外部接続なし)。
- 外部疎通: `TASK-AUDIO-002`のintegration_smoke(TC-09)/
  integration_live(TC-10)は、この環境に`FFMPEG_PATH`/`FFPROBE_PATH`
  が設定されずffmpeg/ffprobe実行体も導入されていないため未確認の
  まま(既定skip)。
- 全体回帰: 326 passed, 23 deselected, 105 xfailed(予期しないfailなし、
  TASK-AUDIO-001完了時点の318から+8)。
- 文書修正: `docs/commands/audio-validation.md`(担当分。
  `現在のダンプでは欠落`という揮発性注記を削除し、`CURRENT_STATE.md`
  参照へ置換。実機能確認コマンドが誤って`test_audio_validation.py`を
  対象にしていた不整合(TC-10は`test_audio_thresholds.py`が正)を
  修正し、対応関係を明記。対象8 caseがすべてpassする旨とTC-09/TC-10
  未確認を記録。
  `rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands/audio-validation.md`
  で該当なしを確認)。

### TASK-AUDIO-003 完了

- 対象: `tests/test_production_manifest.py`(TC-03,06,09)、
  `tests/test_audio_packaging.py`(TC-01,04,07,10)、
  `tests/test_build_pipeline.py`(TC-02,05,08)の計10 case。
  `documentation_repair_ownership: ["docs/commands/audio-packaging.md"]`。
  外部接続(ffmpeg実行)は本タスク単独の対象外(`mp3_encoder`は
  fake encoderをtestで注入、実ffmpeg encoderは呼び出されない)。
- Red確認: dataclass shape(`ManifestOutput`/`ProductionManifest`/
  `ChapterAudioInput`/`ChapterMetadata`/`ChapterArtifact`/
  `ChapterBuildContent`/`BuildResult`の`__post_init__`型検証)は
  保持しつつ、`ProductionManifest.validate`/`.to_mapping`、
  `ChapterPackager.package`、`BuildPipeline.run`の本体のみ
  `NotImplementedError`化した中間版で10 failed(全件import error・
  構文errorなし)。
- production実装: `script/schemas/production_manifest.py`
  (`ManifestOutput`/`ProductionManifest`は14-audio-packaging.md
  10節のmanifest JSON schemaに対応、`source_segments`重複を
  構築時・`.validate()`双方で検出、`.to_mapping()`でJSON化)、
  `script/audio/packaging.py`(`ChapterPackager.package(wavs,
  metadata)`はmanifest順(`order`)で結合、`voice_content_hash`が
  segment間で異なる場合は改変とみなし黙って互換扱いせずerror、
  破損WAV・framerate/channels不一致は`_merge_wavs()`で常にerror
  (warningへ格下げしない)、`mp3_encoder`はcallable必須注入
  (既定の実ffmpeg encoderを自動配線しない設計とし、本タスクの
  自動テストが実ffmpegを呼ぶ経路を持たないことを保証)。
  `ChapterPackager`自体はdiskへ書き込まず`mp3_bytes`のみ返す)、
  `script/pipelines/build.py`(`BuildPipeline.run(build_request_id)`
  は承認gate確認(`approval_gate_check`、既定True)→ 未承認なら
  `chapter_content_provider`を一切呼ばず`PERMISSION_DENIED`
  (副作用ゼロを`call_count`で実測確認)→ mp3/text各形式を
  `ArtifactService.register()`(既存の`TASK-ARTIFACT-001`成果)経由で
  atomic登録(`ChapterPackager`や`BuildPipeline`自身では atomic
  write を再実装せず、`ArtifactService.register()`→
  `copy_immutable()`の既存atomic書込み+hash計算+version管理を
  再利用する設計に変更)→ `ProductionManifest`を組み立て
  `.validate()`→ `BuildResult`を返す。versionは
  `ArtifactService.list_versions()`(公開API)から算出し
  `artifact_id`/`destination_relative`へ埋め込むことで、再実行時に
  version番号のみ変化しfileが衝突しないことを保証)。
  [[implementation_assumptions.md]]に仮定を記録
  (`ArtifactService.register()`への委譲設計、`mp3_encoder`必須注入
  かつ既定実装なしの設計、`voice_content_hash`不一致を改変検出として
  扱う判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 336 passed, 23 deselected, 95 xfailed(予期しないfailなし、
  TASK-AUDIO-002完了時点の326から+10)。
- 文書修正: `docs/commands/audio-packaging.md`(担当分。揮発性の
  古い件数注記を除去し、production/対象10 case全passの実測結果を
  記載)。

## Phase5完了(TTS・Pipeline・Audio)

- 完了タスク: TASK-NARRATION-001, TASK-PIPELINE-001, TASK-TTS-001,
  TASK-VOICEVOX-001(external_gate、通常10 case確認済・外部2件未確認)、
  TASK-AUDIO-001, TASK-AUDIO-002(external_gate、通常8 case確認済・
  外部2件未確認), TASK-AUDIO-003 の計7タスク。
- 対象case数(累計、Phase5開始時308 passedから): 336 passed
  (Phase5で+28)。
- 全体回帰: 336 passed, 23 deselected, 95 xfailed, 予期しないfailなし。
- 外部接続未確認(既定skip、この環境に該当runtime/変数なし):
  `TASK-VOICEVOX-001`(VOICEVOX Engine, `VOICEVOX_URL`未設定)、
  `TASK-AUDIO-002`(ffmpeg/ffprobe, `FFMPEG_PATH`/`FFPROBE_PATH`未設定)。
  いずれも設定済みかつ到達不能の場合はfailする実装(skipで隠さない)。
- 置いた仮定: `implementation_assumptions.md`にPhase5内の各タスク分を
  個別記録済み(`SynthesisResult.audio_bytes`追加、TTS共通層での
  engine非依存part分割、LUFS未実装、approved二重防御、
  `ArtifactService.register()`への委譲等)。
- 次の開始タスク: Phase6 `TASK-WORKER-001`(Worker契約・dispatch)。

## Phase6: Desktop・Worker・UI

### TASK-WORKER-001 完了

- 対象: `tests/test_worker_protocol.py`(TC-01,03,05,07,09)、
  `tests/test_worker_dispatch.py`(TC-02,04,06,08,10)の計10 case。
  `documentation_repair_ownership: ["docs/commands/worker.md"]`
  (`TASK-WORKER-002`と共有する文書のため、本タスクの担当分のみ更新)。
- Red確認: `WorkerEvent.__init__`/`.to_json_line`、`WorkerRequest.__init__`/
  `.from_json_line`、`HandlerRegistry.register`/`.dispatch`、`main`の本体のみ
  `NotImplementedError`化した中間版で10 failed(全件import error・構文
  errorなし)。
- production実装: `script/worker/protocol.py`(`WorkerEvent`/`WorkerRequest`は
  21-electron-python-worker-interface.md 5.2/5.3節のrequest/eventを
  `**data`形式で保持する既存STEP4 scaffoldの形を維持しつつ、構築時に
  業務検証を行う: `WorkerRequest`は`job_id`/`job_type`必須、
  `WorkerEvent`は`event`が既知種別(started/progress/artifact/warning/
  error/completed)必須、`artifact`eventは`path`必須かつ5.7節の
  「相対pathのみ」を`PurePosixPath`/`PureWindowsPath`両方で絶対path
  判定し拒否。`to_json_line()`/`from_json_line()`で1行1JSONの
  シリアライズ/parseを提供)、`script/worker/handlers.py`
  (`HandlerRegistry.register/dispatch`は未登録job_typeへ例外を投げず
  `error` eventを返してprocessを継続させ、`dispatch`はstarted→
  (handler由来のprogress/artifact等)→completedの順でeventを生成し、
  handler内の`WorkerError`/予期しない例外を`error` eventへ変換する。
  progressの`current`が直前より逆行した場合も`error`へ変換し
  「完了後に進捗を逆行させない」契約を能動的に強制する)、
  `script/worker/cli.py`(`main(stdin, stdout, *, registry=None,
  stderr=None) -> int`は1行を1requestとしてparseし、handlerの技術ログ
  (`log`callback)をstdoutと分離した`stderr`へ書き、各eventをstdoutへ
  1行1JSONでflushする。requestのJSON不正はそのrequestのみ`error`event
  にして次のrequestの処理を継続する(1件の不正で全体を止めない))。
  [[implementation_assumptions.md]]に仮定を記録(`WorkerRequest`/
  `WorkerEvent`の`**data`保持形状をSTEP4 scaffold通り維持した判断、
  `main`が1呼び出しで複数requestを順次処理できる設計にした判断、
  progress逆行を能動的にerror化した判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 346 passed, 23 deselected, 85 xfailed(予期しないfailなし、
  Phase5完了時点の336から+10)。
- 文書修正: `docs/commands/worker.md`(担当分。`TASK-WORKER-001`分の
  対象ファイル欄・成功条件を実測結果へ更新。`TASK-WORKER-002`分は
  未着手のまま記述を維持)。

### TASK-WORKER-002 完了

- 対象: `tests/test_worker_cancellation.py`(TC-01,03,05,07,09)、
  `tests/test_worker_runtime_failures.py`(TC-02,04,06,08,10)の計10 case。
  `documentation_repair_ownership: []`(対象外)。
- Red確認: `CancellationToken.__init__`(shapeとして保持)は維持しつつ
  `.requested`/`.raise_if_cancelled`の本体のみ、`WorkerRuntime.__init__`
  (shapeとして保持)は維持しつつ`.run`の本体のみ、`recover_after_abnormal_exit`
  本体のみを`NotImplementedError`化した中間版で10 failed(全件import
  error・構文errorなし。TC-08の`WorkerRuntime(None)`検証は`__init__`が
  未stubbのため引き続き正しく`WorkerError`を送出し、後続の`.run()`呼出し
  でNotImplementedErrorにより同テストが失敗することを確認)。
- production実装: `script/worker/cancellation.py`(`CancellationToken`は
  外部から注入された`is_requested: Callable[[], bool]`を読み取るだけの
  薄いラッパーとし、内部に可変状態を持たない。cancel要求の発生源
  (Electron側のOS終了シグナル相当)はテスト側が注入する)、
  `script/worker/runtime.py`(`WorkerRuntime(handler, *, timeout_seconds=
  None, grace_period_seconds=1.0, clock=None, cleanup=None)`は
  `handler: Callable[[WorkerRequest, CancellationToken], Iterator[
  WorkerEvent]]`を構築時に注入する設計とし(STEP4 scaffoldの
  `*args/**kwargs`から具体的signatureへ、`TASK-AUDIO-003`の
  `ChapterPackager`と同型の進化)、`.run(request, token)`は
  started→(handler中継)→completed/cancelled/errorの順でeventを生成する。
  `token.requested()`検知時は`cancel_requested`eventを出し
  `grace_period_seconds`分の猶予を与える。猶予内にhandlerが自ら
  `token.raise_if_cancelled()`で`WorkerError(code="cancelled")`を送出
  すれば`cancelled`(`forced=False`)、猶予超過まで停止しなければ
  `generator.close()`で強制終了し`cancelled`(`forced=True`)を出す
  (force terminate契約)。timeout超過も同様に`generator.close()`+
  cleanup+`error`(`code="timeout"`)へ変換する。`recover_after_abnormal_exit
  (job)`は22-job-lifecycle-and-recovery.md 5.6節どおり、`running`のまま
  残ったJobを常に`failed`(`reason="stale_job_detected_on_startup"`)へ
  復旧判断する純粋関数とし、filesystem/DBへの副作用を一切持たない
  (呼び出し側が`discard_partial_artifacts=True`を見て実際の破棄・
  未登録を行う))。
  `script/worker/protocol.py`の`_VALID_EVENT_TYPES`へ`cancel_requested`/
  `cancelled`を追加(既存の6種別に対する後方互換な追加。追加後に
  `TASK-WORKER-001`の対象10 caseを再実行し全件pass・回帰なしを確認済み)。
  [[implementation_assumptions.md]]に仮定を記録(`WorkerRuntime`の
  handler注入設計、grace period/force terminateの意味づけ(決定的な
  `clock`注入によるテスト設計)、`recover_after_abnormal_exit`を副作用
  なしの純粋決定関数とした判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: 356 passed, 23 deselected, 75 xfailed(予期しないfailなし、
  TASK-WORKER-001完了時点の346から+10)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-DESKTOP-001 完了

- 対象: `electron/tests/main_security.test.ts`(TC-01,03,05,07,09)、
  `electron/tests/preload_contract.test.ts`(TC-02,04,06,08)の計9 case。
  `documentation_repair_ownership: []`(対象外)。Python側の変更なし。
- Red確認: `createMainWindow`/`buildWalkwiseApi`/`installPreloadBridge`/
  `main`(renderer bootstrap)の本体のみ`throw new Error("STEP4
  intermediate stub: ...")`化した中間版でVitestを実行し、6 failedを
  確認(全件import error・型errorなし)。TC-03(静的scan)・TC-04
  (package.json直接読取り)は本体呼び出し自体を伴わないため元々pass、
  TC-08(必須入力欠落)はstubが無条件でthrowするため`toThrow()`assertion
  が引き続きpassする(本セッション全体で確立した「無条件throwに対する
  必須入力検証テストは中間版でも合法的にpassしうる」という既存precedent
  と同種、3件のpass自体は正しいRed確認として扱った)。
- production実装: `electron/main/index.ts`(`createMainWindow(options)`は
  `preloadPath`/`rendererEntry`必須検証後、20-electron-desktop-
  architecture.md 5.4節どおりの固定`webPreferences`
  (`nodeIntegration:false, contextIsolation:true, sandbox:true`)を
  構築し、`browserWindowFactory`(既定は実`BrowserWindow`)へ注入する
  DI設計とした)、`electron/preload/index.ts`(`ALLOWED_CHANNELS`は
  20-electron-desktop-architecture.md 5.6節の16固定IPCチャネル名を
  そのまま列挙し、`buildWalkwiseApi(ipc)`はchannelごとに型付き
  method(`project.list/create/get`, `source.register`,
  `approval.list/approve/requestChanges`, `buildRequest.create`,
  `job.start/get/subscribeProgress/cancel`, `artifact.list/openFolder`,
  `voice.listEngines/preview`)だけを持つobjectを返す(任意channel・
  生ipcRenderer・fs・child_processは一切公開しない)。
  `installPreloadBridge(bridge, ipc)`が`contextBridge
  .exposeInMainWorld("walkwise", api)`を呼ぶ。実Electron preload実行時
  (`process.versions.electron`存在時)のみ自動的に`installPreloadBridge
  (contextBridge, ipcRenderer)`を呼ぶ末尾guardを追加し、Node/vitest実行
  時は発火しない)、`electron/renderer/main.ts`(`main(options)`は
  `mountSelector`必須検証後、`rootComponent`(既定は最小限のplaceholder
  Vue component)を`appFactory`(既定は実`createApp`)経由でmountする。
  `fs`/`child_process`等のNode APIを一切importしない)。`package.json`は
  既存のbuild/typecheck/test/package scriptsがそのまま契約を満たすため
  変更なし。
- 対象テスト結果: 9 passed。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし、
  本タスクはPython非対象)。TypeScript型検査success、error 0件。
  Vitest 16 test files/76 tests、全passed(このタスクの9 caseが
  `test.fails`から実assertionへ解除され、他15 test filesの67 caseは
  引き続きplaceholderのまま)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。
- 備考: preload/index.tsの実装中、docコメント内に`TASK-UI-*/TASK-
  DESKTOP-003`という表記を書いたところ`*/`がJSDocブロックコメントを
  早期終了させ`electron/renderer/main.ts`でTypeScript構文errorになった
  (自己発見・`npm run typecheck`で検出し、表記を`TASK-UI-001〜005や
  TASK-DESKTOP-003`へ修正して解消)。

### TASK-DESKTOP-002 完了(external_gate、通常テストのみ確認済み)

- 対象: `electron/tests/bootstrap.test.ts`(TC-01,03,05,07,09 + TC-11
  integration_smoke)、`electron/tests/worker_manager.test.ts`
  (TC-02,04,06,08,10 + TC-12 integration_live)の計10 case(+2未確認)。
  `documentation_repair_ownership: []`(対象外)。
- Red確認: `WorkerManager`のconstructor検証(shape、`command`/`spawn`
  必須)は保持しつつ`.start`/`.stop`/`.request`の本体のみ、
  `resolvePythonExecutable`本体のみ、`bootstrapApplication`本体のみを
  `throw new Error("STEP4 intermediate stub: ...")`化した中間版で
  Vitestを実行し、9 failed(全件STEP4 stub由来、import/構文errorなし)。
  TC-08(必須入力欠落)は`bootstrapApplication`の中間stubも
  `WorkerManager`constructorの実検証も両方throwするため引き続きpass
  (既存precedentと同種)。TC-11/TC-12は環境変数未設定のため元々skip。
- production実装: `electron/main/database.ts`
  (`openApplicationDatabase(path, options)`は`connectionFactory`を
  必須注入とし、実sqlite driverの選定自体は対象外として保留)、
  `electron/main/worker_manager.ts`(`WorkerManager`は`spawn`必須注入の
  DIで実subprocessを起動、stdout を`\n`区切りでJSON Lines parseし
  `job_id`でpending requestと対応付け、`completed`/`cancelled`は
  resolve、`error`はreject、不正JSON行はstderr相当のログとして無視し
  processは継続。`stop()`は冪等、processは常に1回だけkillする。
  `resolvePythonExecutable(options)`は`WALKWISE_PYTHON_EXECUTABLE`
  環境変数を優先し、なければplatform既定(win32:"python", 他:"python3")
  を返す)、`electron/main/bootstrap.ts`(`bootstrapApplication(options)`
  はdata root確保→backup→DB open→migration→stale job recovery→
  worker起動+health確認(既定2回retry)の順で初期化し、migration失敗時は
  DBを閉じてworkerを一切起動せずerrorを送出、worker health失敗時は
  retry後にworker停止・DB close・診断可能なerrorを送出する。戻り値の
  `shutdown()`はworker停止+DB closeを冪等に行う)。
  横断変更として`script/worker/cli.py`(`TASK-WORKER-001`所有)へ
  `if __name__ == "__main__":`entrypointを追加した(`main(stdin,
  stdout)`自体の契約は変更しない純粋な追加、smoke/live gate用の実行
  可能entrypointとして必要だったため。追加後に`TASK-WORKER-001`/
  `TASK-WORKER-002`の全20 caseを再実行し回帰なしを確認済み)。
  [[implementation_assumptions.md]]に仮定を記録
  (`connectionFactory`必須注入かつ実sqlite driver未選定、
  `WorkerManager`の`spawn`必須注入、`WALKWISE_PYTHON_EXECUTABLE`という
  新規環境変数名の採用、cli.pyへの`__main__`entrypoint追加)。
- 対象テスト結果: 10 passed(TC-01〜10、外部接続なし)。
- 外部疎通: `TASK-DESKTOP-002`のintegration_smoke(TC-11)/
  integration_live(TC-12)は、この環境に`WALKWISE_RUN_INTEGRATION_SMOKE`
  /`WALKWISE_RUN_INTEGRATION_LIVE`が設定されないため未確認のまま
  (既定skip)。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし、
  cli.py entrypoint追加は純粋な追加でテスト結果に影響しない)。
  TypeScript型検査success、error 0件。Vitest 16 test files/76 tests、
  74 passed + 2 skipped(このタスクの10 caseが`test.fails`から実
  assertionへ解除され、2 caseが正しくskip、残り55 caseは引き続き
  placeholder)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-UI-001 完了

- 対象: `electron/tests/project_ipc.test.ts`(TC-01,03,05,07,09)、
  `electron/renderer/tests/ProjectList.test.ts`(TC-02,04,06,08)の計9
  case。`documentation_repair_ownership: []`(対象外)。
- 横断的な基盤整備: Vue SFCの実DOM testが可能な既存tooling
  (`@vue/test-utils`、`jsdom`、`@vitejs/plugin-vue`)が`package.json`に
  一切なかったため、devDependenciesへ追加し`vitest.config.ts`を新規
  作成した(`plugins: [vue()]`、既定environment "node"、DOM必須の
  testファイルは`/** @vitest-environment jsdom */`docblockで個別に
  jsdomへ切り替え)。追加後に既存16 test filesを再実行し回帰なしを
  確認済み。これがないと「静的文字列が存在するだけのテスト」しか
  書けず、本タスク以降のUI-*タスク全体が禁止事項に抵触するため、
  必要な基盤整備と判断した。
- Red確認: `registerProjectIpcHandlers`本体のみ、`listProjects`/
  `createProject`本体のみを`throw`化。`ProjectList.vue`は`<script
  setup>`冒頭に`throw`文を追加してmount自体を失敗させる中間版とした
  (テストがvi.spyOnで`listProjects`/`createProject`をmock置換するため、
  api層だけをstub化しても検出できず、component自体をstub化する必要が
  あった)。Vitestで8 failed(全件STEP4 stub由来)、TC-08は
  `registerProjectIpcHandlers`の中間stubも無条件throwのため引き続き
  pass(既存precedentと同種)。
- production実装: `electron/main/ipc/projects.ts`
  (`registerProjectIpcHandlers(context)`はcontext/ipcMain/
  projectService必須検証後、`project:list`/`project:create`を登録し、
  createは`title/domain/purpose/usagePurpose/targetAudienceDescription`
  必須文字列+`sourceStrategy`1件以上という01-project-list-and-create.md
  4/8節のvalidationを副作用前に行う)、`electron/renderer/api/projects.ts`
  (`listProjects`/`createProject`は`window.walkwise.project`を既定注入
  としつつ、testからfake apiを注入できる設計)、
  `electron/renderer/screens/ProjectList.vue`(empty/loading/error/
  successの4状態、必須項目+source_strategy未選択時はdisabled、
  Enterは有効時のみ作成を実行、フォーム項目に順序どおりの
  `tabindex`を明示)。
  [[implementation_assumptions.md]]に仮定を記録(Vue testing基盤の
  追加、ProjectList.vueが未実装のTASK-UI-005側router/store/AppShellへ
  依存せず独立して動作する設計)。
- 対象テスト結果: 9 passed。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし)。
  TypeScript型検査success。Vitest 16 test files/76 tests、74 passed +
  2 skipped(このタスクの9 caseが`test.fails`から実assertionへ解除、
  残り46 caseは引き続きplaceholder)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-UI-002 完了

- 対象: `electron/tests/source_approval_ipc.test.ts`(TC-01,03,05,07,09)、
  `electron/renderer/tests/ProjectWorkspace.test.ts`(TC-02,04,06,08)の
  計9 case。`documentation_repair_ownership: []`(対象外)。
- Red確認: `registerSourceIpcHandlers`/`registerApprovalIpcHandlers`
  本体のみ、`ProjectWorkspace.vue`は`<script setup>`冒頭throwで中間版化。
  Vitestで8 failed(全件STEP4 stub由来)、TC-08は無条件throwのため
  引き続きpass(既存precedentと同種)。
- production実装: `electron/main/ipc/sources.ts`
  (`registerSourceIpcHandlers(context)`は`source:register`を登録し、
  02-project-workspace-and-source-import.md 4/8/13節どおり
  `mediaType`が`text/pdf/image`以外なら`unsupported_media_type`で
  副作用前に拒否)、`electron/main/ipc/approvals.ts`
  (`registerApprovalIpcHandlers(context)`は`approval:list/approve/
  request-changes`を登録し、差し戻し理由の必須検証を10節どおり実施)、
  `electron/renderer/screens/ProjectWorkspace.vue`(Source 5状態の
  日本語表示+review/retry導線、MVP対象外形式(epub/kindle/video)を
  選択肢に一切表示しない、差し戻し理由の空値をUI側でも拒否)。
  型のみを`ProjectWorkspace.types.ts`(新規、この`.vue`とtestの両方が
  参照)へ切り出した。
  [[implementation_assumptions.md]]に仮定を記録(`.vue`のnamed export
  がplain tscで型付けできない問題への対処、承認済みIPCチャネル一覧に
  ない「再処理」を`source:register`の再呼び出しとして解釈した判断、
  ProjectWorkspace.vueをprops駆動にした設計)。
- 対象テスト結果: 9 passed。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし)。
  TypeScript型検査success。Vitest 16 test files/76 tests、74 passed +
  2 skipped(このタスクの9 caseが実assertionへ解除、残り37 caseは
  引き続きplaceholder)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-UI-003 完了

- 対象: `electron/tests/build_voice_ipc.test.ts`(TC-01,03,05,07,09)、
  `electron/renderer/tests/BuildSettings.test.ts`(TC-02,04,06,08)の計9
  case。`documentation_repair_ownership: []`(対象外)。
- Red確認: `registerVoiceIpcHandlers`/`registerBuildIpcHandlers`本体の
  みthrow化、`BuildSettings.vue`は`<script setup>`冒頭throwで中間版化。
  Vitestで8 failed(全件STEP4 stub由来)、TC-08は無条件throwのため
  引き続きpass(既存precedentと同種)。
- production実装: `electron/main/ipc/voice.ts`
  (`registerVoiceIpcHandlers(context)`は`voice:list-engines`(engine
  未接続時は空speakers一覧を正常結果として返す、例外にしない)と
  `voice:preview`(speakerId/text必須)を登録)、
  `electron/main/ipc/builds.ts`(`registerBuildIpcHandlers(context)`は
  `build-request:create`(出力形式1件以上必須、mp3を含む場合は
  voiceProfileId必須、03-build-settings.md 4/8節どおり)と`job:start`
  (`approvalGateChecker.isSatisfied()`を先に確認し、未充足なら
  `approval_gate_not_satisfied`を送出してbuildService.startJobを
  一切呼ばない、22-job-lifecycle-and-recovery.md 5.5節と一致)を登録)、
  `electron/renderer/screens/BuildSettings.vue`(text-only選択時は
  voice controls全disabledで制作開始可能、mp3選択時はspeaker未選択の
  間disabled、VOICEVOX未接続時はエラー+再確認導線を表示しmp3選択自体を
  実質不可にする、COEIROINK/M4B/EPUBは一切表示しない)。型を
  `BuildSettings.types.ts`(新規)へ切り出した(`ProjectWorkspace.types.ts`
  と同じ理由)。
  [[implementation_assumptions.md]]に仮定を記録(承認ゲート確認を
  `job:start`側で行い、`ApprovalGateCheckerLike`をDIとした設計判断)。
- 対象テスト結果: 9 passed。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし)。
  TypeScript型検査success。Vitest 16 test files/76 tests、74 passed +
  2 skipped(このタスクの9 caseが実assertionへ解除、残り28 caseは
  引き続きplaceholder)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-UI-004 完了

- 対象: `electron/tests/job_artifact_ipc.test.ts`(TC-01,03,05,07,09)、
  `electron/renderer/tests/JobsAndArtifacts.test.ts`(TC-02,04,06,08)の
  計9 case。`documentation_repair_ownership: []`(対象外)。
- Red確認: `registerJobIpcHandlers`/`registerArtifactIpcHandlers`本体の
  みthrow化、`JobsAndArtifacts.vue`は`<script setup>`冒頭throwで中間版
  化。Vitestで8 failed(全件STEP4 stub由来)、TC-08は無条件throwのため
  引き続きpass(既存precedentと同種)。
- production実装: `electron/main/ipc/jobs.ts`(`registerJobIpcHandlers
  (context)`は`job:get/subscribe-progress/cancel/start`を登録し、
  04-job-progress.md 8節どおりcancelはqueued/runningのみ、再試行は
  failed/cancelledのみ許可(不正遷移は`invalid_job_transition`で永続
  状態を変更しない)。`job:subscribe-progress`は`event.sender.send
  ("job:progress-event", ...)`でprogressを配信する)、
  `electron/main/ipc/artifacts.ts`(`registerArtifactIpcHandlers
  (context)`は`artifact:list`(返る各Artifactの`filePath`が相対pathで
  あることを再検証)と`artifact:open-folder`を登録)、
  `electron/renderer/screens/JobsAndArtifacts.vue`(cancelは確認
  ダイアログ経由でのみIPCを呼ぶ、retryボタンはfailed/cancelledのみ
  有効、stale注記表示、技術detailは`<details>`で既定折り畳み、
  Artifactは`artifact_type`ごとに最新versionのみ表示(入力データ自体は
  変更しない))。型を`JobsAndArtifacts.types.ts`(新規)へ切り出した。
  [[implementation_assumptions.md]]に仮定を記録(cancel確認を2段階
  クリックで表現した設計、stale/技術detailの表示条件)。
- 対象テスト結果: 9 passed。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし)。
  TypeScript型検査success。Vitest 16 test files/76 tests、74 passed +
  2 skipped(このタスクの9 caseが実assertionへ解除、残り19 caseは
  引き続きplaceholder)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-UI-005 完了

- 対象: `electron/renderer/tests/navigation.test.ts`(TC-01,03,05,07,09)、
  `electron/renderer/tests/accessibility.test.ts`(TC-02,04,06,08)の計9
  case。`documentation_repair_ownership: []`(対象外)。これでUI-001〜005
  全5画面タスクが完了。
- Red確認: `resolveNavigation`/`AppStore.setError`本体のみthrow化、
  `AppShell.vue`は`<script setup>`冒頭throwで中間版化。Vitestで8 failed
  (全件STEP4 stub由来)、TC-05は`NAVIGATION_SCREENS`という静的定数のみを
  検証する内容で本体stub呼出しを経由しないため元々pass(前例と異なる
  性質だが正当なRed、`AppStateValidationError`という具体的例外型を
  求めるTC-08は逆に汎用`Error`との型不一致で正しくfailした)。
- production実装: `electron/renderer/router.ts`(`resolveNavigation
  (options)`は無効screen名・Project文脈欠落時に`projects-list`へ
  安全に戻す純粋関数。`NAVIGATION_SCREENS`は承認済み5画面
  (docs/screens/README.md 6節)を固定順序で列挙)、
  `electron/renderer/stores/app.ts`(`AppStore`はloading/currentProjectId/
  errorを一元管理し、`setError`は利用者向けmessageと技術detailを
  分離保持、message空値は副作用前に拒否)、
  `electron/renderer/components/AppShell.vue`(5画面へのnav button、
  errorがあればerror summaryへfocus移動(`watch(..., {immediate:true})`
  +`nextTick`)、aria-describedbyで技術detailと関連付け、技術detailは
  `<details>`で既定折り畳み、loading skeletonはrole="status")。
  型を`AppShell.types.ts`(新規)へ切り出した。
  [[implementation_assumptions.md]]に仮定を記録(focus管理の実装方式、
  screens/README.mdの5画面固定順序をNAVIGATION_SCREENSの正本とした判断)。
- 対象テスト結果: 9 passed。
- 全体回帰: Python 356 passed/23 deselected/75 xfailed(変化なし)。
  TypeScript型検査success。Vitest 16 test files/76 tests、74 passed +
  2 skipped(このタスクの9 caseが実assertionへ解除、残り10 caseは
  引き続きplaceholder。これでPhase6のUI画面5タスクはすべて実装完了)。
- 文書修正: なし(`documentation_repair_ownership: []`のため対象外)。

### TASK-DESKTOP-003 完了(external_gate、通常テストのみ確認済み)

- 対象: `tests/integration/test_mvp_flow.py`(TC-01,03,05,07,09 +
  TC-11 integration_smoke)、`electron/tests/e2e/mvp-flow.test.ts`
  (TC-02,04,06,08,10 + TC-12 integration_live)の計10 case(+2未確認)。
  `documentation_repair_ownership: ["docs/commands/end-to-end.md"]`
  (`TASK-E2E-001`と共有する文書のため、本タスクの担当分のみ更新)。
  Python側`script/integration/mvp_flow.py`、TypeScript側は
  `electron/tests/e2e/mvp-flow.test.ts`自身が契約上の"production"を
  兼ねる(契約のsource_filesに本fileが自ら列挙されている)。
- Red確認: Python側`run_mvp_flow`本体のみ`NotImplementedError`化した
  中間版でtests/integration/test_mvp_flow.pyを実行し5 failed(全件
  STEP4 stub由来、TC-11は既定skipのため対象外)。TypeScript側は
  別モジュールのstubが存在しないため、fake backend内の1箇所
  (`buildService.startJob`の出力formatsループを空配列に置換)を
  意図的に破壊してTC-02が正しく失敗することを確認(vacuousな
  passでないことの検証、既存precedentの通常Red確認とは異なる形だが
  同等の目的を満たす)、その後復元してGreenを再確認した。
- production実装: `script/integration/mvp_flow.py`
  (`run_mvp_flow(dependencies)`はProject作成→Source登録→承認gate
  確認→worker実行(再試行可能errorのみ上限回数内で再試行)→build実行
  という順序を制御する薄いorchestratorとし、各工程の実装(実IPC/DB/
  file/worker)は`MvpFlowDependencies`のcallableとして呼び出し側が
  注入する。承認未充足は`PERMISSION_DENIED`でworker/buildを一切
  開始しない)、`electron/tests/e2e/mvp-flow.test.ts`(既存の全IPC
  module(`projects/sources/approvals/voice/builds/jobs/artifacts`)の
  `registerXIpcHandlers`をin-memory fake serviceで結線し、Project作成
  →text登録→4承認→試聴→Build Request作成→Job起動→Artifact一覧まで
  の縦切りをJSON Lines契約どおりのIPC呼出し列で検証する)。
  `tests/conftest.py`の`desktop_connectivity_gate` placeholder
  fixtureも実装した(`WALKWISE_PYTHON_EXECUTABLE`の設定確認+
  `script.worker.cli`/`script.persistence.database`のimport可否
  確認のみ、作品生成は行わない)。
  [[implementation_assumptions.md]]に仮定を記録(callableベースの
  薄いorchestrator設計、E2E統合中に発見した`job:start`channel名の
  重複という技術的負債)。
- 対象テスト結果: Python 5 passed、TypeScript 5 passed(外部接続なし)。
- 外部疎通: `TASK-DESKTOP-003`のintegration_smoke(TC-11)/
  integration_live(TC-12)は、この環境に`WALKWISE_PYTHON_EXECUTABLE`/
  `WALKWISE_RUN_INTEGRATION_LIVE`が設定されないため未確認のまま
  (既定skip)。
- 全体回帰: Python 361 passed, 23 deselected, 70 xfailed(予期しない
  failなし、TASK-UI-005完了時点の356から+5)。TypeScript型検査
  success。Vitest 16 test files/76 tests、73 passed + 3 skipped
  (このタスクの5 caseが実assertionへ解除、1 caseが正しくskip)。
- 文書修正: `docs/commands/end-to-end.md`(担当分。`TASK-DESKTOP-003`
  分の対象ファイル欄・成功条件を実測結果へ更新。`TASK-E2E-001`分は
  未着手のまま記述を維持)。
- 備考: これでPhase6(Desktop・Worker・UI)の全9タスクが完了した。

## Phase 7: 移行・品質・配布 進行中

### TASK-MIGRATION-001 完了

- 対象: `tests/test_legacy_migration.py`(TC-01,03,05,07,09の5 case)、
  `tests/test_legacy_input_priority.py`(TC-02,04,06,08,10の5 case)。
  `documentation_repair_ownership: ["docs/commands/migration.md"]`。
- Red確認: `LegacyBook.__init__`/`LegacySection.__init__`/
  `LegacyAudioInput.__init__`/`LegacyAudioInput.resolve`/
  `MigrationReport`の4 method/`migrate_legacy_project`の本体のみを
  `NotImplementedError`化した中間版で10 failed(全件STEP4 stub由来、
  import/構文errorなし)を確認。
- production実装: `script/migration/legacy_models.py`(`LegacyBook`:
  `bookId`必須検証+`project_id` property、`LegacySection`:
  `sectionId`優先・`fileName`fallbackの`chapter_id` property、
  `LegacyAudioInput`: `TASK-CORE-002`の`normalize_unit_id`
  (`full_book`→`book`)を内部で適用し、02-process-input-output.md
  12節の優先順位3〜7(`text/speech`→`speak_dedicated`→`fixed`→
  `merged_gemini_fixed`→`merged`)に従い注入可能な`exists`callable
  経由で最初に存在する旧テキストを解決する`resolve()`)、
  `script/migration/report.py`(`MigrationReport`: conversions/
  warnings/provenance/unmigratedの4リストを追記専用で記録)、
  `script/migration/adapters.py`(`migrate_legacy_project(path,
  destination)`: `path/project/project-plan.yaml`の存在で新形式
  優先を判定しskip、`book.json`の未知fieldを推測せず
  `report.unmigrated`/`warnings`へ記録、`project/approval.yaml`
  (または`approval.yaml`)が存在し`status`が`approved`以外の場合は
  destinationへの書込前に`AppError(PERMISSION_DENIED)`で停止、
  `sections.json`不在時は`full_book`単位を`book`chapterへ正規化し
  provenanceへ記録、決定的`migration-report.json`をdestinationへ
  出力)。`script/core/hashing.py`/`identifiers.py`/`serialization.py`
  (`TASK-CORE-002`)の既存関数(`normalize_unit_id`, `load_json`,
  `load_yaml`, `dump_json`)をそのまま再利用し、新規依存は追加していない。
  [[implementation_assumptions.md]]に3件の仮定を記録
  (`migration-report.json`という新形式出力の設計判断、approval.yaml
  gateの解釈、legacy approvals.yaml変換を実体化しなかった判断)。
- 対象テスト結果: 10 passed。
- 全体回帰: Python 371 passed, 23 deselected, 60 xfailed(予期しない
  failなし、TASK-DESKTOP-003完了時点の361から+10)。TypeScript型検査
  success(変更なし)。Vitest 16 test files/76 tests、73 passed +
  3 skipped(このタスクはPython専用のため変化なし)。
- 文書修正: `docs/commands/migration.md`(担当分。対象ファイル欄・
  成功条件を実測結果へ更新)。
- 次タスク: `TASK-E2E-001`(external_gate、sample-book fixture整備)。

### TASK-E2E-001 完了(external_gate、通常テストのみ確認済み)

- 対象: `tests/integration/test_sample_book_e2e.py`(TC-01〜10の計10 case、
  外部接続なし。TC-11 integration_smoke/TC-12 integration_liveは
  `voicevox_connectivity_gate`を再利用し`VOICEVOX_URL`未設定のため既定skip)。
  `documentation_repair_ownership: ["docs/commands/end-to-end.md"]`
  (`TASK-DESKTOP-003`と共有する文書のうち本タスクの担当分のみ更新)。
  `run_sample_book_acceptance(...)`はこのtest file自身が契約上の
  "production"を兼ねる(契約のsource_filesに本fileと
  `tests/fixtures/sample_book/`の両方が列挙されている、
  `TASK-DESKTOP-003`のmvp-flow.test.tsと同型の自己参照production)。
- fixture: `tests/fixtures/sample_book/`配下に決定的なsample fixtureを新規
  作成した(`sources.yaml`3件(公式ガイド/無料教材/公開目次)、`claims.yaml`
  4件(definition/numeric_fact/limitation/generated_analogyの各1件、
  公開目次単独を出典にするものは含めない)、`script.yaml`8segment、
  `approvals.yaml`4gate全承認、`coverage-map.yaml`(1件`missing`を含む)、
  `ai-routing-plan.yaml`(9工程→economy/standard/high_assuranceの対応)、
  `model-policy.yaml`)。異常fixtureは`fixtures/`配下へ7種
  (`unsupported-claim.yaml`, `source-conflict.yaml`,
  `high-assurance-unconfigured.yaml`, `invalid-reference.yaml`,
  `budget-stop.yaml`, `cache-invalidation.yaml`,
  `unapproved-output-request.yaml`)を、基底fixtureへの差分overlay形式で
  作成した(`docs/spec-proposals/task/1_sample-book-end-to-end-validation.md`
  11節のfile一覧に対応)。
- Red確認: `run_sample_book_acceptance`本体のみ`NotImplementedError`化した
  中間版で10 failed(全件STEP4 stub由来、TC-11/12は既定skipのまま維持)を
  確認。
- production実装: `run_sample_book_acceptance(fixture_dir, destination_dir,
  ai_client, tts_synthesize, scenario="normal", ai_cache=None,
  budget_guard=None)`は、基底fixtureを読み込みscenario別overlayを適用した
  後、(1)segment/claim/coverageの参照整合性検証、(2)公開目次単独を出典と
  する主張の拒否、(3)`TASK-APPROVAL-001`の`ApprovalBundle`を用いた
  claim conflict未解決時のverified_script承認拒否、(4)`TASK-AI-002`の
  `AIRouter`/`AICache`/`BudgetGuard`をそのまま再利用した9工程分のAI
  routing・cache・予算制御(high_assurance未設定時はAIRouterが実装済みの
  `EXTERNAL_UNAVAILABLE`を自然に送出し黙った降格をしない)、(5)
  verified_script承認後だけのTTS実行、(6)preview_audio承認後だけの
  deliverables書込み、という順で検証・実行し、`script/persistence/files.py`
  の`atomic_write_bytes`(`TASK-FILE-001`)で章MP3/text/audio manifest/
  validation reportを書き出す。実際のcurriculum/draft/claims生成
  パイプライン(Phase3/4本体)は再実装せず、AI/TTSは呼び出し側が注入する
  mockに限定した(`TASK-DESKTOP-003`の薄いorchestrator設計を踏襲)。
  [[implementation_assumptions.md]]に3件の仮定を記録
  (`run_sample_book_acceptance`を「完成した教材内容」ではなく
  「仕様間の配線検証」に限定した設計判断、7種の異常fixtureとエラーcode
  対応表、TC-11/12を`TASK-VOICEVOX-001`の実装済みadapterへそのまま
  委譲した判断)。
- 対象テスト結果: 10 passed(TC-01〜10)。TC-11/12は`VOICEVOX_URL`未設定の
  ため既定skip。
- 全体回帰: Python 381 passed, 23 deselected, 50 xfailed(予期しないfail
  なし、TASK-MIGRATION-001完了時点の371から+10)。TypeScript型検査
  success(変更なし)。Vitest 16 test files/76 tests、73 passed+3 skipped
  (このタスクはPython専用のため変化なし)。
- 外部疎通: この環境に`VOICEVOX_URL`が未設定のため未確認のまま(既定skip)。
- 文書修正: `docs/commands/end-to-end.md`(担当分。`TASK-E2E-001`分の
  対象ファイル欄・成功条件を実測結果へ更新)。
- 次タスク: `TASK-RELEASE-001`(external_gate、Windows packaging)。

### TASK-RELEASE-001 完了(external_gate、通常テストのみ確認済み)

- 対象: `electron/tests/packaging_contract.test.ts`(TC-01,04,07,10の
  計4 case)、`tests/test_backup_restore.py`(TC-02,05,08の計3 case)、
  `tests/test_license_manifest.py`(TC-03,06,09の計3 case)。合計10 case
  中、外部接続なしの10 caseを本実装・確認、smoke/live(TC-11/TC-12)は
  実装済みだがこの環境に`WALKWISE_PYTHON_EXECUTABLE`/`FFMPEG_PATH`/
  `FFPROBE_PATH`/`TESSERACT_CMD`のいずれも未設定のため未確認(既定skip)。
  `documentation_repair_ownership`: `docs/commands/packaging.md`,
  `docs/commands/backup-restore.md`(task-command-matrix.mdより)。
- Red確認: Python側`create_backup`/`verify_backup`/`restore_backup`
  本体のみ`NotImplementedError`化した中間版で3 failed(TC-02,05,08、
  全件STEP4 stub由来)を確認。TypeScript側は`resolveRuntimeDependencies`
  本体を`throw`化しつつ、`electron-builder.yml`の
  `deleteAppDataOnUninstall`/`forceCodeSigning`と
  `resources/release-manifest.json`の`code_signing.signed`を意図的に
  反転させ、TC-01/07/10が正しく失敗しTC-04は無関係のため正しくpassのまま
  であることを確認した(TASK-DESKTOP-003で確立した「静的artifactの
  意図的破壊によるRed確認」を踏襲)。
- production実装: `electron/main/runtime.ts`(`resolveRuntimeDependencies`:
  Python/ffmpeg/ffprobe/Tesseractの`--version`取得を注入可能な
  `probeVersion` hook経由で順に確認し、副作用なし)、
  `electron-builder.yml`(Windows x64 nsis限定、`forceCodeSigning: false`、
  `deleteAppDataOnUninstall: false`(17節5.8節の「uninstallで利用者データを
  自動削除しない」を直接表現)、`resources/release-manifest.json`を
  `extraResources`で同梱)、`resources/release-manifest.json`(新規、
  platform/code_signing/auto_update/user_data/third_party_licensesの
  各節を持つ静的artifact。Electron/Vueのみ`bundled: true`、Python側
  依存・VOICEVOX・COEIROINK・ffmpeg・TesseractはPoC未決定のため
  `bundled: false`)、`script/maintenance/backup.py`
  (`create_backup(data_root, destination)`: `TASK-FILE-001`の
  `copy_immutable`を再利用し1世代分をhash付きでコピー、
  `verify_backup(backup_dir)`: manifest記録hashと再計算hashを照合し
  valid/corrupted/missingへ分類、`restore_backup(backup_dir,
  destination_data_root)`: 検証に成功したfileだけを復旧し、破損・欠落
  fileは黙って復旧せず明示的に報告する)。
  [[implementation_assumptions.md]]に4件の仮定を記録(license manifestを
  新規静的JSON artifactとして実装した設計判断、TC-06のffmpeg/Tesseract
  存在確認を`TASK-AUDIO-002`/`TASK-OCR-001`の既存adapter再利用で満たした
  判断、「Python worker bundling strategy」をbackup対象範囲の分離
  (install先/bundled runtimeとuser dataの分離)として解釈した判断、
  backup破損時の「部分復旧+明示report」設計)。
- 対象テスト結果: Python 6 passed(TC-02,03,05,06,08,09)、TypeScript
  4 passed(TC-01,04,07,10)。TC-11/TC-12は環境変数未設定のため既定skip。
- 全体回帰: Python 387 passed, 23 deselected, 44 xfailed(予期しないfail
  なし、TASK-E2E-001完了時点の381から+6。実行中に`test_container_contract.py`
  の実Docker呼出し2件が一時的にerrorとなったが、再実行で387 passed/
  エラー0を確認した一過性事象であり、本タスクの変更とは無関係)。
  TypeScript型検査success。Vitest 16 test files/76 tests、73 passed +
  3 skipped(このタスクは新規Vitest test.fails解除4件を含むが総数69は
  変わらず73+3のまま)。
- 外部疎通: `WALKWISE_PYTHON_EXECUTABLE`/`FFMPEG_PATH`/`FFPROBE_PATH`/
  `TESSERACT_CMD`のいずれもこの環境に未設定のため未確認のまま(既定skip)。
- 文書修正: `docs/commands/packaging.md`, `docs/commands/backup-restore.md`
  (いずれも担当分。対象ファイル欄・成功条件を実測結果へ更新)。
- 次タスク: `TASK-RELEASE-002`(performance/resilience/release acceptance)。

### TASK-RELEASE-002 完了(MVP最終タスク)

- 対象: `tests/performance/test_large_sources.py`(TC-01,03,05,07,09の
  計5 case)、`tests/resilience/test_failure_recovery.py`(TC-02,04,06,08,10
  の計5 case)。合計10 case、すべて通常pytestからは除外される
  `performance`/`resilience`marker専用実行(`WALKWISE_RUN_PERFORMANCE=1`/
  `WALKWISE_RUN_RESILIENCE=1`のopt-in)で実測pass。`documentation_repair_
  ownership`: `docs/commands/performance.md`, `docs/commands/release.md`
  (task-command-matrix.mdより。`testing.md`は共通文書のため対象外)。
  このタスクは新規productionモジュールを作らず、両test file自身が
  scenarioの実装境界を兼ね、既存の完了済み実装(`TASK-FILE-001`の
  `atomic_write_bytes`、`TASK-JOB-001`の`JobService`/`can_transition`、
  `TASK-WORKER-002`の`WorkerRuntime`/`recover_after_abnormal_exit`、
  `TASK-SOURCE-002`の`normalize_text`)を再利用した。
- Red確認: 専用production moduleがないため、既存の再利用対象へ的を絞った
  一時的破壊で正当なRedを確認した: (1)`script/persistence/files.py`の
  `atomic_write_bytes`の例外処理を握り潰す変更→TC-01が正しくfail、
  (2)`script/domain/job_state.py`の`CANCEL_REQUESTED→CANCELLED`遷移を
  削除→TC-06が正しくfail、(3)`script/services/jobs.py`の
  `recover_stale`をno-op化→TC-02/04が正しくfail。4件のfailを確認後、
  3ファイルを復元しGreenを再確認した。残り6 case(03,05,07,08,09,10)は
  既存の完了済み実装(`normalize_text`の決定性・`JobService`の入力検証)を
  そのまま検証しており、重複するRed確認は行わなかった(理由を
  `implementation_assumptions.md`に記録)。
- production実装: 新規productionモジュールなし。
  `tests/performance/test_large_sources.py`は`_measure()`という
  test-only helper(`time.perf_counter`+`tracemalloc`による実測、
  固定閾値を用いない)を用いてTC-01(disk full注入によるENOSPC耐性、
  `atomic_write_bytes`を実際に呼び出す)、TC-03(2MBの合成テキストで
  `normalize_text`を実測)、TC-05(測定helper自体のunit test)、
  TC-07(既存成果物のhash不変)、TC-09(再実行時の論理的決定性、
  timingではなくoutput_hash一致で判定)を実装した。
  `tests/resilience/test_failure_recovery.py`は`TASK-JOB-001`のtest
  harness(`connect_database`+`MigrationRunner`+実SQLite)を再利用し、
  TC-02(`JobService.recover_stale`+`recover_after_abnormal_exit`による
  stale Job復旧と再試行)、TC-04(復旧処理時間の実測記録)、
  TC-06(`JobService.request_cancel`の許可状態限定+`WorkerRuntime`の
  cooperative cancel+`JobRepository`による最終確定)、TC-08(必須入力欠落の
  安定validation error)、TC-10(RUNNING状態への不正retryが既存行を
  変更しないことをbefore/after比較で確認)を実装した。
- 既知のIPC技術的負債の解消(directive第6節): `electron/main/ipc/builds.ts`
  と`jobs.ts`が共に`"job:start"`を登録していた重複を解消した。
  `builds.ts`を正とし、bareな`buildRequestId`文字列(新規Job起動、既存挙動)と
  `{parentJobId}`オブジェクト(再試行、`jobs.ts`から移設)の両payload形状を
  1つのhandlerで処理するよう拡張した(`jobService`は`BuildIpcContext`の
  任意項目とし、未注入時は再試行payloadだけを安定errorで拒否、新規Job起動
  側の挙動・契約は無変更)。`jobs.ts`からは`job:start`の登録を削除し、
  `RETRYABLE_STATUSES`を`export`してbuilds.ts側から再利用した。
  この修正に伴い、既完了タスクの3つのVitest test fileを同一`ipcMain`
  インスタンス共有へ更新し再回帰した: `electron/tests/job_artifact_ipc.test.ts`
  (TASK-UI-004)、`electron/renderer/tests/JobsAndArtifacts.test.ts`
  (TASK-UI-004)、`electron/tests/e2e/mvp-flow.test.ts`のTC-DESKTOP-003-06
  (TASK-DESKTOP-003)。3ファイルとも`registerJobIpcHandlers`と
  `registerBuildIpcHandlers`(`jobService`注入込み)を同一fake`ipcMain`へ
  登録する形へ更新し、再試行が単一handler経由で機能することを確認した
  (公開契約・IPC channel一覧・画面仕様の意味変更なし)。詳細は
  `implementation_assumptions.md`に記録。
- release checklist: `release/checklist.md`を実測結果に基づき全面更新した。
  「MVP code complete」(はい)と「release ready」(いいえ、実runtime未確認の
  ため)を明確に分離して判定した。
- 対象テスト結果: 10 passed(TC-01〜10、opt-in実行)。
- 全体回帰: Python 394 passed, 23 deselected, 37 xfailed(予期しないfail
  なし、TASK-RELEASE-001完了時点の387から+7)。この+7は10 case中
  `unit`層の7 case(TC-04,05,06,07,08,09,10)がxfailから実passへ解除された
  分であり、`resilience`/`performance`層の3 case(TC-01,02,03)は通常
  pytestから引き続きmarker除外される(`-m "not performance and not
  resilience"`)ため、23 deselectedの構成には変化がない。3 caseは
  `WALKWISE_RUN_PERFORMANCE=1`/`WALKWISE_RUN_RESILIENCE=1`のopt-in実行で
  別途10/10 pass確認済み。TypeScript型検査success。Vitest 16 test files/
  76 tests、73 passed+3 skipped(IPC job:start統合修正後も全件green)。
  Docker: `docker compose build test`成功、`--collect-only -q`454件収集
  (host一致)、通常回帰387 passed+7 skipped=394でhostと完全一致。
- 外部疎通: このタスクはexternal_gate対象外(契約7節)。
- 文書修正: `docs/commands/performance.md`, `docs/commands/release.md`
  (いずれも担当分)、`release/checklist.md`(全面更新)。
- 備考: これでMVP対象50タスクが全完了した(Phase1〜7)。次はpost-MVPの
  `TASK-EPUB-001`(依存順、`TASK-M4B-001`→`TASK-ASR-001`と続く)。
  `TASK-COEIR-001`は引き続き永久blocked。

## Post-MVP 進行中

### TASK-EPUB-001 完了(post-MVP)

- 対象: `tests/test_epub_extraction.py`(TC-01〜10の計10 case、外部接続
  なし)。`documentation_repair_ownership: ["docs/commands/epub.md"]`。
- Red確認: `detect_drm_or_encryption`/`EpubTextExtractor.extract`本体のみ
  `NotImplementedError`化した中間版で10 failed(全件STEP4 stub由来、
  import/構文errorなし)を確認。
- production実装: `script/source_processing/epub/models.py`
  (`EpubChapter`: `spine_index`/`xhtml_path`必須、`order`/`chapter_title`/
  `text`/`annotations`既定値、`EpubExtractionReport`: `epub_version`/
  `chapters`必須、`chapters`/`warnings`をtuple化)、
  `script/source_processing/epub/extract.py`(`detect_drm_or_encryption`:
  `META-INF/encryption.xml`の存在で暗号化EPUBを検出、`EpubTextExtractor.
  extract`: `zipfile`+`xml.etree.ElementTree`という標準ライブラリのみで
  `container.xml`→`rootfile`(package document)→`manifest`/`spine`を解決し、
  spineのitemref順(manifest記載順やfile名順ではなく)でXHTML本文を抽出。
  DRM検出時は解除せず`unsupported_drm`で`AppError(VALIDATION_ERROR)`停止。
  spineの重複itemrefは`AppError`で拒否、未知manifest参照・不正XHTMLは
  当該spine itemだけをwarning付きでskipし他は継続(9節「他は継続」に
  対応)。XHTML抽出時、`<ruby>`要素はbase文字列だけを本文へ含めreading
  (ルビ読み)は`annotations.ruby`へchar_offset付きで分離、`epub:type=
  "footnote"`要素とその参照(`<a epub:type="noteref">`)は本文へ一切
  含めず`annotations.footnotes`へ分離、`<img>`はsrc/alt/char_offsetを
  `annotations.images`へ記録し本文へは挿入しない(5.3節「本文へ無条件で
  埋め込まない」を字句どおり実装)。新規依存の追加なし(標準ライブラリの
  `zipfile`/`xml.etree.ElementTree`のみ)。
  [[implementation_assumptions.md]]に3件の仮定を記録(EPUB解析に外部
  ライブラリ(ebooklib等)を追加せず標準ライブラリのみで実装した判断、
  footnote/ruby/imageのHTML構造解釈、`extract()`が一切filesystemへ
  書き込まない設計(ingestion pipelineへの統合は対象外と判断))。
- 対象テスト結果: 10 passed(TC-01〜10)。
- 全体回帰: Python 404 passed, 23 deselected, 27 xfailed(予期しないfail
  なし、TASK-RELEASE-002完了時点の394から+10)。TypeScript型検査
  success(変更なし)。Vitest 16 test files/76 tests、73 passed+3 skipped
  (このタスクはPython専用のため変化なし)。
- 外部疎通: このタスクはexternal_gate対象外(契約7節)。
- 文書修正: `docs/commands/epub.md`(担当分。対象ファイル欄・成功条件を
  実測結果へ更新)。
- 次タスク: `TASK-M4B-001`(post-MVP、M4B出力)。

### TASK-M4B-001 完了(post-MVP、external_gate)

- 対象: `tests/test_m4b_output.py`(TC-01,03,04,05,06,07,08の計7 case、
  外部接続なし)。TC-09(integration_smoke)/TC-02,10(integration_live)は
  実装済みだが`FFMPEG_PATH`未設定のため既定skip。
  `documentation_repair_ownership: ["docs/commands/m4b.md"]`。
- Red確認: `M4BTool.check_runtime`/`M4BBuilder.build`/`M4BManifest.
  __init__`本体のみ`NotImplementedError`化した中間版で7 failed(全件
  STEP4 stub由来、TC-09/02/10は既定skipのまま維持)を確認。
- production実装: `script/schemas/m4b_manifest.py`(`M4BManifest`:
  `project_id`/`chapters`必須、`chapter_id`重複拒否、
  `validation.all_chapters_passed`が`True`のときのみ構築を許可
  (12節)、`compatibility.tested_players`が空なら`status`を
  `approved`にできない(12節)、`output_type`を`"m4b"`固定)、
  `script/audio/m4b.py`(`M4BTool.check_runtime`:
  `TASK-AUDIO-002`の`AudioMeasurementAdapter`/`TASK-OCR-001`の
  `OcrClient`と同型の`ffmpeg_cmd`/`runner`注入パターンで
  `ffmpeg -version`疎通確認、`M4BBuilder.build(chapters, metadata,
  output)`: 全章の`script_approved`/`preview_approved`/
  `audio_validation_passed`を確認しいずれか不足ならAppError
  (PERMISSION_DENIED)でM4B生成前に停止(5.2節承認gate)、chapter_id
  重複を事前拒否、章順(`order`)でchapter atomを並べ替え、
  `audio-validation-thresholds.md`がprovisionalであるため
  `validation.validation_threshold_status`は常に`"provisional"`固定
  (仕様冒頭の状態注記どおり)、`metadata`の不明フィールドはNoneのまま
  保持しAI補完しない(5.5節)、`compatibility.status`は
  `tested_players`が明示されたときだけ`"approved"`)。
  新規依存の追加なし(`subprocess`標準ライブラリのみ)。
  [[implementation_assumptions.md]]に3件の仮定を記録(全文MP3を
  作らない方針の実装への反映、chapter入力に`script_approved`/
  `preview_approved`/`audio_validation_passed`という3個別boolean
  fieldを採用した設計、validation_threshold_statusを常時provisional
  固定にした判断)。
- 対象テスト結果: 7 passed(TC-01,03〜08)。TC-02,09,10は`FFMPEG_PATH`
  未設定のため既定skip。
- 全体回帰: Python 411 passed, 23 deselected, 20 xfailed(予期しないfail
  なし、TASK-EPUB-001完了時点の404から+7)。TypeScript型検査
  success(変更なし)。Vitest 16 test files/76 tests、73 passed+3 skipped
  (このタスクはPython専用のため変化なし)。
- 外部疎通: `FFMPEG_PATH`がこの環境に未設定のため未確認のまま(既定skip、
  `TASK-AUDIO-002`と同じ`ffmpeg_connectivity_gate`を再利用)。
- 文書修正: `docs/commands/m4b.md`(担当分。対象ファイル欄・成功条件を
  実測結果へ更新)。
- 次タスク: `TASK-ASR-001`(post-MVP、ASR照合)。

### TASK-ASR-001 完了(post-MVP、external_gate) — post-MVP最終タスク

- 対象: `tests/test_asr_verification.py`(TC-01〜10の計10 case、外部
  接続なし)。TC-11(integration_smoke)/TC-12(integration_live)は
  実装済みだが`WALKWISE_ASR_ENABLED`未設定のため既定skip。
  `documentation_repair_ownership: ["docs/commands/asr.md"]`。
- Red確認: `LocalWhisperCompatibleClient.check_connectivity`/
  `transcribe`/`ASRVerifier.verify`/`normalize_for_comparison`本体のみ
  `NotImplementedError`化した中間版で10 failed(全件STEP4 stub由来、
  TC-11/12は既定skipのまま維持)を確認。
- production実装: `script/asr/base.py`(`ASRConnectivityResult`/
  `ASRSegment`/`ASRTranscript`という最小限の補助dataclassを追加し
  (契約表にない追加、`TASK-AI-001`の`AIRequest`/`AIResult`等と同型の
  precedentを踏襲)、`ASRClient` Protocolを`check_connectivity()`/
  `transcribe(audio_path)`の2 methodで定義、`LocalWhisperCompatibleClient`
  (`TASK-OCR-001`の`OcrClient`と同型の`command`/`runner`注入adapter):
  `check_connectivity`は`<command> --version`相当のみ実行し文字起こし
  はしない、`transcribe`はJSON出力形式でCLIを起動しsegment配列を
  読み込む(openai-whisper CLI互換の`--output_format json`規約))、
  `script/asr/verification.py`(`normalize_for_comparison`: 用語辞書を
  長い表記から順に置換、原稿自体は変更しない、`ASRVerifier.verify`:
  tts_segments件数とASR segment件数が一致すればsegment単位で
  アラインメント、不一致ならchapter単位への結合比較にfallbackし
  理由を記録(5.2節)、文字誤り率(CER)/単語誤り率(WER)を素朴な
  Levenshtein距離で算出、`ASRVerificationReport`の`status`は
  `"pass"/"warning"/"review_required"`の3値のみ構造的に許可し
  `"fail"`を一切設定不可能にした(5.5節・12節の自動fail禁止を型で
  強制)、`threshold_status`は依存する検査閾値仕様が未確定のため常に
  `"provisional"`)。`tests/conftest.py`の`asr_connectivity_gate`
  placeholderを実装(`WALKWISE_ASR_ENABLED`の設定確認+
  `LocalWhisperCompatibleClient.check_connectivity()`)。新規依存の
  追加なし(`subprocess`/`json`/`tempfile`標準ライブラリのみ)。
  [[implementation_assumptions.md]]に4件の仮定を記録(補助dataclass
  追加の判断、CER/WER暫定閾値、segment件数不一致によるfallback判定
  方法、statusを型で3値限定してfail禁止を構造的に保証した設計)。
- 対象テスト結果: 10 passed(TC-01〜10)。TC-11,12は`WALKWISE_ASR_ENABLED`
  未設定のため既定skip。
- 全体回帰: Python 421 passed, 23 deselected, 10 xfailed(予期しないfail
  なし、TASK-M4B-001完了時点の411から+10。残る10 xfailedはすべて
  永久blockedの`TASK-COEIR-001`分)。TypeScript型検査success(変更なし)。
  Vitest 16 test files/76 tests、73 passed+3 skipped(このタスクは
  Python専用のため変化なし)。
- 外部疎通: `WALKWISE_ASR_ENABLED`がこの環境に未設定のため未確認のまま
  (既定skip)。
- 文書修正: `docs/commands/asr.md`(担当分。対象ファイル欄・成功条件を
  実測結果へ更新)。
- 備考: これでpost-MVP対象3タスク(`TASK-EPUB-001`/`TASK-M4B-001`/
  `TASK-ASR-001`)が全完了した。残るタスクは永久blockedの
  `TASK-COEIR-001`のみであり、公式API世代・endpoint・話者識別子等が
  確定するまで実装しない。次は最終repository-wide reviewと完了報告。

## 最終repository-wide review

- `git status --short`のuntracked一覧を確認したところ、repository root直下に
  意図しない`-version`という名前のfileが存在した(内容: `fake-m4b-bytes`)。
  原因は`tests/test_m4b_output.py::test_tc_m4b_001_07`が、本来
  `M4BBuilder.build()`用の`_fake_success_runner()`(`Path(args[-1])`へ
  無条件で書き込む汎用fake)を`M4BTool.check_runtime()`へ誤って再利用して
  いたため、`["ffmpeg", "-version"]`呼出し時に`args[-1]`が`"-version"`と
  なり、それがそのままcwd相対pathとして書き込まれていたことによる
  (`Path("-version").parent`は`.`)。
- 修正: 該当testを、`M4BTool`用の他の疎通確認testと同型の、
  filesystemへ一切書き込まない専用fake(`fake_version_runner`)へ
  差し替えた。既存の`_fake_success_runner`自体はbuild系呼出し専用の
  ままとし、他箇所への影響はない(`tests/test_m4b_output.py`内で
  `_fake_success_runner`が`M4BTool`へ渡されている箇所は他になし)。
- 確認: 誤生成された`-version`fileを削除し、`tests/test_m4b_output.py`の
  対象7 caseを再実行してpass、その後Python全体回帰
  (421 passed, 23 deselected, 10 xfailed)を再確認し、以後
  `git status --short`に不要なfileが再出現しないことを確認した。
- そのほかの確認事項: `script/`配下の残存`NotImplementedError`は
  legacy(`merged_text_fixer.py`/`mindmap_builder.py`、いずれもどの
  taskからも参照されない既存の未使用scaffold)と`TASK-COEIR-001`
  (永久blocked)のみ。`electron/`配下の残存`test.fails(`は0件。
  Python/TypeScript双方で`TODO`/`FIXME`/`XXX`は0件。
  `docs/commands/README.md`に残っていた「`TASK-DEV-001`のみ完了」という
  古い記述を実測値(53/54完了)へ更新した(`docs/tasks/README.md`の
  「431 xfailed」はSTEP3空実装段階の開始時baselineとして意図的に
  固定された記述であり、実装完了を主張するものではないため変更して
  いない)。

## TASK-REVIEW-001: 実行時統合とリポジトリ整理

- 契機: 53/54タスク完了(post-MVP含む)後の再監査で、個別task契約が
  mock/DI設計でpassしている状態と「実際に起動・操作できるアプリ」の間に
  大きな乖離があることが判明した。具体的には、`electron/main/index.ts`が
  `createMainWindow()`をexportするだけで`app.whenReady()`を呼ぶ経路が
  存在しない、`python -m script.worker.cli`が空の`HandlerRegistry()`で
  起動し`health`すら拒否する、Electronの各`*ServiceLike`にWorker/SQLite
  接続の実装が1つもない、Rendererの5画面がどこにも結線されていない、
  `job:progress-event`をpreloadが購読していない、`ProjectWorkspace.vue`が
  ブラウザの`File.name`を実pathとして送っている、`npm run build`が
  型検査のみで実HTML/JS/CSSを生成しない、という7点が確認された。
- 対応方針: 個別taskの追加実装ではなく、既存の承認済みservice
  (`script/services/*`)・既存のIPC contract(`electron/main/ipc/*.ts`)を
  そのまま再利用し、それらを実際に結線する層(Worker command registry・
  Electron⇔Worker adapter・composition root・Renderer root・安全な
  file picker・実build pipeline)だけを新規実装した。新しい業務ロジックは
  一切追加していない。
- **Python Worker command registry**(`script/worker/commands.py`、新規):
  `build_default_registry(data_root, connection)`が、`health`/`db.migrate`/
  `job.recover_stale`/`project.*`/`source.*`/`approval.*`/
  `build_request.*`/`job.*`/`artifact.*`/`voice.*`の20 job_typeを
  既存serviceへ委譲するhandlerとして登録する。`script/worker/handlers.py`の
  `HandlerRegistry.dispatch`を、handlerがgeneratorの`return`値を持つ場合に
  `completed`eventの`result`欄へ付与するよう後方互換に拡張した(既存の
  値なしhandlerは`result`なしの従来どおりの`completed`event)。
  `script/worker/cli.py`の`__main__`entrypointは、`WALKWISE_DB_PATH`
  環境変数が設定されている場合のみ実registryを使い、未設定時は従来どおり
  空registry(安全側の既定、既存test非破壊)。`tests/test_worker_commands.py`
  (新規8 case)で、health/migrate/project/source/approval/build/job(fail-closed
  gate含む)/artifact/voiceの往復をRed(空registryで失敗確認)→Green
  (実registryでpass)の順に確認。加えてshell上で実subprocess
  (`echo '{"job_id":...}' | python -m script.worker.cli`)への
  `health`/`db.migrate`/`project.create`往復を実測し、exit code 0を確認した。
- **Electron⇔Worker service adapter**(`electron/main/worker_service_adapters.ts`、
  新規): Project/Source/Approval/Build/Job/Artifact/Voice各`*ServiceLike`を
  `WorkerManager.request()`経由のPython呼び出しへ委譲する実装。
  camelCase(TS)⇔snake_case(Python)のfield変換のみを行い、DBスキーマ・
  業務ルールはPython側にのみ存在させる設計とした。`JobServiceLike.
  subscribeProgress`は、Worker側にまだ実際のbuild pipeline実行ループが
  接続されていないため(job.startはqueued/running状態遷移のみ)、
  `job:get`を500ms間隔でpollingしてProgressEventへ変換する暫定実装
  とした(既知の制約、真のpush型progressではない)。
  `ApprovalGateCheckerLike`は新設した`build_request.approval_gate_satisfied`
  job_typeへ委譲し、rubber-stamp(常にtrueを返す)にしないよう設計した。
  `tests/electron/tests/worker_service_adapters.test.ts`(新規8 case)で、
  fake child processが返すJSON Linesを使った実WorkerManager往復を検証。
- **Electron composition root**(`electron/main/app_entry.ts`、
  `electron/main/electron_main.ts`、いずれも新規): `main()`が
  `app.whenReady()`→`runCompositionRoot()`を呼び出す。`runCompositionRoot()`は
  1つのWorkerManagerを構築し(spawn時に`WALKWISE_DB_PATH`環境変数を設定)、
  `bootstrapApplication()`(既存契約、変更なし)の`openDatabase`/
  `runMigrations`/`recoverStaleJobs`/`createWorkerManager`をすべて同じ
  WorkerManager経由の`request()`へ委譲する形で結線し、その後7つの
  adapterを構築してIPC handlerを単一`ipcMain`へ登録、最後に
  `createMainWindow()`(既存契約、変更なし)を呼ぶ。`electron/main/index.ts`
  自体は変更していない(既存testが`vi.mock("electron")`環境でimportしても
  `app.whenReady()`が誤発火しないよう、実行処理を別fileへ分離)。
  bootstrap後(IPC登録〜window作成)で例外が起きた場合に、bootstrap済みの
  `context`を呼び出し側へ返せずWorker/DBがcleanupされずに残り続ける
  資源leakを発見し(`context.shutdown()`を呼ばずに再送出していた)、
  try/catchで`context.shutdown()`してから再送出するよう修正。
  `electron/tests/app_entry.test.ts`(新規3 case)で、正常起動時の
  channel重複なし登録、bootstrap失敗時のIPC/window未登録、window作成
  失敗時のWorker cleanup(Red→Green確認済み)を検証。
- **IPC channel不整合の修正**: `electron/preload/index.ts`の
  `subscribeProgress`が、main側が実際にsendするchannel
  (`job:progress-event`、`electron/main/ipc/jobs.ts`)ではなく
  `job:subscribe-progress`(登録用channel名)を購読していた不具合を修正
  (`electron/tests/preload_contract.test.ts`に専用test追加)。
  `project:get`(preloadは呼ぶが`electron/main/ipc/projects.ts`に
  handlerが存在しなかった)、`source:list`/`source:retry`
  (`electron/main/ipc/sources.ts`)、`job:list`
  (`electron/main/ipc/jobs.ts`、project配下のJob一覧を返す新規SQL join)を
  追加。関連する既存test(`ProjectServiceLike`/`SourceServiceLike`/
  `JobServiceLike`を実装するfake一式)を型エラーなく更新した。
- **Renderer root**(`electron/renderer/App.vue`、新規): 以前
  `electron/renderer/main.ts`は空のplaceholder divをmountするだけだった。
  `router.ts`(`resolveNavigation`)・`stores/app.ts`(`AppStore`)・
  5画面(ProjectList/ProjectWorkspace/BuildSettings/JobsAndArtifacts、
  AppShell経由)・`window.walkwise`を実際に結線するroot componentを新規
  実装し、`main.ts`の既定rootComponentを空placeholderからこれへ変更した。
  `ProjectList.vue`に「開く」button(`open-project` emit)を追加し、
  Project選択→workspace遷移の導線を新設(既存の一覧表示・作成form動作は
  変更なし)。`electron/renderer/index.html`(Vite entry、新規)を追加。
  `electron/renderer/tests/App.test.ts`(新規5 case)で、fake
  `window.walkwise`に対する実DOM操作(button click)経由の
  Project→Source/Approval読込→file選択→Build設定→Job/Artifact表示→
  cancel、日本語errorメッセージ表示、を検証。
- **安全なfile picker**(`electron/main/ipc/files.ts`、新規): 以前
  `ProjectWorkspace.vue`は`<input type=file>`/drag&dropが返す
  `File.name`(拡張子付きファイル名のみで実在するpathではない)を
  そのまま`filePath`として送っており、main/Workerは対象fileを一度も
  実際に読めなかった。`dialog:select-source-file` IPC channelを新設し、
  main process側の`dialog.showOpenDialog()`のみでfile選択を行い、
  拡張子allowlist・実在・通常ファイル(非ディレクトリ)・非symlink・
  非UNC path・非path-traversalを検証してから絶対pathを返す設計へ変更した。
  `ProjectWorkspace.vue`から`<input type=file>`/drop-zoneを削除し、
  「ファイルを選択…」buttonから`selectSourceFile`prop経由でdialogを
  呼ぶよう変更(既存test`TC-UI-002-04`を新しい安全な導線へ更新)。
  加えて`script/schemas/source_metadata.py`の`SourceMetadata.from_file`へ
  symlink拒否を追加した(Electron層のdialog検証を経由しない直接呼び出しに
  対する多重防御、`tests/test_source_service.py`に専用testをRed→Green確認済みで追加)。
  `electron/tests/files_ipc.test.ts`(新規11 case)で拡張子/実在/
  ディレクトリ/symlink/UNC/traversal/相対pathの各拒否パターンを検証。
- **実build pipeline**: 以前`npm run build`は`tsc --noEmit`(型検査のみ)で
  実HTML/JS/CSSを一切生成しなかった。`vite.config.ts`(Renderer、
  `electron/renderer/index.html`を入力に`dist/renderer/`へ出力)・
  `tsconfig.main.json`(main/preloadをCommonJSへcompile、`dist/main/`・
  `dist/preload/`へ出力)・`scripts/finalize-dist.mjs`(root
  `package.json`の`"type":"module"`に関わらずdist側をCommonJSとして
  実行させるため、`dist/main/package.json`・`dist/preload/package.json`へ
  `{"type":"commonjs"}`を書き込む)を新規追加。`package.json`の`main`を
  `dist/main/electron_main.js`へ設定し、`scripts`を
  `dev`/`typecheck`/`build:main`/`build:renderer`/`build`/`test`/`start`/
  `package`へ再構成した(`electron`パッケージが誤って`dependencies`に
  入っていたためelectron-builderが拒否する設定不備も発見・
  `devDependencies`へ修正)。`npm run build`実行で`dist/main/
  electron_main.js`・`dist/preload/index.js`・`dist/renderer/index.html`の
  生成を確認し、`npx electron-builder --dir`で`release/win-unpacked/
  Walkwise.exe`を生成、`asar list`で`app.asar`内entrypointの存在を
  確認、`Walkwise.exe --version`の実行(exit code 0)を確認した。
- **fail-closed承認gateの確認**: `registerBuildIpcHandlers`
  (`electron/main/ipc/builds.ts`)が`approvalGateChecker`未注入時に
  登録自体を失敗させる実装は既存(Phase A)のままだったが、
  `buildService`は注入されていて`approvalGateChecker`だけが欠落する
  ケースを単独で検証するtestがなかったため、専用test
  (`electron/tests/build_voice_ipc.test.ts`)を追加した。
- **legacy scaffoldの整理**: `script/ai_clients/gemini/mindmap_builder.py`
  (`build_final_mindmap`/`load_sections`/`process_section`/`Section`)と
  `merged_text_fixer.py`(`fix_text_file_with_gemini`)は、全body
  `NotImplementedError`のlegacy互換scaffoldで、どのtask・test・pipelineからも
  参照されていないことを確認した(直接import・test参照とも0件)。
  実装を推測で追加する根拠(仕様・test caseのいずれも存在しない)が
  ないため、両fileを削除し、`script/ai_clients/gemini/__init__.py`の
  `__all__`から関連exportを除去、moduleの先頭docstringに削除理由を記録した
  (将来これらの機能が必要になった場合はGeminiClient契約へ新規taskとして
  追加する旨を明記)。
- **`.env`依存testの修正**: `tests/test_container_contract.py::
  test_tc_env_001_02`が、gitignore対象で清潔なcheckoutには存在しない
  実`.env`fileの存在を要求しており(`assert (_REPO_ROOT / ".env").is_file()`)、
  清潔なcheckoutでは必ず失敗する状態だった。commit対象の
  `.env.example`(新規)の存在確認へ置き換え、実`.env`を一時退避した状態で
  該当testがpassすることを確認した(clean-checkout相当の動作確認)。
- **文書整理**: root `README.md`(空だったものを新規執筆、環境構築・起動・
  build・package・環境変数・既知の制限を記載)、`release/checklist.md`
  (v1.0→v2.0、契約実装/実行時統合/実app起動を分離して記載)、
  `docs/commands/CURRENT_STATE.md`(version 9.0→10.0、TASK-REVIEW-001
  節を新設し「契約実装complete」と「実アプリ動作確認済み」の分離を明記)、
  `docs/commands/STEP6_MANIFEST.json`(`mvp_status.runtime_integration_review`
  object新設)、`package.json`(version `0.0.0-step4`→`0.1.0`、
  `description`/`author`追加)を更新した。
- **確認**: Python全体回帰 430 passed / 23 deselected / 10 xfailed
  (TASK-ASR-001時点421から+9、新規: worker command registry test 8件 +
  source symlink拒否test 1件)。TypeScript型検査success、error 0件。
  Vitest 20 test files / 106 tests、103 passed + 3 skipped(TASK-ASR-001
  時点16 files/73 passedから、composition root・Worker adapter・
  file picker・Renderer root関連のtest追加分)。`npm run build`・
  `npx electron-builder --dir`とも成功。
- **未解決**: 実GUI起動(本開発環境にディスプレイなし)、外部runtime
  (Gemini/Tesseract/VOICEVOX/ffmpeg)への実接続、Windows installerの
  実インストール・実uninstall、code signingは、いずれもこの開発環境・
  本reviewの範囲では確認・実装していない(詳細は`release/checklist.md`)。

## 実際のbuild execution pipeline統合について(調査結果、未実装の理由)

継続instructionで最優先とされた「`job.start`から実際にSource読込→AI資料分析→
Curriculum/原稿生成→Claim検査→Narration→TTS→音声検査→MP3/M4B/text
packaging→Artifact登録→Job成功、を実行する経路の接続」について、
実装前に既存contractを調査した結果、**この接続には現在どの承認済み仕様にも
test caseにも存在しない、最低3つの新しい設計決定が必要**であることが判明した。
これらを推測で決めることは、本reviewが禁止する「新しい業務仕様の推測実装」に
該当するため、実装しなかった。調査結果は以下のとおり。

1. **verified scriptの永続化先が存在しない**: `script/schemas/script.py`の
   `ScriptDocument`はdocstring上で`chapters/<chapter_id>/<stage>/script.yaml`への
   対応を説明しているが、これへ実際に書き込む(`dump_yaml`等を呼ぶ)production
   codeはリポジトリ全体に1つも存在しない。`script/pipelines/narration.py`の
   `build_verified_script()`は、in-memoryの`ScriptDocument`を返すだけで
   永続化しない。実在するのは`tests/fixtures/sample_book/script.yaml`という
   test fixtureのみ。
2. **`BuildRequest`からchapterを特定する経路が存在しない**: `BuildRequest`
   (`script/domain/models.py`)は`chapter_id`を一切持たない。`ProjectPlan`
   (`script/schemas/project_plan.py`)の`chapters`は未型付けの`Mapping`で、
   `chapter_id`フィールドの存在も検証されていない。`BuildPipeline.run()`
   自体が単一chapter限定の設計であり、複数chapterを持つBuildRequestを
   どう扱うか(chapterごとに`run()`を何度呼ぶか等)も既存契約に定義がない。
3. **VoiceProfileの永続化からの読込経路が存在しない**: `script/profiles/voices.py`の
   `VoiceProfileRepository`は、呼び出し側がin-memoryで渡した
   `Sequence[VoiceProfile]`から構築される設計で、fileや DBから読み込む
   loaderが存在しない。`BuildRequest.voice_profile_id`(文字列)を実際の
   `VoiceProfile`(ひいてはVOICEVOX speaker_id)へ解決する経路がない。

`script/pipelines/build.py`の`BuildPipeline.run(build_request_id)`自体は
承認gate確認・複数出力形式(mp3/text)のArtifact登録・manifest生成までを
既に実装・test済みであり(`tests/test_build_pipeline.py`)、
`chapter_content_provider: Callable[[BuildRequest], ChapterBuildContent]`を
注入すれば動作する設計になっている。つまり**「注入する関数を書けば
接続できる」という状態ではあるが、その関数が読むべきfileの場所・形式・
chapter特定方法・voice profile解決方法がどれも仕様として決まっていない**、
というのが本reviewでの調査結論である。

この決定(仕様承認)を経ずに実装すると、将来の正式仕様と食い違う独自の
file形式・orchestration方式を生み出すリスクが高いため、実装を見送った。
次の作業者への申し送り: 上記3点を人間が仕様決定(`docs/spec-proposals/`
経由の正規プロセスを推奨)した後、`script/worker/commands.py`の`job_start`
handlerから`BuildPipeline.run()`を(非同期実行に変更した上で)呼び出す
形で接続する。

## TASK-REVIEW-001 完了時点のまとめ(次回作業者向け)

- **完了**: composition root、Worker command registry、Electron⇔Worker
  adapter、IPC channel不整合修正、Renderer root(App.vue)、安全なfile
  picker、fail-closed承認gate確認、実build pipeline(vite/tsc)、
  package生成確認、legacy scaffold(mindmap_builder等)削除、`.env`依存
  test修正、docs/tasks・docs/spec-proposals/taskの完了済みfile削除、
  Markdown link validator新規実装・0 broken確認、dump script除外追加、
  STEP3/STEP4 scaffold削除。
- **失敗中のtest**: なし(Python 435 passed / 23 deselected / 10 xfailed
  [すべてTASK-COEIR-001分] / 0 failed、Docker 428 passed + 7 skipped
  [docker CLI非対応環境skip] = 435でhostと完全一致、TypeScript typecheck
  success、Vitest 103 passed / 3 skipped / 0 failed)。
- **未接続・未実装**: 実際のbuild execution pipeline(Job1つから章単位で
  実際にAI原稿生成→TTS→packagingを実行する経路。上記3点の仕様決定待ち)。
  実GUI起動(本開発環境にディスプレイなし)。外部runtime
  (Gemini/Tesseract/VOICEVOX/ffmpeg)への実接続。Windows NSISインストーラー
  の実インストール・実uninstall。code signing。
- **次の開始地点**: (1) 人間が「実際のbuild execution pipeline統合」に
  必要な3つの設計決定(verified script永続化先、BuildRequest→chapter
  特定方法、VoiceProfile永続化読込)を`docs/spec-proposals/`経由で正式化する。
  (2) ディスプレイのある環境で`npm run start`の実GUI起動を確認する。
  (3) 各種`.env`変数を設定し`docs/commands/external-connectivity.md`の
  順序(設定確認→integration_smoke→integration_live)で外部runtime疎通を
  確認する。(4) `npm run package`でのフルインストーラー生成・実インストール・
  実uninstallを確認する。`TASK-COEIR-001`は今回も含め一貫して永久blockedの
  まま維持されており、推測実装は一切行っていない。

## TASK-BUILD-EXEC-001: 実際のbuild execution pipeline統合(2026-07-22完了)

上記「実際のbuild execution pipeline統合について(調査結果、未実装の理由)」で
指摘した3つの未決定設計を、人間が承認済み設計として確定した
(`docs/tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md`)。
承認内容は次のとおり。

1. verified scriptの正本location: `data/library/<project_id>/chapters/<chapter_id>/verified/script.yaml`。
2. TTS入力優先順位: `segments[].tts_text`→`segments[].text`(draft/legacy原稿へのfallbackなし)。
3. MVPの`BuildRequest`はProject全体を対象とする(`chapter_id`列は追加しない)。
4. chapter順序の正本は`project-plan.yaml`の`chapters[]`(order昇順)であり、folder名の文字列順ではない。
5. VoiceProfileの正本はSQLite(`voice_profiles`テーブル)であり、YAMLではない。

この承認に基づき実装した内容(詳細は`docs/db/06-voice-profiles-table.md`、
`docs/specifications/14-audio-packaging.md` 10節、`docs/specifications/22-job-lifecycle-and-recovery.md`
5.7節):

- **migration**: `voice_profiles`テーブル新設 + `build_requests.voice_profile_id`の
  FK化 + `jobs.error_code`/`error_stage`/`error_detail_json`追加
  (`script/persistence/sql/0002_voice_profiles_and_build_execution.sql`)。
  適用前に既存DBの孤立`voice_profile_id`参照を検出するfail-closedな
  事前確認(`check_orphaned_build_request_voice_profiles`)を追加。
- **VoiceProfile永続化**: `VoiceProfileRecord`/`VoiceProfileRecordStatus`
  (draft/approved/archived)、`VoiceProfileRepository`、
  `VoiceProfileService`(Project所属・name重複・status遷移・archive専用
  [物理削除なし]を検証)。
- **BuildRequest検証強化**: mp3出力時のVoiceProfile必須(`voice_profile_required`)、
  同一Project所属・approved限定(`voice_profile_project_mismatch`/
  `voice_profile_not_approved`/`voice_profile_archived`)。
- **chapter順序・verified script解決**: `script/services/build_target_resolution.py`。
  1chapterでも問題があれば、TTS呼び出し前にJob全体を`build_target_not_ready`
  として拒否する(部分的な完了chapterのみの出力はしない)。
- **VoiceProfile snapshot**: `script/services/voice_profile_snapshot.py`。
  Job開始時に1回だけDBから読み込み、Job全体で不変(Job途中のProfile更新は
  反映しない)。config_hashは決定的(同じ設定→同じhash)。
- **Build Execution Orchestrator**: `script/pipelines/build_execution.py`。
  既存の単一chapter向け`BuildPipeline`(`script/pipelines/build.py`)は
  変更せず、複数chapterの実TTS合成・音声検証・chapter packaging・text
  出力・production manifest・Artifact登録までを実際に順序制御する新しい層
  として追加した。text-onlyのBuildはTTS/VOICEVOX/音声検証/ffmpegを一切
  呼び出さない。Artifactは全chapterの合成が成功した後にまとめて登録し、
  途中失敗時は1件も登録しない。
- **Worker/Electron配線**: `script/worker/commands.py`の`job.start`が、
  承認gate確認後に実際に`BuildExecutionOrchestrator.run()`を呼び出すよう
  になった(新しい`build.execute`は追加せず、既存の`job.start`を再利用)。
  `voice_profile.create/list/get/update/archive`をWorker commandとして
  新設し、Electron main(`electron/main/ipc/voice_profiles.ts`、
  `createVoiceProfileServiceAdapter`)・preload(`voice-profile:*`
  channel)まで配線した。

**未解決(人間承認が必要、実装せず報告)**: `docs/screens/03-build-settings.md`
(承認済み画面仕様)は、VOICEVOXのspeaker/style一覧から都度選択するモデルを
前提としており、Project単位で事前登録・承認するVoiceProfileを選択する導線を
定義していない。Electron main側の配線(IPC/adapter/Worker command)は
実装・テスト済みだが、`BuildSettings.vue`のUI/UX刷新(VoiceProfile一覧
picker追加、または別のVoiceProfile管理画面の新設)は、既存画面仕様との
食い違いを解消する人間の設計判断が必要なため、今回は変更していない
(TASK-BUILD-EXEC-001完了reportの停止報告を参照)。

Python側regression: 498 passed, 23 skipped(既定opt-in), 3 deselected
(Docker daemon未起動環境要因、コード変更と無関係), 10 xfailed
(すべてTASK-COEIR-001), 0 failed。TypeScript/Vitest: 110 passed, 3 skipped
(既定opt-in), 0 failed。`npx tsc --noEmit`成功。`TASK-COEIR-001`は
今回も一貫して永久blockedのまま(実装・接続一切なし)。

## TASK-VOICE-PROFILE-UI-001: Build SettingsへのVoiceProfile選択・管理導線(2026-07-22完了)

上記「未解決・人間承認が必要な項目」で報告したBuild Settings画面とVoiceProfile
選択導線の不整合を、人間承認済みUI仕様に基づき実装した。承認プロセス:

1. まず`docs/spec-proposals/build-settings-voice-profile-ui.md`として、
   コード変更なしの調査・3案比較(案A: Build Settings内で完結、案B: Project
   単位で分離管理、案C: 選択+modal)・推奨案・人間判断事項の一覧を提案した。
2. 人間が次を承認: VoiceProfile管理場所はProject Workspace(第6画面は追加
   しない)、承認済みProfile編集後もapprovedを維持、Build画面からの新規作成は
   不可、旧speaker/style直接選択UIは削除、VoiceProfile未作成時はtext-only
   Buildのみ許可、text-only時はVoiceProfile欄をdisabledグレー表示、Profile
   複製はMVPで実装しない。
3. 承認内容に基づき実装した。

実装内容:

- **Project Workspace**(`docs/screens/02-project-workspace-and-source-import.md`
  v1.2、`electron/renderer/screens/ProjectWorkspace.vue`): 「音声設定」section
  (第6画面ではなく既存画面へ統合)。VoiceProfile一覧(status日本語表示、
  speaker表示名優先)、新規作成・編集modal(role="dialog"、aria-modal、
  Escape close、focus trap、初期focus)、承認(draft→approved、二重送信防止)、
  archive(JobsAndArtifacts.vueのcancel確認と同じ二段階確認方式、物理削除なし)。
- **Build Settings**(`docs/screens/03-build-settings.md` v1.2、
  `electron/renderer/screens/BuildSettings.vue`): 旧来のVOICEVOX speaker/style
  直接選択・speedスライダー・試聴機能を削除し、このProjectのapproved
  VoiceProfileを1件選択するだけの画面へ変更した。旧実装の不整合(生の
  speaker_idを`voiceProfileId`としてそのまま送信していた問題)を是正した。
  選択中Profileがarchive等で無効化された場合、選択を解除し利用者向け通知を
  表示する。
- **共有error mapping**(`electron/renderer/voiceProfileErrors.ts`):
  backendの安定したerror code(`voice_profile_required`等)を利用者向け
  日本語messageへ変換する処理を、両画面から重複実装せず共有した。
- **electron main IPC/adapter拡張**: 前task(`TASK-BUILD-EXEC-001`)で追加した
  `electron/main/ipc/voice_profiles.ts`/`worker_service_adapters.ts`が
  pause設定(`sentence_pause_ms`等)・`settings_json`・(updateのみ)
  `engine`/`speaker_id`/`style_id`を欠落させていたgapを埋めた(Python
  Worker側`script/worker/commands.py`は当時から対応済みだった)。

Renderer実装は完了したが、次は今回も実装せず報告する(実runtime確認・外部
接続を要するため): 実GUI目視確認(この開発環境にディスプレイなし)、実
VOICEVOX Engineへの接続確認。いずれもTASK-REVIEW-001時点から状態変化なし。

regression: Python 498 passed / 0 failed(Renderer中心の変更のため対象外だが、
`git diff -- script tests`が空であることを確認済み)。TypeScript/Vitest
128 passed, 3 skipped(既定opt-in), 0 failed(21 test files、17件新規
ProjectWorkspace test + 7件accessibility test追加を含む)。`npm run build`
成功。Markdown link check: 0 broken(172 files, 320 links。自分の新規
proposal fileが`docs/tasks/TASK-BUILD-EXEC-001-...md`への相対path形式の
参照を含んでいたため、既存の`test_no_dangling_references_to_deleted_task_and_proposal_paths`
testを一時的に落としていたことを発見・是正した)。
