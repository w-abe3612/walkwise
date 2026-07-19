---
spec_id: db-03-build-requests-table
title: "build_requests テーブル"
status: approved
version: "1.1"
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
| `output_formats_json` | text | not null | - | JSON配列文字列。許可値`mp3`/`text`、1件以上、重複禁止、canonical order `mp3`→`text`(4.1節) |
| `voice_profile_id` | text | null | `null` | `09-voice-profile-schema.md`の`voice_profile_id`(MVPはVOICEVOXのみ)。`output_formats_json`が`mp3`を含まない場合は`null`可 |
| `status` | text | not null | `"draft"` | `draft` / `queued` / `running` / `completed` / `failed` / `cancel_requested` / `cancelled` |
| `created_at` | text (ISO8601) | not null | - | |
| `updated_at` | text (ISO8601) | not null | - | |

## 3. PK/FK/unique/check/index

- PK: `build_request_id`
- FK: `project_id` → `projects.project_id`
- unique: `build_request_id`
- check:
  - `output_formats_json`がSQLiteで利用可能な場合`json_valid(output_formats_json)`を満たす。
  - 配列要素が`mp3`/`text`のみ、1件以上、重複なし。
  - `output_formats_json`が`mp3`を含む場合、`voice_profile_id`が空でない(非NULL)。
  - `status`が定義済み列挙値のいずれか。
- index: `project_id`、`status`

SQLiteのCHECK制約だけでは配列要素の内容(許可値・重複・`mp3`含有時の
`voice_profile_id`必須)を完全に検証できない場合があるため、
Application Service層でも同じ規則を必ず検証する(4.1節)。

## 4. Build Request仕様の詳細

### 4.1 output_formats_json

- SQLite logical typeは`text`。JSON配列文字列として保存する。
- 1件以上必須。許可値は`mp3`と`text`だけ。
- 重複値は禁止する。
- canonical orderは`mp3`、`text`の順に統一する(表示・比較・テストを安定させるため)。
- カンマ区切り文字列(`"mp3,text"`)は使用しない。JSON配列文字列
  (`"[\"mp3\",\"text\"]"`)のみを許可する。
- 複数出力形式に対応する新しい関連テーブル(`build_request_output_formats`等)は
  MVPでは追加しない。

### 4.2 voice_profile_idの派生整合性

- `output_formats_json`が`mp3`を含む場合: `voice_profile_id`必須。
- `output_formats_json`が`text`のみの場合: `voice_profile_id`は`null`可。
- `mp3`を含むにもかかわらず`voice_profile_id`が`null`の行は、DBのCHECK制約
  および Application Service層の両方で拒否する。

## 5. archive/delete規則

物理削除は行わない。Build Requestは実行履歴として保持し続ける。

## 6. 更新責務

- `status`はElectron mainが、対応するJobの状態(`22-job-lifecycle-and-recovery.md`)に
  応じて更新する。
- Build Request自体は、承認ゲート未充足の場合`queued`へ進めない
  (`22-job-lifecycle-and-recovery.md` 5.5節)。

## 7. 正常例

```json
{
  "build_request_id": "br-0001",
  "project_id": "database-foundations",
  "output_formats_json": "[\"mp3\",\"text\"]",
  "voice_profile_id": "sample-voicevox-profile",
  "status": "draft",
  "created_at": "2026-07-19T21:00:00+09:00",
  "updated_at": "2026-07-19T21:00:00+09:00"
}
```

textのみの例:

```json
{
  "build_request_id": "br-0002",
  "project_id": "database-foundations",
  "output_formats_json": "[\"text\"]",
  "voice_profile_id": null,
  "status": "draft",
  "created_at": "2026-07-19T21:05:00+09:00",
  "updated_at": "2026-07-19T21:05:00+09:00"
}
```

## 8. 異常例

| ケース | 扱い |
|---|---|
| 存在しない`project_id`を参照する行を挿入しようとする | FK制約違反として拒否する |
| `output_formats_json`が`epub`等MVP対象外の値を含む | check制約違反として拒否する |
| `output_formats_json`が空配列 | check制約違反として拒否する(1件以上必須) |
| `output_formats_json`に`mp3`が重複して含まれる | check制約違反として拒否する(重複禁止) |
| `mp3`を含むのに`voice_profile_id`が`null` | DB制約またはApplication Service層で拒否する |
| 承認ゲート未充足のまま`status`を`queued`へ更新しようとする | Application Service層で拒否する(`22`参照) |

## 9. migration時の注意

- 本テーブルは新規migrationとして`output_formats_json`列を持つ形で作成する。
  単一値`output_format`列は正本として使用しない。
- 将来、`mp3`/`text`以外の出力形式(EPUB等)を追加する場合、
  `output_formats_json`のCHECK制約(許可値)を更新するmigrationを追加する。
  既存行の値は変更しない。
