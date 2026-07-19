---
test_case_contract_id: CONTRACT-TASK-DESKTOP-003
implementation_task_id: TASK-DESKTOP-003
title: Desktop最短end-to-end導線
status: review
version: '1.0'
release_scope: MVP
phase: 5. Workerとデスクトップ
depends_on:
- TASK-UI-005
- TASK-WORKER-002
- TASK-AUDIO-003
spec_refs:
- docs/specifications/19-application-scope-and-mvp.md
- docs/specifications/audiobook-creation-pipeline.md
test_files:
- tests/integration/test_mvp_flow.py
- electron/tests/e2e/mvp-flow.test.ts
source_files:
- electron/tests/e2e/mvp-flow.test.ts
- script/integration/mvp_flow.py
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-DESKTOP-003 Desktop最短end-to-end導線 — タスク契約書・テストケース
## 1. 目的
Project作成からtext登録、承認、VOICEVOX試聴、章MP3/text成果物表示までをデスクトップ上で通す。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- 実IPC/DB/file/worker統合
- 正常導線
- 承認gate拒否
- worker失敗/retry
- 再起動後永続化
- 複数artifact
- 原本不変
- fixture VOICEVOX mock mode

## 4. 対象外
- post-MVP機能
- 性能試験
- installer

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/integration/mvp_flow.py` | `run_mvp_flow(dependencies) -> MvpFlowResult` | Project作成からArtifactまでの縦切りをmock依存で実行する。 |
| `electron/tests/e2e/mvp-flow.test.ts` | `desktop flow` | 起動、Project、Source、承認、Build、Job、Artifactを画面経由で確認する。 |

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
- 対象: **Desktop統合runtime**
- 必須fixture: `desktop_connectivity_gate`
- 設定: 追加の秘密環境変数なし
- 疎通確認: アプリ起動、preload API公開、DB/worker healthまでを確認し、作品生成は行わない。
- 実機能確認: 疎通成功後、mock AI/TTSで最短MVP導線を最後まで実行する。
- 実機能テストは疎通fixtureを引数として必須要求する。
- 設定不足時はnetworkへ出ず、秘密値を表示せず明示的にskipする。
- 疎通失敗時は疎通テストをfailとし、その実行に属する実機能テストは理由付きskipとする。
- 疎通確認で生成物、DB更新、課金の大きい処理を行わない。避けられない最小課金は明記する。

## 8. fixture契約
- `tmp_path`配下だけを使用する一時Project/data root
- 固定timezone付きclock
- 決定的ID generator
- 秘密値を含まない設定fixture
- 成功・validation error・timeout・破損応答を返す依存stub/mock
- `desktop_connectivity_gate`: 疎通結果、version、接続先の秘密でない識別情報を保持するsession scope fixture

## 9. テストケース
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

## 10. STEP3テスト空実装への引継ぎ
- `tests/integration/test_mvp_flow.py`
- `electron/tests/e2e/mvp-flow.test.ts`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `electron/tests/e2e/mvp-flow.test.ts`
- `script/integration/mvp_flow.py`

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
