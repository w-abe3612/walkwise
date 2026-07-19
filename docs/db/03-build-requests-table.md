---
spec_id: db-03-build-requests-table
title: "build_requests テーブル"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/22-job-lifecycle-and-recovery.md
  - ../specifications/19-application-scope-and-mvp.md
---

# build_requests テーブル

## 1. 目的

利用者が画面から作成する、1回の出力意図(出力形式・声・対象範囲)を保持する。
Build Requestに対応するファイルは存在しないため、本テーブルが唯一の正本である。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `build_request_id` | text | not null | - | PK |
| `project_id` | text | not null | - | FK → projects.project_id |
| `output_format` | text | not null | - | `mp3` / `text`(MVP範囲、複数選択は将来カンマ区切りまたは別テーブル検討) |
| `voice_profile_id` | text | not null | - | `09-voice-profile-schema.md`の`voice_profile_id`(MVPはVOICEVOXのみ) |
| `status` | text | not null | `"draft"` | `draft` / `queued` / `running` / `completed` / `failed` / `cancel_requested` / `cancelled` |
| `created_at` | text (ISO8601) | not null | - | |
| `updated_at` | text (ISO8601) | not null | - | |

## 3. PK/FK/unique/check/index

- PK: `build_request_id`
- FK: `project_id` → `projects.project_id`
- unique: `build_request_id`
- check: `output_format`が`mp3`/`text`のいずれか。`voice_profile_id`が空でない。
  `status`が定義済み列挙値のいずれか。
- index: `project_id`、`status`

## 4. archive/delete規則

物理削除は行わない。Build Requestは実行履歴として保持し続ける。

## 5. 更新責務

- `status`はElectron mainが、対応するJobの状態(`22-job-lifecycle-and-recovery.md`)に
  応じて更新する。
- Build Request自体は、承認ゲート未充足の場合`queued`へ進めない
  (`22-job-lifecycle-and-recovery.md` 5.5節)。

## 6. 正常例

```json
{
  "build_request_id": "br-0001",
  "project_id": "database-foundations",
  "output_format": "mp3",
  "voice_profile_id": "sample-voicevox-profile",
  "status": "draft",
  "created_at": "2026-07-19T21:00:00+09:00",
  "updated_at": "2026-07-19T21:00:00+09:00"
}
```

## 7. 異常例

| ケース | 扱い |
|---|---|
| 存在しない`project_id`を参照する行を挿入しようとする | FK制約違反として拒否する |
| `output_format`が`epub`等MVP対象外の値である | check制約違反として拒否する |
| 承認ゲート未充足のまま`status`を`queued`へ更新しようとする | Application Service層で拒否する(`22`参照) |

## 8. migration時の注意

将来、複数出力形式の同時選択をサポートする場合、`output_format`を
単一列からJSON配列列、または`build_request_output_formats`関連テーブルへ
変更するmigrationを追加する。既存行は単一値をそのまま新形式へ変換する。
