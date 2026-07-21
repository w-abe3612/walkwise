---
spec_id: db-06-voice-profiles-table
title: "voice_profiles テーブル"
status: approved
version: "1.0"
approved_at: "2026-07-22"
last_updated: "2026-07-22"
spec_refs:
  - 00-database-overview.md
  - 03-build-requests-table.md
  - ../specifications/09-voice-profile-schema.md
  - ../tasks/TASK-BUILD-EXEC-001-build-execution-pipeline-and-voice-profile-db.md
---

# voice_profiles テーブル

## 1. 目的

Projectごとに登録するVOICEVOX話者・パラメータ設定(VoiceProfile)を、
SQLiteを正本として保持する。従来の`09-voice-profile-schema.md`はYAML時代の
in-memoryモデル(`script/schemas/profiles.py::VoiceProfile`、6値status)を
定義しているが、本テーブルはBuild実行が実際に参照する**別のDB正本モデル**
(`script/domain/models.py::VoiceProfileRecord`、3値status)である。両者は
意図的に別concept(TASK-BUILD-EXEC-001 5.1節)。

## 2. column定義

| column | logical type | null | default | 備考 |
|---|---|---|---|---|
| `voice_profile_id` | text | not null | - | PK |
| `project_id` | text | not null | - | FK → projects.project_id |
| `name` | text | not null | - | Project内で一意 |
| `engine` | text | not null | - | MVPは`voicevox`のみ(`coeiroink`はTASK-COEIR-001が恒久blockedのため未接続) |
| `speaker_id` | text | not null | - | engineが認識するspeaker識別子 |
| `style_id` | text | null | `null` | |
| `speed_scale` | real | not null | `1.0` | `> 0` |
| `pitch_scale` | real | not null | `0.0` | |
| `intonation_scale` | real | not null | `1.0` | |
| `volume_scale` | real | not null | `1.0` | `> 0` |
| `sentence_pause_ms` | integer | not null | `250` | `>= 0` |
| `paragraph_pause_ms` | integer | not null | `600` | `>= 0` |
| `section_pause_ms` | integer | not null | `1000` | `>= 0` |
| `chapter_pause_ms` | integer | not null | `1500` | `>= 0` |
| `settings_json` | text | not null | `'{}'` | JSON object文字列。engine固有の追加設定 |
| `status` | text | not null | `'draft'` | `draft` / `approved` / `archived` |
| `created_at` | text (ISO8601) | not null | - | |
| `updated_at` | text (ISO8601) | not null | - | |

## 3. PK/FK/unique/check/index

- PK: `voice_profile_id`
- FK: `project_id` → `projects.project_id`
- unique: `(project_id, name)`
- check:
  - `json_valid(settings_json)`
  - `speed_scale > 0`
  - `volume_scale > 0`
  - `sentence_pause_ms >= 0 AND paragraph_pause_ms >= 0 AND section_pause_ms >= 0 AND chapter_pause_ms >= 0`
  - `status IN ('draft', 'approved', 'archived')`
- index: `project_id`、`status`

## 4. VoiceProfile仕様の詳細

### 4.1 Project所属

VoiceProfileは必ず1つのProjectに属する。別ProjectのVoiceProfileを
BuildRequestが参照することはできない(`voice_profile_project_mismatch`)。

### 4.2 status遷移とBuildでの使用条件

- `draft`: 新規作成直後の初期状態。Buildでは使用できない
  (`voice_profile_not_approved`)。
- `approved`: 新規Buildで選択できる唯一の状態。
- `archived`: 新規Buildで選択できない(`voice_profile_archived`)。
  archive後は`name`等の変更もできない。

物理削除は実装しない。archiveのみで、過去のBuildが参照した
VoiceProfileの履歴は保持し続ける。

### 4.3 mp3/text出力との関係

`03-build-requests-table.md`のとおり、`build_requests.output_formats_json`が
`mp3`を含む場合、`voice_profile_id`(approved状態)が必須である。`text`のみの
場合は`voice_profile_id`が`null`でもよい。

### 4.4 snapshot(不変化)

BuildExecutionOrchestratorは、Job開始時に一度だけ本テーブルからVoiceProfileを
読み込み、Job全体で不変のsnapshotとして扱う(Job実行中に本テーブルの行が
更新されても、実行中のJobには反映しない)。詳細:
`script/services/voice_profile_snapshot.py`、`14-audio-packaging.md`(manifest)。

## 5. archive/delete規則

物理削除は行わない。`status`を`archived`へ遷移させることで、新規Buildからの
選択だけを禁止する。過去にBuildが参照したVoiceProfileの行は削除しない。

## 6. 更新責務

`script/services/voice_profiles.py::VoiceProfileService`が、Project所属検証・
name重複検証・status遷移・archive後の変更禁止をすべて検証したうえで更新する。
DBのCHECK/UNIQUE/FK制約は最終防御線であり、Application Service層の検証を
省略する理由にはしない。

## 7. 正常例

```json
{
  "voice_profile_id": "vp-0001",
  "project_id": "database-foundations",
  "name": "ナレーター1",
  "engine": "voicevox",
  "speaker_id": "3",
  "style_id": null,
  "speed_scale": 1.0,
  "pitch_scale": 0.0,
  "intonation_scale": 1.0,
  "volume_scale": 1.0,
  "sentence_pause_ms": 250,
  "paragraph_pause_ms": 600,
  "section_pause_ms": 1000,
  "chapter_pause_ms": 1500,
  "settings_json": "{}",
  "status": "approved",
  "created_at": "2026-07-22T00:00:00+09:00",
  "updated_at": "2026-07-22T00:00:00+09:00"
}
```

## 8. 異常例

| ケース | 扱い |
|---|---|
| 存在しない`project_id`を参照する行を挿入しようとする | FK制約違反として拒否する(`project not found`) |
| 同一Project内で既存の`name`と重複する | UNIQUE制約違反として拒否する(`conflict`) |
| `speed_scale`や`volume_scale`が0以下 | check制約違反として拒否する |
| `settings_json`が不正なJSONまたはobject以外 | Application Service層で拒否する(`voice_profile_invalid`) |
| draft状態のVoiceProfileをmp3 Buildで参照する | `voice_profile_not_approved`として拒否する |
| archived状態のVoiceProfileを新規Buildで参照する | `voice_profile_archived`として拒否する |
| 別ProjectのVoiceProfileを参照する | `voice_profile_project_mismatch`として拒否する |
| archived状態のVoiceProfileを更新しようとする | `voice_profile_archived`として拒否する |

## 9. migration時の注意

- 本テーブルは`0002_voice_profiles_and_build_execution.sql`で新設した。
- 同一migrationで`build_requests.voice_profile_id`を本テーブルへのFIDへ変更した
  (テーブル再作成パターン。SQLiteは既存列へのFK追加を`ALTER TABLE`で
  直接行えないため)。
- migration適用前に、`build_requests.voice_profile_id`の参照先不在行がないことを
  `script/persistence/migrations.py::check_orphaned_build_request_voice_profiles`で
  確認する(fail-closed。孤立行を検出した場合は移行を進めず、件数とIDを報告する)。
