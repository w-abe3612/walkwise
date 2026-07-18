---
status: ready
version: "1.0"
created_at: "2026-07-19"
---

# フロント・DB管理 仕様草案作成タスク一覧

## 実行開始

最初に次を読む。

```text
docs/tasks/20_app-management-spec-drafting-master.md
```

その後、原則として番号順に実行する。

| 順序 | task_id | ファイル | テーマ | 依存 | 主成果物 |
|---:|---|---|---|---|---|
| 20 | `SPEC-APP-000` | `20_app-management-spec-drafting-master.md` | 全体制御 | なし | 事前監査・最終報告 |
| 21 | `SPEC-APP-001` | `21_spec-draft-app-current-state-and-terminology.md` | 現状監査と製品用語の整理 | なし | `00-current-state-and-terminology.md` |
| 22 | `SPEC-APP-002` | `22_spec-draft-app-product-scope-and-mvp.md` | 製品範囲・利用者導線・MVP | SPEC-APP-001 | `01-product-scope-and-mvp.md` |
| 23 | `SPEC-APP-003` | `23_spec-draft-app-architecture-and-runtime.md` | アプリケーション構成・技術スタック・起動方式 | SPEC-APP-001, SPEC-APP-002 | `02-architecture-and-runtime.md` |
| 24 | `SPEC-APP-004` | `24_spec-draft-app-frontend-information-architecture.md` | フロント画面・情報設計・操作導線 | SPEC-APP-002, SPEC-APP-003 | `03-frontend-information-architecture.md` |
| 25 | `SPEC-APP-005` | `25_spec-draft-app-backend-api.md` | バックエンドAPIとapplication service境界 | SPEC-APP-003, SPEC-APP-004 | `04-backend-api-and-service-boundary.md` |
| 26 | `SPEC-APP-006` | `26_spec-draft-app-persistence-strategy.md` | ファイルとDBの永続化責務 | SPEC-APP-001, SPEC-APP-003, SPEC-APP-005 | `05-persistence-strategy.md` |
| 27 | `SPEC-APP-007` | `27_spec-draft-app-database-schema.md` | DB論理スキーマ・制約・履歴 | SPEC-APP-006 | `06-database-logical-schema.md` |
| 28 | `SPEC-APP-008` | `28_spec-draft-app-workflow.md` | Project・制作依頼・Jobの状態遷移 | SPEC-APP-002, SPEC-APP-007 | `07-project-task-job-workflow.md` |
| 29 | `SPEC-APP-009` | `29_spec-draft-app-material-import.md` | 素材インポート画面と処理草案 | SPEC-APP-004, SPEC-APP-005, SPEC-APP-006, SPEC-APP-008 | `08-material-import-workflow.md` |
| 30 | `SPEC-APP-010` | `30_spec-draft-app-review-approval.md` | 原稿・出典・承認・編集画面 | SPEC-APP-004, SPEC-APP-008 | `09-review-and-approval-workflow.md` |
| 31 | `SPEC-APP-011` | `31_spec-draft-app-output-settings.md` | 出力形式・出力プロファイル・成果物管理 | SPEC-APP-002, SPEC-APP-004, SPEC-APP-008 | `10-output-and-export-settings.md` |
| 32 | `SPEC-APP-012` | `32_spec-draft-app-voice-selection.md` | 声・音声プロファイル・試聴選択 | SPEC-APP-004, SPEC-APP-008 | `11-voice-selection-and-preview.md` |
| 33 | `SPEC-APP-013` | `33_spec-draft-app-job-monitoring.md` | 処理進捗・ログ・通知・中断復旧 | SPEC-APP-005, SPEC-APP-008 | `12-job-monitoring-and-recovery.md` |
| 34 | `SPEC-APP-014` | `34_spec-draft-app-security-migration.md` | セキュリティ・権利・バックアップ・移行 | SPEC-APP-006, SPEC-APP-007, SPEC-APP-009, SPEC-APP-014 | `13-security-backup-migration.md` |
| 35 | `SPEC-APP-015` | `35_spec-draft-app-testing-acceptance.md` | テスト戦略・受け入れ条件・運用診断 | SPEC-APP-003, SPEC-APP-004, SPEC-APP-005, SPEC-APP-006, SPEC-APP-008 | `14-testing-and-acceptance.md` |
| 36 | `SPEC-APP-016` | `36_spec-draft-app-additional-features.md` | AIによる追加機能提案と優先順位 | SPEC-APP-002, SPEC-APP-004, SPEC-APP-008, SPEC-APP-009, SPEC-APP-010, SPEC-APP-011, SPEC-APP-012, SPEC-APP-013, SPEC-APP-014, SPEC-APP-015 | `15-additional-feature-proposals.md` |
| 37 | `SPEC-APP-017` | `37_spec-draft-app-integrated-proposal.md` | フロント・DB管理の統合仕様草案 | SPEC-APP-002, SPEC-APP-003, SPEC-APP-004, SPEC-APP-005, SPEC-APP-006, SPEC-APP-007, SPEC-APP-008, SPEC-APP-009, SPEC-APP-010, SPEC-APP-011, SPEC-APP-012, SPEC-APP-013, SPEC-APP-014, SPEC-APP-015, SPEC-APP-016 | `16-integrated-application-proposal.md` |
| 38 | `SPEC-APP-018` | `38_spec-draft-app-spec-promotion.md` | 草案のレビュー・仕様昇格手順 | SPEC-APP-017 | `17-specification-promotion-plan.md` |
| 39 | `SPEC-APP-019` | `39_spec-draft-app-final-report.md` | 夜間成果の統合報告と次の作業順 | SPEC-APP-018 | `APP_MANAGEMENT_REVIEW_CHECKLIST.md` |

## 夜間に使わない状態

```text
approved
done
```

## 夜間に使える状態

```text
review
provisional
blocked
human_review_required
```

## 期待する最終判断材料

- 推奨frontend/backend/packaging案
- SQLite等DBの採用範囲
- fileとDBの正本境界
- ERD
- 主要画面一覧
- APIとJob model
- 素材import、出力、声選択の導線
- AI追加提案機能
- MVP範囲
- 仕様昇格順序と承認条件
- 実装タスク候補
