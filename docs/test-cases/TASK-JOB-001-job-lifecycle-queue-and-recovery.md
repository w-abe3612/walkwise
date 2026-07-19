---
test_case_contract_id: CONTRACT-TASK-JOB-001
implementation_task_id: TASK-JOB-001
title: Job状態遷移・FIFO・再試行・stale復旧
status: review
version: '1.0'
release_scope: MVP
phase: 1. 永続化と業務サービス
depends_on:
- TASK-BUILD-001
- TASK-DB-002
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
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-JOB-001 Job状態遷移・FIFO・再試行・stale復旧 — タスク契約書・テストケース
## 1. 目的
同時実行1件のFIFO queue、合法な状態遷移、cancel要求、再試行、stale Job復旧を提供する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- 状態遷移表
- queue順序
- parent_job_id再試行
- approval gate hook
- 起動時stale検出
- progress更新
- finished_at規則

## 4. 対象外
- Python subprocess制御
- UI購読
- 並列実行

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/domain/job_state.py` | `can_transition(current: JobStatus, target: JobStatus) -> bool` | 状態遷移表を純粋関数で判定する。 |
| `script/services/jobs.py` | `JobService.enqueue(...) -> Job` | approval gate確認後FIFO末尾へqueued Jobを追加する。 |
| `script/services/jobs.py` | `JobService.start_next() -> Job | None` | runningがない場合だけ最古queuedをrunningへする。 |
| `script/services/jobs.py` | `JobService.request_cancel/retry/recover_stale` | 取消、親参照付き再試行、起動時stale失敗化を行う。 |

### 5.1 共通規則
- 公開関数・methodは型注釈を持つ。
- 業務上予測可能な失敗は安定したerror codeへ変換する。
- 入力正本を直接変更しない。既存正常成果物を失敗時に削除・上書きしない。
- 外部依存、時計、乱数、filesystem、DBはテストで注入または隔離可能にする。
- 本書にない公開symbolを安易に追加しない。内部helperは非公開とする。

## 6. テスト層と実行方針
| layer | 外部接続 | 目的 |
|---|---:|---|
| `unit` | なし | 純粋処理、validation、状態遷移、error変換 |
| `integration_mock` | なし | DB、filesystem、HTTP/subprocess/IPCをfixtureまたはmockで結合 |
| `integration_smoke` | 明示opt-in | 軽量な疎通確認だけを行う |
| `integration_live` | 明示opt-in | 疎通成功後だけ最小の実機能を検証する |
| `e2e` | 原則mock | UI/worker/DB/fileを含む利用者導線 |
| `performance` / `resilience` | 専用実行 | 性能・障害注入。通常pytestから除外 |

通常の`pytest`は外部API、VOICEVOX、COEIROINK、Tesseract、ffmpeg、ASR modelへ接続しない。

## 7. 外部疎通ゲート
このタスクの通常受入は外部API疎通を必要としない。外部依存を間接利用する場合も、当該adapterタスクの疎通fixtureを再利用し、本タスク独自の無秩序な実接続を追加しない。

## 8. fixture契約
- `tmp_path`配下だけを使用する一時Project/data root
- 固定timezone付きclock
- 決定的ID generator
- 秘密値を含まない設定fixture
- 成功・validation error・timeout・破損応答を返す依存stub/mock

## 9. テストケース
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

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_job_lifecycle.py`
- `tests/test_job_queue.py`
- `tests/test_stale_job_recovery.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `script/services/jobs.py`
- `script/domain/job_state.py`

公開symbolは5節と一致させ、未実装本体は型付きの`NotImplementedError`または言語相当の明示的未実装errorを返す。import、構文、pytest/test collectionを壊す未定義参照を残さない。

## 12. 変更許可範囲
- STEP2: 本書と`docs/test-cases/INDEX.md`、共通policy文書のみ。
- STEP3: 10節のtest fileと共通fixture設定のみ。
- STEP4: 11節のsource fileと必要なpackage `__init__`のみ。
- 承認済み仕様、DB、画面仕様の意味変更は別の仕様変更として扱う。

## 13. 完了条件
- 公開契約、正常系、異常系、境界値、入力不変、再実行時挙動がテスト可能である。
- すべてのcase IDが一意で、予定test fileへ割り当てられている。
- 外部実機能テストは、該当する場合、疎通確認fixtureを必須依存している。
- 通常pytestが外部接続や有料APIを呼ばない。
- post-MVP/blockedの範囲がMVPへ混入していない。
