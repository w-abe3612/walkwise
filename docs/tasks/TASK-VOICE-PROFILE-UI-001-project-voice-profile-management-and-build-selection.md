---
document_type: implementation_task
task_id: TASK-VOICE-PROFILE-UI-001
status: complete
release_scope: release-readiness
priority: P0
created_at: "2026-07-22"
approved_design: docs/spec-proposals/build-settings-voice-profile-ui.md(2026-07-22承認)
depends_on:
  - TASK-BUILD-EXEC-001
related_existing_tasks:
  - TASK-UI-002
  - TASK-UI-003
  - TASK-UI-005
completed_at: "2026-07-22"
---

# TASK-VOICE-PROFILE-UI-001: Project VoiceProfile管理とBuild選択

## 1. 背景

`TASK-BUILD-EXEC-001`で、Project単位のVoiceProfile(SQLite正本)のbackend
一式(migration、Repository、Service、Worker command、Electron adapter/IPC/
preload)が実装・テスト済みになった。しかし、Rendererには次の問題が残っていた。

- Project画面からVoiceProfileを作成・編集・承認・archiveできない。
- Build Settings画面が保存済みVoiceProfileを選択しておらず、旧来のVOICEVOX
  speaker/style直接選択のままだった。
- 旧`BuildSettings.vue`の`submitBuild()`が、生の`speaker_id`を
  `voiceProfileId`としてそのまま`build-request:create`へ送信していた
  (`voice_profiles.voice_profile_id`とは型・出自が異なる別の識別子)。

この不整合により、現行UIのままでは新backend上でmp3 Buildが実行不能だった。

## 2. 人間承認内容

`docs/spec-proposals/build-settings-voice-profile-ui.md`(2026-07-22承認)に
基づき、次を承認済み方針として実装した。

| 項目 | 承認内容 |
|---|---|
| VoiceProfile管理場所 | Project Workspace画面 |
| 第6画面追加 | 追加しない |
| 承認済みProfile編集 | 編集後もapprovedを維持する |
| Build画面から新規作成 | できない(Project Workspace側でのみ作成) |
| 旧speaker/style直接選択UI | 削除する |
| VoiceProfile未作成時 | text-only Buildは許可、mp3 Buildは禁止 |
| text-only時 | VoiceProfile欄をdisabledのグレー表示にする(非表示にはしない) |
| Profile複製 | MVPでは実装しない |

## 3. 実装対象

1. Project WorkspaceへのVoiceProfile管理section追加(第6画面ではなく既存
   `02-project-workspace-and-source-import.md`画面への統合)
2. VoiceProfile作成modal(role="dialog"、aria-modal、Escape close、
   focus trap、初期focus)
3. VoiceProfile編集modal(archivedは編集不可)
4. draftからapprovedへの変更操作(二重送信防止)
5. VoiceProfile archive操作(二段階確認、物理削除ではない)
6. Build SettingsのVoiceProfile選択(approvedのみ、draft/archivedは非表示)
7. speaker/style直接選択UIの削除(Build Settings画面から)
8. voiceProfileId payload不整合の修正(生のspeaker_idではなく実際の
   `voice_profile_id`を送信)
9. 空状態・エラー表示(0件/draftのみ/archivedのみ/取得失敗/選択中Profile
   無効化)
10. Renderer test追加・更新
11. 承認済み仕様文書への反映

electron main IPC/adapter層(`electron/main/ipc/voice_profiles.ts`、
`electron/main/worker_service_adapters.ts`)についても、`TASK-BUILD-EXEC-001`
時点で欠落していたpause設定・`settings_json`・(updateのみ)engine/
speaker_id/style_idのフィールド伝搬を、本task内で補完した(Python Worker側
`script/worker/commands.py`は当時から対応済みだった)。

## 4. 実装対象外

- 第6画面
- Build SettingsからのProfile新規作成
- Profile複製
- approved編集後のdraft差し戻し
- approvedからdraftへ戻す操作
- archived解除
- Profile物理削除
- 章単位VoiceProfile、segment単位VoiceProfile
- VoiceProfile使用履歴UI
- 自動既定Profile作成、Profile未作成時の自動fallback、speaker_idからの
  Profile自動生成
- COEIROINK対応、外部runtime接続

## 5. 変更ファイル

- 追加: `electron/renderer/voiceProfileErrors.ts`、
  `docs/spec-proposals/build-settings-voice-profile-ui.md`、
  `electron/tests/voice_profiles_ipc.test.ts`は`TASK-BUILD-EXEC-001`で追加済みのため対象外
- 修正: `electron/renderer/App.vue`、
  `electron/renderer/screens/ProjectWorkspace.vue`/`.types.ts`、
  `electron/renderer/screens/BuildSettings.vue`/`.types.ts`、
  `electron/main/ipc/voice_profiles.ts`、`electron/main/worker_service_adapters.ts`、
  `electron/tests/voice_profiles_ipc.test.ts`、
  `electron/tests/worker_service_adapters.test.ts`、
  `electron/tests/build_voice_ipc.test.ts`、`electron/tests/source_approval_ipc.test.ts`、
  `electron/renderer/tests/BuildSettings.test.ts`、
  `electron/renderer/tests/ProjectWorkspace.test.ts`、
  `electron/renderer/tests/accessibility.test.ts`、
  `electron/renderer/tests/App.test.ts`、
  `docs/screens/02-project-workspace-and-source-import.md`、
  `docs/screens/03-build-settings.md`、`docs/spec-proposals/README.md`、
  `docs/commands/CURRENT_STATE.md`、`docs/notes/implementation_assumptions.md`、
  `docs/notes/progress.md`

## 6. acceptance criteria

- Project WorkspaceでVoiceProfile一覧を表示できる。
- Project WorkspaceでProfileを作成でき、作成直後はdraftになる。
- Profileを編集でき、approved編集後もapprovedのまま維持される。
- Profileをarchiveでき、archivedは編集不可になる。
- Build Settingsでapproved Profileだけ選択でき、speaker/style直接選択が
  削除されている。
- BuildRequestへ実際の`voice_profile_id`を送信し、speaker_idを
  voiceProfileIdとして送らない。
- text-onlyはProfileなしでBuild可能、mp3はapproved Profile必須。
- text-only時はVoiceProfile欄がdisabled表示になる。
- Profile複製・第6画面が存在しない。
- `npm run typecheck`成功、対象Vitest・Vitest全体成功、`npm run build`成功、
  対象Python回帰成功、Markdown link check成功。

## 7. test commands

```powershell
npm run typecheck
npm test -- electron/renderer/tests/ProjectWorkspace.test.ts electron/renderer/tests/BuildSettings.test.ts electron/renderer/tests/accessibility.test.ts electron/renderer/tests/App.test.ts electron/renderer/tests/navigation.test.ts
npm test -- --run
npm run build
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_build_request_service.py tests/test_voice_profile_persistence.py tests/test_worker_commands.py
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
python scripts/check_markdown_links.py
```

## 8. stop conditions(該当なし、実装完了)

次のいずれにも該当しなかった。

- preloadのVoiceProfile APIがRenderer要件を満たしていない
- approvedへのstatus更新APIが存在しない
- VoiceProfile updateでstatusを維持できない
- VoiceProfile schemaの必須項目が仕様文書とコードで矛盾する
- Project WorkspaceがProject IDを安全に取得できない
- BuildRequest型がvoiceProfileId nullを許可しない(既存の`voiceProfileId?: string`
  optional型のまま、未選択時は`undefined`を送る設計で解決した)
- rendererとbackendでvoice_profile_idの型が一致しない
- archived Profileがbackend上で更新可能になっている(既存backendは
  archived更新を`voice_profile_archived`で拒否することを確認済み)
- 既存の未コミット変更と競合する
- 既存テストが承認済み仕様と逆の挙動を正本としている

## 9. 完了報告

実装完了。詳細はセッションの完了報告(会話ログ)、および
`docs/notes/progress.md`のTASK-VOICE-PROFILE-UI-001節を参照。

- 実装: complete
- Python regression: 498 passed, 23 skipped, 3 deselected(Docker daemon
  未起動、環境要因), 10 xfailed(TASK-COEIR-001)、0 failed
- TypeScript/Vitest: typecheck成功、Vitest 128 passed, 3 skipped, 0 failed
- npm build: 成功
- Markdown link check: 0 broken(172 files, 320 links)
- 実GUI目視確認・実VOICEVOX接続: 未確認(この開発環境では引き続き未確認)
- release ready判定: 別軸(未確認項目により「いいえ」のまま)

`TASK-REVIEW-001`・`TASK-COEIR-001`は本task中も無変更のまま維持した。
