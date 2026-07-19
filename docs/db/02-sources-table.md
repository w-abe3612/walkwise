---
spec_id: db-02-sources-table
title: "sources テーブル"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/image-material-ingestion.md
  - ../specifications/19-application-scope-and-mvp.md
---

# sources テーブル

## 1. 目的

Project配下に登録されたSource(素材)のmetadata、種類、処理状態、
原本ファイルへの参照を保持する。原本ファイル自体はimmutableなファイル
正本であり、本テーブルはその索引を保持する。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `source_id` | text | not null | - | PK |
| `project_id` | text | not null | - | FK → projects.project_id |
| `media_type` | text | not null | - | `text` / `pdf` / `image` のいずれか(MVP範囲、`19-application-scope-and-mvp.md`) |
| `status` | text | not null | `"registered"` | `registered` / `processing` / `ready` / `failed` |
| `original_file_path` | text | not null | - | Project rootからの相対パス。immutable領域 |
| `content_hash` | text | not null | - | SHA-256 |
| `created_at` | text (ISO8601) | not null | - | |
| `updated_at` | text (ISO8601) | not null | - | |

## 3. PK/FK/unique/check/index

- PK: `source_id`
- FK: `project_id` → `projects.project_id`
- unique: `source_id`
- check: `media_type`が`text`/`pdf`/`image`のいずれか。`status`が
  `registered`/`processing`/`ready`/`failed`のいずれか。
- index: `project_id`

## 4. archive/delete規則

物理削除は行わない。Projectがarchiveされた場合、配下のSourceレコードも
そのまま保持する。個別Sourceの削除機能はMVPでは提供しない。

## 5. 更新責務

- `status`は、抽出・処理Job(将来の`docs/spec-proposals/`側の各処理仕様が
  承認された後に実行される)の結果に応じてElectron mainが更新する。
- PDF・画像の抽出処理が未実装の間、`status`は`registered`のまま維持され、
  「処理待ち」として画面に表示される(`19-application-scope-and-mvp.md` 5.3節)。

## 6. 正常例

```json
{
  "source_id": "database-book-chapter1",
  "project_id": "database-foundations",
  "media_type": "text",
  "status": "ready",
  "original_file_path": "sources/originals/database-book-chapter1.txt",
  "content_hash": "sha256:...",
  "created_at": "2026-07-19T21:00:00+09:00",
  "updated_at": "2026-07-19T21:00:00+09:00"
}
```

## 7. 異常例

| ケース | 扱い |
|---|---|
| 存在しない`project_id`を参照する行を挿入しようとする | FK制約違反として拒否する |
| `media_type`が`epub`等MVP対象外の値である | check制約違反として拒否する(EPUB等はMVP対象外、`19`参照) |
| 同一原本ファイルの重複登録 | `content_hash`の一致をApplication Service層で警告表示するが、DB制約としては禁止しない(利用者が意図的に重複登録する場合があるため) |

## 8. migration時の注意

将来、PDF/OCR抽出処理が仕様承認・実装された場合、抽出結果の参照列
(例: `extracted_text_path`)を追加のmigrationとして導入する。既存行には
`null`を設定する。
