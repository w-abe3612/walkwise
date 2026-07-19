---
spec_id: db-02-sources-table
title: "sources テーブル"
status: approved
version: "1.1"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/image-material-ingestion.md
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/source-storage-and-common-schema.md
  - ../specifications/pdf-direct-text-extraction.md
  - ../specifications/ocr-and-scanned-pdf.md
  - ../specifications/rights-and-license-management.md
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
| `status` | text | not null | `"registered"` | `registered` / `processing` / `ready` / `review_required` / `failed` |
| `original_file_path` | text | not null | - | Project rootからの相対パス。immutable領域 |
| `content_hash` | text | not null | - | SHA-256 |
| `created_at` | text (ISO8601) | not null | - | |
| `updated_at` | text (ISO8601) | not null | - | |

## 3. PK/FK/unique/check/index

- PK: `source_id`
- FK: `project_id` → `projects.project_id`
- unique: `source_id`
- check: `media_type`が`text`/`pdf`/`image`のいずれか。`status`が
  `registered`/`processing`/`ready`/`review_required`/`failed`のいずれか。
- index: `project_id`

## 4. archive/delete規則

物理削除は行わない。Projectがarchiveされた場合、配下のSourceレコードも
そのまま保持する。個別Sourceの削除機能はMVPでは提供しない。

## 5. 更新責務

- `status`は、抽出・処理Job(PDF直接抽出`pdf-direct-text-extraction.md`、
  OCR`ocr-and-scanned-pdf.md`。いずれも承認済みでMVP必須)の結果に応じて
  Electron mainが更新する。
- `text`のSourceは抽出処理を必要としないため、登録直後に`ready`へ遷移できる。
- `pdf`/`image`のSourceは、登録後`processing`へ遷移し、抽出・OCR Jobの結果に
  応じて`ready`(高品質)、`review_required`(低信頼・高リスク要素検出)、
  `failed`(抽出失敗)のいずれかへ遷移する。
- 抽出・OCRされた本文そのもの(extracted/normalized/structured)は、DBの列としては
  保持せず、`source-storage-and-common-schema.md`が定義するファイル側の
  ディレクトリ構成(`sources/extracted/`等)とchunk manifestを正本とする。
  DBに大型派生コンテンツのパス列を無計画に追加しない。

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
| `media_type`が`epub`等MVP対象外の値である | check制約違反として拒否する(EPUBはpost-MVP、`19`参照) |
| 同一原本ファイルの重複登録 | `content_hash`の一致をApplication Service層でwarning表示するが、DB制約としては禁止しない(登録拒否・自動統合をしない、`source-storage-and-common-schema.md`) |
| PDF/OCR抽出が低信頼・高リスク要素(数式・コード・表・図)を検出 | `status`を`review_required`へ更新し、人間確認へ送る |

## 8. migration時の注意

抽出結果本文へのパスはDB列として追加せず、
`source-storage-and-common-schema.md`のディレクトリ構成とchunk manifest
(ファイル側)から解決する。DBとファイルの責務境界(`17-local-data-persistence-policy.md`)
を優先し、検索・制約上の必要性が個別に確認された場合のみ、将来のmigrationで
参照列の追加を検討する。
