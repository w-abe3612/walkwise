---
spec_id: db-05-artifacts-table
title: "artifacts テーブル"
status: approved
version: "1.1"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/14-audio-packaging.md
  - ../specifications/21-electron-python-worker-interface.md
  - 03-build-requests-table.md
---

# artifacts テーブル

## 1. 目的

Jobが生成した成果物(MP3、テキスト等)の索引を保持する。成果物本体は
ファイルが正本であり、本テーブルはパス・版・hashの索引を保持する。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `artifact_id` | text | not null | - | PK |
| `job_id` | text | not null | - | FK → jobs.job_id |
| `project_id` | text | not null | - | FK → projects.project_id(横断検索用の非正規化列) |
| `artifact_type` | text | not null | - | `mp3_chapter` / `text_verified_script`(MVP範囲) |
| `file_path` | text | not null | - | Project rootからの相対パス |
| `version_number` | integer | not null | `1` | 同一`artifact_type`内で1から増加 |
| `content_hash` | text | not null | - | SHA-256 |
| `created_at` | text (ISO8601) | not null | - | |

## 3. PK/FK/unique/check/index

- PK: `artifact_id`
- FK: `job_id` → `jobs.job_id`、`project_id` → `projects.project_id`
- unique: (`project_id`, `artifact_type`, `version_number`)
- check: `version_number >= 1`
- index: `project_id`、`artifact_type`

## 4. archive/delete規則

物理削除は行わない。再生成時も既存versionを削除せず、新しい`version_number`で
新規行を追加する(`21-electron-python-worker-interface.md`の`artifact`イベントを
受けて挿入する)。

### 4.1 1つのBuild Requestから複数Artifactを生成する

`build_requests.output_formats_json`(`03-build-requests-table.md`)がMP3と
テキストを同時選択している場合、同一Build Request配下のJobから複数の
`artifact_type`(`mp3_chapter`と`text_verified_script`)の行を作成できる。
形式ごとに別Artifact行・別ファイルとして生成し、一方の生成が他方を
上書きしない。unique制約(`project_id`,`artifact_type`,`version_number`)は
`artifact_type`ごとに独立したversion系列を許容する設計であり、
複数形式の同時生成を妨げない。

## 5. 更新責務

Artifact行は挿入専用とし、更新(UPDATE)は行わない。再生成のたびに
新しい行を挿入する。

## 6. 正常例

```json
{
  "artifact_id": "artifact-0001",
  "job_id": "job-0001",
  "project_id": "database-foundations",
  "artifact_type": "mp3_chapter",
  "file_path": "audio/chapters/01_ch01.mp3",
  "version_number": 1,
  "content_hash": "sha256:...",
  "created_at": "2026-07-19T21:10:00+09:00"
}
```

## 7. 異常例

| ケース | 扱い |
|---|---|
| 同一(`project_id`,`artifact_type`,`version_number`)で重複挿入 | unique制約違反として拒否する |
| 既存versionを上書きする更新操作 | Application Service層で禁止する(挿入専用の運用) |
| 存在しない`job_id`を参照する行を挿入しようとする | FK制約違反として拒否する |

## 8. migration時の注意

将来EPUB等の出力形式が承認された場合、`artifact_type`の許容値を
追加するmigrationを行う(check制約の更新)。既存行の値は変更しない。
