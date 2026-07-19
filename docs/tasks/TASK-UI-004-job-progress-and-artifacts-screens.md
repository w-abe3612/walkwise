---
document_type: claude_code_implementation_task
task_id: TASK-UI-004
order: 148
title: Job進捗・cancel/retry・成果物画面
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 5. Workerとデスクトップ
depends_on:
- TASK-DESKTOP-002
- TASK-JOB-001
- TASK-ARTIFACT-001
contract_ref: docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md
preparation_ref: docs/spec-proposals/task/148_task-ui-004-job-progress-and-artifacts-screens.md
spec_refs:
- docs/screens/04-job-progress.md
- docs/screens/05-artifacts.md
test_files:
- electron/tests/job_artifact_ipc.test.ts
- electron/renderer/tests/JobsAndArtifacts.test.ts
source_files:
- electron/main/ipc/jobs.ts
- electron/main/ipc/artifacts.ts
- electron/renderer/screens/JobsAndArtifacts.vue
command_documents:
- docs/commands/testing.md
- docs/commands/ui.md
documentation_repair_ownership: []
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-UI-004 Job進捗・cancel/retry・成果物画面


## 1. 目的

Job購読、進捗、cancel確認、失敗再試行、Artifact一覧、保存先folder openを実装する。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-DESKTOP-002`
- `TASK-JOB-001`
- `TASK-ARTIFACT-001`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-UI-004-job-progress-and-artifacts-screens.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/screens/04-job-progress.md`
- `docs/screens/05-artifacts.md`

関連コマンド文書:

- `docs/commands/testing.md`
- `docs/commands/ui.md`

## 4. 変更範囲

### テスト

- `electron/tests/job_artifact_ipc.test.ts`
- `electron/renderer/tests/JobsAndArtifacts.test.ts`

### production source

- `electron/main/ipc/jobs.ts`
- `electron/main/ipc/artifacts.ts`
- `electron/renderer/screens/JobsAndArtifacts.vue`

### 扱う範囲

- job:get/subscribe/cancel/start retry
- 状態別button
- stale注記
- 技術detail折畳み
- artifact:list
- latest version既定
- open folder
- 再生成導線

### 対象外

- Artifact削除
- OS通知
- 過去version差分

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. コマンド文書の整合性

関連するコマンド文書を実行し、対象パス・marker・環境変数・実行順序が実装と一致することを確認する。
古い欠落記述を発見した場合は、担当タスクを確認して勝手に重複修正せず、完了報告へ記録する。


## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `electron/main/ipc/jobs.ts` | `job:get/subscribe/cancel/retry handlers` | 合法状態だけを操作し進捗eventを購読配信する。 |
| `electron/main/ipc/artifacts.ts` | `artifact:list/open-folder handlers` | 相対pathを検証してOSへ委譲する。 |
| `electron/renderer/screens/JobsAndArtifacts.vue` | `jobs/artifacts UI` | 進捗、stale注記、cancel確認、retry、最新成果物を表示する。 |

### 共通規則
- 公開関数・methodは型注釈を持つ。
- 業務上予測可能な失敗は安定したerror codeへ変換する。
- 入力正本を直接変更しない。既存正常成果物を失敗時に削除・上書きしない。
- 外部依存、時計、乱数、filesystem、DBはテストで注入または隔離可能にする。
- 本書にない公開symbolを安易に追加しない。内部helperは非公開とする。

## 7. テストケース

本タスクでは次のcase IDをすべて本実装する。

| ID | 優先 | layer | テスト内容 | Given | When | Then | 実装先 |
|---|---|---|---|---|---|---|---|
| TC-UI-004-01 | P0 | unit | cancel確認 | running Job | cancel click | 確認後だけIPCを呼ぶ | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-02 | P0 | unit | retry条件 | failed/cancelled/other | render | 前2つだけretry可能 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-03 | P0 | unit | 最新Artifact | 複数version | render | 最新を既定表示し旧versionを破壊しない | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-04 | P1 | unit | job:get/subscribe/cancel/start retry | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「job:get/subscribe/cancel/start retry」を実行する | 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-05 | P1 | unit | 状態別button | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「状態別button」を実行する | 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。 | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-06 | P1 | unit | stale注記 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「stale注記」を実行する | 「stale注記」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-07 | P1 | unit | 技術detail折畳み | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「技術detail折畳み」を実行する | 「技術detail折畳み」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `job:get/subscribe/cancel/retry handlers`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `job:get/subscribe/cancel/retry handlers`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `electron/tests/job_artifact_ipc.test.ts` |

実装規則:

- Pythonは対象caseの`xfail(strict=True)`と明示的`pytest.fail`を、実際のassertionへ置き換える。
- Vitestは対象caseの`test.fails`と明示的errorを、実際の検証へ置き換える。
- case ID、Given、When、Thenを削除しない。
- 先にテストを本実装し、productionが未実装であることによるRedを確認する。
- import error、構文error、fixture欠落だけをRed確認として扱わない。
- mock対象と実接続対象を混同しない。
- 既存成果物・入力の不変性、再実行時の決定性、失敗時の部分成果物を検証する。

## 8. 実装手順

1. `git status --short`と`git diff --stat`で開始状態を記録する。
2. `docs/commands/preflight.md`を実行し、予定test fileが`109/109`存在することを確認する。
3. 正本、ソース空実装、テスト空実装を読み、公開signatureとcase IDを照合する。
4. このタスクのテストだけを本実装する。
5. 対象テストを実行し、production未実装に起因するRedを確認して記録する。
6. このタスクのsourceだけを本実装する。
7. 対象テストを再実行して成功させる。
8. 関連コマンド文書の手順を実行する。
9. 全Python回帰、TypeScript型検査、Vitest回帰を実行する。
10. 担当する古い記述を修正し、文書と実状態を一致させる。
11. 差分を確認し、完了報告を作成する。

## 9. 対象コマンド

### Python collection

```powershell
# Python対象なし
```

### 外部接続なしのPython対象テスト

```powershell
# Python対象なし
```

### Vitest対象テスト

```powershell
npm test -- electron/tests/job_artifact_ipc.test.ts electron/renderer/tests/JobsAndArtifacts.test.ts
```

### 全体回帰

```powershell
python -m compileall -q script tests
python -m pytest --collect-only -q
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
npm run typecheck
npm test
```

Node依存が未導入で`package-lock.json`がない場合は、`docs/commands/environment.md`の初回固定手順に従う。
依存導入ができない環境では成功を装わず、未実行理由を報告する。


## 10. 外部接続

このタスク単独の外部接続は不要である。HTTP、音声engine、OCR、ffmpeg、ASRなどを間接利用する場合も、
対応adapterのmockまたは既存connectivity gateを使用し、独自の実接続経路を追加しない。


## 11. 完了条件

- case ID 9件がすべて実テストになり、対象テストがpassする。
- 対象sourceに、このタスク由来の`NotImplementedError`・明示的未実装errorが残らない。
- 対象外タスクのxfailやblocked状態を解除していない。
- 通常テストが外部API・外部runtimeへ接続しない。
- 外部gate対象の場合、smoke成功記録なしにliveを実行していない。
- Python全体、TypeScript型検査、Vitest全体の結果を報告している。
- 担当コマンド文書が実装と一致し、古い欠落記述を残していない。
- 入力正本と既存正常成果物を破壊していない。

## 12. 停止条件

次の場合は実装を推測で続行せず、`blocked`として報告する。

- 上位仕様と公開signatureが矛盾する。
- 必須fixture・runtime・公式情報が不足する。
- 依存タスクが未完了で、公開境界を確定できない。
- 権利・license・credit条件が不明な外部engineを有効化する必要がある。
- 実データ、秘密値、利用者Projectをテストへ使う必要が生じる。
- 本タスクの変更許可範囲を超える仕様変更が必要になる。

## 13. Claude Code完了報告

```text
タスクID:
開始時Git状態:
変更ファイル:
実装したcase ID:
Red確認コマンドと原因:
対象テスト結果:
全体pytest結果:
TypeScript型検査結果:
Vitest結果:
外部疎通実行の有無:
smoke結果:
live結果:
修正した古い文書記述:
未実行項目と理由:
残課題:
```
