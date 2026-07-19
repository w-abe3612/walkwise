---
document_type: claude_code_implementation_task
task_id: TASK-DESKTOP-003
order: 150
title: Desktop最短end-to-end導線
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 5. Workerとデスクトップ
depends_on:
- TASK-UI-005
- TASK-WORKER-002
- TASK-AUDIO-003
contract_ref: docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md
preparation_ref: docs/spec-proposals/task/150_task-desktop-003-desktop-end-to-end-integration.md
spec_refs:
- docs/specifications/19-application-scope-and-mvp.md
- docs/specifications/audiobook-creation-pipeline.md
test_files:
- tests/integration/test_mvp_flow.py
- electron/tests/e2e/mvp-flow.test.ts
source_files:
- electron/tests/e2e/mvp-flow.test.ts
- script/integration/mvp_flow.py
command_documents:
- docs/commands/end-to-end.md
- docs/commands/testing.md
documentation_repair_ownership:
- docs/commands/end-to-end.md
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-DESKTOP-003 Desktop最短end-to-end導線


## 1. 目的

Project作成からtext登録、承認、VOICEVOX試聴、章MP3/text成果物表示までをデスクトップ上で通す。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-UI-005`
- `TASK-WORKER-002`
- `TASK-AUDIO-003`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/specifications/19-application-scope-and-mvp.md`
- `docs/specifications/audiobook-creation-pipeline.md`

関連コマンド文書:

- `docs/commands/end-to-end.md`
- `docs/commands/testing.md`

## 4. 変更範囲

### テスト

- `tests/integration/test_mvp_flow.py`
- `electron/tests/e2e/mvp-flow.test.ts`

### production source

- `electron/tests/e2e/mvp-flow.test.ts`
- `script/integration/mvp_flow.py`

### 扱う範囲

- 実IPC/DB/file/worker統合
- 正常導線
- 承認gate拒否
- worker失敗/retry
- 再起動後永続化
- 複数artifact
- 原本不変
- fixture VOICEVOX mock mode

### 対象外

- post-MVP機能
- 性能試験
- installer

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. 古い記述の修正責任

このタスクは、実装と同時に次の古い状態記述を修正する責任を持つ。

- `docs/commands/end-to-end.md`

修正方針:

1. 対象ファイル一覧の`— 現在のダンプでは欠落`および`— 存在`のような揮発性注記を削除する。
2. 個別コマンド文書はパスと実行方法を正本とし、存在状態は`CURRENT_STATE.md`へ集約する。
3. 「19件存在・90件欠落・22件収集・17 xfailed / 5 skipped」など、現在と矛盾する記述を残さない。
4. 実測せずにpass件数やNode検査結果を創作しない。
5. 修正後、`rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands`を実行し、
   意図的な履歴説明以外に古い状態が残っていないことを確認する。



## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `script/integration/mvp_flow.py` | `run_mvp_flow(dependencies) -> MvpFlowResult` | Project作成からArtifactまでの縦切りをmock依存で実行する。 |
| `electron/tests/e2e/mvp-flow.test.ts` | `desktop flow` | 起動、Project、Source、承認、Build、Job、Artifactを画面経由で確認する。 |

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
| TC-DESKTOP-003-01 | P0 | e2e | 最短導線 | mock AI/TTSと空data | E2Eを実行 | Project→text Source→承認→text Artifactまで完了 | `tests/integration/test_mvp_flow.py` |
| TC-DESKTOP-003-02 | P0 | e2e | mp3導線 | mock VOICEVOX | E2E | preview承認後に章MP3を一覧表示 | `electron/tests/e2e/mvp-flow.test.ts` |
| TC-DESKTOP-003-03 | P0 | e2e | 再起動保持 | Project作成後アプリ再起動 | 一覧 | 同じProject/Job/Artifactを表示 | `tests/integration/test_mvp_flow.py` |
| TC-DESKTOP-003-04 | P1 | integration_mock | 実IPC/DB/file/worker統合 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「実IPC/DB/file/worker統合」を実行する | 「実IPC/DB/file/worker統合」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/tests/e2e/mvp-flow.test.ts` |
| TC-DESKTOP-003-05 | P1 | unit | 正常導線 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「正常導線」を実行する | 「正常導線」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/integration/test_mvp_flow.py` |
| TC-DESKTOP-003-06 | P1 | unit | worker失敗/retry | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「worker失敗/retry」を実行する | 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。 | `electron/tests/e2e/mvp-flow.test.ts` |
| TC-DESKTOP-003-07 | P1 | unit | 再起動後永続化 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `run_mvp_flow(dependencies) -> MvpFlowResult`を通じて「再起動後永続化」を実行する | 「再起動後永続化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/integration/test_mvp_flow.py` |
| TC-DESKTOP-003-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `run_mvp_flow(dependencies) -> MvpFlowResult`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `electron/tests/e2e/mvp-flow.test.ts` |
| TC-DESKTOP-003-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `run_mvp_flow(dependencies) -> MvpFlowResult`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/integration/test_mvp_flow.py` |
| TC-DESKTOP-003-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `electron/tests/e2e/mvp-flow.test.ts` |
| TC-DESKTOP-003-11 | P0 | integration_smoke | Desktop統合runtimeの疎通確認 | 実接続テストが明示的に有効化され、必要な設定が存在する | アプリ起動、preload API公開、DB/worker healthまでを確認し、作品生成は行わない。 | ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。 | `tests/integration/test_mvp_flow.py` |
| TC-DESKTOP-003-12 | P1 | e2e | Desktop統合runtimeの実機能テスト | `desktop_connectivity_gate`が成功済み | 疎通成功後、mock AI/TTSで最短MVP導線を最後まで実行する。 | 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。 | `electron/tests/e2e/mvp-flow.test.ts` |

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
python -m pytest --collect-only -q tests/integration/test_mvp_flow.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/integration/test_mvp_flow.py
```

### Vitest対象テスト

```powershell
npm test -- electron/tests/e2e/mvp-flow.test.ts
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


## 10. 外部疎通・実機能テスト

このタスクは外部接続gate対象である。通常テストで外部接続してはならない。

必須順序:

```text
設定確認
↓
integration_smoke
↓ 成功時のみ
integration_live
```

契約:

- 対象: **Desktop統合runtime**
- 必須fixture: `desktop_connectivity_gate`
- 設定: 追加の秘密環境変数なし
- 疎通確認: アプリ起動、preload API公開、DB/worker healthまでを確認し、作品生成は行わない。
- 実機能確認: 疎通成功後、mock AI/TTSで最短MVP導線を最後まで実行する。
- 実機能テストは疎通fixtureを引数として必須要求する。
- 設定不足時はnetworkへ出ず、秘密値を表示せず明示的にskipする。
- 疎通失敗時は疎通テストをfailとし、その実行に属する実機能テストは理由付きskipとする。
- 疎通確認で生成物、DB更新、課金の大きい処理を行わない。避けられない最小課金は明記する。

- smoke失敗時はliveを実行しない。
- live testは対応するconnectivity fixtureを必須引数にする。
- 秘密値をログ・例外・pytest reportへ出さない。
- 固定・短時間・最小回数の入力だけを使用する。


## 11. 完了条件

- case ID 12件がすべて実テストになり、対象テストがpassする。
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
