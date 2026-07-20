# Walkwise

Walkwise は、個人の学習用途向けに、資料(テキスト/PDF/画像、post-MVPでEPUB)から
音声ブック(MP3)またはテキスト原稿を生成するWindowsデスクトップアプリです。
Electron(Vue 3、Renderer/main/preload)+ Python(素材処理・AI原稿生成・TTS音声合成・
音声パッケージング)の構成で、SQLiteをmetadata・実行状態の正本とします。

現在の状態(release readyかどうか)は [`release/checklist.md`](release/checklist.md) を、
実装済みタスクの一覧は [`docs/tasks/INDEX.md`](docs/tasks/INDEX.md) を参照してください。

## 1. 前提環境

- Node.js 22系、npm
- Python 3.12以上(Docker経由のテスト実行を推奨、`docker compose` v2)
- Windows 10/11 x64(初期配布対象。開発自体はWindows上のGit Bash/PowerShellを前提)

## 2. 環境変数

外部AI(Gemini)・外部TTS(VOICEVOX)・OCR(Tesseract)・音声処理(ffmpeg)・ASRなど、
実runtimeに接続する機能は環境変数で設定します。[`.env.example`](.env.example) を
`.env` としてcopyし、必要な値だけ設定してください(`.env`自体は`.gitignore`/
`.dockerignore`で除外されるため、commitやDocker build contextに含まれません)。

通常のテスト実行(`python -m pytest`の非opt-inマーカー、`npm test`)はこれらの
環境変数を一切必要としません。外部接続を伴う疎通確認・実機能テストの手順は
[`docs/commands/external-connectivity.md`](docs/commands/external-connectivity.md) を
参照してください。

## 3. セットアップ

```powershell
npm ci
python -m pip install -r requirements.txt   # Dockerを使わずhostで直接実行する場合のみ
```

Pythonの通常テストはDocker経由が正本です。

```powershell
docker compose build test
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```

## 4. 起動・開発

```powershell
npm run dev     # Renderer(Vue)のみをViteの開発サーバーで確認する(Electron本体は起動しない)
npm run start   # npm run buildを実行後、実Electronアプリを起動する
```

`npm run start`は、実際の`app.whenReady()`起動経路
(`electron/main/app_entry.ts`)を経由し、Python Workerをsubprocessとして起動し、
`electron-main`↔`Worker`↔`SQLite`の実接続でアプリを立ち上げます
(Workerの実行体は`WALKWISE_PYTHON_EXECUTABLE`未設定時、Windowsでは`python`、
それ以外では`python3`を既定で使用します)。

## 5. Build・Package

```powershell
npm run build     # dist/main, dist/preload, dist/renderer を生成する
npm run package   # npm run buildを実行後、electron-builderでWindows向けpackageを生成する
```

`npm run build`は`typecheck`→`main/preload`のTypeScript compile(CommonJS出力)→
`Renderer`のVite build、の順に実行され、失敗時は後続stepを実行しません。
`npm run package`は`electron-builder.yml`(Windows x64/nsis限定、
`forceCodeSigning: false`)に従って`release/`配下へ出力します。code signingは
初期配布では未実施です(リスクと対処法は`resources/release-manifest.json`を参照)。

## 6. テスト

```powershell
npm run typecheck
npm test -- --run
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```

外部runtimeの疎通確認・実機能テスト(opt-in、`WALKWISE_RUN_INTEGRATION_SMOKE=1`等)は
[`docs/commands/external-connectivity.md`](docs/commands/external-connectivity.md) を、
性能・障害注入テストは `docs/commands/performance.md` を参照してください。

## 7. 既知の制限

- macOS/Linuxパッケージは対象外(初期対象はWindows x64のみ)。
- 自動更新は非対応(手動再インストール方式)。
- COEIROINK/リリンちゃんは統合されていません(`TASK-COEIR-001`、公式API世代・
  endpoint・話者識別子・利用条件が未確認のため永久blocked)。
- 実際のAI原稿生成→TTS音声合成→M4B/MP3出力の一連のbuild pipeline統合(Job1つから
  章単位で実処理を実行する経路)は現時点で未接続です。個別のpipeline(素材処理・
  原稿生成・音声合成・音声パッケージング)自体はそれぞれ実装・テスト済みです。
- Job進捗のRenderer表示は、`job:get`の定期polling(500ms間隔)による暫定実装です
  (push型の実進捗イベントではありません)。
- 実GUI起動・外部runtime(Gemini/Tesseract/VOICEVOX/ffmpeg)への実接続・Windows
  インストーラーの実インストールは、この開発環境では未確認です。詳細は
  [`release/checklist.md`](release/checklist.md) を参照してください。

## 8. ドキュメント構成

- [`docs/tasks/`](docs/tasks/): 個別タスクの実装契約(完了済みタスクの詳細記録)。
- [`docs/commands/`](docs/commands/): 各分野の再現可能な実行コマンド集。
- [`docs/specifications/`](docs/specifications/): 承認済み仕様書。
- [`docs/notes/progress.md`](docs/notes/progress.md): 実装進捗の詳細な実測記録。
- [`docs/notes/implementation_assumptions.md`](docs/notes/implementation_assumptions.md):
  実装上の設計判断・前提の記録。
