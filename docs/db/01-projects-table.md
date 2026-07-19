---
spec_id: db-01-projects-table
title: "projects テーブル"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/03-project-plan-schema.md
---

# projects テーブル

## 1. 目的

Project(作品)のmetadata・状態・企画ファイルへの参照を保持する。
企画本文自体は`project-plan.yaml`がファイル正本であり、本テーブルは
一覧表示・検索・状態管理のためのメタデータを保持する。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `project_id` | text | not null | - | PK。`01-common-identifiers-and-versioning.md`のID形式 |
| `title` | text | not null | - | 表示名 |
| `domain` | text | not null | - | |
| `planning_stage` | text | not null | `"registered"` | `03-project-plan-schema.md`の4状態のいずれか |
| `content_revision` | integer | not null | `1` | `project-plan.yaml`の`content_revision`と一致させる |
| `plan_file_path` | text | not null | - | Project rootからの相対パス(`project/project-plan.yaml`) |
| `created_at` | text (ISO8601) | not null | - | |
| `updated_at` | text (ISO8601) | not null | - | |
| `archived_at` | text (ISO8601) | null | `null` | archive日時。未archiveは`null` |

## 3. PK/FK/unique/check/index

- PK: `project_id`
- FK: なし
- unique: `project_id`(PKにより保証)
- check: `planning_stage`が`registered`/`curriculum_draft`/`review_pending`/`approved`のいずれか
- index: `archived_at`(archive済みを除外する一覧表示のため)

## 4. archive/delete規則

物理削除は行わない。`archived_at`へ日時を設定することでarchiveを表現する。
archive済みProjectは既定の一覧表示から除外するが、関連するSource・BuildRequest・
Job・Artifactのレコードは保持し続ける。

## 5. 更新責務

- `title`、`domain`、`planning_stage`、`content_revision`は、企画ファイル
  (`project-plan.yaml`)の変更に追従してElectron mainが更新する。
- `updated_at`は、いずれかの列が変更されるたびに更新する。

## 6. 正常例

```json
{
  "project_id": "database-foundations",
  "title": "データベース基礎",
  "domain": "database",
  "planning_stage": "registered",
  "content_revision": 1,
  "plan_file_path": "project/project-plan.yaml",
  "created_at": "2026-07-19T21:00:00+09:00",
  "updated_at": "2026-07-19T21:00:00+09:00",
  "archived_at": null
}
```

## 7. 異常例

| ケース | 扱い |
|---|---|
| `planning_stage`に未知の値を挿入しようとする | check制約違反として拒否する |
| `project_id`が`01-common-identifiers-and-versioning.md`のID形式に違反する | Application Service層のバリデーションで事前に拒否する |
| 同一`project_id`を重複登録しようとする | PK制約違反として拒否する |

## 8. migration時の注意

初期migrationでは、`archived_at`をnull許容の列として作成する。将来、
複数利用者対応を追加する場合は、所有者を表す列を新しいmigrationとして
追加し、既存行には既定の単一利用者IDを設定する。
