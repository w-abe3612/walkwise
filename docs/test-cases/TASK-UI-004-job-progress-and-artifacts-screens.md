---
test_case_contract_id: CONTRACT-TASK-UI-004
implementation_task_id: TASK-UI-004
title: Job進捗・cancel/retry・成果物画面
status: review
version: '1.0'
release_scope: MVP
phase: 5. Workerとデスクトップ
depends_on:
- TASK-DESKTOP-002
- TASK-JOB-001
- TASK-ARTIFACT-001
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
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-UI-004 Job進捗・cancel/retry・成果物画面 — タスク契約書・テストケース
## 1. 目的
Job購読、進捗、cancel確認、失敗再試行、Artifact一覧、保存先folder openを実装する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- job:get/subscribe/cancel/start retry
- 状態別button
- stale注記
- 技術detail折畳み
- artifact:list
- latest version既定
- open folder
- 再生成導線

## 4. 対象外
- Artifact削除
- OS通知
- 過去version差分

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `electron/main/ipc/jobs.ts` | `job:get/subscribe/cancel/retry handlers` | 合法状態だけを操作し進捗eventを購読配信する。 |
| `electron/main/ipc/artifacts.ts` | `artifact:list/open-folder handlers` | 相対pathを検証してOSへ委譲する。 |
| `electron/renderer/screens/JobsAndArtifacts.vue` | `jobs/artifacts UI` | 進捗、stale注記、cancel確認、retry、最新成果物を表示する。 |

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
| TC-UI-004-01 | P0 | unit | cancel確認 | running Job | cancel click | 確認後だけIPCを呼ぶ | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-02 | P0 | unit | retry条件 | failed/cancelled/other | render | 前2つだけretry可能 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-03 | P0 | unit | 最新Artifact | 複数version | render | 最新を既定表示し旧versionを破壊しない | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-04 | P1 | unit | job:get/subscribe/cancel/start retry | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「job:get/subscribe/cancel/start retry」を実行する | 再試行可能errorだけを上限回数内で再試行し、同一requestの成果物を重複登録しない。 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-05 | P1 | unit | 状態別button | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「状態別button」を実行する | 承認済み状態遷移表にある遷移だけが成功し、不正遷移では永続状態を変更しない。 | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-06 | P1 | unit | stale注記 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「stale注記」を実行する | 「stale注記」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-07 | P1 | unit | 技術detail折畳み | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `job:get/subscribe/cancel/retry handlers`を通じて「技術detail折畳み」を実行する | 「技術detail折畳み」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/tests/job_artifact_ipc.test.ts` |
| TC-UI-004-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `job:get/subscribe/cancel/retry handlers`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `electron/renderer/tests/JobsAndArtifacts.test.ts` |
| TC-UI-004-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `job:get/subscribe/cancel/retry handlers`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `electron/tests/job_artifact_ipc.test.ts` |

## 10. STEP3テスト空実装への引継ぎ
- `electron/tests/job_artifact_ipc.test.ts`
- `electron/renderer/tests/JobsAndArtifacts.test.ts`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `electron/main/ipc/jobs.ts`
- `electron/main/ipc/artifacts.ts`
- `electron/renderer/screens/JobsAndArtifacts.vue`

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
