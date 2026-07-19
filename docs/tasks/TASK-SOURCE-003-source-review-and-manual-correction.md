---
document_type: claude_code_implementation_task
task_id: TASK-SOURCE-003
order: 122
title: 資料レビュー・修正差分・再処理
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 2. 資料入力
depends_on:
- TASK-SOURCE-002
- TASK-SOURCE-001
contract_ref: docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md
preparation_ref: docs/spec-proposals/task/122_task-source-003-source-review-and-manual-correction.md
spec_refs:
- docs/specifications/source-preprocessing.md
- docs/screens/02-project-workspace-and-source-import.md
test_files:
- tests/test_source_review_service.py
source_files:
- script/services/source_review.py
- script/schemas/source_review.py
command_documents:
- docs/commands/source-review.md
- docs/commands/testing.md
documentation_repair_ownership:
- docs/commands/source-review.md
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-SOURCE-003 資料レビュー・修正差分・再処理


## 1. 目的

review_required箇所を原本/抽出/修正版の差分として管理し、人間承認後に新revisionを作る。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-SOURCE-002`
- `TASK-SOURCE-001`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-SOURCE-003-source-review-and-manual-correction.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/specifications/source-preprocessing.md`
- `docs/screens/02-project-workspace-and-source-import.md`

関連コマンド文書:

- `docs/commands/source-review.md`
- `docs/commands/testing.md`

## 4. 変更範囲

### テスト

- `tests/test_source_review_service.py`

### production source

- `script/services/source_review.py`
- `script/schemas/source_review.py`

### 扱う範囲

- review item model
- 元ページlocator
- manual correction file
- 再OCR要求
- 問題なし承認
- status ready遷移
- original/extracted不変
- revision/hash更新

### 対象外

- GUI
- AI自動修正の確定
- Source削除

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. 古い記述の修正責任

このタスクは、実装と同時に次の古い状態記述を修正する責任を持つ。

- `docs/commands/source-review.md`

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
| `script/schemas/source_review.py` | `SourceReviewIssue/CorrectionPatch/ReviewDecision` | 問題、修正差分、人間判断を型付けする。 |
| `script/services/source_review.py` | `SourceReviewService.apply_correction(command) -> ReviewResult` | rawを変えず修正版とdiffを新revisionへ保存する。 |
| `script/services/source_review.py` | `SourceReviewService.mark_resolved/require_reprocessing` | 問題解消または再処理要求を記録する。 |

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
| TC-SOURCE-003-01 | P0 | integration_mock | 修正revision | review issueへ手動修正 | apply_correction | raw不変で新revision・diff・provenanceを作る | `tests/test_source_review_service.py` |
| TC-SOURCE-003-02 | P0 | unit | 再処理 | OCR設定変更を要求 | require_reprocessing | 旧正常結果を残し新Job候補を作る | `tests/test_source_review_service.py` |
| TC-SOURCE-003-03 | P1 | unit | review item model | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「review item model」を実行する | 「review item model」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-04 | P1 | unit | 元ページlocator | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「元ページlocator」を実行する | 「元ページlocator」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-05 | P1 | integration_mock | manual correction file | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「manual correction file」を実行する | 「manual correction file」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-06 | P1 | unit | 再OCR要求 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「再OCR要求」を実行する | 「再OCR要求」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-07 | P1 | unit | 問題なし承認 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を通じて「問題なし承認」を実行する | 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `SourceReviewIssue/CorrectionPatch/ReviewDecision`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_source_review_service.py` |
| TC-SOURCE-003-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_source_review_service.py` |

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
python -m pytest --collect-only -q tests/test_source_review_service.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_source_review_service.py
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
