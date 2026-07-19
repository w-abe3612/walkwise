---
document_type: claude_code_implementation_task
task_id: TASK-E2E-001
order: 152
title: サンプル1章fixture・仕様間受入検証
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 6. 移行・品質・配布
depends_on:
- TASK-DESKTOP-003
- TASK-MIGRATION-001
contract_ref: docs/test-cases/TASK-E2E-001-sample-book-fixtures-and-acceptance.md
preparation_ref: docs/spec-proposals/task/152_task-e2e-001-sample-book-fixtures-and-acceptance.md
spec_refs:
- docs/spec-proposals/task/1_sample-book-end-to-end-validation.md
- docs/specifications/audiobook-creation-pipeline.md
test_files:
- tests/integration/test_sample_book_e2e.py
source_files:
- tests/fixtures/sample_book/
- tests/integration/test_sample_book_e2e.py
command_documents:
- docs/commands/end-to-end.md
- docs/commands/testing.md
documentation_repair_ownership: []
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-E2E-001 サンプル1章fixture・仕様間受入検証


## 1. 目的

1作品1章8〜10segment、3資料、4主張、4承認、AI routing、cache、音声manifestを持つ決定的fixtureで全体受入を行う。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-DESKTOP-003`
- `TASK-MIGRATION-001`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-E2E-001-sample-book-fixtures-and-acceptance.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/spec-proposals/task/1_sample-book-end-to-end-validation.md`
- `docs/specifications/audiobook-creation-pipeline.md`

関連コマンド文書:

- `docs/commands/end-to-end.md`
- `docs/commands/testing.md`

## 4. 変更範囲

### テスト

- `tests/integration/test_sample_book_e2e.py`

### production source

- `tests/fixtures/sample_book/`
- `tests/integration/test_sample_book_e2e.py`

### 扱う範囲

- sample project
- 正常fixture
- unsupported/conflict/invalid ref/budget/cache/unapproved fixture
- mock AI/TTS E2E
- optional real VOICEVOX手動
- validation report
- 参照整合性

### 対象外

- 製品用教材の内容完成
- COEIROINK
- 長時間性能

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. コマンド文書の整合性

関連するコマンド文書を実行し、対象パス・marker・環境変数・実行順序が実装と一致することを確認する。
古い欠落記述を発見した場合は、担当タスクを確認して勝手に重複修正せず、完了報告へ記録する。


## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `tests/fixtures/sample_book/` | `deterministic fixture contract` | 1作品1章8〜10segment、3資料、4主張、4承認を固定する。 |
| `tests/integration/test_sample_book_e2e.py` | `run_sample_book_acceptance(...)` | mock AI/TTSで全工程と異常fixtureを検証する。 |

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
| TC-E2E-001-01 | P0 | e2e | 正常sample | 決定的sample fixture | mock E2E | 4claim追跡、4承認、章MP3/text/manifestを生成 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-02 | P0 | e2e | 異常fixtures | unsupported/conflict/invalid ref/budget/unapproved | 各実行 | 正しいgateで停止し既存成果物を保持 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-03 | P0 | e2e | cache | 同じfixtureを再実行 | E2E | AI/TTS mock callがcache hit分だけ減る | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-04 | P1 | unit | unsupported/conflict/invalid ref/budget/cache/unapproved fixture | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `deterministic fixture contract`を通じて「unsupported/conflict/invalid ref/budget/cache/unapproved fixture」を実行する | 同じcache keyでは外部処理を再実行せず、入力・model・prompt・version差分ではmissする。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-05 | P1 | unit | optional real VOICEVOX手動 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `deterministic fixture contract`を通じて「optional real VOICEVOX手動」を実行する | 「optional real VOICEVOX手動」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-06 | P1 | unit | validation report | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `deterministic fixture contract`を通じて「validation report」を実行する | 正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-07 | P1 | unit | 参照整合性 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `deterministic fixture contract`を通じて「参照整合性」を実行する | 「参照整合性」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `deterministic fixture contract`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `deterministic fixture contract`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-11 | P0 | integration_smoke | 任意の実VOICEVOXの疎通確認 | 実接続テストが明示的に有効化され、必要な設定が存在する | 実VOICEVOXを使う任意テストでは、先に`GET /speakers`を行う。 | ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。 | `tests/integration/test_sample_book_e2e.py` |
| TC-E2E-001-12 | P1 | integration_live | 任意の実VOICEVOXの実機能テスト | `voicevox_connectivity_gate`が成功済み | 疎通成功後だけサンプルの短い試聴区間を合成する。通常E2Eはmock TTSで完結する。 | 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。 | `tests/integration/test_sample_book_e2e.py` |

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
python -m pytest --collect-only -q tests/integration/test_sample_book_e2e.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/integration/test_sample_book_e2e.py
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

- 対象: **任意の実VOICEVOX**
- 必須fixture: `voicevox_connectivity_gate`
- 設定: `VOICEVOX_URL`
- 疎通確認: 実VOICEVOXを使う任意テストでは、先に`GET /speakers`を行う。
- 実機能確認: 疎通成功後だけサンプルの短い試聴区間を合成する。通常E2Eはmock TTSで完結する。
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
