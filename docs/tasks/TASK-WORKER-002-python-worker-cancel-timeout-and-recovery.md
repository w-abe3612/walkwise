---
document_type: claude_code_implementation_task
task_id: TASK-WORKER-002
order: 142
title: Python worker cancel・timeout・異常終了復旧
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 5. Workerとデスクトップ
depends_on:
- TASK-WORKER-001
- TASK-JOB-001
contract_ref: docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md
preparation_ref: docs/spec-proposals/task/142_task-worker-002-python-worker-cancel-timeout-and-recovery.md
spec_refs:
- docs/specifications/21-electron-python-worker-interface.md
- docs/specifications/22-job-lifecycle-and-recovery.md
test_files:
- tests/test_worker_cancellation.py
- tests/test_worker_runtime_failures.py
source_files:
- script/worker/cancellation.py
- script/worker/runtime.py
command_documents:
- docs/commands/testing.md
- docs/commands/worker.md
documentation_repair_ownership: []
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-WORKER-002 Python worker cancel・timeout・異常終了復旧


## 1. 目的

cancel要求、graceful終了、強制終了、timeout、途中JSON、stale状態をJob結果へ安全に変換する。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-WORKER-001`
- `TASK-JOB-001`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-WORKER-002-python-worker-cancel-timeout-and-recovery.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/specifications/21-electron-python-worker-interface.md`
- `docs/specifications/22-job-lifecycle-and-recovery.md`

関連コマンド文書:

- `docs/commands/testing.md`
- `docs/commands/worker.md`

## 4. 変更範囲

### テスト

- `tests/test_worker_cancellation.py`
- `tests/test_worker_runtime_failures.py`

### production source

- `script/worker/cancellation.py`
- `script/worker/runtime.py`

### 扱う範囲

- cancel token/signal
- grace period
- force terminate契約
- timeout
- 途中終了
- 一時成果物cleanup
- 既存正常成果物保持
- Job status mapping

### 対象外

- Electron UI
- 並列worker
- OS service化

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. コマンド文書の整合性

関連するコマンド文書を実行し、対象パス・marker・環境変数・実行順序が実装と一致することを確認する。
古い欠落記述を発見した場合は、担当タスクを確認して勝手に重複修正せず、完了報告へ記録する。


## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `script/worker/cancellation.py` | `CancellationToken.requested()/raise_if_cancelled()` | cooperative cancelを提供する。 |
| `script/worker/runtime.py` | `WorkerRuntime.run(request, token) -> Iterator[WorkerEvent]` | timeout、例外、部分成果物cleanupを管理する。 |
| `script/worker/runtime.py` | `recover_after_abnormal_exit(job) -> RecoveryDecision` | 中途半端な出力を正式成果物にせず復旧判断する。 |

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
| TC-WORKER-002-01 | P0 | integration_mock | cooperative cancel | 長処理中にcancel | runtime | cancel_requested→cancelled eventで停止 | `tests/test_worker_cancellation.py` |
| TC-WORKER-002-02 | P0 | integration_mock | timeout | handlerが期限超過 | runtime | timeout errorとcleanupを実行 | `tests/test_worker_runtime_failures.py` |
| TC-WORKER-002-03 | P0 | integration_mock | 異常終了 | 一時file作成後process kill | recover | 正式成果物へ登録せず既存成果物を保持 | `tests/test_worker_cancellation.py` |
| TC-WORKER-002-04 | P1 | unit | grace period | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CancellationToken.requested()/raise_if_cancelled()`を通じて「grace period」を実行する | 「grace period」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_worker_runtime_failures.py` |
| TC-WORKER-002-05 | P1 | unit | force terminate契約 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CancellationToken.requested()/raise_if_cancelled()`を通じて「force terminate契約」を実行する | 「force terminate契約」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_worker_cancellation.py` |
| TC-WORKER-002-06 | P1 | unit | 途中終了 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CancellationToken.requested()/raise_if_cancelled()`を通じて「途中終了」を実行する | 「途中終了」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_worker_runtime_failures.py` |
| TC-WORKER-002-07 | P1 | unit | 既存正常成果物保持 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CancellationToken.requested()/raise_if_cancelled()`を通じて「既存正常成果物保持」を実行する | 「既存正常成果物保持」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_worker_cancellation.py` |
| TC-WORKER-002-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `CancellationToken.requested()/raise_if_cancelled()`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_worker_runtime_failures.py` |
| TC-WORKER-002-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `CancellationToken.requested()/raise_if_cancelled()`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_worker_cancellation.py` |
| TC-WORKER-002-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_worker_runtime_failures.py` |

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
python -m pytest --collect-only -q tests/test_worker_cancellation.py tests/test_worker_runtime_failures.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_worker_cancellation.py tests/test_worker_runtime_failures.py
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
