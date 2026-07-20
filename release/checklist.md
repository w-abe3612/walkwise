---
document_type: release_acceptance_checklist
status: review
version: '1.0'
last_updated: '2026-07-20'
related_task: TASK-RELEASE-002
---

# Walkwise MVP release checklist

本書は`docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md`
5節「release acceptance」の公開契約を満たす、人間判定用のrelease受入チェックリストである。
「コード実装済み」と「実runtime未確認」を混同しない。実runtime未確認の項目が残る場合でも、
**MVP code complete** と **release ready(実機配布可)** は別々に判定する。

## 1. MVP code complete(コード実装・自動テストで確認済み)

- [x] MVP対象50タスクすべてが実装完了(TASK-COEIR-001のみ永久blocked、post-MVP 3件は対象外)。
- [x] Python通常回帰: 394 passed / 23 deselected / 37 xfailed(2026-07-20実測、
      `python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"`)。
- [x] TypeScript型検査: `npm run typecheck` success、error 0件。
- [x] Vitest: 73 passed / 3 skipped(76 total)、`test.fails`placeholder 0件。
- [x] mock E2E(`TASK-DESKTOP-003`): Desktop起動→Project作成→承認→Build→Job→Artifactの
      縦切りがmock AI/TTS/worker/DB/fileでpass。
- [x] mock E2E(`TASK-E2E-001`): sample-book fixture(1章8segment、3資料、4主張、4承認)で
      正常系・7種の異常fixture・cache挙動がpass。
- [x] migration(`TASK-MIGRATION-001`): 旧book.json/sections.json変換、新形式優先、
      legacy text priorityがpass。
- [x] backup/restore(`TASK-RELEASE-001`): hash検証付きbackup/restore、部分破損時の
      明示的な部分復旧がpass。
- [x] packaging contract(`TASK-RELEASE-001`): Windows x64/nsis限定、code signing未実施表示、
      uninstall時データ非削除の設定がpass。
- [x] performance/resilience(`TASK-RELEASE-002`): disk full、強制終了/再起動、大規模入力の
      実測記録、cancel/restart、既存成果物保持、入力不変性がpass
      (`WALKWISE_RUN_PERFORMANCE=1`/`WALKWISE_RUN_RESILIENCE=1`のopt-in実行で10/10確認)。
- [x] 既知のIPC技術的負債(`electron/main/ipc/builds.ts`と`jobs.ts`の`job:start`
      channel重複)を解消済み。`builds.ts`が両payload形状(bareな`buildRequestId`文字列と
      `{parentJobId}`retryオブジェクト)を1つのhandlerで処理し、`jobs.ts`は
      `job:start`を登録しない。`TASK-UI-003`/`TASK-UI-004`/`TASK-DESKTOP-003`の
      関連テストを同一`ipcMain`上で再回帰し、pass確認済み(詳細は
      `docs/notes/implementation_assumptions.md`)。

## 2. 実環境未確認(コード実装済みだが、この開発環境ではruntime疎通未確認)

以下はすべて実装済み(mock/injectable設計で外部接続なしのテストはpass済み)だが、
実際のruntime・実サービスへの疎通はこの環境に必要な環境変数・実行体がないため未確認。
既定skipであり、失敗を隠すものではない。

- [ ] Gemini API(`TASK-AI-001`、`GEMINI_API_KEY`未設定)。
- [ ] Tesseract OCR(`TASK-OCR-001`、`TESSERACT_CMD`未設定)。
- [ ] VOICEVOX Engine(`TASK-VOICEVOX-001`/`TASK-E2E-001`、`VOICEVOX_URL`未設定・Engine未起動)。
- [ ] ffmpeg/ffprobe(`TASK-AUDIO-002`、`FFMPEG_PATH`/`FFPROBE_PATH`未設定)。
- [ ] 実Python Worker subprocess(`TASK-DESKTOP-002`/`003`、`WALKWISE_PYTHON_EXECUTABLE`未設定)。
- [ ] 実Electron起動(実ウィンドウ生成・実preload読込は本環境で未実施。単体/統合testは
      mockされたBrowserWindow/contextBridgeで検証済み)。
- [ ] Windows installer実インストール(`electron-builder`によるnsisインストーラー生成・
      実インストール・実uninstallは未実施。設定内容の静的検証のみ実施)。
- [ ] code signing(初期方針どおり未実施。`resources/release-manifest.json`に
      リスクと対処法を記録済み)。
- [ ] 配布runtime群の疎通(`TASK-RELEASE-001`、`WALKWISE_PYTHON_EXECUTABLE`/
      `FFMPEG_PATH`/`FFPROBE_PATH`/`TESSERACT_CMD`のいずれも未設定)。
- [ ] ASR(`TASK-ASR-001`、post-MVP、未着手)。
- [ ] COEIROINK(`TASK-COEIR-001`、公式API世代・endpoint・話者識別子が未確認のため
      永久blocked。実装しない)。

## 3. MVP release判定

- **code complete**: はい(MVP対象50/50タスク完了、通常回帰・mock E2E・performance/resilience
  すべてpass)。
- **mock E2Eの成功**: はい(`TASK-DESKTOP-003`/`TASK-E2E-001`とも通常テストでpass)。
- **release ready(実機配布可)**: いいえ。上記2節の実runtime未確認項目(特にElectron実起動・
  Windows installer実インストール・実Python Worker疎通)が確認されるまで、実機配布は
  推奨しない。
- **release readyでない理由**: 本開発環境には実VOICEVOX Engine、実Tesseract、実ffmpeg、
  実Python実行体、実Electronランタイム起動環境が用意されていないため、これらの疎通・
  実機能確認(`docs/commands/external-connectivity.md`の順序: 設定確認→
  integration_smoke→成功時のみintegration_live)を実施できていない。実配布判断は、
  これらのruntimeが用意できる環境で本書2節の各項目をチェック後に行う。

## 4. 既知の制限(MVP範囲内で意図的に対応しないもの)

- macOS/Linuxパッケージは対象外(初期対象はWindows x64のみ、
  `23-distribution-and-platform-policy.md` 5.1節)。
- 自動更新は非対応(手動再インストール方式、同5.5節)。
- COEIROINK/リリンちゃんは統合しない(`TASK-COEIR-001`永久blocked)。
- EPUB取込、M4B出力、ASR照合はpost-MVP(`TASK-EPUB-001`/`TASK-M4B-001`/`TASK-ASR-001`)。

## 5. 実行記録

```text
実行日時: 2026-07-20
対象タスク: TASK-RELEASE-002
実行コマンド:
  python -m pytest --collect-only -q
  python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
  WALKWISE_RUN_PERFORMANCE=1 WALKWISE_RUN_RESILIENCE=1 python -m pytest -ra tests/performance/test_large_sources.py tests/resilience/test_failure_recovery.py
  npm run typecheck
  npm test -- --run
収集件数: Python 454(host)/Docker未再確認、TypeScript 16 test files
pass / fail / xfail / skip: Python 394 passed / 0 failed / 37 xfailed / 23 deselected、Vitest 73 passed / 0 failed / 3 skipped
外部疎通の有無: なし(通常受入は外部接続不要)
外部疎通結果: 該当なし(本タスクは`external_gate`対象外)
未解決事項: 実runtime群(Gemini/Tesseract/VOICEVOX/ffmpeg/Python Worker/Electron/ASR/
  COEIROINK)はいずれも未確認のまま(既定skip)。Docker側のPhase7全体再確認は完了済み
  (`docker compose build test`成功、`--collect-only -q`454件収集、通常回帰
  387 passed + 7 skipped = 394でhostと完全一致)。
```
