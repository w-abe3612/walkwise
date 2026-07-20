---
document_type: implementation_task
task_id: TASK-REVIEW-001
status: ready
release_scope: release-readiness
priority: P0
created_at: '2026-07-20'
source_review: audio_book_creation_dump_2026-07-20_221016.txt
---

# TASK-REVIEW-001 実アプリ結線・リリース動作検証・完了済みタスク整理

## 1. 目的

既存の単体テスト契約を壊さず、WalkwiseがWindows上で実際に起動し、RendererからElectron main、Python Worker、SQLite、AI/TTS/OCR/音声処理の境界まで正しく結線される状態を作る。

現在の「53/54タスク完了」は個別契約とmock中心のテスト完了を示すが、実行可能なElectronアプリ、実Worker command registry、実サービスadapter、配布buildの完成を保証していない。本タスクではリポジトリ全体を再監査し、未結線・未実装・不整合を修正した後、完了済みのタスク文書を削除して現役文書だけが残る状態へ整理する。

## 2. 監査で確認済みのP0/P1問題

### 2.1 Electronアプリが実際には起動できない

- `package.json`にElectronの`main` entryがない。
- `npm run build`は`tsc --noEmit`だけで、`dist/`を生成しない。
- Renderer用`index.html`と本番Vite build設定が存在しない。
- `electron-builder.yml`は`dist/**`と`runtime/`を同梱対象にするが、現在どちらも生成・配置されない。
- `electron/main/index.ts`は`createMainWindow()`をexportするだけで、`app.whenReady()`、bootstrap、IPC登録、window生成、shutdown処理を実行しない。
- `electron/renderer/main.ts`はplaceholder rootをmountする関数だけで、自動起動も`AppShell`・各画面の組み立てもない。

### 2.2 Python Workerの実subprocessが機能しない

- `python -m script.worker.cli`は空の`HandlerRegistry`で起動する。
- `health` commandを送ると`unknown_job_type`になりexit code 1となる。
- Project、Source、AI、TTS、Build等の実command handlerがregistryへ登録されない。
- `WorkerRuntime`のcancel/timeout/recoveryとCLI dispatchが実アプリ経路で結線されていない。

### 2.3 Electron mainの実サービスadapterがない

- `bootstrapApplication()`はDB、migration、stale recovery、WorkerManagerをすべて注入前提とするが、実アプリ用composition rootがない。
- `openApplicationDatabase()`は`connectionFactory`を要求するだけで、実SQLite接続adapterがない。
- 各IPC moduleは`*ServiceLike` interfaceへ委譲するが、Python Workerまたは永続化層へ接続する実adapterがない。
- bootstrap途中で`recoverStaleJobs`、Worker生成、spawn等が失敗した場合にDB closeが保証されない経路を再確認する必要がある。
- `BuildPipeline`の`approval_gate_check`が未注入時に常にtrueとなるため、productionではfail-closedへ変更する必要がある。

### 2.4 Rendererが画面単体のままで、利用者導線が結線されていない

- `ProjectList.vue`以外はprops注入前提で、`window.walkwise`へ接続するcontainer/rootがない。
- Project一覧の項目を選択してworkspaceへ進む処理がない。
- `AppShell.vue`、router、store、各画面を切り替える実root componentがない。
- Source一覧取得、再試行、承認一覧、Build設定、Job一覧、Artifact一覧を読み込むrenderer API wrapperが不足している。
- 「確認する」「VOICEVOX再確認」「承認画面へ」「再生成」等のUI要素に実処理がない。

### 2.5 IPC契約に不整合がある

- mainはJob進捗を`job:progress-event`で送るが、preloadは`job:subscribe-progress`をlistenしているため進捗を受信できない。
- `job:progress-event`がpreload allowlistにない。
- preloadには`project:get`があるがmain側handlerがない。
- workspaceで必要なSource一覧・Source再試行等のchannelが定義されていない。
- 全IPC handlerを同一の実`ipcMain`へ登録する統合テストが不足している。

### 2.6 ファイル入力が実用上機能せず、安全境界も不十分

- `ProjectWorkspace.vue`は選択したFileの`name`だけを`filePath`として送るため、main/Workerは実ファイルを読み込めない。
- main側`source:register`はRendererから渡された任意pathを非空確認だけで受理する。
- main processの`dialog.showOpenDialog()`またはElectronの安全なFile path解決APIを使い、Rendererから任意の絶対pathを直接受け取らない設計へ変更する必要がある。

### 2.7 未実装の公開compatibility APIが残っている

`script/ai_clients/gemini/mindmap_builder.py`の次の公開関数は`NotImplementedError`のままexportされている。

- `build_final_mindmap`
- `load_sections`
- `process_section`

利用を継続するなら実装とテストを追加する。廃止するならpublic export、manifest、文書から削除し、明示的なmigration noteを残す。

### 2.8 テスト・文書・生成物の衛生問題

- `tests/test_container_contract.py`は秘密ファイル`.env`が実際に存在することを要求する。clean checkoutやダンプ復元で失敗するため、`.env.example`等を使う安全な契約へ変更する。
- `.pytest_cache/`がダンプに含まれ、`.gitignore`とdump scriptのskip対象にも不足がある。
- root `README.md`が実質空。
- `STEP4_README.md`、`tests/README.md`、STEP3/STEP4 manifest、複数のcommand文書に「空実装」「未着手」等の古い記述が残る。
- `release/checklist.md`にはASR等の完了状態と食い違う記述が残る。
- `package.json`のversionが`0.0.0-step4`のまま。

## 3. 実装方針

### 3.1 先に実行可能なcomposition rootを作る

次を追加または修正する。

- Electron main entrypoint
- `app.whenReady()`、single-instance、window lifecycle、shutdown
- data root作成
- DB/migration/stale recoveryの実adapter
- Python Worker subprocess生成
- Worker health確認
- 全IPC handler登録
- preload pathとrenderer entryの解決
- startup error画面または安全なdialog
- developmentとproductionでentryを切り替える設定

composition rootはテスト可能なfactoryへ分離し、Electron globalを直接mockしなくても主要な初期化順を検証できるようにする。

### 3.2 本番buildを構成する

- ViteでRendererのHTML/JS/CSSを生成する。
- main/preloadを実行可能なJavaScriptへcompile/bundleする。
- `package.json.main`を生成物へ向ける。
- `npm run dev`、`npm run build`、`npm run start`、`npm run package`を定義する。
- `npm run build`後に`dist/`内のmain、preload、renderer/index.htmlが存在することをテストする。
- `runtime/`の生成・同梱方法を実装するか、存在しないpathをelectron-builder設定から除外する。
- packageを実際に生成し、展開済みappがentrypointを解決できることを確認する。

### 3.3 Worker command registryを実装する

- `health`/`ping` handlerを必ず登録する。
- 実アプリで必要なProject、Source処理、AI、TTS、Build、Job cancel等のcommand mappingを明示する。
- handler内で既存service/pipelineを再利用する。
- commandごとの入力schemaを検証する。
- `WorkerRuntime`を使ってcancel/timeout/cleanupを実経路へ接続する。
- `python -m script.worker.cli`へhealth requestを送り、started→completedが返るsubprocess testを追加する。
- 未知commandはerrorを返すがprocessを継続することを確認する。

### 3.4 IPCとservice adapterを実装する

- WorkerManagerと各`*ServiceLike`を接続する実adapterを作る。
- Project/Source/Approval/Build/Job/Artifact/VoiceのDTOをPythonとのJSON Lines schemaへ変換する。
- エラーcodeを失わずRendererへ返す。
- Job progress event channelを`job:progress-event`へ統一する。
- subscription解除時にmain側listenerも確実に解除する。
- 不要な`project:get`を削除するかmain handlerを実装する。
- 全handlerを1つの`ipcMain`へ登録し、channel重複がないことをテストする。

### 3.5 Renderer rootと実画面導線を実装する

- `AppRoot.vue`等を追加し、`AppShell`、router、store、全5画面を組み立てる。
- Project選択、workspace遷移、build設定、Job/Artifact表示を接続する。
- `window.walkwise`用のtyped API wrapperを全機能分作る。
- loading/empty/error/retryを実通信へ接続する。
-未配線button/linkを実装するか、機能が未提供ならUIから削除する。
- Job progress購読を実際にstoreへ反映する。

### 3.6 安全なファイル選択を実装する

- Rendererから任意path文字列を受け取る設計を廃止する。
- main processでfile dialogを開き、選択結果を検証する。
- 許可拡張子・media type・file存在・通常fileであることを検証する。
- Project data root外の入力はimmutable copyとしてProject配下へ取り込む。
- path traversal、UNC、symlink、device path等の境界テストを追加する。

### 3.7 fail-closedとresource cleanupを再確認する

- Approval gate未注入時はBuildを拒否する。
- bootstrapの全失敗経路でDB/Workerがcleanupされる。
- Worker spawn失敗、health失敗、migration失敗、stale recovery失敗をテストする。
- 既存正常Artifactを失敗時に上書きしない。

### 3.8 実runtime smokeを段階的に実施する

利用可能なruntimeだけ、必ず次の順序で実行する。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

対象:

- Python Worker subprocess
- Electron window/preload/renderer
- SQLite migration
- Tesseract
- Gemini
- VOICEVOX
- ffmpeg/ffprobe
- M4B
- ASR
- Windows package/install/uninstall

秘密値や利用者データをログへ出さない。runtimeがない場合は「未確認」と記録し、成功扱いにしない。

## 4. 必須テスト

最低限、次を新規追加または強化する。

1. `npm run build`が実生成物を作るtest。
2. package.json main entryとelectron-builder同梱pathの整合test。
3. 実Python subprocess health test。
4. Worker registryに必須commandが登録されるtest。
5. Electron composition rootが同一ipcMainへ全channelを重複なく登録するtest。
6. preloadのJob progress channel test。
7. Project作成→Project選択→Source選択→承認→Build→Job progress→ArtifactのRenderer統合test。
8. file dialogとpath validation test。
9. bootstrap各失敗経路のresource cleanup test。
10. fail-closed approval gate test。
11. clean checkoutで`.env`なしでも通常テストがpassするtest。
12. package展開後のmain/preload/renderer entry存在test。
13. Markdown内部linkの存在確認test。
14. completed task cleanup後にIndex/Manifestへ削除済みpathが残らないtest。

mockだけのE2Eを「実Electron起動確認」と呼ばない。mock E2E、subprocess smoke、packaged-app smokeを別々に記録する。

## 5. 完了済みタスク文書の削除

実装・回帰・実行可能性確認が完了した後に実施する。先に削除してはいけない。

### 5.1 `docs/tasks/`

- 完了済み53タスクの`TASK-*.md`を削除する。
- 未解決の`TASK-COEIR-001-coeiroink-client-adapter.md`は残す。
- 本タスク`TASK-REVIEW-001-runtime-integration-and-repository-cleanup.md`は人間の完了承認まで残す。
- `16_image-material-ingestion.md`が完了済みタスクに吸収済みなら削除する。
- `INDEX.md`、`README.md`、`EXECUTION_ORDER.md`、`STEP7_MANIFEST.json`を、現役タスクだけを参照する内容へ更新する。
- 削除前に、必要な設計判断が`docs/specifications/`、`docs/commands/`、`docs/notes/`へ残っていることを確認する。

### 5.2 `docs/spec-proposals/`

- `docs/spec-proposals/task/`配下の完了済み・採用済み・不要になったtask proposalを削除する。
- 未解決のCOEIROINK proposalだけは残す。
- `100_implementation-preparation-master-plan.md`と`1_`〜`3_`の旧提案が実行済み・吸収済みなら削除する。
- `INDEX.md`、`IMPLEMENTATION_INDEX.md`、`README.md`を現役proposalだけに更新する。
- `audio-validation-thresholds.md`等、まだprovisionalな設計資料はtask fileではないため、状態を確認して必要なら残す。
- `coeiroink-client.md`はblocked解消に必要なため残す。

### 5.3 参照切れ防止

削除後に次を実行し、削除済みpathへの参照を修正する。

```powershell
rg -n "docs/tasks/TASK-|docs/spec-proposals/task/" .
```

Markdown内部link validatorを追加し、存在しない相対linkが0件であることを確認する。

### 5.4 旧scaffold成果物の整理

以下は現状を確認し、役目を終えていれば削除または正式文書へ置換する。

- `STEP4_README.md`
- `STEP4_MANIFEST.json`
- `tests/README.md`
- `tests/STEP3_MANIFEST.json`
- STEP3/STEP4前提の古いコメント・文言
- `.pytest_cache/`

`.gitignore`と`dumps/dump_all_files.py`へ`.pytest_cache`、build cache、coverage等の除外を追加する。

## 6. 文書更新

- root `README.md`へ環境構築、起動、build、package、外部runtime設定、制限を書く。
- `docs/commands/CURRENT_STATE.md`は「契約実装完了」と「実アプリ動作確認完了」を分離する。
- `release/checklist.md`を現在状態へ合わせる。
- staleな`未着手`、`空実装`、`現在のダンプでは欠落`を修正する。
- `docs/notes/progress.md`へ監査前後の実測値と修正結果を書く。
- `docs/notes/implementation_assumptions.md`へ新たなcomposition root、Worker command、file dialog、packaging判断を書く。
- package versionから`step4`表現を外し、適切なpre-release versionへ更新する。

## 7. 実行順序

1. git差分とbaseline保存。
2. 現在のテストを実測。
3. P0問題を再現する失敗テスト追加。
4. Electron build/start composition実装。
5. Worker registryとservice adapter実装。
6. IPC修正。
7. Renderer rootと導線実装。
8. file input安全化。
9. package buildとsubprocess smoke。
10. 全体回帰。
11. 文書整合化。
12. 完了済みtask/proposal削除。
13. link validatorと全体回帰を再実行。
14. runtimeが存在する範囲でsmoke/live。
15. 最終報告。

## 8. 禁止事項

- 既存テストの削除や期待値弱体化でpassさせること。
- 実アプリ未起動のままrelease readyと記録すること。
- fake serviceだけのE2Eを実runtime E2Eとして扱うこと。
- RendererへNode API、DB handle、ChildProcessを直接公開すること。
- Rendererから任意の絶対pathをmainへ渡すこと。
- Approval gateを既定trueにすること。
- 実行済みtask文書を、設計判断の移管前に削除すること。
- `TASK-COEIR-001`を推測で実装すること。
- 外部serviceを無断で呼ぶこと。
- gitの破壊的操作。

## 9. 完了条件

- `npm run build`で実行可能なdistが生成される。
- Electron main entry、preload、renderer HTMLが存在する。
- `npm run start`または同等のsmokeでappが起動する。
- 実Python subprocessのhealth requestが成功する。
- 必須Worker commandが登録される。
- Rendererの主要導線が実IPC adapterへ接続される。
- Job progressがRendererへ届く。
- 安全なfile pickerからSource取込できる。
- clean checkoutで通常Python/TypeScriptテストがpassする。
- package生成が成功し、entryとruntime pathが解決できる。
- mock E2E、subprocess smoke、packaged-app smokeを分けて結果記録する。
- 完了済みtask/proposal filesが削除される。
- COEIROINKと本review task以外の実行済みtask fileが`docs/tasks/`に残らない。
- completed proposalが`docs/spec-proposals/task/`に残らない。
- Markdown参照切れが0件。
- 実runtime未確認項目は明示される。

## 10. 最終報告形式

```text
# TASK-REVIEW-001 実行結果

## 結論
- 契約実装: complete / incomplete
- 実アプリ起動: pass / fail / unverified
- package生成: pass / fail / unverified
- release ready: yes / no

## 修正したP0/P1問題
- 問題
- 原因
- 修正
- テスト

## 実測
- Python collection/pass/fail/xfail/skip
- TypeScript typecheck
- Vitest
- npm build
- Electron smoke
- Worker subprocess smoke
- package build
- Markdown link validation

## 外部runtime
- Gemini
- Tesseract
- VOICEVOX
- ffmpeg/ffprobe
- ASR
- COEIROINK

## 文書削除
- docs/tasksから削除したファイル
- docs/spec-proposalsから削除したファイル
- 残した現役ファイル
- 参照修正

## 未解決
- blocker
- 次の作業
```