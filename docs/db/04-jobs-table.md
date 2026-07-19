---
spec_id: db-04-jobs-table
title: "jobs テーブル"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 00-database-overview.md
  - ../specifications/22-job-lifecycle-and-recovery.md
  - ../specifications/21-electron-python-worker-interface.md
---

# jobs テーブル

## 1. 目的

Build Requestから分解された実行単位(Job)の状態・実行履歴を保持する。
Jobに対応するファイルは存在しないため、本テーブルが唯一の正本である。
進捗の詳細メッセージ・技術ログはMVPでは別テーブル(`job_events`)にせず、
Job行内の最小列(`last_message`)、およびElectron mainのファイルログとして保持する
(`docs/db/README.md` 7節、`00-database-overview.md`参照)。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `job_id` | text | not null | - | PK |
| `build_request_id` | text | not null | - | FK → build_requests.build_request_id |
| `job_type` | text | not null | - | 例: `source_processing` / `script_generation` / `tts` / `audio_packaging` |
| `status` | text | not null | `"queued"` | `queued` / `running` / `succeeded` / `failed` / `cancel_requested` / `cancelled` |
| `parent_job_id` | text | null | `null` | 再試行元Jobへの参照。FK → jobs.job_id(自己参照) |
| `progress_current` | integer | null | `null` | 直近の`progress`イベントの`current`(`21`参照) |
| `progress_total` | integer | null | `null` | 直近の`progress`イベントの`total` |
| `last_message` | text | null | `null` | 直近の利用者向け進捗メッセージ |
| `started_at` | text (ISO8601) | null | `null` | |
| `finished_at` | text (ISO8601) | null | `null` | |

## 3. PK/FK/unique/check/index

- PK: `job_id`
- FK: `build_request_id` → `build_requests.build_request_id`、`parent_job_id` → `jobs.job_id`
- unique: `job_id`
- check: `status`が定義済み列挙値のいずれか
- index: `build_request_id`、`status`

## 4. archive/delete規則

物理削除は行わない。失敗したJobも含め、すべての実行履歴を保持する。

## 5. 更新責務

- `status`、`progress_current`、`progress_total`、`last_message`は、
  `21-electron-python-worker-interface.md`のJSON Linesイベントを受けて
  Electron mainが更新する。
- `parent_job_id`は、失敗Jobの再試行として新しいJobを作成する場合にのみ設定する
  (`22-job-lifecycle-and-recovery.md` 5.4節)。

## 6. 正常例

```json
{
  "job_id": "job-0001",
  "build_request_id": "br-0001",
  "job_type": "tts",
  "status": "running",
  "parent_job_id": null,
  "progress_current": 2,
  "progress_total": 10,
  "last_message": "章2を処理中",
  "started_at": "2026-07-19T21:00:00+09:00",
  "finished_at": null
}
```

## 7. 異常例

| ケース | 扱い |
|---|---|
| 存在しない`build_request_id`を参照する行を挿入しようとする | FK制約違反として拒否する |
| `status`が`cancelled`から直接`running`へ更新される | Application Service層で拒否する(`22`参照) |
| アプリ強制終了で`status: running`のまま残る | 次回起動時のstale job検出により`failed`へ更新する |

## 8. migration時の注意

進捗イベントの詳細履歴(複数の`progress`イベントすべて)を保持する要求が
将来生じた場合、`job_events`テーブルを新設するmigrationを追加する
(`docs/db/README.md` 7節の昇格手順に従う)。既存の`jobs.last_message`列は
「直近のメッセージ」の役割のまま維持し、詳細履歴は新テーブル側に持たせる。
