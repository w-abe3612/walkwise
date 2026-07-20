---
document_type: preparation_state
status: in_progress
version: "10.0"
last_updated: "2026-07-20"
current_state_verified: "2026-07-20"
verified_by: "TASK-REVIEW-001 runtime integration and repository cleanup review"
---

# 実装準備状態(実測)

本書はダンプ記載の数値ではなく、`2026-07-20`にリポジトリを直接実測した結果を正本とする。
過去のダンプに基づく件数(19件存在・90件欠落・22件収集・17 xfailed / 5 skipped 等)は
すべて古い状態であり、現在の状態を示すものではない。

## 0. TASK-REVIEW-001: 契約実装完了 と 実アプリ動作確認済み の分離(重要)

version 9.0までの本書は、個別task契約が(主にmock/DI設計で)すべてpassしている状態を
「実装完了」と記述していたが、これは**Electronが実際に起動する**ことや
**Python Workerが実際にrequestへ応答する**こと、**Rendererの5画面が実際に
window.walkwiseへ結線されている**ことを意味しなかった。実際、`TASK-REVIEW-001`の
監査時点で以下が判明していた。

- `electron/main/index.ts`は`createMainWindow()`をexportするだけで、`app.whenReady()`を
  呼び出すコードがどこにも存在せず、`npm start`相当の起動手段が皆無だった。
- `python -m script.worker.cli`は空の`HandlerRegistry()`で起動し、`health`すら
  `unknown_job_type`で拒否していた。
- Electronの各`*ServiceLike`(Project/Source/Approval/Build/Job/Artifact/Voice)には、
  Worker/SQLiteへ接続する実装が1つも存在しなかった。
- `electron/renderer/main.ts`は空のplaceholder divをmountするだけで、5画面のどれも
  表示・結線されていなかった。
- `job:progress-event`(mainが実際にsendするchannel)をpreloadが購読しておらず、
  進捗がRendererへ届かなかった。
- `ProjectWorkspace.vue`はブラウザの`File.name`(実在するpathではない)を
  そのまま`source:register`へ送っており、対象fileを一度も実際に読めなかった。
- `npm run build`は`tsc --noEmit`(型検査のみ)で、実HTML/JS/CSSを一切生成しなかった。

これらはすべて本reviewで実装・修正・検証済みである(詳細は
[`release/checklist.md`](../../release/checklist.md)の2節、
[`docs/notes/implementation_assumptions.md`](../notes/implementation_assumptions.md)の
TASK-REVIEW-001節を参照)。**「契約実装complete」と「実アプリ起動」は依然として
別の軸であり続ける**: 本reviewはcomposition root・Worker registry・IPC adapter・
Renderer root・build/packageを実装し実サブプロセス往復・実package生成までは
検証したが、実ディスプレイでのGUI起動・外部runtime(Gemini/Tesseract/VOICEVOX/
ffmpeg)への実接続は、この開発環境(headless)では引き続き未確認である。

## 集計

| 項目 | 件数 |
|---|---:|
| STEP2タスク契約 | 54 |
| 契約上のtest file | 109 |
| 現在存在するtest file | 109 |
| 現在欠落するtest file | 0 |
| STEP6の計画command document | 38 |
| 実装完了タスク | 53(MVP全50件完了 + post-MVP全3件完了。残るのは永久blockedの`TASK-COEIR-001`のみ) |
| 未実装タスク(STEP3/STEP4空実装のまま) | 1(blocked 1件のみ、`TASK-COEIR-001`) |

## 判定

STEP3のPythonテスト空実装・STEP4のソース空実装は109/109件そろっている。
Phase1(開発基盤・Core・DB)の8タスク、Phase2(Project・Source・Build・Job・
Approval)の7タスク、Phase3(資料入力の7件)、Phase4(教材生成AIの7件)、
Phase5(TTS・Pipeline・Audioの7件)、Phase6(`TASK-WORKER-001`/
`TASK-WORKER-002`/`TASK-DESKTOP-001`/`TASK-DESKTOP-002`/`TASK-UI-001`〜
`005`/`TASK-DESKTOP-003`の9件、全完了)、Phase7(`TASK-MIGRATION-001`/
`TASK-E2E-001`/`TASK-RELEASE-001`/`TASK-RELEASE-002`の4件、全完了)、
合計50タスク(**MVP対象50/50、全完了**)は本実装・Red確認・対象テスト・
Phase全体回帰まで完了し、Python対象394ケース+Vitest対象73 caseが
すべてpassする(うち`TASK-OCR-001`の2 case(TC-11/TC-12)はTesseract
未導入、`TASK-AI-001`の2 case(TC-11/TC-12)は`GEMINI_API_KEY`未設定、
`TASK-VOICEVOX-001`の2 case(TC-11/TC-12)は`VOICEVOX_URL`未設定・
VOICEVOX Engine未起動、`TASK-AUDIO-002`の2 case(TC-09/TC-10)は
`FFMPEG_PATH`/`FFPROBE_PATH`未設定・ffmpeg/ffprobe未導入、
`TASK-DESKTOP-002`の2 case(TC-11/TC-12)と`TASK-DESKTOP-003`の2 case
(TC-11/TC-12)は`WALKWISE_RUN_INTEGRATION_SMOKE`/
`WALKWISE_RUN_INTEGRATION_LIVE`/`WALKWISE_PYTHON_EXECUTABLE`未設定の
ため、`TASK-E2E-001`の2 case(TC-11/TC-12)は`VOICEVOX_URL`未設定・
VOICEVOX Engine未起動のため、`TASK-RELEASE-001`の2 case(TC-11/TC-12)は
`WALKWISE_PYTHON_EXECUTABLE`/`FFMPEG_PATH`/`FFPROBE_PATH`/
`TESSERACT_CMD`のいずれも未設定のため、この環境では未確認、既定skip)。
`TASK-RELEASE-002`の10 case中3 case(TC-01,02,03)は`performance`/
`resilience`markerにより通常pytestからは除外されるが、
`WALKWISE_RUN_PERFORMANCE=1`/`WALKWISE_RUN_RESILIENCE=1`のopt-in実行で
10/10 pass確認済み。post-MVPの`TASK-EPUB-001`(EPUBテキスト抽出、
外部接続なし、10 case全pass)、`TASK-M4B-001`(M4B出力、external_gate、
7 case実測pass・TC-02,09,10は`FFMPEG_PATH`未設定のため既定skip)、
`TASK-ASR-001`(ASRによる原稿・音声照合、external_gate、10 case実測
pass・TC-11,12は`WALKWISE_ASR_ENABLED`未設定のため既定skip)も
完了した。**これで全54タスク中53タスク(MVP対象50件+post-MVP対象3件)が
完了し、残るのは永久blockedの`TASK-COEIR-001`だけである。**人間承認
gateの通過は完了済み53タスクの変更範囲に限る。

**MVP判定**: code completeは「はい」(MVP対象50/50タスク完了)。
release readyは「いいえ」(Gemini/Tesseract/VOICEVOX/ffmpeg/実Python
Worker/実Electron起動/Windows installer実インストール等の実runtime群が
この開発環境で未確認のため。詳細は`release/checklist.md`)。

**post-MVP判定**: 3/3タスクが完了。ASR/M4Bともexternal_gateのため、
実際のffmpeg/ローカルWhisper互換runtimeでの疎通・実機能確認は
この環境では未実施(既定skip、失敗を隠すものではない)。

`TASK-RELEASE-002`完了に伴い、`TASK-DESKTOP-003`が申し送っていた
`electron/main/ipc/builds.ts`と`jobs.ts`の`job:start` channel重複を
解消した(builds.tsを正として両payload形状を統合、jobs.tsの登録を削除)。
影響を受けた`TASK-UI-004`/`TASK-DESKTOP-003`の関連Vitest testを
同一`ipcMain`共有へ更新し再回帰・pass確認済み(詳細は
`implementation_assumptions.md`)。

`TASK-COEIR-001`(COEIROINK)は、公式API世代・endpoint・話者識別子・
利用条件・リリンちゃんの正式な解決方法が確認できるまで、引き続き
永久blockedとして実装しない。次は最終repository-wide reviewと完了報告。

## 現在確認できるtest file

契約上の109件すべてが存在する。個別ファイル名の一覧は
[`STEP6_MANIFEST.json`](STEP6_MANIFEST.json)の`planned_test_files`を正本とする。
本書には重複して一覧を持たない。

## 欠落test file

なし(0件)。

## 実測した確認結果(2026-07-20、TASK-REVIEW-001完了時点 — 実行時統合実装後)

TASK-ASR-001完了時点(下記節)からの差分。契約実装の件数(53/54タスク)自体は
変化していない。実行時統合の実装により、Worker command登録・Renderer wiring・
安全なfile picker・実build pipeline関連のtestが新規に追加されている。

| 確認 | 結果 |
|---|---|
| Python構文 (`python -m compileall -q script tests`) | 成功 |
| pytest collection (`--collect-only -q`) | 463件収集(TASK-ASR-001時点の454から+9: worker command registry test 8件 + source symlink拒否 test 1件) |
| pytest通常実行 (`-m "not integration_smoke and not integration_live and not performance and not resilience"`) | 430 passed, 23 deselected, 10 xfailed(TASK-ASR-001時点の421から+9、xfailedは`TASK-COEIR-001`分のまま変化なし) |
| TypeScript型検査 (`npm run typecheck`) | 成功、error 0件 |
| Vitest (`npm test -- --run`) | 20 test files / 106 tests、103 passed + 3 skipped(TASK-ASR-001時点の16 files/73 passedから、composition root・Worker adapter・file picker・Renderer root(App.vue)関連のtest追加) |
| `npm run build` | 成功。`dist/main/electron_main.js`・`dist/preload/index.js`・`dist/renderer/index.html`の生成を確認 |
| `npx electron-builder --dir` | 成功。`release/win-unpacked/Walkwise.exe`生成、`app.asar`内entrypoint存在確認、`--version`実行確認(exit code 0) |
| Python Worker subprocess smoke(`echo '...' \| python -m script.worker.cli`) | 成功。`health`/`db.migrate`/`project.create`の実応答をJSON Linesで確認、exit code 0 |
| 実GUI起動(`npm run start`での実ウィンドウ表示) | 未確認(本開発環境にディスプレイなし) |
| 外部接続(Gemini/Tesseract/VOICEVOX/ffmpeg) | 0(この開発環境では引き続き未設定) |

## 実測した確認結果(2026-07-20、TASK-ASR-001完了時点 — 全53タスク完了、残りTASK-COEIR-001のみ)

外部接続なしで次を確認した。

| 確認 | 結果 |
|---|---|
| 契約上のtest file 109件の存在確認 | 109/109 成功(欠落0) |
| Python構文 (`python -m compileall -q script tests`) | 成功 |
| pytest collection (`--collect-only -q`) | 454件収集、未知marker warningなし(host/Docker一致) |
| pytest通常実行、host (`-m "not integration_smoke and not integration_live and not performance and not resilience"`) | 421 passed, 23 deselected, 10 xfailed(TASK-ASR-001完了時点で再測、TASK-M4B-001完了時点の411から+10。残る10 xfailedはすべて`TASK-COEIR-001`分) |
| pytest performance/resilience opt-in、host (`WALKWISE_RUN_PERFORMANCE=1 WALKWISE_RUN_RESILIENCE=1`) | `tests/performance/test_large_sources.py`+`tests/resilience/test_failure_recovery.py`の10 case全pass(Phase7 close-out時点で確認済み) |
| `npm ci` | 成功(470 packages、vulnerabilities 0件、Phase6完了時点で確認済み) |
| TypeScript型検査 (`npm run typecheck`) | 成功、error 0件(TASK-ASR-001完了時点で再確認、変化なし) |
| Vitest (`npm test -- --run`) | 16 test files / 76 tests、73 passed + 3 skipped(TASK-ASR-001完了時点で再確認、変化なし。EPUB/M4B/ASRはいずれもPython専用) |
| Docker (`docker compose build test`) | 成功(TASK-ASR-001完了時点で再確認) |
| Docker pytest collection | 454件収集(host一致) |
| Docker pytest通常実行 | 414 passed, 7 skipped, 23 deselected, 10 xfailed(414+7=421でhostと完全一致) |
| `TASK-ASR-001` integration_smoke(`WALKWISE_ASR_ENABLED`未設定) | 既定でskip(未実行、未確認として記録) |
| `TASK-M4B-001` integration_smoke(`FFMPEG_PATH`未設定) | 既定でskip(未実行、未確認として記録。`TASK-AUDIO-002`と同じ`ffmpeg_connectivity_gate`を再利用) |
| `TASK-OCR-001` integration_smoke(`TESSERACT_CMD`未設定) | 明示opt-in時も秘密値なしでskip(設定確認段階で正しく停止) |
| `TASK-AI-001` integration_smoke(`GEMINI_API_KEY`未設定) | 既定でskip(未実行、未確認として記録) |
| `TASK-VOICEVOX-001`/`TASK-E2E-001` integration_smoke(`VOICEVOX_URL`未設定) | 既定でskip(未実行、未確認として記録。`TASK-E2E-001`は`TASK-VOICEVOX-001`と同じ`voicevox_connectivity_gate`を再利用) |
| `TASK-RELEASE-001`/`TASK-RELEASE-002` integration_smoke(`WALKWISE_PYTHON_EXECUTABLE`/`FFMPEG_PATH`/`FFPROBE_PATH`/`TESSERACT_CMD`未設定) | 既定でskip(未実行、未確認として記録) |
| `TASK-AUDIO-002` integration_smoke(`FFMPEG_PATH`/`FFPROBE_PATH`未設定) | 既定でskip(未実行、未確認として記録) |
| 外部接続 | 0 |

pytestの実行方法によって「23 deselected」(`-m`でmarker除外)と「23 skipped」
(marker除外なし、conftestの動的skip)のいずれかで表示されるが、対象件数はどちらも
同じ23件であり、内容に矛盾はない。

## 完了タスク一覧(Phase1: 8件)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-DEV-001` | `pyproject.toml`, `tests/conftest.py`, `script/__init__.py` | 10 |
| `TASK-ENV-001` | `Dockerfile`, `docker-compose.yml`, `.dockerignore` | 9 |
| `TASK-CORE-001` | `script/core/config.py`, `errors.py`, `logging.py` | 8 |
| `TASK-CORE-002` | `script/core/identifiers.py`, `hashing.py`, `serialization.py` | 8 |
| `TASK-FILE-001` | `script/persistence/paths.py`, `files.py`, `locking.py` | 9 |
| `TASK-DOMAIN-001` | `script/domain/models.py`, `enums.py`, `validation.py` | 9 |
| `TASK-DB-001` | `script/persistence/database.py`, `migrations.py`, `sql/0001_initial.sql` | 10 |
| `TASK-DB-002` | `script/persistence/repositories.py`, `unit_of_work.py` | 8 |

新規依存として`requirements.txt`へ`pyyaml==6.0.2`を追加(`TASK-CORE-002`、
`load_yaml/dump_yaml`実装に必須)。

## 完了タスク一覧(Phase2: 7件)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-PROJECT-001` | `script/schemas/project_plan.py`, `script/services/projects.py` | 7 |
| `TASK-SOURCE-001` | `script/schemas/source_metadata.py`, `script/services/sources.py` | 8 |
| `TASK-RIGHTS-001` | `script/schemas/rights.py`, `script/services/rights.py` | 10 |
| `TASK-BUILD-001` | `script/services/build_requests.py` | 8 |
| `TASK-JOB-001` | `script/domain/job_state.py`, `script/services/jobs.py` | 10 |
| `TASK-ARTIFACT-001` | `script/services/artifacts.py` | 9 |
| `TASK-APPROVAL-001` | `script/schemas/approvals.py`, `script/services/approvals.py` | 10 |

Phase2の`ApprovalService`は他タスクと異なりDBを使わず、`project/approvals.yaml`
(file正本)を読み書きする設計とした。詳細な仮定は`docs/notes/implementation_assumptions.md`
の該当タスク節を参照。

## 完了タスク一覧(Phase3: 7件全完了)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-INGEST-001` | `script/source_processing/orchestrator.py`, `text_ingestion.py` | 9 |
| `TASK-IMAGE-001` | `script/source_processing/images/ingestion.py`, `manifest.py` | 10 |
| `TASK-IMAGE-002` | `script/source_processing/images/preprocess.py`, `quality.py` | 8 |
| `TASK-PDF-001` | `script/source_processing/pdf/extract.py`, `models.py` | 10 |
| `TASK-OCR-001` | `script/source_processing/ocr/client.py`, `pipeline.py` | 10(+2未確認) |
| `TASK-SOURCE-002` | `script/source_processing/normalize.py`, `chunking.py`, `manifests.py` | 10 |
| `TASK-SOURCE-003` | `script/schemas/source_review.py`, `script/services/source_review.py` | 10 |

新規依存として`requirements.txt`へ`PyMuPDF==1.24.14`/`pypdf==6.10.2`/
`cryptography==47.0.0`を追加(`TASK-PDF-001`、PyMuPDF primary / pypdf
secondary adapter実装に必須。`cryptography`はDocker全体回帰で発見した
横断バグ修正、詳細は`docs/notes/implementation_assumptions.md`参照)。

`TASK-OCR-001`は`tests/conftest.py`(`TASK-DEV-001`所有)の
`tesseract_connectivity_gate` placeholder fixtureを実装した。他タスクが
担当しない1対1専用fixtureのため。詳細は`docs/notes/implementation_assumptions.md`
を参照。

## 完了タスク一覧(Phase4: 7件全完了、Phase5: 7件全完了)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-AI-001` | `script/ai_clients/base.py`, `registry.py`, `gemini/client.py`(既存legacy実装は無変更) | 10(+2未確認) |
| `TASK-AI-002` | `script/ai/routing.py`, `cache.py`, `budget.py` | 10 |
| `TASK-AI-003` | `script/pipelines/source_analysis.py`, `script/schemas/source_analysis.py` | 10 |
| `TASK-CURRICULUM-001` | `script/pipelines/curriculum.py`, `script/schemas/curriculum.py`, `script/schemas/chapter_spec.py` | 10 |
| `TASK-SCRIPT-001` | `script/pipelines/draft_generation.py`, `script/schemas/script.py` | 9 |
| `TASK-CLAIM-001` | `script/pipelines/claims.py`, `script/schemas/claims.py` | 10 |
| `TASK-PROFILE-001` | `script/profiles/characters.py`, `script/profiles/voices.py`, `script/schemas/profiles.py` | 9 |
| `TASK-NARRATION-001` | `script/pipelines/narration.py`, `script/pipelines/semantic_review.py` | 10 |
| `TASK-PIPELINE-001` | `script/pipelines/impact.py`, `script/pipelines/regeneration.py` | 10 |
| `TASK-TTS-001` | `script/tts_clients/base.py`, `registry.py`, `models.py` | 10 |
| `TASK-VOICEVOX-001` | `script/tts_clients/voicevox/client.py`, `adapter.py`(既存legacy実装は無変更) | 10(+2未確認) |
| `TASK-AUDIO-001` | `script/audio/synthesis.py`, `cache.py`, `preview.py` | 10 |
| `TASK-AUDIO-002` | `script/audio/validation.py`, `measurements.py`, `thresholds.py` | 8(+2未確認) |
| `TASK-AUDIO-003` | `script/schemas/production_manifest.py`, `script/audio/packaging.py`, `script/pipelines/build.py` | 10 |

`TASK-AI-001`は`tests/conftest.py`の`gemini_connectivity_gate`、
`TASK-VOICEVOX-001`は同`voicevox_connectivity_gate`、`TASK-AUDIO-002`は
同`ffmpeg_connectivity_gate` placeholder fixtureを実装した
(`TASK-OCR-001`と同様の1対1専用fixture)。
`TASK-AUDIO-001`は依存タスク(`TASK-TTS-001`/`TASK-VOICEVOX-001`)の
`script/tts_clients/models.py`(`SynthesisResult.audio_bytes`追加)と
`script/tts_clients/voicevox/adapter.py`(その値の設定)を横断的に
拡張した(後方互換な追加、両タスクの全対象テストを再実行し回帰なしを
確認済み。詳細は`implementation_assumptions.md`)。
`TASK-CLAIM-001`は`docs/commands/fact-checking.md`、`TASK-PROFILE-001`は
`docs/commands/profiles.md`、`TASK-PIPELINE-001`は
`docs/commands/regeneration.md`、`TASK-TTS-001`は`docs/commands/tts.md`、
`TASK-AUDIO-002`は`docs/commands/audio-validation.md`、`TASK-AUDIO-003`は
`docs/commands/audio-packaging.md`(いずれも担当分)を修正した。
`TASK-NARRATION-001`/`TASK-VOICEVOX-001`/`TASK-AUDIO-001`は
`documentation_repair_ownership`が空のため対象外(`tts.md`のvoicevox
関連行は`TASK-TTS-001`が既に「未着手」として記述済みだったが、
`TASK-VOICEVOX-001`自体は文書修正を担当しないため、その記述は本タスク
完了後もまだ更新されていない既知の不整合として残る)。

詳細は`docs/notes/implementation_assumptions.md`および`docs/notes/progress.md`を参照。

## 完了タスク一覧(Phase6: 9件全完了)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-WORKER-001` | `script/worker/protocol.py`, `handlers.py`, `cli.py` | 10 |
| `TASK-WORKER-002` | `script/worker/cancellation.py`, `runtime.py` | 10 |
| `TASK-DESKTOP-001` | `electron/main/index.ts`, `electron/preload/index.ts`, `electron/renderer/main.ts` | 9 |
| `TASK-DESKTOP-002` | `electron/main/bootstrap.ts`, `database.ts`, `worker_manager.ts` | 10(+2未確認) |
| `TASK-UI-001` | `electron/main/ipc/projects.ts`, `electron/renderer/screens/ProjectList.vue`, `electron/renderer/api/projects.ts` | 9 |
| `TASK-UI-002` | `electron/main/ipc/sources.ts`, `approvals.ts`, `electron/renderer/screens/ProjectWorkspace.vue` | 9 |
| `TASK-UI-003` | `electron/main/ipc/voice.ts`, `builds.ts`, `electron/renderer/screens/BuildSettings.vue` | 9 |
| `TASK-UI-004` | `electron/main/ipc/jobs.ts`, `artifacts.ts`, `electron/renderer/screens/JobsAndArtifacts.vue` | 9 |
| `TASK-UI-005` | `electron/renderer/router.ts`, `stores/app.ts`, `components/AppShell.vue` | 9 |
| `TASK-DESKTOP-003` | `script/integration/mvp_flow.py`, `electron/tests/e2e/mvp-flow.test.ts` | 10(+2未確認) |

`TASK-WORKER-001`は`docs/commands/worker.md`(`TASK-WORKER-002`と共有する
文書のうち自タスク担当分のみ)を修正した。`TASK-DESKTOP-003`は
`docs/commands/end-to-end.md`(`TASK-E2E-001`と共有する文書のうち自タスク
担当分のみ)を修正した。`TASK-WORKER-002`/`TASK-DESKTOP-001`/
`TASK-DESKTOP-002`/`TASK-UI-002`/`TASK-UI-003`/`TASK-UI-004`/`TASK-UI-005`
は`documentation_repair_ownership`が空のため対象外。
`TASK-WORKER-002`は依存タスク`TASK-WORKER-001`の`script/worker/protocol.py`
(`_VALID_EVENT_TYPES`へ`cancel_requested`/`cancelled`を追加)を横断的に
拡張した(後方互換な追加、`TASK-WORKER-001`の全対象テストを再実行し
回帰なしを確認済み。詳細は`implementation_assumptions.md`)。
`TASK-DESKTOP-001`はPython側の変更なし(Electron/TypeScriptのみ)。
`TASK-DESKTOP-002`は依存タスク`TASK-WORKER-001`の`script/worker/cli.py`
(実行可能な`__main__` entrypointを追加、`main(stdin, stdout)`契約自体は
無変更)を横断的に拡張した(`TASK-WORKER-001`/`TASK-WORKER-002`の全20
caseを再実行し回帰なしを確認済み)。`TASK-DESKTOP-002`のintegration_smoke
(TC-11)/integration_live(TC-12)は`WALKWISE_RUN_INTEGRATION_SMOKE`/
`WALKWISE_RUN_INTEGRATION_LIVE`未設定のためこの環境では未確認。
`ProjectWorkspace.types.ts`/`BuildSettings.types.ts`/`JobsAndArtifacts.types.ts`
/`AppShell.types.ts`(新規、plain tscでの`.vue`named export型付け制約への
対処)を追加した。UI-001〜005の5画面タスクはこれで全完了。
`TASK-DESKTOP-003`のintegration_smoke(TC-11)/integration_live(TC-12)は
`WALKWISE_PYTHON_EXECUTABLE`/`WALKWISE_RUN_INTEGRATION_LIVE`未設定のため
この環境では未確認。E2E統合の過程で`electron/main/ipc/builds.ts`
(`TASK-UI-003`)と`electron/main/ipc/jobs.ts`(`TASK-UI-004`)が同じ
`"job:start"` channel名を異なるpayload形状で登録しているという技術的
負債を発見し、修正はせず`implementation_assumptions.md`へ記録して
後続作業(実Electron main entrypoint構築時)へ申し送った。

詳細は`docs/notes/implementation_assumptions.md`および`docs/notes/progress.md`を参照。

## Phase6完了(Desktop・Worker・UI)

- 完了タスク: `TASK-WORKER-001`, `TASK-WORKER-002`, `TASK-DESKTOP-001`,
  `TASK-DESKTOP-002`(external_gate), `TASK-UI-001`〜`005`,
  `TASK-DESKTOP-003`(external_gate)の計9タスク。
- 対象case数: Python 361 passed(Phase5完了時点の326から、Phase6で
  Python側は`TASK-WORKER-001/002`の20 case+`TASK-DESKTOP-003`の5 case=25
  caseを追加)。Vitest 16 test files/76 tests中69 caseが実assertion
  (Phase6で60 case追加: `TASK-DESKTOP-001`9+`TASK-DESKTOP-002`10+
  `TASK-UI-001`〜`005`各9×5=45+`TASK-DESKTOP-003`5=69のうちPhase5末の
  9を除く60)。
- 全体回帰: Python 361 passed, 23 deselected, 70 xfailed、Docker
  354 passed+7 skipped(354+7=361でhost一致)、TypeScript型検査success、
  Vitest 73 passed+3 skipped、予期しないfailなし。
- 外部接続未確認(既定skip、この環境に該当runtime/変数なし):
  `TASK-DESKTOP-002`(Python worker subprocess、
  `WALKWISE_RUN_INTEGRATION_SMOKE`/`_LIVE`)、`TASK-DESKTOP-003`
  (Desktop統合runtime、`WALKWISE_PYTHON_EXECUTABLE`/
  `WALKWISE_RUN_INTEGRATION_LIVE`)。いずれも設定済みかつ到達不能なら
  failする実装(skipで隠さない)。
- 置いた仮定: `implementation_assumptions.md`にPhase6内の各タスク分を
  個別記録済み(Vue testing基盤の導入、`.vue`named export型付け回避策、
  各画面のprops駆動設計、承認ゲートDI設計、`run_mvp_flow`の薄い
  orchestrator設計、`job:start`channel名重複という技術的負債)。
- 技術的負債: `electron/main/ipc/builds.ts`と`jobs.ts`の`"job:start"`
  channel名重複(上記参照、実main entrypoint構築時に解消が必要)。
- 次の開始タスク: Phase7 `TASK-MIGRATION-001`(legacy入力形式の変換)。

## 完了タスク一覧(Phase7: 全4件完了)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-MIGRATION-001` | `script/migration/legacy_models.py`, `adapters.py`, `report.py` | 10 |
| `TASK-E2E-001` | `tests/integration/test_sample_book_e2e.py`, `tests/fixtures/sample_book/` | 10(+2未確認) |
| `TASK-RELEASE-001` | `electron-builder.yml`, `electron/main/runtime.ts`, `script/maintenance/backup.py`, `resources/release-manifest.json` | 10(+2未確認) |
| `TASK-RELEASE-002` | `tests/performance/test_large_sources.py`, `tests/resilience/test_failure_recovery.py`, `release/checklist.md` | 10 |

`TASK-MIGRATION-001`は`docs/commands/migration.md`(担当分)を修正した。
新規依存の追加なし(`TASK-CORE-002`の`normalize_unit_id`/`load_json`/
`load_yaml`/`dump_json`をそのまま再利用)。`TASK-E2E-001`は
`docs/commands/end-to-end.md`(`TASK-DESKTOP-003`と共有する文書のうち
自タスク担当分のみ)を修正した。`run_sample_book_acceptance`は
`TASK-AI-002`の`AIRouter`/`AICache`/`BudgetGuard`、`TASK-APPROVAL-001`の
`ApprovalBundle`、`TASK-FILE-001`の`atomic_write_bytes`をそのまま再利用し、
新規依存の追加なし。integration_smoke/live(TC-11/TC-12)は
`TASK-VOICEVOX-001`の`voicevox_connectivity_gate`をそのまま再利用した。
`TASK-RELEASE-001`は`docs/commands/packaging.md`,
`docs/commands/backup-restore.md`(いずれも担当分)を修正した。
`resources/release-manifest.json`(新規静的artifact)を追加し、
`electron-builder.yml`の`extraResources`で同梱対象とした。`backup.py`は
`TASK-FILE-001`の`copy_immutable`を、TC-06の存在確認は
`TASK-AUDIO-002`の`AudioMeasurementAdapter`/`TASK-OCR-001`の`OcrClient`を
そのまま再利用し、新規依存の追加なし。`TASK-RELEASE-002`は
`docs/commands/performance.md`, `docs/commands/release.md`(いずれも
担当分)、`release/checklist.md`(全面更新)を修正した。新規production
moduleは追加せず、両test file自身が`TASK-FILE-001`の
`atomic_write_bytes`、`TASK-JOB-001`の`JobService`/`can_transition`、
`TASK-WORKER-002`の`WorkerRuntime`/`recover_after_abnormal_exit`、
`TASK-SOURCE-002`の`normalize_text`をそのまま呼び出す形でscenarioを
実装した。同タスクで`electron/main/ipc/builds.ts`/`jobs.ts`の
`job:start` channel重複を解消し(詳細は次段落)、`TASK-UI-004`/
`TASK-DESKTOP-003`の関連Vitest 3ファイルを再回帰・pass確認した。
詳細は`docs/notes/implementation_assumptions.md`および
`docs/notes/progress.md`を参照。

## Phase7完了(Migration・E2E・Release)・MVP全50タスク完了

- 完了タスク: `TASK-MIGRATION-001`, `TASK-E2E-001`, `TASK-RELEASE-001`
  (external_gate), `TASK-RELEASE-002`の計4タスク。これでPhase1〜7の
  MVP対象50タスクが全完了した。
- 対象case数: Python 394 passed(Phase6完了時点の361から、Phase7で
  Python側は+33 case)。Vitest 16 test files/76 tests中73 caseが実assertion
  (Phase6末の69から、`TASK-RELEASE-001`の+4)。
- 全体回帰: Python 394 passed, 23 deselected, 37 xfailed、Docker
  387 passed+7 skipped(387+7=394でhost一致)、TypeScript型検査success、
  Vitest 73 passed+3 skipped、予期しないfailなし。
- 既知のIPC技術的負債を解消: `electron/main/ipc/builds.ts`と`jobs.ts`の
  `job:start` channel重複(Phase6で発見・申し送り)を`TASK-RELEASE-002`で
  解消した。builds.tsを正として両payload形状(新規Job起動の
  buildRequestId文字列/再試行の`{parentJobId}`オブジェクト)を1つの
  handlerで処理し、jobs.ts側の`job:start`登録を削除した。
- 外部接続未確認(既定skip、この環境に該当runtime/変数なし):
  `TASK-OCR-001`(Tesseract)、`TASK-AI-001`(Gemini)、
  `TASK-VOICEVOX-001`/`TASK-E2E-001`(VOICEVOX)、`TASK-AUDIO-002`
  (ffmpeg/ffprobe)、`TASK-DESKTOP-002`/`003`(Python worker subprocess)、
  `TASK-RELEASE-001`/`TASK-RELEASE-002`(配布runtime群)。いずれも
  設定済みかつ到達不能ならfailする実装(skipで隠さない)。
- MVP判定: code complete=はい、release ready=いいえ(実runtime群未確認、
  詳細は`release/checklist.md`)。
- 次: post-MVPの`TASK-EPUB-001`→`TASK-M4B-001`→`TASK-ASR-001`。
  `TASK-COEIR-001`は永久blocked。

## 完了タスク一覧(post-MVP: 3/3件全完了)

| task_id | 対象ファイル(production) | case数 |
|---|---|---:|
| `TASK-EPUB-001` | `script/source_processing/epub/extract.py`, `models.py` | 10 |
| `TASK-M4B-001` | `script/audio/m4b.py`, `script/schemas/m4b_manifest.py` | 7(+3未確認) |
| `TASK-ASR-001` | `script/asr/base.py`, `script/asr/verification.py` | 10(+2未確認) |

`TASK-EPUB-001`は`docs/commands/epub.md`(担当分)を修正した。新規依存の
追加なし(Python標準ライブラリの`zipfile`/`xml.etree.ElementTree`のみで
EPUB(zip+XML)を解析し、`ebooklib`等の外部ライブラリを追加していない)。
`EpubTextExtractor.extract()`はfilesystemへの書込みを一切行わない
純粋な読込み専用関数とした(資料登録pipelineへの統合は対象外、詳細は
`implementation_assumptions.md`)。`TASK-M4B-001`は`docs/commands/m4b.md`
(担当分)を修正した。新規依存の追加なし。`M4BTool.check_runtime`は
`TASK-AUDIO-002`の`AudioMeasurementAdapter`と同型の`ffmpeg_cmd`/
`runner`注入パターンを踏襲し、TC-09/TC-02/TC-10は`TASK-AUDIO-002`と
同じ`ffmpeg_connectivity_gate`を再利用した。`validation_threshold_
status`は依存仕様(`audio-validation-thresholds.md`)がprovisionalの
ため常に`"provisional"`固定とし、全文MP3を生成する経路は一切実装
しなかった。`TASK-ASR-001`は`docs/commands/asr.md`(担当分)を修正した。
新規依存の追加なし(`subprocess`/`json`/`tempfile`標準ライブラリのみ)。
`LocalWhisperCompatibleClient`は`TASK-OCR-001`の`OcrClient`と同型の
`command`/`runner`注入patternを踏襲し、`ASRVerificationReport.status`は
`"pass"/"warning"/"review_required"`の3値のみを型で許可し`"fail"`を
構造的に設定不可能にした(5.5節の自動fail禁止を型で保証)。
詳細は`implementation_assumptions.md`を参照。

- 対象case数: Python 421 passed(Phase7完了時点の394から、post-MVPで
  Python側は+27 case[`TASK-EPUB-001`10+`TASK-M4B-001`7+`TASK-ASR-001`10])。
- 全体回帰: Python 421 passed, 23 deselected, 10 xfailed(残り10はすべて
  `TASK-COEIR-001`分)、Docker 414 passed+7 skipped(414+7=421でhost
  一致)、TypeScript型検査success、Vitest 73 passed+3 skipped(変化なし、
  3タスクともPython専用のため)、予期しないfailなし。
- 外部接続未確認(既定skip): `TASK-M4B-001`のTC-02,09,10
  (`FFMPEG_PATH`未設定)、`TASK-ASR-001`のTC-11,12
  (`WALKWISE_ASR_ENABLED`未設定)。
- **post-MVP 3/3件完了。全54タスク中53タスクが完了し、残るのは
  永久blockedの`TASK-COEIR-001`のみ。次は最終repository-wide reviewと
  完了報告。**

## 次に必要な作業

1. Phase1〜7(MVP対象50タスク)とpost-MVP対象3タスク
   (`TASK-EPUB-001`/`TASK-M4B-001`/`TASK-ASR-001`)がすべて完了した。
   全54タスク中53タスクが完了し、残るのは永久blockedの
   `TASK-COEIR-001`のみである。次に必要な作業は、実runtime群が用意
   できた場合の疎通確認(下記6.)と、最終repository-wide review・
   完了報告のみ。`TASK-COEIR-001`は公式API世代・endpoint・話者識別子・
   利用条件が確認できるまで実装しない。
2. `TASK-DESKTOP-002`のintegration_smoke/integration_live(TC-11/TC-12)は
   `WALKWISE_RUN_INTEGRATION_SMOKE`/`WALKWISE_RUN_INTEGRATION_LIVE`と
   実Python実行体が用意可能な環境で、config確認→smoke→(成功時のみ)liveの
   順で確認する。
3. `TASK-UI-001`で追加した`@vue/test-utils`/`jsdom`/`@vitejs/plugin-vue`+
   `vitest.config.ts`は、以後のUI-*タスクすべてがそのまま再利用する
   (再導入不要)。DOM操作を伴うtest fileには
   `/** @vitest-environment jsdom */`docblockを付与する。
2. `TASK-OCR-001`のintegration_smoke/integration_live(TC-11/TC-12)は
   この開発環境にTesseract runtimeが未導入のため未確認のまま。`TESSERACT_CMD`
   と実際のTesseract実行体が用意可能な環境で、`WALKWISE_RUN_INTEGRATION_SMOKE=1`
   →成功時のみ`WALKWISE_RUN_INTEGRATION_LIVE=1`の順で確認する。
3. `TASK-AI-001`のintegration_smoke/integration_live(TC-11/TC-12)は
   `GEMINI_API_KEY`が未設定のため未確認のまま。実キーが用意可能な環境で
   同様の順序で確認する。
3b. `TASK-VOICEVOX-001`のintegration_smoke/integration_live(TC-11/TC-12)は
   `VOICEVOX_URL`が未設定・VOICEVOX Engineも未起動のため未確認のまま。
   実際のVOICEVOX Engineが用意可能な環境で同様の順序で確認する。
3c. `TASK-AUDIO-002`のintegration_smoke/integration_live(TC-09/TC-10)は
   `FFMPEG_PATH`/`FFPROBE_PATH`が未設定・ffmpeg/ffprobeも未導入のため
   未確認のまま。実際のffmpeg/ffprobeが用意可能な環境で同様の順序で
   確認する。
4. 各タスクは、自身の`documentation_repair_ownership`に列挙された文書だけを修正する。
   本書とSTEP6_MANIFEST.jsonの全体集計は、進捗に応じて実装タスク側から更新する。
5. `docs/commands/`配下の分野別コマンド文書のうち、Phase1完了タスクが担当する
   `environment.md`, `configuration.md`, `data-validation.md`, `storage.md`,
   `database.md`、Phase2完了タスクが担当する`projects.md`, `sources.md`,
   `rights.md`, `builds.md`, `jobs.md`, `artifacts.md`, `approvals.md`、
   Phase3完了タスクが担当する`source-processing.md`, `images.md`, `pdf.md`,
   `ocr.md`, `source-review.md`、`TASK-AI-001`が担当する`ai.md`、
   `TASK-AI-003`が担当する`content-generation.md`(自タスク分のみ)、
   `TASK-CLAIM-001`が担当する`fact-checking.md`、`TASK-PROFILE-001`が
   担当する`profiles.md`、`TASK-PIPELINE-001`が担当する
   `regeneration.md`、`TASK-TTS-001`が担当する`tts.md`(自タスク分のみ)、
   `TASK-AUDIO-002`が担当する`audio-validation.md`、`TASK-AUDIO-003`が
   担当する`audio-packaging.md`は修正済み。
   `TASK-IMAGE-002`/`TASK-AI-002`/`TASK-CURRICULUM-001`/`TASK-SCRIPT-001`/
   `TASK-NARRATION-001`/`TASK-VOICEVOX-001`/`TASK-AUDIO-001`は
   `documentation_repair_ownership`が空のため対象外。残りの分野別文書は、
   それぞれの担当タスク実装時に古い記述を修正する。
6. `TASK-OCR-001`(Tesseract)、`TASK-AI-001`(Gemini)、
   `TASK-VOICEVOX-001`/`TASK-AUDIO-002`(ffmpeg/ffprobe)、
   `TASK-DESKTOP-002`/`TASK-DESKTOP-003`(Python worker subprocess)、
   `TASK-RELEASE-001`/`TASK-RELEASE-002`(配布runtime群)、
   `TASK-M4B-001`(ffmpeg)、`TASK-ASR-001`(ローカルWhisper互換runtime)
   は、いずれも本実装済みで疎通のみ未確認の`external_gate=true`タスク
   である。実runtimeが用意できた環境で、config確認→
   `integration_smoke`→(成功時のみ)`integration_live`の順で確認する。
   `TASK-COEIR-001`(COEIROINK)は公式API世代・endpoint・話者識別子・
   利用条件が未確認のため引き続きblocked。
