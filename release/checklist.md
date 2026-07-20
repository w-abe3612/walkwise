---
document_type: release_acceptance_checklist
status: review
version: '2.0'
last_updated: '2026-07-20'
related_task: TASK-REVIEW-001
---

# Walkwise MVP release checklist

本書は`docs/tasks/TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md`の
完了条件(9節)を満たす、人間判定用のrelease受入チェックリストである。
「コード実装済み(contract implementation complete)」と「実アプリとして起動・動作する
ことを確認済み(real app verified running)」と「release ready(実機配布可)」の3つを
混同しない。

v1.0(TASK-RELEASE-002時点)は、個別task契約がすべてmock/DI設計でpassしている一方、
Electronの`app.whenReady()`を実際に呼び出す起動経路が存在せず、Python Workerの
handler registryが空で、Rendererの5画面がどこにも結線されていない、という状態だった。
本v2.0は、その実行時統合(composition root・Worker command registry・IPC adapter・
Renderer root・安全なfile picker・実build/package)を実装・検証した結果を反映する。

## 1. 契約実装(MVP + post-MVP、変更なし)

- [x] MVP対象50タスク + post-MVP対象3タスク(EPUB/M4B/ASR)すべて実装完了。
      `TASK-COEIR-001`のみ、公式API世代・endpoint・話者識別子・利用条件が未確認のため
      永久blocked。
- [x] Python通常回帰: 435 passed / 23 deselected / 10 xfailed(2026-07-20実測、
      `python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"`)。
- [x] TypeScript型検査: `npm run typecheck` success、error 0件。
- [x] Vitest: 103 passed / 3 skipped(106 total)、`test.fails`placeholder 0件。

## 2. 実行時統合(TASK-REVIEW-001で新規に実装・検証)

- [x] **Electron composition root**(`electron/main/app_entry.ts`): `app.whenReady()`→
      data root確保→backup→Python Worker起動→DB migration→stale job recovery→
      health確認→全IPC handler登録(単一`ipcMain`、channel重複なし)→
      `BrowserWindow`作成、を実際に行うentrypointを新規実装。bootstrap失敗時・
      window作成失敗時のいずれも、Worker subprocess/DBを後始末してから例外を
      伝播することをtestで確認済み(`electron/tests/app_entry.test.ts`)。
- [x] **Python Worker command registry**(`script/worker/commands.py`): 以前
      `python -m script.worker.cli`は空の`HandlerRegistry()`で起動しており、
      `health`すら`unknown_job_type`で拒否していた。既存の承認済みservice
      (Project/Source/Approval/Build/Job/Artifact/Voice)へ委譲する20種類の
      job_typeを実装し、実subprocess経由の`health`/`db.migrate`/`project.create`
      往復をshell上で実測確認(`echo '{"job_id":...}' | python -m script.worker.cli`、
      exit code 0)。
- [x] **Electron⇔Worker service adapter**(`electron/main/worker_service_adapters.ts`):
      Project/Source/Approval/Build/Job/Artifact/Voice各`*ServiceLike`を、
      WorkerManager経由でPython側へ委譲する実装を新規追加(以前はどの
      `*ServiceLike`にも実装が存在しなかった)。
- [x] **IPC channel不整合の修正**: `job:progress-event`(mainが実際にsendするchannel)を
      preloadが購読していなかった不具合を修正。`project:get`(preloadは呼ぶが
      main handlerが存在しなかった)、`source:list`/`source:retry`/`job:list`
      (Workspace/Jobs画面に必要だが存在しなかった)を新規追加。
- [x] **Renderer root**(`electron/renderer/App.vue`): 以前`electron/renderer/main.ts`は
      空のplaceholder divをmountするだけで、5画面のどれも表示・結線されていなかった。
      router(`resolveNavigation`)・store(`AppStore`)・5画面・`window.walkwise`を
      実際に結線し、Project一覧→workspace→build設定→job/artifactの縦切りを
      実DOM操作(mock `window.walkwise`)で検証(`electron/renderer/tests/App.test.ts`)。
- [x] **安全なfile picker**(`electron/main/ipc/files.ts`): 以前`ProjectWorkspace.vue`は
      ブラウザの`File.name`(実在するpathではない)をそのまま`source:register`へ
      送っており、main/Workerは対象fileを一度も実際に読めなかった。
      `dialog.showOpenDialog()`経由でのみfile選択できるよう変更し、拡張子・実在・
      通常ファイル・非symlink・非UNC・非traversalを検証。加えて
      `SourceMetadata.from_file`(Python側)へもsymlink拒否を追加(多重防御)。
- [x] **fail-closed承認gate**: `registerBuildIpcHandlers`は`approvalGateChecker`
      未注入時に登録自体が失敗することを確認(既存実装のまま、専用testを追加)。
      実装は`build_request.approval_gate_satisfied`(Python側の実判定)へ委譲し、
      Electron main側のcheckerをrubber-stampにしないよう設計。
- [x] **実build pipeline**: 以前`npm run build`は`tsc --noEmit`(型検査のみ)で、
      実HTML/JS/CSSを一切生成していなかった。`vite.config.ts`(Renderer)・
      `tsconfig.main.json`(main/preload、CommonJS出力)・
      `scripts/finalize-dist.mjs`を新規追加し、`npm run build`で
      `dist/main/electron_main.js`・`dist/preload/index.js`・
      `dist/renderer/index.html`が実際に生成されることを確認。
      `package.json`の`main`フィールドを`dist/main/electron_main.js`へ設定。
- [x] **package生成**: `npx electron-builder --dir`を実行し、
      `release/win-unpacked/Walkwise.exe`が生成され、`app.asar`内に
      `dist/main/electron_main.js`・`dist/preload/index.js`・
      `dist/renderer/index.html`が存在することを`asar list`で確認。
      `Walkwise.exe --version`が実行できることを確認(exit code 0)。
      (packageを試みる過程で、`electron`パッケージが誤って`dependencies`に
      入っていたためelectron-builderが拒否する既存の設定不備も発見・修正した。)

## 3. 実行結果の区別(混同しないこと)

- **mock E2E**(`TASK-DESKTOP-003`/`TASK-E2E-001`): fakeサービスによるIPC契約検証。従来どおりpass。
- **Python Worker subprocess smoke**(本review新規): 実`python -m script.worker.cli`
  subprocessへJSON Linesを送り、`health`/`db.migrate`/`project.create`の実応答を
  確認(shellでの手動実行+`electron/tests/app_entry.test.ts`のWorkerManager往復test)。
- **packaged-app smoke**(本review新規): `electron-builder --dir`で実packageを生成し、
  `app.asar`内entrypointの存在と`--version`実行を確認。**GUIウィンドウの実起動
  (`app.whenReady()`後の実際のBrowserWindow表示)は、本開発環境にディスプレイが
  ないため未確認。**

## 4. 実環境未確認(この開発環境で確認できなかった項目)

- [ ] **実GUI起動**: `npm run start`でElectronの実ウィンドウが表示され、Renderer上で
      Project作成→Source登録→承認→Build→Job進捗→Artifact表示が目視確認できること。
      本開発環境(headless)にディスプレイがないため未実施。composition root自体は
      mock Electron + 実WorkerManager + 実subprocessでtest済み。
- [ ] Gemini API(`GEMINI_API_KEY`未設定)。
- [ ] Tesseract OCR(`TESSERACT_CMD`未設定)。
- [ ] VOICEVOX Engine(`VOICEVOX_URL`未設定・Engine未起動。ただし`voice.list_engines`
      handlerはVOICEVOX起動有無に関わらず例外を投げない設計であることはtest済み)。
- [ ] ffmpeg/ffprobe(`FFMPEG_PATH`/`FFPROBE_PATH`未設定)。
- [ ] Windows NSISインストーラーの実インストール・実uninstall(`electron-builder --dir`
      による unpacked package生成とexe起動確認のみ実施。インストーラー生成自体
      (`electron-builder`のfullビルド)は未実施)。
- [ ] code signing(初期方針どおり未実施。`resources/release-manifest.json`に
      リスクと対処法を記録済み)。
- [ ] COEIROINK(`TASK-COEIR-001`、公式API世代・endpoint・話者識別子が未確認のため
      永久blocked。実装しない)。
- [ ] **実際のbuild execution pipeline**(AI原稿生成→TTS音声合成→M4B/MP3出力)の
      章単位進捗emit。`job.start`はJobの queued/running状態遷移のみを実装し、
      実際の生成処理本体は未接続のまま。調査の結果、この接続には
      (a) verified scriptの永続化先、(b) `BuildRequest`からchapterを特定する経路、
      (c) VoiceProfileを永続化から読み込む経路、の3点が現在どの承認済み仕様にも
      存在しないことが判明した。これらを推測で決めることは新しい業務仕様の
      推測実装に当たるため実装しなかった(詳細は`docs/notes/progress.md`の
      「実際のbuild execution pipeline統合について」節)。Renderer側の進捗表示は
      `job:get`の500ms pollingで実装した暫定措置(真のpush型progressではない)。

## 5. MVP release判定

- **contract実装**: complete(MVP 50/50 + post-MVP 3/3、`TASK-COEIR-001`のみ永久blocked)。
- **実アプリ起動**: unverified(composition root自体はmock Electron + 実subprocessで
  検証済みだが、実ディスプレイでのGUI起動は本環境で実施不可)。
- **package生成**: pass(`electron-builder --dir`成功、entrypoint解決確認、
  実行ファイル起動確認)。
- **release ready(実機配布可)**: いいえ。実GUI起動、外部runtime疎通(Gemini/
  Tesseract/VOICEVOX/ffmpeg)、実際のbuild pipeline統合、Windowsインストーラーの
  実インストール、code signingのいずれも未確認のため。

## 6. 既知の制限(意図的に対応しないもの、または本reviewの対象外)

- macOS/Linuxパッケージは対象外(初期対象はWindows x64のみ)。
- 自動更新は非対応(手動再インストール方式)。
- COEIROINK/リリンちゃんは統合しない(`TASK-COEIR-001`永久blocked)。
- 実際のAI原稿生成→TTS→M4B/MP3のbuild pipeline統合(章単位の実処理実行)は
  本reviewの対象外(個別pipelineの実装・testはPhase1〜6で完了済みだが、
  Worker経由の1本の実行フローへの統合は、未決定の設計判断3点(2節参照)を
  人間が決定した後の別task)。

## 7. 実行記録

```text
実行日時: 2026-07-20
対象タスク: TASK-REVIEW-001
実行コマンド:
  python -m compileall -q script tests dumps
  python -m pytest --collect-only -q
  python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
  npm ci
  npm run typecheck
  npm test -- --run
  npm run build
  npx electron-builder --dir
  release/win-unpacked/Walkwise.exe --version
  echo '{"job_id":"smoke-1","job_type":"health","parameters":{}}' | python -m script.worker.cli
  docker compose build test
  docker compose run --rm test python -m pytest --collect-only -q
  docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
収集件数: Python 468(host/Docker一致)、TypeScript/Vitest 20 test files
pass / fail / xfail / skip: Python 435 passed / 0 failed / 10 xfailed / 23 deselected(host)、
  Docker 428 passed + 7 skipped(docker CLI非対応環境skip) = 435でhostと完全一致、
  Vitest 103 passed / 0 failed / 3 skipped
npm run build: 成功(dist/main, dist/preload, dist/renderer/index.html生成確認)
electron-builder --dir: 成功(release/win-unpacked/Walkwise.exe生成、
  app.asar内entrypoint確認、--version実行確認)
Worker subprocess smoke: 成功(health/db.migrate/project.createの実応答確認、exit code 0)
外部疎通: 未実施(Gemini/Tesseract/VOICEVOX/ffmpeg/実GUI起動はこの開発環境で未確認)
未解決事項: 実GUI起動、外部runtime疎通、実際のbuild pipeline統合(未決定の設計判断3点)、
  Windowsインストーラーの実インストール、code signing。
```
