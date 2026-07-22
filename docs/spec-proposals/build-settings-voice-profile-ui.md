---
spec_id: build-settings-voice-profile-ui
title: "Build SettingsへのVoiceProfile選択・管理導線(UI仕様案)"
status: approved
version: "1.0"
last_updated: "2026-07-22"
approved_at: "2026-07-22"
depends_on:
  - "TASK-BUILD-EXEC-001 (完了、backend実装済み。詳細はdocs/notes/progress.mdを参照)"
spec_refs:
  - ../screens/03-build-settings.md
  - ../screens/02-project-workspace-and-source-import.md
  - ../screens/README.md
  - ../db/06-voice-profiles-table.md
  - ../specifications/09-voice-profile-schema.md
  - ../specifications/10-tts-client-common-interface.md
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/20-electron-desktop-architecture.md
  - ../specifications/22-job-lifecycle-and-recovery.md
---

# Build SettingsへのVoiceProfile選択・管理導線(UI仕様案)

> **承認済み(2026-07-22、`TASK-VOICE-PROFILE-UI-001`)**
> 本書の提案は人間承認済みであり、`docs/screens/02-project-workspace-and-source-import.md`
> (音声設定section)・`docs/screens/03-build-settings.md`(VoiceProfile選択)へ実装・
> 反映済みである。承認内容は次のとおり。
>
> - VoiceProfile管理場所: Project Workspace(第6画面は追加しない)
> - 承認済みProfile編集: 編集後もapprovedを維持する(10節の選択肢1を採用)
> - Build Settingsからの新規作成: 不可(Project Workspace側でのみ作成)
> - 旧speaker/style直接選択UI: 削除済み
> - VoiceProfile未作成時: text-only Buildは許可、mp3 Buildは禁止
> - text-only時のVoiceProfile欄: disabledのグレー表示(非表示にはしない)
> - Profile複製機能: MVPでは実装しない
>
> 詳細な実装内容は`docs/tasks/`配下の`TASK-VOICE-PROFILE-UI-001`完了報告、および
> `docs/notes/progress.md`を参照。5節「案A」・6節「案B」・7節「案C」の比較検討・
> 9節の推奨理由は、承認済み内容の背景として引き続き参照する。

## 1. 背景

`TASK-BUILD-EXEC-001`により、Project単位で登録・承認するVoiceProfile
(SQLite正本、`docs/db/06-voice-profiles-table.md`)のbackend一式
(migration、Repository、Service、Worker command、Electron adapter/IPC/preload)が
実装・テスト済みになった。しかし、Rendererの`BuildSettings.vue`(承認済み画面仕様
`03-build-settings.md` v1.1)は、これ以前に確定した「VOICEVOXのspeaker/style一覧
から都度選択する」モデルのままであり、新しいVoiceProfileを選択・作成・承認する
導線を一切持たない。本書は、この導線をどう追加するかのUI仕様を、実装前に
複数案比較・検討するための提案書である。

## 2. 現行UI

`electron/renderer/screens/BuildSettings.vue`(現状、変更なし)の実際の挙動:

- **speaker選択**: `speakers: readonly SpeakerOptionView[]`をpropsで受け取り、
  `<select data-testid="speaker-select">`で1件選択する。`speakers`は
  `voice:list-engines` IPCが返すVOICEVOX speaker一覧(`speakerId`/`displayName`)で、
  Project概念を持たない、engine全体の候補一覧である。
- **style選択**: 現行UIにはstyle選択欄が存在しない(speaker単位の選択のみ)。
- **speed等の設定**: `speedScale`のスライダー(0.5〜2.0)のみ実装されている。
  pitch/intonation/volume/pauseは現行UIに存在しない。
- **出力形式選択**: `mp3`/`text`のチェックボックス(複数選択可、1件以上必須)。
- **BuildRequest送信内容**: `submitBuild()`が
  `createBuildRequest({ outputFormats, voiceProfileId: selectedFormats.mp3 ? selectedSpeakerId.value : undefined })`
  を呼ぶ。**重要な問題**: ここで`voiceProfileId`として渡される値は
  `selectedSpeakerId`(生のVOICEVOX speaker_id文字列、例: `"3"`)であり、
  新backendが要求する実際の`voice_profiles.voice_profile_id`
  (`vp-xxxxxxxx`のような別のDB主キー文字列)ではない。現行コードのままmp3
  Buildを実行すると、`BuildRequestService.create()`が`voice_profile_id`の
  Project所属確認(`ProjectRepository`検索ではなく`VoiceProfileService.assert_usable_for_build`)を行い、
  存在しない`voice_profile_id`として`voice_profile_not_found`(NOT_FOUND)を
  返すため、**現行UIのままでは新backend上でmp3 Buildが実行不能**である
  (テキストのみのBuildは`voiceProfileId`が`undefined`のため影響を受けない)。
- **voice:list-enginesの利用方法**: マウント時(または画面側の未実装の呼び出し元)が
  `voice:list-engines`を呼び、`health`(接続可否)と`speakers`一覧を取得する。
  `health.available === false`の間は、mp3を選択してもspeaker選択・speedスライダー・
  試聴ボタンをすべてdisabledにする。

## 3. 実装済みbackend

- **VoiceProfileの項目**: `voice_profile_id`/`project_id`/`name`/`engine`/
  `speaker_id`/`style_id`/`speed_scale`/`pitch_scale`/`intonation_scale`/
  `volume_scale`/`sentence_pause_ms`/`paragraph_pause_ms`/`section_pause_ms`/
  `chapter_pause_ms`/`settings_json`/`status`/`created_at`/`updated_at`
  (`docs/db/06-voice-profiles-table.md`)。
- **status**: `draft`/`approved`/`archived`の3値。新規作成は必ず`draft`。
  `archived`は新規Buildで選択不可、かつ`archived`後は一切更新不可
  (物理削除はしない)。
- **Project所属**: VoiceProfileは必ず1つのProjectに属する。別ProjectのVoiceProfileは
  参照できない(`voice_profile_project_mismatch`)。
- **create/list/get/update/archive API**:
  - Worker command(Python側実装名): `voice_profile.create` / `voice_profile.list` /
    `voice_profile.get` / `voice_profile.update` / `voice_profile.archive`
  - Electron main IPC channel名(`electron/main/ipc/voice_profiles.ts`):
    `voice-profile:create` / `voice-profile:list` / `voice-profile:get` /
    `voice-profile:update` / `voice-profile:archive`
  - preload API(`electron/preload/index.ts`): `window.walkwise.voiceProfile.{create,list,get,update,archive}`
  - これらはすべて実装・テスト済みだが、**どの画面からも呼び出されていない**
    (現行Rendererに未接続)。
- **BuildRequestで必要になるvoice_profile_id**: `output_formats`が`mp3`を含む場合、
  `voice_profile_id`(実際のVoiceProfile主キー)が必須(`voice_profile_required`)。
  `text`のみの場合は省略可。
- **approvedのみ使用可能という制約**: `draft`は`voice_profile_not_approved`、
  `archived`は`voice_profile_archived`として、mp3 Buildでの新規参照を拒否する
  (`script/services/build_requests.py`、`script/services/voice_profiles.py`)。

## 4. 不整合

```text
現行UI: speaker一覧(voice:list-engines、engine全体、Project概念なし)から
        都度1件選択し、その生speaker_idをBuildRequestのvoiceProfileId欄へ
        そのまま送信している。
新backend: BuildRequestのvoice_profile_idは、Project単位で事前登録・承認された
        VoiceProfile(DB主キー、`voice_profiles`テーブル)でなければならない。
問題: 型・出自が異なる2つの識別子(speaker_id vs voice_profile_id)を
        現行コードが混同しており、現行UIのままではmp3 Buildが実行時エラーになる。
必要なUI判断: VoiceProfileをどこで作成・承認するか、Build Settingsでは
        何を選ぶだけにするか、旧speaker/style直接選択をどう扱うかを
        確定する必要がある(5〜9節で検討)。
```

```text
現行UI: VoiceProfileの作成・編集・承認・archive操作が画面のどこにも存在しない。
新backend: create/list/get/update/archiveのfull CRUDが既に動作可能。
問題: backendのstatus遷移(draft→approved→archived)を操作する手段が
        利用者に一切提供されていない。
必要なUI判断: どの画面でVoiceProfileの作成・承認・archiveを行うか(5〜7節)。
```

```text
現行UI: 5画面構成(`docs/screens/README.md` 7節)を前提に設計されている。
新backend: VoiceProfileはProjectに対して複数存在し得る、独立したライフサイクルを
        持つリソースである。
問題: 「Build設定の一部」として画面へ埋め込むか、「Projectの設定」として
        独立管理するかで、画面構成・navigationへの影響が大きく異なる。
必要なUI判断: 第6画面を許可するか、既存画面内へ統合するか(7節、12節)。
```

## 5. UI案A: Build Settings内でProfileを管理

Build Settings画面自体に、VoiceProfile選択・新規作成・編集・archive・
approvedへの変更操作をすべて置く。

| 評価観点 | 内容 |
|---|---|
| 利点 | Build実行までの導線が1画面で完結する。他画面への遷移が不要。 |
| 欠点 | 「1回の出力意図を設定する」画面(Build Request作成)と「Projectの再利用可能な資源を管理する」画面(VoiceProfile CRUD+承認)という、性質の異なる2つの責務が1画面に混在する。既存の`03-build-settings.md`の目的(3節「出力形式とVOICEVOXの声・パラメータを選択し…Jobを起動する画面」)を大きく超える。 |
| 画面の複雑さ | 高い。一覧+作成フォーム+編集フォーム+承認操作+archive確認+既存の出力形式/speed等の設定が同一画面に同居する。 |
| 初心者の分かりやすさ | 低〜中。初回Build時に「まずProfileを作る」「それを承認する」「それから選ぶ」という3段階の作業を、Build実行という単発操作の画面内でこなす必要があり、迷いやすい。 |
| 実装規模 | 中〜大。一覧・作成・編集・承認・archiveのUI一式をBuild Settings内に新設する必要がある。 |
| 既存画面への影響 | 大。既存の`03-build-settings.md`(validation規則、状態表、キーボード操作)をほぼ全面的に書き換える必要がある。 |

## 6. UI案B: Project Settingsとして別画面で管理

Project WorkspaceまたはVoiceProfile専用の新画面でVoiceProfileを管理し、
Build SettingsではapprovedなProfileを選ぶだけにする。

| 評価観点 | 内容 |
|---|---|
| 利点 | 「Projectの資源管理」と「1回のBuild実行設定」が分離される。VoiceProfileがProjectに対して複数・再利用可能というDB設計(`docs/db/06-voice-profiles-table.md`)と自然に一致する。Build Settingsは既存の「選択するだけ」という単純さを保てる。 |
| 欠点 | 独立した新画面(第6画面)を追加する場合、`docs/screens/README.md` 7節の「MVPでは5画面を基本とする」制限に対する昇格判断が必要になる。Project WorkspaceへUIを統合する場合は新画面を避けられるが、既存の`02-project-workspace-and-source-import.md`(Source一覧・承認バッジ表示が中心)へ新しい責務を追加することになる。 |
| 追加画面の必要性 | 独立画面案では必要(第6画面)。Project Workspace統合案では不要。 |
| navigationへの影響 | Build Settingsへ行く前に、Project WorkspaceでProfileを承認済みにしておく、という順序が生まれる(既存の承認ワークフロー[資料・企画・原稿・試聴音声]と同じ操作順の思想と一致する)。 |
| 実装規模 | 中。既存のSource一覧・承認一覧の実装パターン(一覧表示+ステータスバッジ+操作ボタン)を流用できる。 |
| 将来の複数Profile管理との相性 | 高い。将来、章単位や用途別に複数Profileを使い分ける場合も、Project単位の管理画面が自然な拡張の起点になる。 |

## 7. UI案C: 選択ダイアログと編集ダイアログ

Build Settingsでは選択欄(dropdown)のみを表示し、作成・編集はmodal/dialogで行う。

| 評価観点 | 内容 |
|---|---|
| 利点 | Build Settings画面自体には選択欄1つだけが増える程度の変更で済み、既存画面の単純さをほぼ維持できる。画面遷移(route変更)が発生しない。 |
| 欠点 | modalには、既存の各画面仕様が共通して要求するキーボード操作・破壊操作確認・状態表示(empty/loading/success/error/disabled)を、modal内でも同様に満たす必要があり、モーダル自体の仕様策定が追加で必要になる。 |
| modalの複雑さ | 中〜高。作成フォーム・編集フォーム・archive確認(破壊操作相当)をmodal内に持つ場合、フォーム項目数(9節参照)がやや多い。 |
| 画面遷移の少なさ | 最も少ない(route変更なし)。 |
| accessibility | modalのfocus trap、Escで閉じる、開いた際のfocus移動など、既存画面にはない新しい要求が生じる。対応は可能だが、既存screens仕様に前例がない分、明示的な仕様化が必要。 |
| テスト容易性 | 既存の`mount()` + `data-testid`パターンはmodal単体コンポーネントとしてテスト可能なため大きな支障はないが、「どのタイミングでmodalが開くか」の遷移テストが追加で必要になる。 |

## 8. 比較表

| 観点 | 案A(Build Settings内で完結) | 案B(Project単位で分離管理) | 案C(選択+modal) |
|---|---|---|---|
| 責務の分離 | 低(混在) | 高 | 中〜高 |
| 第6画面の要否 | 不要 | 独立画面案では必要、Project Workspace統合案では不要 | 不要 |
| Build Settings自体の複雑さ | 高 | 低(選択のみ) | 低〜中(選択欄+modal起動ボタン) |
| DB設計(Project単位で複数Profile)との一致 | 低 | 高 | 中(modalの置き場所次第でBと同等になり得る) |
| 初期実装規模 | 大 | 中 | 中 |
| 既存承認済み画面仕様への影響 | 大(03を全面改訂) | 中(02へ追記、03へ選択欄追加) | 小〜中(03へ選択欄+modal起動、modal自体は新規) |
| 将来の拡張性(章単位Profile等) | 低 | 高 | 中 |

## 9. 推奨案

**案Bの「Project Workspace統合」変種と、案Cの「modal」機構を組み合わせる案を推奨する。**
具体的には次のとおり。

```text
Project Workspace(02-project-workspace-and-source-import.md、既存画面)
  → 折り畳み式の「音声設定(VoiceProfile)」sectionを追加し、
    一覧表示・新規作成・編集・承認(draft→approved)・archiveを、
    modal/dialogを併用して行う(第6画面は追加しない)。

Build Settings(03-build-settings.md)
  → 現行の`voice:list-engines`によるspeaker直接選択を廃止し、
    Project Workspaceで承認済み(approved)のVoiceProfile一覧から
    1件選択するだけの、単純なdropdownへ置き換える。
```

推奨理由:

- 「Projectの再利用可能な資源(VoiceProfile)を管理する」ことと「1回のBuildを
  実行する」ことという性質の異なる2つの作業を分離でき、Build Settings自体は
  現行と同程度の単純さを維持できる。
- `docs/db/06-voice-profiles-table.md`の設計(VoiceProfileはProjectに対して
  複数存在し、承認ライフサイクルを持つ)と直接一致する。
- 第6画面を追加せず、既存の`02`(Source登録・承認バッジ表示という「Projectの
  準備状態を整える」画面)へ自然に統合できる。既存のSource一覧・承認一覧の
  実装パターン(状態バッジ+一覧+操作ボタン)を流用できる。
- draft編集とBuild実行が画面として分離されるため、「承認前のProfileでうっかり
  本番Buildしてしまう」導線を作らずに済む(現行のBuild Settingsのシンプルさを
  壊さない)。

**この推奨は`proposal`であり、承認済み仕様ではない。** 特に次の点は
既存仕様からは決定できず、人間判断が必要である(18節)。

- MVPで実装する範囲: VoiceProfileの一覧表示・選択・新規作成・draft→approved
  遷移・archiveの最小セット。
- MVPでは実装しない範囲: Profile複製機能、章単位/segment単位のProfile上書き、
  Profile使用履歴の詳細表示(どのBuild/Artifactがどのsnapshotを使ったか、は
  backendのmanifestには既に記録されているが、UI上での閲覧は対象外とする)。
- 既存speaker/style UIの扱い: 14節のとおり、VoiceProfile作成・編集modal内の
  候補取得手段として`voice:list-engines`を引き続き使う。Build Settings画面
  自体からは、speaker/style直接選択を削除する(VoiceProfile IDへ一本化)。
- text-only時の表示: 10節参照(人間判断事項)。
- mp3時の必須表示: approved VoiceProfileが1件も無い場合、mp3チェックボックス
  自体は選択可能なままにするが、送信(制作開始)を`voice_profile_required`
  相当の理由でdisabledにし、Project Workspaceの音声設定sectionへの導線を
  表示する。
- Profileが0件の場合の表示: 12節参照。
- approved Profileが0件の場合の表示: 12節参照。

## 10. 状態遷移

```text
新規作成
→ draft

draft編集
→ draft(そのまま)

draftを承認する(approved化)
→ approved
  (承認操作の主体・確認ステップの要否は人間判断事項。18節)

任意の状態(draft/approved)からarchiveする
→ archived
  (archivedからの復帰は不可。既存backend`VoiceProfileService`の
  archive-onlyポリシーと一致させ、UI側でも「元に戻す」操作は提供しない)
```

**approved Profile編集後の扱い(重要、人間判断が必要)**:

現行backend(`script/services/voice_profiles.py::VoiceProfileService.update`)は、
`archived`状態のみ更新を拒否し、`approved`状態の更新は制限していない
(更新後もstatusは`approved`のまま維持される)。つまり、UI仕様として何も
追加指定しなければ、**選択肢1(編集後もapprovedを維持)が追加のbackend変更
なしにそのまま実現できる状態にある**。次の3択のいずれを採用するかは、
既存の承認ワークフロー仕様(`07-approval-workflow.md`は`verified_script`等
4つのgateについてのみ定義しており、VoiceProfile自体の承認再要求ルールは
定義していない)からは決定できないため、人間判断事項として残す。

```text
1. 編集後もapprovedを維持する(現行backendのまま、追加実装不要)
2. 編集するとdraftへ自動的に戻し、再承認を必須にする(backend変更が必要:
   update時にstatus=approvedならdraftへ強制遷移させるロジックの追加)
3. approved Profileは直接編集させず、複製(新しいdraftとして複製)のみ許可する
   (backend変更が必要: 複製APIの新設)
```

なお、VoiceProfileはJob開始時に1回だけ読み込まれ、Job全体で不変のsnapshotとして
扱われるため(`script/services/voice_profile_snapshot.py`)、選択肢1を採用しても
**過去に実行済みのBuildの成果物・manifestが後から変化することはない**
(snapshotは`voice_profile_config_hash`と共にmanifestへ既に記録されている)。
この点は選択肢1のリスクを下げる材料として付記する。

## 11. 画面項目

### 11.1 Project Workspace「音声設定」section(新設、既存02画面への追加)

| 項目 | 型 | 備考 |
|---|---|---|
| VoiceProfile一覧 | テーブルまたはカード一覧 | name、engine、speaker表示名、status(バッジ)、更新日時 |
| 新規作成ボタン | ボタン | modalを開く |
| 編集ボタン(行ごと) | ボタン | archived行では非表示またはdisabled(10節の遷移規則どおり編集不可) |
| 承認ボタン(行ごと、draftのみ) | ボタン | draft→approved |
| archiveボタン(行ごと、draft/approvedのみ) | ボタン | 破壊操作相当、確認ステップを伴う(既存画面の破壊操作確認の慣例に合わせる) |

### 11.2 VoiceProfile作成/編集modal

| 項目 | 型 | 必須 |
|---|---|---|
| name | 文字列 | 必須(Project内一意、重複はbackendが`conflict`で拒否) |
| engine | 選択式(MVPは`voicevox`固定) | 必須 |
| speaker | 選択式(`voice:list-engines`から取得した候補) | 必須 |
| style | 選択式(speakerに対応する候補、任意) | 任意 |
| speed_scale/pitch_scale/intonation_scale/volume_scale | スライダー(`09-voice-profile-schema.md`の値域に合わせる) | 任意(既定値あり) |
| pause設定(sentence/paragraph/section/chapter) | 数値入力またはスライダー | 任意(既定値あり) |

### 11.3 Build Settings画面(改訂案)

| 項目 | 型 | 必須 |
|---|---|---|
| 出力形式 | チェックボックス(mp3、テキスト) | 既存どおり、1件以上必須 |
| VoiceProfile選択 | 選択式(このProjectのapproved Profileのみ) | mp3選択時のみ必須。speaker/style直接選択・speedスライダーは廃止 |
| (VoiceProfile選択欄からの遷移導線) | リンクまたはボタン | 「音声設定を管理」→Project Workspaceの音声設定sectionへ遷移 |

## 12. 空状態

| 状況 | Build Settings画面の表示 |
|---|---|
| ProjectにVoiceProfileが1件もない | VoiceProfile選択欄の代わりに「音声設定がまだありません。Project画面で作成してください」+導線リンクを表示。text-only Buildは通常どおり実行可能。 |
| draftしか存在しない | 「承認済みの音声設定がありません(draftのみ)」+導線リンク。mp3は選択不可(送信disabled)。 |
| archivedしか存在しない | 上記と同様の表示(「承認済みの音声設定がありません」で統一するか、archived専用文言にするかは人間判断事項、18節)。 |
| approved Profileが存在しない(上記2つの一般化) | 同上。 |
| 選択中Profileが(別ウィンドウ・別session等で)archiveされた | 送信(制作開始)時にbackendが`voice_profile_archived`を返す。UIは選択を解除し、「選択していた音声設定は利用できなくなりました。再度選択してください」を表示する(13節)。 |
| Profile取得に失敗した(IPCエラー) | 既存の他画面と同じ「取得に失敗しました」の要約メッセージ+再試行ボタン(`01`/`02`画面のerror状態と統一)。 |
| mp3選択後にProfileが未選択 | 既存パターンを踏襲し、送信ボタンをdisabledにする(speaker未選択時の現行動作と同じ)。 |
| text-onlyへ変更した | VoiceProfile選択欄をdisabled化する(現行のspeaker-select disabled化と同じ扱いを踏襲。非表示にするかdisabled表示のままにするかは18節の人間判断事項)。 |
| 別Projectへ移動した | VoiceProfile一覧をそのProjectのIDで再取得する。前のProjectで選択していたIDを引き継がない(初期状態へ戻す)。 |
| BuildRequest作成時にproject mismatchが返った | 通常は発生しない想定(UIが常に現在のProjectのapproved一覧のみを提示するため)が、防御的に「選択した音声設定はこのProjectのものではありません」という専用メッセージを表示し、内部コード`voice_profile_project_mismatch`はログにのみ残す。 |

## 13. エラー表示

利用者向け表示と内部エラーコードを分離する(既存の`approval_gate_not_satisfied`の
扱いと同じ方針)。

| 内部エラーコード(backend) | 利用者向け表示(案) |
|---|---|
| `voice_profile_required` | 「MP3を出力するには音声設定を選択してください」 |
| `voice_profile_not_found` | 「選択した音声設定が見つかりません。再度選択してください」 |
| `voice_profile_project_mismatch` | 「選択した音声設定はこのプロジェクトのものではありません」 |
| `voice_profile_not_approved` | 「この音声設定はまだ承認されていません。Project画面で承認してください」 |
| `voice_profile_archived` | 「この音声設定はアーカイブ済みのため使用できません」 |
| `voice_profile_invalid`(作成/編集modal内) | 「入力内容を確認してください」+具体的な項目名 |
| `conflict`(name重複、作成/編集modal内) | 「同じ名前の音声設定が既にあります」 |
| `approval_gate_not_satisfied`(既存) | 既存どおり「承認画面へ」の導線を表示(変更なし) |

## 14. IPC利用関係

```text
voice:list-engines
  → 用途を「VoiceProfile作成・編集modal内での、speaker/style候補取得」に限定する。
    Build Settings画面自体からは呼ばなくなる(現行は画面ロード時に呼んでいる)。

voice-profile:list
  → Project Workspaceの音声設定sectionでは全status(draft/approved/archived)を
    表示するために使う。
  → Build Settingsでは、取得結果をapprovedのみへ絞り込んで選択肢とする
    (絞り込みをRenderer側で行うか、IPC呼び出し時にstatusフィルタ引数を
    渡すかはUI実装時の判断事項とし、本書では確定しない)。

voice-profile:create / voice-profile:update / voice-profile:archive
  → Project Workspaceの音声設定section(一覧・modal)からのみ呼ぶ。
    Build Settingsからは呼ばない。

build-request:create
  → 既存の`voiceProfileId`パラメータの意味を、「生のspeaker_id」から
    「実際のvoice_profiles.voice_profile_id」へ修正する
    (2節で述べた現行コードの不整合の是正)。

job:start
  → 変更なし(既存どおり)。
```

`voice:list-engines`(VOICEVOX engine自体のspeaker/style列挙)と
`voice-profile:*`(Project単位のVoiceProfile CRUD)は、本書を通じて
一貫して別concept・別用途として扱う(混同しないこと)。

## 15. 既存仕様への影響

- `docs/screens/03-build-settings.md`(v1.1、承認済み): 4節(入力項目)・
  6節(IPC)・8節(validation)の改訂が必要になる見込み(承認後に実施)。
  現時点では未変更。
- `docs/screens/02-project-workspace-and-source-import.md`(v1.1、承認済み):
  3節(表示項目)・5節(操作)・6節(IPC)への「音声設定section」追記が
  必要になる見込み(承認後に実施)。現時点では未変更。
- `docs/screens/README.md`(7節、5画面方針): 本提案は第6画面を追加しない
  構成を推奨しているため、7節の制限とは矛盾しない。
- `docs/specifications/09-voice-profile-schema.md`(YAML時代のVoiceProfile
  schema、承認済み): 本提案が扱う新しいDB正本モデルとは別concept
  (`docs/db/06-voice-profiles-table.md`で既に明記済み)であり、本提案は
  この仕様を変更しない。
- `docs/specifications/10-tts-client-common-interface.md`: 変更不要
  (`voice:list-engines`の実装自体は変更しない)。

## 16. 実装対象候補(MVP、承認後)

- Project Workspaceへの「音声設定」section追加(一覧・新規作成・編集・
  承認・archiveのmodal込み)。
- Build SettingsのVoiceProfile選択dropdownへの置き換え(speaker/style直接
  選択・speedスライダーの削除)。
- `build-request:create`呼び出し時の`voiceProfileId`修正(2節の不整合是正)。
- 13節のエラーコード→表示メッセージのmapping実装。
- 対応するRenderer test(`BuildSettings.test.ts`の更新、Project Workspace側の
  新規test)。

## 17. 実装対象外(MVP、承認後も対象外)

- Profile複製機能。
- 章・segment単位でのVoiceProfile上書き(既存`03-build-settings.md` 13節の
  MVP対象外方針を維持)。
- Profile使用履歴の画面表示(どのBuildがどのsnapshot/hashを使ったかは
  manifestに記録済みだが、UI表示はMVP対象外)。
- COEIROINK関連の表示(既存どおりMVP対象外、`TASK-COEIR-001`は無関係のまま)。

## 18. 人間判断事項

1. VoiceProfile管理をどこに置くか(9節の推奨: Project Workspace内section。
   案A/B/Cのいずれか、または別案)。
2. 新しい第6画面を許可するか(9節の推奨: 許可せず、既存02画面へ統合)。
3. approved Profile編集後に再承認を必要とするか(10節の3択のいずれか)。
4. Profile複製機能をMVPへ含めるか(17節の推奨: 対象外)。
5. Build Settingsから新規作成できるようにするか(9節の推奨: できなくし、
   Project Workspaceへの導線リンクのみ提供)。
6. 旧speaker/style直接選択UIを削除するか(9節の推奨: 削除し、VoiceProfile
   選択へ一本化)。
7. Profile未作成時にBuildを完全に禁止するか(9節の推奨: text-onlyは許可、
   mp3のみ禁止)。
8. text-only時にVoiceProfile欄を非表示にするか、disabled表示にするか
   (12節: 現行のspeaker-select disabled化を踏襲する案を挙げたが未確定)。
9. （追加提起）archived専用Profileしか存在しない場合の文言を、「draftのみ」の
   場合と区別して表示するか(12節)。
10. （追加提起）draft→approvedの承認操作に、既存の4段階承認ワークフロー
    (`07-approval-workflow.md`)のような差し戻し・コメント機能を持たせるか、
    単純なボタン操作のみとするか。

## 19. 承認欄

```text
承認者:
承認日:
承認範囲: 9節の推奨案(Project Workspace統合 + modal)を採用するか、
          または18節の人間判断事項の回答を踏まえた別案を採用するか。
コメント:
```
