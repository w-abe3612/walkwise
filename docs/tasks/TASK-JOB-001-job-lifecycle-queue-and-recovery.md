---
document_type: claude_code_implementation_task
task_id: TASK-JOB-001
order: 113
title: Job状態遷移・FIFO・再試行・stale復旧
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 1. 永続化と業務サービス
depends_on:
- TASK-BUILD-001
- TASK-DB-002
contract_ref: docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md
preparation_ref: docs/spec-proposals/task/113_task-job-001-job-lifecycle-queue-and-recovery.md
spec_refs:
- docs/specifications/22-job-lifecycle-and-recovery.md
- docs/db/04-jobs-table.md
test_files:
- tests/test_job_lifecycle.py
- tests/test_job_queue.py
- tests/test_stale_job_recovery.py
source_files:
- script/services/jobs.py
- script/domain/job_state.py
command_documents:
- docs/commands/jobs.md
- docs/commands/testing.md
documentation_repair_ownership:
- docs/commands/jobs.md
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-JOB-001 Job状態遷移・FIFO・再試行・stale復旧


## 1. 目的

同時実行1件のFIFO queue、合法な状態遷移、cancel要求、再試行、stale Job復旧を提供する。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-BUILD-001`
- `TASK-DB-002`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-JOB-001-job-lifecycle-queue-and-recovery.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/specifications/22-job-lifecycle-and-recovery.md`
- `docs/db/04-jobs-table.md`

関連コマンド文書:

- `docs/commands/jobs.md`
- `docs/commands/testing.md`

## 4. 変更範囲

### テスト

- `tests/test_job_lifecycle.py`
- `tests/test_job_queue.py`
- `tests/test_stale_job_recovery.py`

### production source

- `script/services/jobs.py`
- `script/domain/job_state.py`

### 扱う範囲

- 状態遷移表
- queue順序
- parent_job_id再試行
- approval gate hook
- 起動時stale検出
- progress更新
- finished_at規則

### 対象外

- Python subprocess制御
- UI購読
- 並列実行

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. 古い記述の修正責任

このタスクは、実装と同時に次の古い状態記述を修正する責任を持つ。

- `docs/commands/jobs.md`

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
| `script/domain/job_state.py` | `can_transition(current: JobStatus, target: JobStatus) -> bool` | 状態遷移表を純粋関数で判定する。 |
| `script/services/jobs.py` | `JobService.enqueue(...) -> Job` | approval gate確認後FIFO末尾へqueued Jobを追加する。 |
| `script/services/jobs.py` | `JobService.start_next() -> Job | None` | runningがない場合だけ最古queuedをrunningへする。 |
| `script/services/jobs.py` | `JobService.request_cancel/retry/recover_stale` | 取消、親参照付き再試行、起動時stale失敗化を行う。 |

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
| TC-JOB-001-01 | P0 | integration_mock | FIFO | queued Jobが3件 | start_nextを繰り返す | created/enqueued順で1件ずつrunningになる | `tests/test_job_lifecycle.py` |
| TC-JOB-001-02 | P0 | unit | 不正遷移 | cancelled Job | runningへ遷移 | 拒否し状態を維持する | `tests/test_job_queue.py` |
| TC-JOB-001-03 | P0 | integration_mock | stale復旧 | 起動前からrunningのJob | recover_staleする | failedと異常終了messageへ更新する | `tests/test_stale_job_recovery.py` |
| TC-JOB-001-04 | P1 | unit | 状態遷移表 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「状態遷移表」を実行する | 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。 | `tests/test_job_lifecycle.py` |
| TC-JOB-001-05 | P1 | unit | parent_job_id再試行 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「parent_job_id再試行」を実行する | 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。 | `tests/test_job_queue.py` |
| TC-JOB-001-06 | P1 | unit | approval gate hook | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「approval gate hook」を実行する | 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。 | `tests/test_stale_job_recovery.py` |
| TC-JOB-001-07 | P1 | unit | finished_at規則 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `can_transition(current: JobStatus, target: JobStatus) -> bool`を通じて「finished_at規則」を実行する | 「finished_at規則」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_job_lifecycle.py` |
| TC-JOB-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `can_transition(current: JobStatus, target: JobStatus) -> bool`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_job_queue.py` |
| TC-JOB-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `can_transition(current: JobStatus, target: JobStatus) -> bool`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_stale_job_recovery.py` |
| TC-JOB-001-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_job_lifecycle.py` |

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
python -m pytest --collect-only -q tests/test_job_lifecycle.py tests/test_job_queue.py tests/test_stale_job_recovery.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_job_lifecycle.py tests/test_job_queue.py tests/test_stale_job_recovery.py
```

### Vitest対象テスト

```powershell
# Vitest対象なし
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

- case ID 10件がすべて実テストになり、対象テストがpassする。
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
