---
task_id: SPEC-APP-000
task_type: specification_drafting_orchestration
status: ready
created_at: "2026-07-19"
requested_source_dump: "audio_book_creation_dump_2026-07-19_013737.txt"
output_root: "docs/spec-proposals/generated-specifications/app-management"
---

# フロント画面・DB管理仕様の草案を夜間生成する

## 1. 目的

現在のコマンド中心・ファイル中心のオーディオブック作成ツールへ、
ローカル管理画面とデータベース管理を導入するための仕様草案を作成する。

利用者が最低限求めている操作は次のとおりである。

- コマンドを一つ実行すると管理画面が開く。
- オーディオブック作成タスクを新規作成できる。
- 素材をインポートできる。
- 出力形式を選べる。初期候補はMP3、テキスト、EPUB。
- 使用する声・音声プロファイルを選べる。

この要求だけで画面とDBを決めず、既存仕様とコードを調査し、
不足機能、運用上の機能、異常系をClaude Codeから追加提案する。

## 2. 成果物の位置付け

```text
docs/specifications/
＝ 承認済み正本。変更・昇格しない。

docs/spec-proposals/generated-specifications/app-management/
＝ 今回作る未承認草案。

docs/tasks/
＝ 今回Claude Codeへ渡す一時的な草案作成指示。
```

`docs/tasks/`は本来実装タスク置き場であるため、今回のファイルは
`SPEC-APP-*`と`spec-draft-app-*`で明確に区別する。

## 共通安全規則

- 本タスクは**仕様草案の作成**であり、実装ではない。
- `script/`、`tests/`、依存パッケージ、`Dockerfile`、`docker-compose.yml`を変更しない。
- パッケージをインストールしない。
- Webサーバー、DB、VOICEVOX、COEIROINK、ブラウザを起動しない。
- `docs/specifications/`の承認済み仕様を正本として扱う。
- 草案は`docs/spec-proposals/generated-specifications/app-management/`へ出力する。
- 草案の`status`は`review`、`provisional`、`blocked`のいずれかとし、`approved`にしない。
- 人間の承認なしに`docs/specifications/`へ移動しない。
- 既存ファイルを削除しない。
- 根拠不足は推測で確定せず、`evidence_gap`または`human_review_required`として残す。
- 技術選定は少なくとも3案を比較し、採用案・不採用案・判断条件を記録する。
- 既存のファイル正本を無断でDB正本へ変更しない。
- 著作権、録音許可、個人情報の法的判断を代行しない。
- 外部情報を調査する場合は公式ドキュメントを優先し、参照日を記録する。
- Markdown、YAML、JSON、Mermaidの構文を可能な範囲で検査する。

## 3. 最初に読むもの

最低限、存在するものを次の順に確認する。

1. `docs/specifications/00-specification-guidelines.md`
2. `docs/specifications/01-common-identifiers-and-versioning.md`
3. `docs/specifications/02-process-input-output.md`
4. `docs/specifications/03-project-plan-schema.md`
5. `docs/specifications/07-approval-workflow.md`
6. `docs/specifications/09-voice-profile-schema.md`
7. `docs/specifications/14-audio-packaging.md`
8. `docs/specifications/16-ai-assisted-development-workflow.md`
9. `docs/specifications/17-file-based-data-persistence-policy.md`
10. `docs/specifications/18-ai-model-routing-and-cost-control.md`
11. `docs/specifications/audiobook-creation-pipeline.md`
12. `docs/specifications/kindle-capture.md`
13. `docs/specifications/image-material-ingestion.md`
14. `docs/spec-proposals/generated-specifications/`
15. 現在の`script/`、`config/`、`data/`、`deliverables/`。読み取りのみ。

存在しないファイルはエラー終了せず、事前監査へ記録する。

## 4. 重要な設計課題

### 4.1 用語を分離する

少なくとも次を混同しない。

```text
Project / Audiobook
＝ 一冊または一つの制作企画

Build Request / User Task
＝ 利用者が画面から作成する制作依頼

Job / Job Run
＝ OCR、原稿生成、TTS、export等の実行単位

Source
＝ 素材

Artifact
＝ MP3、テキスト、EPUB等の生成物

Specification Task
＝ docs/tasks等の開発用タスク。製品内データとは別物
```

最終的な日本語ラベルも提案する。

### 4.2 DBの役割を比較する

最低限、次の3案を比較する。

1. ファイル正本＋SQLiteは索引・ジョブ管理のみ
2. SQLiteをメタデータ正本、原素材・大型成果物はファイル保存
3. PostgreSQL等を正本とするサーバー型

初期仮説は2であるが、結論を固定しない。
既存のファイルベース仕様、バックアップ、移行、可搬性を評価する。

### 4.3 起動方式を比較する

最低限、次を比較する。

- Python API＋Vue/React等のSPA
- Python API＋サーバーレンダリング/HTMX等
- Tauri/Electron等のデスクトップ包装

Windowsローカル利用、Docker、TTSエンジン、ファイル選択、
「一つのコマンドで起動しブラウザが開く」要件を評価する。

## 5. 実行順

```text
事前監査
↓
21 現状・用語
↓
22 製品範囲・MVP
↓
23 アーキテクチャ・起動方式
├─ 24 フロント画面
├─ 25 バックエンドAPI
└─ 26 永続化方式
    └─ 27 DB論理設計
↓
28 Project / Task / Job状態遷移
├─ 29 素材インポート
├─ 30 レビュー・承認
├─ 31 出力設定
├─ 32 声選択
└─ 33 実行監視・復旧
↓
34 セキュリティ・移行・バックアップ
↓
35 テスト・受け入れ
↓
36 AIによる追加機能提案
↓
37 統合草案
↓
38 仕様昇格手順
↓
39 最終報告
```

依存タスクが完全に確定しなくても、草案は`provisional`で進めてよい。

## 6. 生成先

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

ファイル名は既存と衝突する場合、内容を上書きせず`.new.md`等へ退避し、報告する。

## 7. 草案の共通必須項目

各草案へ次を含める。

- 目的
- 背景
- 対象
- 対象外
- 既存仕様との関係
- 用語
- 正常系
- 異常系
- UIまたはAPIの入出力
- 状態遷移
- データ所有者・正本
- バリデーション
- セキュリティ・プライバシー
- テスト観点
- 移行・互換性
- 未決定事項
- 人間レビュー項目
- 仕様昇格条件

## 8. 事前監査

最初に次へ保存する。

```text
docs/tasks/app-management-preflight-report.md
```

必須内容:

- 実際に存在した承認済み仕様
- 現在のCLI・スクリプト・データ保存方法
- 既存フロント・API・DBの有無
- 既存依存パッケージ
- 既存の仕様草案との重複
- 指定ダンプ名と実ファイルの不一致
- 変更予定ファイル
- 変更禁止ファイル

## 9. 終了時の報告

次へ保存する。

```text
docs/tasks/app-management-overnight-report.md
```

必須内容:

- 実行したタスク
- 生成した草案
- 採用推奨案
- 比較した代替案
- AIが追加提案した機能
- MVP推奨範囲
- DB採用案と正本境界
- 起動コマンド案
- evidence gap
- human review required
- blocked
- 仕様昇格候補と順序
- 実装を開始していないこと
- ソース・テスト・依存関係を変更していないこと
- Markdown/YAML/JSON/リンク検査結果

## 10. 終了条件

- 21〜39の各タスクに成果物またはblocked理由がある。
- 統合草案と仕様昇格計画がある。
- 人間承認を偽装していない。
- 実装コードを変更していない。
- DB導入で既存原資料を失う設計になっていない。
- 一つのコマンドから画面を開く案が比較されている。
