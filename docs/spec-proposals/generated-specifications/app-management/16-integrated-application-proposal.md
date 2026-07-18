---
spec_id: app-management-16-integrated-application-proposal
task_id: SPEC-APP-017
title: "フロント・DB管理の統合仕様草案"
status: provisional
version: "0.1"
created_at: "2026-07-19"
depends_on:
  - app-management-01-product-scope-and-mvp
  - app-management-02-architecture-and-runtime
  - app-management-03-frontend-information-architecture
  - app-management-04-backend-api-and-service-boundary
  - app-management-05-persistence-strategy
  - app-management-06-database-logical-schema
  - app-management-07-project-task-job-workflow
  - app-management-08-material-import-workflow
  - app-management-09-review-and-approval-workflow
  - app-management-10-output-and-export-settings
  - app-management-11-voice-selection-and-preview
  - app-management-12-job-monitoring-and-recovery
  - app-management-13-security-backup-migration
  - app-management-14-testing-and-acceptance
  - app-management-15-additional-feature-proposals
---

# フロント・DB管理の統合仕様草案

## 目的

個別草案 (00〜15)の矛盾を解消し、MVPとして一貫した管理アプリの統合草案を作る。

## 背景

本書は`docs/spec-proposals/generated-specifications/app-management/`配下の全個別草案を
統合する最終レイヤーである。個別草案間で確認した限り、明確な矛盾は検出されなかったが、
複数の`human_review_required`・`evidence_gap`が横断的に存在する (下記参照)。

## 対象

- 全体構成図。
- MVP screen/API/entity対応表。
- end-to-end sequence。
- 正本一覧。
- feature capability。
- 非機能要件。
- 未決定事項の集約。

## 対象外

- 各個別領域の詳細 (該当各書を参照)。

## 既存仕様との関係

各個別草案が既に既存仕様 (承認済み)との関係を明記済みであり、本書はそれらを集約する。
新たに既存仕様と矛盾する決定は行わない。

## 用語

`00-current-state-and-terminology.md`の用語集を全体の正とする。

## 全体構成図

```mermaid
flowchart TB
    subgraph Windowsホスト
        Browser[ブラウザ]
        subgraph Backend [FastAPI Backend 案A採用]
            API[API層]
            AS[Application Service]
            DS[Domain Service]
            AD1[VOICEVOX Adapter 実装済み]
            AD2[COEIROINK Adapter 未実装]
            AD3[Gemini Adapter 実装済み]
        end
        DB[(SQLite メタデータ正本)]
        FS[(ファイルシステム 原本正本)]
        VV[VOICEVOX Engine ローカル]
        CO[COEIROINK Engine ローカル 将来]
    end
    Browser <--> API
    API --> AS --> DS
    AS --> AD1 --> VV
    AS --> AD2 -.未実装.-> CO
    AS --> AD3
    AS --> DB
    AS --> FS
```

## MVP screen/API/entity対応表

| 画面 (`03`) | 主なAPI (`04`) | 関連entity (`06`) |
|---|---|---|
| Dashboard | GET /projects | projects, approval_records, jobs |
| Project新規作成 | POST /projects | projects |
| Project詳細 | GET /projects/{id} | projects, sources, build_requests |
| 素材インポート | POST /projects/{id}/sources | sources, source_revisions |
| 承認一覧・詳細 | GET/POST /projects/{id}/approvals | approval_records |
| 出力設定 | GET/POST output-profiles | output_profiles |
| 声選択 | GET voice-engines, voice-profiles | voice_profile_refs |
| Job一覧・詳細 | GET/POST jobs | jobs, job_events |
| 成果物一覧 | GET /projects/{id}/artifacts | artifacts |
| 設定・診断 | GET /system/health (次期) | app_settings |

## end-to-end sequence (MVPハッピーパス)

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant FS as ファイル正本
    participant DB as SQLite

    User->>UI: 起動コマンド実行
    UI->>API: healthcheck
    User->>UI: 新規Project作成
    UI->>API: POST /projects
    API->>FS: project-plan.yaml 作成
    API->>DB: projects 行挿入
    User->>UI: 素材import
    UI->>API: POST /sources (multipart)
    API->>FS: sources/originals へ保存
    API->>DB: sources, source_revisions 行挿入
    User->>UI: 資料・カリキュラム承認
    UI->>API: POST /approvals/materials_curriculum/approve
    API->>FS: approvals.yaml 更新
    API->>DB: approval_records 同期
    User->>UI: 企画承認 → 原稿生成Job → 原稿承認 → 声・出力設定 → 制作依頼作成
    UI->>API: POST /build-requests/{id}/jobs (各段階)
    API->>DB: jobs, job_events 記録
    API->>FS: 章MP3・manifest 出力
    User->>UI: 成果物確認
    UI->>API: GET /artifacts
```

## 正本一覧 (集約)

`05-persistence-strategy.md`の正本マトリクスをそのまま全体の正本一覧として採用する。
再掲はしない (単一の正本を維持するため、本書からは同書を参照するのみとする)。

## feature capability (機能フラグ想定)

| capability | 状態 | 理由 |
|---|---|---|
| output.epub | disabled | 下位仕様未確定 (`10`) |
| output.full_book_mp3 | disabled | `14-audio-packaging.md`がSHOULD止まり |
| voice.coeiroink | disabled | クライアント未実装 (`11`) |
| import.kindle_capture | 次期 | GUI操作統合が必要 (`08`) |
| import.reference_mode | disabled | copy方式のみMVP採用 (`08`) |

これらのdisabled理由は、実装が進み次第、機能フラグをtrueに切り替えるだけで有効化できる設計とし、
仕様自体の再設計を必要としないようにする。

## 非機能要件

| 項目 | 方針 |
|---|---|
| 可用性 | 単一利用者ローカルのため高可用性要件はなし。stale job復旧 (`12`)で最低限の耐障害性を確保 |
| セキュリティ | loopback限定、認証なし (`13`) |
| 性能 | 具体的数値目標は次期設定 (`14`) |
| 可搬性 | portable manifestによるexport/import (`05`, `15`の#19) |
| 保守性 | Application Service層でCLI/APIのロジックを共有 (`04`) |

## 未決定事項 (横断集約)

各個別草案の未決定事項のうち、複数書にまたがるものを集約する。

- 技術スタック最終決定 (案A/B/C、`02`) — 最優先の`human_review_required`。
- 永続化案最終決定 (案2、`05`) — PoC (`17`)後に確定。
- EPUB出力仕様の新規策定要否 (`10`)。
- COEIROINK実装完了時期 (`11`)。
- 認証機構導入の要否とタイミング (`13`)。

## 人間判断順序

1. 技術スタック (`02`)の採否。
2. 永続化方式 (`05`,`06`)の採否とPoC計画承認。
3. MVP機能範囲 (`01`,`15`のTop5)の最終確認。
4. セキュリティ方針 (`13`)の承認。
5. 個別画面・API詳細 (`03`,`04`,`08`〜`12`)のレビュー。

## 実装分割案

`16-ai-assisted-development-workflow.md`のタスク粒度原則 (1タスク1責務、変更ファイル1〜3、
テストケース3〜10)に従い、次の順で実装タスク (`TASK-APP-*`)へ分割することを推奨する
(実際のタスク作成は仕様承認後、`17-specification-promotion-plan.md`の手順に従う)。

```text
TASK-APP-001 DBスキーマとmigration基盤
TASK-APP-002 Project CRUD API
TASK-APP-003 Source import API (multipart, ファイル保存)
TASK-APP-004 承認API (既存approvals.yaml読み書き)
TASK-APP-005 Job基盤 (状態機械、サブプロセス起動)
TASK-APP-006 Job進捗API (SSE/polling)
TASK-APP-007 出力プロファイルAPI
TASK-APP-008 音声プロファイル参照・試聴API
TASK-APP-009 フロント: Dashboard/Project作成wizard
TASK-APP-010 フロント: 素材import画面
TASK-APP-011 フロント: 承認画面
TASK-APP-012 フロント: 出力・声選択画面
TASK-APP-013 フロント: Job監視・成果物画面
TASK-APP-014 起動launcher (一コマンド起動)
TASK-APP-015 バックアップ・診断機能
```

## 正常系

`end-to-end sequence`のとおり。

## 異常系

各個別草案の異常系表をそのまま集約参照する (重複記載を避ける)。

## UIまたはAPIの入出力

`03`,`04`を参照。

## 状態遷移

`07`を参照。

## データ所有者・正本

`05`を参照。

## バリデーション

### Error

- 個別草案間で正本の記述が矛盾する (今回の確認では検出されなかった)。

### Warning

- 未決定事項が`17`のPoC計画に反映されないまま昇格が進められる。

## セキュリティ・プライバシー

`13`を参照。

## テスト観点

`14`を参照。

## 移行・互換性

各個別草案の移行・互換性節をそのまま踏襲する。

## 未決定事項

上記「未決定事項 (横断集約)」のとおり。

## 人間レビュー項目

- `human_review_required`: 統合草案全体の整合性が実際に矛盾なく成立しているかの最終確認。
- `human_review_required`: 実装分割案 (TASK-APP-001〜015)の順序・粒度の妥当性。
- 草案の採否と未決定事項。

## 仕様昇格条件

- 全個別草案 (00〜15)が`review`または`provisional`状態で存在すること。
- 統合草案が矛盾を含まないことを人間が確認していること。
- 実装分割案が`16-ai-assisted-development-workflow.md`のタスク粒度原則に適合すること。
