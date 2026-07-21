---
document_type: implementation_task
task_id: TASK-BUILD-EXEC-001
status: ready
release_scope: release-readiness
priority: P0
created_at: "2026-07-21"
source_review: audio_book_creation_dump_2026-07-21_235801.txt
approved_design: Build Execution Pipeline 設計承認
depends_on:
  - TASK-REVIEW-001
related_existing_tasks:
  - TASK-BUILD-001
  - TASK-JOB-001
  - TASK-ARTIFACT-001
  - TASK-APPROVAL-001
  - TASK-PROFILE-001
  - TASK-NARRATION-001
  - TASK-TTS-001
  - TASK-VOICEVOX-001
  - TASK-AUDIO-002
  - TASK-AUDIO-003
  - TASK-DESKTOP-003
external_gate: true
---

# TASK-BUILD-EXEC-001 Build Execution Pipeline正本結線・VoiceProfile DB永続化

## 1. 目的

既存の個別機能、mock中心のBuild pipeline、Electron/Worker/SQLite結線を利用し、実際の`Job`が次の処理を一貫して実行できる状態を作る。

```text
Job開始
→ BuildRequest取得
→ Project取得
→ 対象章解決
→ verified script検証
→ VoiceProfile検証
→ TTS
→ 音声検査
→ 章MP3作成
→ text作成
→ production manifest作成
→ Artifact登録
→ Job成功
```

同時に、VoiceProfileの正本をYAMLファイルではなくSQLiteの`voice_profiles`テーブルへ移し、Projectに紐づく設定として登録・取得・更新・アーカイブできるようにする。

このタスクは既存の単体契約を作り直すものではない。既存実装を再利用して、実行時に不足している永続化・解決・オーケストレーションを追加する。

## 2. 承認済み設計

### 2.1 検証済み原稿

正本は次とする。

```text
data/library/<project_id>/chapters/<chapter_id>/verified/script.yaml
```

TTSへ渡す文字列はsegmentごとに次の優先順位で解決する。

```text
1. segments[].tts_text
2. segments[].text
```

次の場合は本番TTSを開始しない。

- ファイルが存在しない
- schema検証に失敗する
- `verified_script`承認ゲートが未承認
- 対象章IDとscript内`chapter_id`が一致しない

下書き、narration派生物、legacy textへ自動フォールバックしてはならない。

安定エラーコード:

```text
verified_script_not_found
verified_script_invalid
verified_script_not_approved
```

### 2.2 BuildRequestの対象章

MVPでは1件のBuildRequestはProject全体を対象とする。

```text
BuildRequest.project_id
→ Projectの正式な章一覧
→ 全章を正式順で処理
```

- `build_requests`へ`chapter_id`を追加しない。
- 章順はProject PlanまたはCurriculumの正式な構造化章一覧から取得する。
- フォルダ名の文字列順で決めない。
- 一部の章だけが準備済みでも部分完成品を作らず、開始前にJob全体を拒否する。
- 部分再生成は既存impact analysis / regeneration planの責務とする。

安定エラーコード:

```text
build_target_not_ready
chapter_order_not_found
chapter_not_found
```

### 2.3 VoiceProfile

VoiceProfileの正本はSQLiteとする。YAML正本を新設しない。

```text
projects.project_id
→ voice_profiles.project_id

build_requests.voice_profile_id
→ voice_profiles.voice_profile_id
```

1 Projectは複数VoiceProfileを持てる。

出力形式ごとの条件:

```text
[text]       : voice_profile_idはnull可
[mp3]        : voice_profile_id必須
[text, mp3]  : voice_profile_id必須
```

VoiceProfileはJob開始時に一度だけ読み込み、検証済みスナップショットをJob全体で使用する。章処理の途中でDBを再読込して設定を混在させてはならない。

### 2.4 失敗時

- Jobを`failed`へ遷移させる。
- 安定エラーコード、失敗段階、利用者向けメッセージを保存する。
- 未完成ファイルを正式Artifactへ登録しない。
- 既存の正常Artifactを削除・上書きしない。
- 別の原稿、声、speaker、style、engine、既定値へ自動変更しない。
- 一部章だけを完成品として表示しない。

## 3. 開始前監査

変更前に必ず次を確認し、実測結果を作業ログへ残す。

1. `git status --short`
2. 現在のmigration runnerが複数SQL migrationをどう検出・適用するか
3. `0001_initial.sql`、DB文書、repository、domain modelの現状
4. `VoiceProfile` schema/modelと`script/profiles/voices.py`の既存責務
5. `BuildRequestService`、`JobService`、`ArtifactService`のpublic契約
6. `script/pipelines/build.py`、audio synthesis/validation/packagingの注入境界
7. `ApprovalService`の対象単位と`verified_script`承認の確認方法
8. Project PlanとCurriculumのどちらが正式章順を保持しているか
9. Worker command registry、handler、Electron service adapter、IPCの実経路
10. production manifestの既存schemaと後方互換性
11. `TASK-REVIEW-001`の未完了条件と重複範囲

既存仕様に承認内容と衝突する明確な規定がある場合は、実装を停止して差分を報告する。推測でどちらかを選ばない。

## 4. DB migration

### 4.1 migration追加

既存migration規則に従い、新しいmigrationを追加する。ファイル名はrunnerの規則を確認して決める。想定例:

```text
script/persistence/sql/0002_voice_profiles_and_build_execution.sql
```

既存の`0001_initial.sql`を、既に適用済みDBのために破壊的に書き換えてはならない。

### 4.2 `voice_profiles`テーブル

最低限、次の情報を保持する。

```text
voice_profile_id
project_id
name
engine
speaker_id
style_id
speed_scale
pitch_scale
intonation_scale
volume_scale
sentence_pause_ms
paragraph_pause_ms
section_pause_ms
chapter_pause_ms
settings_json
status
created_at
updated_at
```

推奨制約:

```text
PRIMARY KEY (voice_profile_id)
FOREIGN KEY (project_id) REFERENCES projects(project_id)
UNIQUE (project_id, name)
status IN ('draft', 'approved', 'archived')
json_valid(settings_json)
```

数値範囲は既存VoiceProfile schemaとTTS adapterの制約を正本として揃える。二重に異なる範囲を定義しない。

`settings_json`は空objectを許可し、canonical JSONとして扱う。

### 4.3 BuildRequest参照

`build_requests.voice_profile_id`が`voice_profiles.voice_profile_id`を参照するようにする。

SQLiteで既存テーブルへ外部キーを安全に追加できない場合は、既存データを保持する正式なtable rebuild migrationを行う。

migrationは次を満たすこと。

- 既存projects、sources、build_requests、jobs、artifactsを保持する
- migration失敗時に中途半端なschemaを残さない
- foreign key enforcementを確認する
- 既存の`voice_profile_id`値がある場合は、参照先不在を黙って削除・null化しない
- 不整合データがある場合はmigrationを停止し、件数とIDを秘密情報なしで報告する

Project削除仕様が明確でないため、`ON DELETE CASCADE`を推測で追加しない。

## 5. Domain・Repository・Service

### 5.1 Domain model

既存の`VoiceProfile` schemaを再利用または明確にadapter変換し、DB用に別の意味を持つ重複モデルを乱立させない。

必要な状態:

```text
draft
approved
archived
```

### 5.2 VoiceProfileRepository

最低限次を実装する。

```text
insert
find
list_by_project
update
archive
```

物理削除は実装しない。

次を安定エラーにする。

```text
voice_profile_not_found
voice_profile_project_mismatch
voice_profile_invalid
voice_profile_not_approved
voice_profile_archived
```

### 5.3 VoiceProfileService

最低限次を担当する。

- Project存在確認
- 同一Project内の名前重複確認
- schema・数値範囲・settings_json検証
- create/update/list/get/archive
- approved以外を新規Buildで使用させない
- 参照済みProfileを履歴ごと保持する
- 別ProjectのProfile参照を拒否する

### 5.4 UnitOfWork

既存UnitOfWorkへVoiceProfileRepositoryを追加する場合は、既存transaction境界を壊さない。public signature変更が広範囲に波及する場合は、後方互換な追加を優先する。

## 6. BuildRequest検証

BuildRequest作成時に最低限次を検証する。

- Projectが存在する
- `mp3`を含む場合はVoiceProfileが指定される
- 指定VoiceProfileが存在する
- VoiceProfileの`project_id`がBuildRequestの`project_id`と一致する
- VoiceProfileが`approved`
- `archived`ではない
- text-onlyではVoiceProfileを要求しない

DB制約だけに任せず、利用者へ安定エラーコードを返す。

## 7. 正式な対象章解決

### 7.1 章順の正本

既存Project Plan / Curriculum schemaを調査し、正式な章ID配列を一つに決定する。

優先順位が既存仕様で明確なら従う。明確でない場合は実装を停止し、以下を報告する。

```text
- Project Planに存在する章情報
- Curriculumに存在する章情報
- 両者が不一致になる可能性
- 推奨案
```

承認なしで独自優先順位を作らない。

### 7.2 事前検証

TTS開始前に全章を検査し、次を一覧化する。

- 章ID
- 章順
- verified script path
- ファイル存在
- schema妥当性
- script内chapter_id一致
- `verified_script`承認状態

一つでも不備があれば、音声生成を一切始めず`build_target_not_ready`で失敗させる。詳細には不備章IDと個別理由を含める。

### 7.3 Path解決

Projectの物理ディレクトリは既存`ProjectPaths`/永続化policyを利用する。`project_id`をそのまま文字列連結し、path traversalや旧project directory互換を壊してはならない。

## 8. VoiceProfile実行時スナップショット

Job開始時にVoiceProfileを一度だけ取得して、immutableな実行設定へ変換する。

最低限含める。

```text
voice_profile_id
voice_profile_name
project_id
engine
speaker_id
style_id
speed_scale
pitch_scale
intonation_scale
volume_scale
sentence_pause_ms
paragraph_pause_ms
section_pause_ms
chapter_pause_ms
settings_json
voice_profile_updated_at
voice_profile_config_hash
```

`voice_profile_config_hash`はcanonical化した設定値から既存hash utilityを使って計算する。

Job中にProfileが更新されても、そのJobの全章は開始時スナップショットを使う。

## 9. Build Execution Orchestrator

既存`script/pipelines/build.py`を中心にするか、新しいapplication serviceを設けるかは既存責務を監査して決める。ただし、既存のmock用BuildPipelineを破壊的に置換しない。

必要な依存をDI可能にする。

```text
BuildRequestRepository / Service
ProjectRepository / Service
VoiceProfileRepository / Service
ApprovalService
ProjectPaths / structured file loader
TTS registry / client
Audio synthesis
Audio validation
Chapter packaging
Production manifest writer
ArtifactService
JobService
Clock / ID generator
Progress emitter
Cancellation token
```

実行順:

```text
1. Job/BuildRequest/Project取得
2. Jobをrunningへ遷移
3. 全対象章とverified scriptを事前検証
4. VoiceProfileを一度取得・検証・snapshot化
5. 出力形式ごとに必要なruntimeをpreflight
6. 章順にsegmentをTTS
7. segment/章音声を検査
8. 章MP3を生成
9. verified text成果物を生成
10. production manifestを生成
11. すべての正式ファイル確定後にArtifactを登録
12. Jobをsucceededへ遷移
```

text-onlyの場合はTTS、VOICEVOX、音声検査、MP3 packagingを呼ばない。

mp3を含む場合だけVoiceProfileとTTS runtimeを要求する。

## 10. 原子的な成果物確定

正式出力は一時領域へ作り、全工程成功後に正式pathへ移す。

- 途中生成物をArtifactとして登録しない
- 既存Artifactを上書きしない
- 新versionとして登録する
- manifestとArtifact DB登録の順序を設計し、片方だけ成功する状態を回復可能にする
- DB transactionとfilesystem atomic writeの境界を明記する
- 失敗時の一時ファイルcleanupを行う
- cleanup失敗は元エラーを隠さずログへ付記する

既存ArtifactServiceのappend-only version規則を維持する。

## 11. Production manifest

既存schemaへ後方互換な形でVoiceProfile snapshotを追加する。

最低限記録する。

```text
voice_profile_snapshot
voice_profile_config_hash
chapter_order
verified_script_paths
verified_script_content_hashes
output_formats
artifact一覧
build_request_id
job_id
project_id
created_at
```

text-onlyの場合は`voice_profile_snapshot`をnullまたはschemaで定義された省略形とする。

既存manifest consumerとtestsを壊す破壊的変更をしない。schema version変更が必要ならmigration/compatibility仕様へ記載する。

## 12. Job進捗・失敗情報

少なくとも次の段階を進捗として通知する。

```text
resolving_build_target
validating_verified_scripts
loading_voice_profile
checking_runtime
synthesizing_chapter
validating_audio
packaging_chapter
writing_text
writing_manifest
registering_artifacts
completed
```

章処理では`chapter_id`と`current/total`を含める。

既存jobsテーブルだけでは安定エラーコード・失敗段階を保存できない場合、migrationで後方互換に追加するか、既存の永続化方針に沿う別の正式な記録先を使用する。推測でログだけに落とさない。

候補項目:

```text
error_code
error_stage
error_detail_json
```

秘密値、API key、原稿全文、絶対pathをエラー詳細へ保存しない。

## 13. Worker・Electron・GUI結線

### 13.1 Worker

既存command registryへ、必要なVoiceProfile操作とBuild実行commandを登録する。

最低限の論理操作:

```text
voice_profile.create
voice_profile.list
voice_profile.get
voice_profile.update
voice_profile.archive
build.execute または既存job.startからの実行
```

既存command名規則を確認し、重複commandを新設しない。

### 13.2 Electron service adapter / IPC

既存の`voice:list-engines`はTTS engine/speaker列挙であり、ProjectのVoiceProfile一覧とは別概念である。混同しない。

Project VoiceProfile用に必要なadapter/APIを追加し、Build Settings画面がDBのVoiceProfileを選択できるようにする。

- Project変更時に対象ProjectのProfileだけを表示
- draft/archivedを新規Buildの選択肢に出さない
- mp3選択時にProfile必須
- text-onlyではProfileなしを許可
- 別ProjectのProfile IDを手入力・改ざんしてもmain/worker側で拒否
- RendererへDB handleや任意SQLを公開しない

UIで新規作成・編集・archiveが現在の画面仕様に含まれない場合、最低限、テストやfixtureだけでなく利用者がProfileを登録できる導線がどこにあるべきかを確認する。仕様不足なら勝手に大規模画面を追加せず停止・報告する。

## 14. 必須テスト

既存テストを削除・弱体化せず、最低限次を追加または強化する。

### 14.1 Migration / DB

1. 空DBへ新migration適用
2. 既存`0001`適用済みDBからのupgrade
3. 既存データ件数保持
4. `voice_profiles` FK / unique / check / JSON制約
5. `build_requests.voice_profile_id` FK
6. 不整合既存voice_profile_idがある場合のfail-closed
7. migration再実行のidempotency/checksum

### 14.2 Repository / Service

8. VoiceProfile create/find/list/update/archive
9. Project別一覧分離
10. 同一Project内name重複拒否
11. 別Project Profile参照拒否
12. draft/archived Profileでmp3 Build拒否
13. text-onlyでProfileなし成功
14. 参照済みProfileを物理削除しない

### 14.3 Target / verified script

15. 正式章順で解決
16. フォルダ文字列順を使わない
17. verified script欠落
18. schema不正
19. chapter_id不一致
20. approval未承認
21. 一章でも不備ならTTSを一度も呼ばない
22. `tts_text`優先、なければ`text`
23. legacy/downstream fallback禁止

### 14.4 Orchestration

24. text-only正常系
25. mp3正常系をfake TTS/fake encoderで完走
26. VoiceProfileをJob開始時に一度だけ読む
27. Job途中のProfile更新が同Jobへ混ざらない
28. TTS失敗時Job failed、Artifact 0
29. 音声検査失敗時Job failed、Artifact 0
30. packaging失敗時Job failed、Artifact 0
31. manifest失敗時Job failed、Artifact 0
32. Artifact登録失敗時の回復可能性
33. 既存正常Artifact非破壊
34. 進捗順序と章番号
35. cancellation時の中途Artifact非登録

### 14.5 Manifest

36. VoiceProfile snapshot全項目
37. canonical config hash安定性
38. Profile編集後も過去manifestが変化しない
39. text-onlyのProfileなし表現
40. chapter order / script hash記録

### 14.6 Worker / Electron

41. Worker command登録
42. Project別Profile一覧
43. IPC入力検証
44. Renderer改ざんによる別Project参照拒否
45. Build Settingsでapproved Profileだけ選択
46. mp3/text条件
47. Job progressがRendererへ届く
48. mock E2EでBuildRequest→Job→Artifact完走

通常テストは外部接続しない。実VOICEVOX/ffmpegはexternal gateで分離する。

## 15. 実行手順

```text
1. git差分とbaseline保存
2. 現行schema・pipeline・Worker/IPC監査
3. 承認内容を仕様書へ反映
4. テスト追加・業務未実装によるRed確認
5. migration実装
6. VoiceProfile repository/service実装
7. BuildRequest検証強化
8. 章順・verified script resolver実装
9. VoiceProfile snapshot実装
10. Build Execution Orchestrator実装
11. manifest/Artifact/Job失敗処理実装
12. Worker/Electron/Renderer結線
13. 対象テスト
14. Python全体回帰
15. TypeScript typecheck/Vitest
16. build/package回帰
17. 利用可能runtimeだけsmoke→live
18. 文書・CURRENT_STATE・progress更新
19. 最終報告
```

## 16. 仕様書・文書更新

最低限、現状と矛盾する箇所を更新する。

```text
docs/specifications/02-process-input-output.md
docs/specifications/09-voice-profile-schema.md
docs/specifications/14-audio-packaging.md
docs/specifications/17-local-data-persistence-policy.md
docs/specifications/21-electron-python-worker-interface.md
docs/specifications/22-job-lifecycle-and-recovery.md
docs/specifications/audiobook-creation-pipeline.md

docs/db/00-database-overview.md
docs/db/03-build-requests-table.md
docs/db/04-jobs-table.md
docs/db/README.md
新規 docs/db/06-voice-profiles-table.md

docs/screens/03-build-settings.md
docs/screens/04-job-progress.md
docs/commands/profiles.md
docs/commands/builds.md
docs/commands/jobs.md
docs/commands/audio-packaging.md
docs/commands/database.md
docs/commands/end-to-end.md
docs/commands/CURRENT_STATE.md

docs/notes/implementation_assumptions.md
docs/notes/progress.md
release/checklist.md
```

`project/voices/`をVoiceProfile正本として記述している箇所はDB正本へ修正する。ただし、将来のexport/debug用途のJSON/YAML出力まで禁止する記述にはしない。

現在状態を実測せずに「完了」「pass」「release ready」と書かない。

## 17. TASK-REVIEW-001との関係

- `TASK-REVIEW-001`は削除・完了扱いにしない。
- 本タスク完了後も、実GUI表示、実VOICEVOX、実ffmpeg、Windows installer等が未確認なら、`TASK-REVIEW-001`のrelease readyは`no`のままとする。
- 本タスクの成果を`TASK-REVIEW-001`の未解決/実測欄へ反映する。
- `docs/tasks/`や`docs/spec-proposals/`の追加cleanupは、人間の完了承認前に実施しない。
- `TASK-COEIR-001`の永久blocked状態を変更しない。

## 18. 禁止事項

- 既存未コミット変更の破棄
- `0001_initial.sql`だけを書き換えて既存DB migrationを省略
- VoiceProfile YAMLを新しい正本として作成
- 別Project Profileの利用
- draft/archived Profileの暗黙利用
- missing Profile時の自動選択
- speaker/style/engine/設定値の自動置換
- Job途中でVoiceProfileを再読込
- フォルダ名順で章順を決定
- verified scriptからlegacy原稿へのfallback
- 一部章だけを正式完成品として登録
- 既存Artifactの上書き・削除
- 失敗をskip、xfail、空catch、dummy assertionで隠す
- fake E2Eを実runtime確認と記録
- 外部runtimeへの無断接続
- COEIROINKの実装・接続
- TASK-REVIEW-001の削除
- gitの破壊的操作

## 19. 停止条件

次の場合はその場で実装を止め、調査結果・選択肢・推奨案を報告する。

1. Project PlanとCurriculumのどちらが正式章順か既存仕様から決定できない
2. VoiceProfileの既存schemaと承認済みDB項目が両立しない
3. 既存DBに参照先のない`build_requests.voice_profile_id`が存在する
4. SQLite migrationでデータ保持を保証できない
5. public signatureの破壊的変更が必要
6. approvalが章単位の`verified_script`承認を表現できない
7. production manifestの後方互換を保てない
8. Artifact DB登録とfilesystem確定の整合を安全に設計できない
9. GUIのVoiceProfile登録導線が仕様不足で決定できない
10. 承認済み仕様と上位仕様が矛盾する
11. 秘密値・利用者データを必要とする
12. 作業対象外の大規模再設計が必要

## 20. 完了条件

- migration前後で既存データが保持される
- `voice_profiles`がProject単位でDB管理される
- BuildRequestから同一Projectのapproved VoiceProfileだけを参照できる
- text-only BuildがVoiceProfileなしで動く
- Project全章が正式順で解決される
- 全章のverified scriptと承認をTTS前に検証する
- verified scriptの`tts_text`→`text`優先が守られる
- VoiceProfile snapshotをJob全体で固定する
- textおよびmp3のmock統合Buildが完走する
- production manifestへProfile snapshot/hashと章情報が残る
- 失敗時にJobがfailedとなり正式Artifactが登録されない
- 既存正常Artifactが保持される
- Worker/Electron/Rendererから実経路を起動できる
- 対象テストと通常全体回帰がpassする
- `npm run typecheck`とVitestがpassする
- `npm run build`とpackage回帰を壊さない
- 外部runtime未確認は未確認として残る
- TASK-REVIEW-001とTASK-COEIR-001が残る
- 文書と実装が一致する

## 21. 完了報告形式

```text
# TASK-BUILD-EXEC-001 実行結果

## 結論
- 実装: complete / incomplete
- mock Build E2E: pass / fail
-実VOICEVOX: pass / fail / unverified
- 実ffmpeg: pass / fail / unverified
- release ready: yes / no

## 開始時baseline
- git status
- migration一覧
- DB schema
- Python collection/pass/fail/xfail/skip
- TypeScript/Vitest
- build/package

## 仕様更新
- 更新した仕様書
- 確定した章順の正本
- VoiceProfile DB正本
- 互換性判断

## DB migration
- migration file
- migration前後schema
- migration前後データ件数
- 既存不整合データ
- rollback/transaction方針

## VoiceProfile
- table定義
- repository/service
- Project所属検証
- status/archived
- BuildRequest参照
- snapshot/hash

## Build実行
- verified script解決
- 章順解決
- approval確認
- text-only経路
- mp3経路
- progress
- failure handling
- cancellation

## Artifact / manifest
- 生成物
- version
- atomic確定
- manifest項目

## Worker / Electron / UI
- command
- adapter
- IPC
- Build Settings導線
- Job progress

## 実測
- 対象テスト
- Python全体
- Docker
- typecheck
- Vitest
- npm build
- package

## 外部runtime
- VOICEVOX
- ffmpeg/ffprobe
- Gemini
- Tesseract
- COEIROINK

## 変更ファイル
- 追加
- 修正
- 削除

## 未解決
- blocker
- 未確認
- 次に必要な人間判断
```