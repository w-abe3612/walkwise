---
spec_id: db-90-schema-migrations-table
title: "schema_migrations テーブル(内部システム管理)"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/17-local-data-persistence-policy.md
---

# schema_migrations テーブル(内部システム管理)

## 1. 目的

適用済みDB migrationの履歴を記録する、内部システム管理テーブルを定義する。
本テーブルは利用者の作品データを表すものではなく、`00-database-overview.md`
5.13節が定義する「製品ドメインテーブル5つ」の制限対象外である。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `migration_id` | text | not null | - | PK。migrationファイルの安定ID(例: `0001_initial`) |
| `checksum` | text | not null | - | 適用時のmigration内容のhash |
| `applied_at` | text (ISO8601) | not null | - | 適用日時 |

## 3. PK/FK/unique/check/index

- PK: `migration_id`
- FK: なし(ドメインテーブルとの外部キー関係を持たない)
- unique: `migration_id`(PKにより保証)
- check: なし
- index: `applied_at`(適用順の確認用)

## 4. archive/delete規則

- 物理削除・論理archiveのいずれも適用しない。
- `projects`テーブルのarchive/delete規則(`01-projects-table.md`)を適用しない。
- 適用済み行は、migration適用処理からの追記のみで更新する。

## 5. 更新責務

- アプリ起動時、Electron mainが未適用のmigrationファイルを検出し、適用後に
  1行を追加する。
- 既存行の`checksum`と、対応するmigrationファイルの現在のhashが一致しない場合、
  migrationファイルが後から書き換えられたとみなし、アプリ起動を停止する
  (`00-database-overview.md` 5.5節)。
- 適用済み行を書き換える運用は行わない。

## 6. 正常例

```json
{
  "migration_id": "0001_initial",
  "checksum": "sha256:...",
  "applied_at": "2026-07-19T21:00:00+09:00"
}
```

## 7. 異常例

| ケース | 扱い |
|---|---|
| 適用済みmigrationファイルの内容が後から変更されている | `checksum`不一致を検出し、アプリ起動を停止する |
| 未適用migrationの適用中にアプリが強制終了する | 次回起動時、バックアップから安全に再試行する(`17-local-data-persistence-policy.md`) |
| `schema_migrations`テーブル自体が存在しない(初回起動) | 初期migrationの一部として作成する |

## 8. migration時の注意

- 本テーブル自体のスキーマ変更は、他のドメインテーブルと同様にmigrationとして
  記録するが、`schema_migrations`が記録手段そのものであるため、初期migration
  (`0001_initial`相当)でテーブル自体を作成することを前提とする。
- 過去に適用したmigrationファイルの内容を書き換えない。変更が必要な場合は
  新しいmigrationファイルを追加する。
