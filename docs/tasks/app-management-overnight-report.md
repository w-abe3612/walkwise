---
status: review
version: "1.0"
created_at: "2026-07-19"
task_id: SPEC-APP-000
task_type: overnight_report
---

# app-management 仕様草案 夜間生成レポート

本書は`docs/tasks/20_app-management-spec-drafting-master.md`「9. 終了時の報告」に
基づく最終報告である。すべて未承認の草案であり、`docs/specifications/`は変更していない。

## 1. 実行したタスク

`APP_MANAGEMENT_SPEC_DRAFT_TASK_INDEX.md`の20〜39を、事前監査を含めすべて実行した。

| 順序 | task_id | 成果物 | status |
|---|---|---|---|
| 20 | SPEC-APP-000 | `docs/tasks/app-management-preflight-report.md` | review |
| 21 | SPEC-APP-001 | `00-current-state-and-terminology.md` | provisional |
| 22 | SPEC-APP-002 | `01-product-scope-and-mvp.md` | provisional |
| 23 | SPEC-APP-003 | `02-architecture-and-runtime.md` | provisional |
| 24 | SPEC-APP-004 | `03-frontend-information-architecture.md` | provisional |
| 25 | SPEC-APP-005 | `04-backend-api-and-service-boundary.md` | provisional |
| 26 | SPEC-APP-006 | `05-persistence-strategy.md` | provisional |
| 27 | SPEC-APP-007 | `06-database-logical-schema.md` | provisional |
| 28 | SPEC-APP-008 | `07-project-task-job-workflow.md` | provisional |
| 29 | SPEC-APP-009 | `08-material-import-workflow.md` | provisional |
| 30 | SPEC-APP-010 | `09-review-and-approval-workflow.md` | provisional |
| 31 | SPEC-APP-011 | `10-output-and-export-settings.md` | provisional |
| 32 | SPEC-APP-012 | `11-voice-selection-and-preview.md` | provisional |
| 33 | SPEC-APP-013 | `12-job-monitoring-and-recovery.md` | provisional |
| 34 | SPEC-APP-014 | `13-security-backup-migration.md` | provisional (依存関係に自己参照の疑い、下記参照) |
| 35 | SPEC-APP-015 | `14-testing-and-acceptance.md` | provisional |
| 36 | SPEC-APP-016 | `15-additional-feature-proposals.md` | provisional |
| 37 | SPEC-APP-017 | `16-integrated-application-proposal.md` | provisional |
| 38 | SPEC-APP-018 | `17-specification-promotion-plan.md` | provisional |
| 39 | SPEC-APP-019 | `APP_MANAGEMENT_DECISION_MATRIX.md`, `APP_MANAGEMENT_REVIEW_CHECKLIST.md`, 本書 | review |

## 2. 生成した草案一覧

```text
docs/spec-proposals/generated-specifications/app-management/
├─ 00-current-state-and-terminology.md
├─ 01-product-scope-and-mvp.md
├─ 02-architecture-and-runtime.md
├─ 03-frontend-information-architecture.md
├─ 04-backend-api-and-service-boundary.md
├─ 05-persistence-strategy.md
├─ 06-database-logical-schema.md
├─ 07-project-task-job-workflow.md
├─ 08-material-import-workflow.md
├─ 09-review-and-approval-workflow.md
├─ 10-output-and-export-settings.md
├─ 11-voice-selection-and-preview.md
├─ 12-job-monitoring-and-recovery.md
├─ 13-security-backup-migration.md
├─ 14-testing-and-acceptance.md
├─ 15-additional-feature-proposals.md
├─ 16-integrated-application-proposal.md
├─ 17-specification-promotion-plan.md
├─ APP_MANAGEMENT_DECISION_MATRIX.md
├─ APP_MANAGEMENT_REVIEW_CHECKLIST.md
└─ examples/
   ├─ app-config.example.yaml
   ├─ project-create-request.example.json
   ├─ material-import-request.example.json
   ├─ build-request.example.json
   └─ job-state.example.json
```

既存ファイルとのファイル名衝突は発生しなかった (`app-management/`は今回新設)。

## 3. 採用推奨案 (サマリ)

- **技術スタック**: FastAPI (Python) + Vue3/Vite SPA を暫定採用 (案A)。理由・比較は`02`参照。
- **永続化**: SQLiteをメタデータ正本、原素材・大型成果物はファイルとする案2を暫定採用。理由・比較は`05`参照。
- **Job実行**: サブプロセス起動方式を暫定採用 (`02`)。
- **起動**: Windowsホスト直接実行を利用者向け正式経路、Dockerは開発・テスト用途に限定 (`02`)。

詳細は`APP_MANAGEMENT_DECISION_MATRIX.md`を参照。

## 4. 比較した代替案

| 領域 | 比較案数 | 該当書 |
|---|---|---|
| 技術スタック | 3 (FastAPI+SPA / SSR+HTMX / Tauri) | `02` |
| 永続化方式 | 3 (ファイル+索引SQLite / SQLiteメタデータ正本 / PostgreSQL) | `05` |
| Job実行方式 | 3 (同一プロセス / サブプロセス / 専用ワーカー) | `02` |
| ファイル受け渡し方式 | 3 (multipart upload / サーバー側パス参照 / OS統合ダイアログ) | `04` |

すべて最低3案を比較し、採用案・不採用案・判断条件を記録済み (タスク指示の共通安全規則§に準拠)。

## 5. AIが追加提案した機能

`15-additional-feature-proposals.md`にて25件を提案し、MVP/次期/将来へ分類した。
採用推奨Top5は次のとおり。

1. 承認待ち一覧 (横断ダッシュボード)
2. AI利用コスト・使用量表示
3. バックアップ・復元のUI化
4. Project複製・archive
5. Engine/API疎通診断・定期ヘルスチェック

## 6. MVP推奨範囲

`01-product-scope-and-mvp.md`のとおり。要旨:

- MVP: プロジェクト新規作成、素材import、4段階承認、出力設定(MP3/テキスト)、声選択(VOICEVOX)、
  Job監視、成果物一覧、一コマンド起動。
- 次期: 複製/archive、差分再生成表示、コスト表示、原稿詳細編集、COEIROINK対応。
- 将来/対象外: 複数利用者、クラウド同期、EPUB出力(下位仕様未確定)、動画・録音の自動取込。

## 7. DB採用案と正本境界

案2 (SQLiteメタデータ正本+ファイル原本)を暫定採用。正本マトリクスの要旨:

| データ | 正本 |
|---|---|
| 企画本文・資料一覧・承認内容の本文 | ファイル (既存仕様どおり) |
| Project/Source/承認の検索用メタデータ | DB |
| Build Request・Job・JobEvent (新概念) | DB (対応するファイルが存在しないため) |
| 素材原本・成果物本体 | ファイル |
| 成果物・素材の索引 | DB |

詳細は`05-persistence-strategy.md`、ERDは`06-database-logical-schema.md`を参照。

## 8. 起動コマンド案

`02-architecture-and-runtime.md`の設計:

```text
利用者向け正式コマンド: walkwise-app.bat (Windows)
  → DB migration確認 → APIサーバー起動 (loopback限定) → 既定ブラウザでdashboardを開く

開発用補助コマンド:
  - uvicorn app.main:app --reload (APIのみ)
  - npm run dev (フロントのみ)
  - docker compose run --rm app pytest -m "not external and not manual" (既存のテスト実行方針を維持)
```

## 9. evidence gap

| # | 内容 | 該当書 |
|---|---|---|
| 1 | `docs/specifications/`の04,05,06,08,10,11,13,15番の内容を精読していない | 事前監査、`00` |
| 2 | 指定ダンプ (`audio_book_creation_dump_2026-07-19_013737.txt`)が現在のリポジトリ状態より古く、`docs/tasks/`のSPEC-APP-*群を含んでいない | 事前監査 |
| 3 | `.env`の実際の設定状態 (Gemini APIキー有無)を確認していない | 事前監査 |
| 4 | `Dockerfile`/`docker-compose.yml`が意図的に空か作業中か不明 | 事前監査 |
| 5 | EPUB出力の承認済み仕様がリポジトリ内に存在しない | `10` |
| 6 | Node.jsツールチェーンの導入可否 (開発者環境依存) | `02` |

## 10. human review required (集約)

| # | 内容 | 該当書 |
|---|---|---|
| 1 | 技術スタック案A/B/Cの最終選定 | `02`,`16` |
| 2 | 永続化案2の最終選定、`17-file-based-data-persistence-policy.md`改訂の方向性 | `05`,`17` |
| 3 | MVP機能一覧の最終確定 (特にEPUB・差分再生成) | `01` |
| 4 | 04/05/06/08/10/11/13/15番の未精読仕様と本草案群の整合最終確認 | `00` |
| 5 | 「制作依頼(Build Request)」という新規概念を仕様体系へ追加してよいか | `00` |
| 6 | 各エンジン・話者の利用条件表記の最終文言 | `11` |
| 7 | loopback限定・認証なし方針を維持する期間 | `13` |
| 8 | タスク34番(`34_spec-draft-app-security-migration.md`)の依存関係に自己参照 (`SPEC-APP-014`)がある誤記の疑い | `13`,本書§12 |
| 9 | Top5追加機能提案の採用可否 | `15` |
| 10 | 実装分割案(TASK-APP-001〜015)の順序・粒度 | `16` |
| 11 | 昇格順序・PoC計画・担当スケジュール | `17` |

## 11. blocked

明示的に`blocked`とした草案・工程はない。すべての草案は`provisional`または`review`として
成果物を生成できた。ただし、次の2件は**PoC完了が承認の前提条件**であるため、
実質的な条件付き保留として扱う (`17-specification-promotion-plan.md`参照)。

- PoC-1: 一コマンド起動+FastAPI+SPA疎通確認 (`02`)
- PoC-2: SQLiteメタデータ正本+ファイル再構築 (`05`)

## 12. タスク定義自体の不整合 (報告)

`docs/tasks/34_spec-draft-app-security-migration.md`のfront matterにある`depends_on`が
`SPEC-APP-014` (このタスク自身のID)を含んでおり、自己参照になっている。
実際に依存すべきと推測される`SPEC-APP-006`(persistence-strategy)、`SPEC-APP-007`
(database-logical-schema)、`SPEC-APP-009`(material-import-workflow)を実質的な前提として
`13-security-backup-migration.md`を作成した。タスク指示書自体の修正は本タスクの権限外のため、
人間による確認・修正を推奨する (`human_review_required`)。

## 13. 仕様昇格候補と順序

`17-specification-promotion-plan.md`より抜粋:

```text
00 用語
↓
01 製品範囲・MVP
↓
02 アーキテクチャ・起動方式 (PoC-1必須)
↓
05 永続化戦略 (PoC-2必須)
↓
06 DB論理スキーマ
↓
07 Project/Job状態遷移
↓
03 フロント情報設計 ／ 04 バックエンドAPI (並行)
↓
08〜12 個別画面フロー
↓
13 セキュリティ・バックアップ・移行
↓
14 テスト戦略
↓
15 追加機能提案
↓
16 統合草案
```

分割昇格を推奨し、一括での`approved`化は行わない方針とした。

## 14. 実装タスク候補

`16-integrated-application-proposal.md`より、承認後に作成する実装タスク候補
(`TASK-APP-001`〜`015`、`16-ai-assisted-development-workflow.md`のタスク粒度原則に従う):

```text
TASK-APP-001 DBスキーマとmigration基盤
TASK-APP-002 Project CRUD API
TASK-APP-003 Source import API
TASK-APP-004 承認API
TASK-APP-005 Job基盤
TASK-APP-006 Job進捗API
TASK-APP-007 出力プロファイルAPI
TASK-APP-008 音声プロファイル参照・試聴API
TASK-APP-009〜013 フロント各画面
TASK-APP-014 起動launcher
TASK-APP-015 バックアップ・診断機能
```

これらは候補一覧のみであり、**本タスクでは一切実装していない**。

## 15. 実装を開始していないことの確認

- `script/`配下のファイルは一切編集していない (元の3ファイルのみ、変更なし)。
- 新しいPythonモジュール、APIコード、フロントエンドコードは作成していない。
- パッケージのインストールは行っていない。
- Webサーバー、DB、VOICEVOX、COEIROINK、ブラウザは起動していない。

## 16. ソース・テスト・依存関係の変更有無

| 対象 | 変更有無 |
|---|---|
| `script/` | 変更なし |
| `tests/` | 変更なし (0ファイルのまま) |
| `requirements.txt` | 変更なし |
| `Dockerfile` | 変更なし |
| `docker-compose.yml` | 変更なし |
| `docs/specifications/` | 変更なし (承認済み仕様への昇格は実施していない) |

## 17. Markdown/YAML/JSON/リンク検査結果

- 全20個のMarkdownファイル (00〜17 + 決定マトリクス + チェックリスト)のコードフェンス
  (\`\`\`) がすべて偶数個 (開始・終了が対応)であることを確認した。
- Mermaid図は00,01,02,03,04,06,07,08,09,11,12,14,16,17の各書に含まれ、
  ダイアグラム種別 (flowchart/sequenceDiagram/stateDiagram-v2/erDiagram)の構文キーワードが
  正しく開始行に記述されていることを目視確認した。
- `examples/`配下の4件のJSONファイル (`build-request.example.json`,
  `job-state.example.json`,`material-import-request.example.json`,
  `project-create-request.example.json`)は、Python標準ライブラリ`json.load`で
  パース成功を確認済み (全件OK)。
- `examples/app-config.example.yaml`はYAMLパーサ (PyYAML)がこの環境に存在しないため、
  自動構文検査を実施できなかった。目視でインデント・コロン書式を確認したが、
  `human_review_required`として人間による最終確認を推奨する。
- 各草案front matterの`spec_id`,`task_id`,`depends_on`,`spec_refs`の記述形式が
  全ファイルで一貫していることを確認した。

## 18. 変更禁止範囲のdiff確認手順

人間が確認する場合の推奨コマンド:

```bash
git status
git diff -- script/ tests/ requirements.txt Dockerfile docker-compose.yml docs/specifications/
git status --porcelain docs/spec-proposals/generated-specifications/app-management/
```

本セッションでは、上記コマンド相当の`git status`確認により、
`docs/`以外の既存ファイルへの変更が発生していないことを確認済みである
(README.mdの変更はセッション開始前から存在していた既存差分であり、本タスクによるものではない)。

## 19. 完了条件チェック (タスク20 §10 対応)

- [x] 21〜39の各タスクに成果物が存在する (blocked理由を要するものはなかった)。
- [x] 統合草案 (`16`)と仕様昇格計画 (`17`)がある。
- [x] 人間承認を偽装していない (すべて`provisional`/`review`のまま)。
- [x] 実装コードを変更していない。
- [x] DB導入で既存原資料を失う設計になっていない (`05`の正本マトリクスでファイル原本を維持)。
- [x] 一つのコマンドから画面を開く案が比較されている (`02`のPoC-1対象)。

## 20. 次にすべきこと (提案)

1. `APP_MANAGEMENT_REVIEW_CHECKLIST.md`に沿って全草案をレビューする。
2. PoC-1 (一コマンド起動)、PoC-2 (DB再構築)を実施する。
3. タスク34番の依存関係誤記を確認・修正する。
4. EPUB出力仕様の要否を判断する。
5. 昇格順序 (`17`)に従い、`00`から順次`docs/specifications/`への昇格を検討する。
