---
test_case_contract_id: CONTRACT-TASK-UI-002
implementation_task_id: TASK-UI-002
title: Project workspace・Source登録/レビュー・承認UI
status: review
version: '1.0'
release_scope: MVP
phase: 5. Workerとデスクトップ
depends_on:
- TASK-DESKTOP-002
- TASK-SOURCE-003
- TASK-APPROVAL-001
spec_refs:
- docs/screens/02-project-workspace-and-source-import.md
- docs/specifications/image-material-ingestion.md
test_files:
- electron/tests/source_approval_ipc.test.ts
- electron/renderer/tests/ProjectWorkspace.test.ts
source_files:
- electron/main/ipc/sources.ts
- electron/main/ipc/approvals.ts
- electron/renderer/screens/ProjectWorkspace.vue
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-UI-002 Project workspace・Source登録/レビュー・承認UI — タスク契約書・テストケース
## 1. 目的
Project詳細、text/pdf/image登録、処理状態、問題箇所レビュー、4段階承認/差し戻しを一つのworkspace導線へ統合する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- file dialog/drop
- Source一覧/状態
- 処理開始
- review item原本/抽出比較
- 再処理/修正/問題なし
- approval badges
- 承認/理由付き差し戻し
- MVP外形式非表示

## 4. 対象外
- 詳細原稿editor
- Source削除
- EPUB表示
- Kindle/動画/録音

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `electron/main/ipc/sources.ts` | `source:register handlers` | path/media typeをmainで再検証しSource serviceへ委譲する。 |
| `electron/main/ipc/approvals.ts` | `approval:list/approve/request-changes handlers` | 差し戻し理由とgateを検証する。 |
| `electron/renderer/screens/ProjectWorkspace.vue` | `workspace UI` | Source状態、review導線、4承認を表示・操作する。 |

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
| TC-UI-002-01 | P0 | unit | Source状態表示 | 5 statusのSource | render | 仕様の日本語表示とreview/retry導線 | `electron/tests/source_approval_ipc.test.ts` |
| TC-UI-002-02 | P0 | unit | 差し戻し | 理由空/あり | request changes | 空は拒否、ありはIPC1回 | `electron/renderer/tests/ProjectWorkspace.test.ts` |
| TC-UI-002-03 | P0 | unit | 対象外非表示 | EPUB/Kindle/video | render | 選択肢にもdisabledにも表示しない | `electron/tests/source_approval_ipc.test.ts` |
| TC-UI-002-04 | P1 | integration_mock | file dialog/drop | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `source:register handlers`を通じて「file dialog/drop」を実行する | 「file dialog/drop」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/renderer/tests/ProjectWorkspace.test.ts` |
| TC-UI-002-05 | P1 | unit | 処理開始 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `source:register handlers`を通じて「処理開始」を実行する | 「処理開始」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/tests/source_approval_ipc.test.ts` |
| TC-UI-002-06 | P1 | unit | 再処理/修正/問題なし | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `source:register handlers`を通じて「再処理/修正/問題なし」を実行する | 「再処理/修正/問題なし」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `electron/renderer/tests/ProjectWorkspace.test.ts` |
| TC-UI-002-07 | P1 | unit | approval badges | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `source:register handlers`を通じて「approval badges」を実行する | 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。 | `electron/tests/source_approval_ipc.test.ts` |
| TC-UI-002-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `source:register handlers`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `electron/renderer/tests/ProjectWorkspace.test.ts` |
| TC-UI-002-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `source:register handlers`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `electron/tests/source_approval_ipc.test.ts` |

## 10. STEP3テスト空実装への引継ぎ
- `electron/tests/source_approval_ipc.test.ts`
- `electron/renderer/tests/ProjectWorkspace.test.ts`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `electron/main/ipc/sources.ts`
- `electron/main/ipc/approvals.ts`
- `electron/renderer/screens/ProjectWorkspace.vue`

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
