---
document_type: claude_code_implementation_task
task_id: TASK-SOURCE-002
order: 121
title: 資料正規化・chunk・index・manifest
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 2. 資料入力
depends_on:
- TASK-INGEST-001
- TASK-PDF-001
- TASK-OCR-001
contract_ref: docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md
preparation_ref: docs/spec-proposals/task/121_task-source-002-source-normalization-chunking-and-index.md
spec_refs:
- docs/specifications/source-preprocessing.md
- docs/specifications/source-storage-and-common-schema.md
test_files:
- tests/test_source_normalization.py
- tests/test_source_chunking.py
- tests/test_source_manifest.py
source_files:
- script/source_processing/normalize.py
- script/source_processing/chunking.py
- script/source_processing/manifests.py
command_documents:
- docs/commands/source-processing.md
- docs/commands/testing.md
documentation_repair_ownership: []
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-SOURCE-002 資料正規化・chunk・index・manifest


## 1. 目的

immutable extracted/rawから低リスク正規化、構造化、約2000文字soft chunk、typed locator、topic検索用indexを生成する。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-INGEST-001`
- `TASK-PDF-001`
- `TASK-OCR-001`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/specifications/source-preprocessing.md`
- `docs/specifications/source-storage-and-common-schema.md`

関連コマンド文書:

- `docs/commands/source-processing.md`
- `docs/commands/testing.md`

## 4. 変更範囲

### テスト

- `tests/test_source_normalization.py`
- `tests/test_source_chunking.py`
- `tests/test_source_manifest.py`

### production source

- `script/source_processing/normalize.py`
- `script/source_processing/chunking.py`
- `script/source_processing/manifests.py`

### 扱う範囲

- Unicode/改行/空白の決定的正規化
- 繰返しheader/footer除去
- diff/hash
- footnote分離
- structured Markdown/YAML/JSON
- soft chunk
- chunk manifest
- typed locators
- 重複hash warning

### 対象外

- AIによる高リスク本文修正
- Project間共通library
- 自動dedup merge

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. コマンド文書の整合性

関連するコマンド文書を実行し、対象パス・marker・環境変数・実行順序が実装と一致することを確認する。
古い欠落記述を発見した場合は、担当タスクを確認して勝手に重複修正せず、完了報告へ記録する。


## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `script/source_processing/normalize.py` | `normalize_text(text, rules) -> NormalizationResult` | 低リスク・決定的変換とdiff/hashを返す。 |
| `script/source_processing/chunking.py` | `chunk_structured_source(source, *, soft_limit=2000) -> list[SourceChunk]` | locatorを保持して決定的chunkを作る。 |
| `script/source_processing/manifests.py` | `build_chunk_manifest(chunks) / build_topic_index(...)` | 参照可能なmanifest/indexを生成する。 |

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
| TC-SOURCE-002-01 | P0 | unit | 低リスク正規化 | 改行・Unicode・反復headerがある | normalizeする | 決定的修正とbefore/after hash/diffを返す | `tests/test_source_normalization.py` |
| TC-SOURCE-002-02 | P0 | unit | soft chunk | 2000文字付近の段落 | chunkする | 意味境界を優先しlocatorを失わない | `tests/test_source_chunking.py` |
| TC-SOURCE-002-03 | P0 | unit | 参照整合 | chunk manifestとtopic index | validateする | 全chunk IDが存在し重複がない | `tests/test_source_manifest.py` |
| TC-SOURCE-002-04 | P1 | unit | Unicode/改行/空白の決定的正規化 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `normalize_text(text, rules) -> NormalizationResult`を通じて「Unicode/改行/空白の決定的正規化」を実行する | 「Unicode/改行/空白の決定的正規化」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_normalization.py` |
| TC-SOURCE-002-05 | P1 | unit | 繰返しheader/footer除去 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `normalize_text(text, rules) -> NormalizationResult`を通じて「繰返しheader/footer除去」を実行する | 「繰返しheader/footer除去」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_chunking.py` |
| TC-SOURCE-002-06 | P1 | unit | footnote分離 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `normalize_text(text, rules) -> NormalizationResult`を通じて「footnote分離」を実行する | 「footnote分離」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_manifest.py` |
| TC-SOURCE-002-07 | P1 | unit | structured Markdown/YAML/JSON | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `normalize_text(text, rules) -> NormalizationResult`を通じて「structured Markdown/YAML/JSON」を実行する | 「structured Markdown/YAML/JSON」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_source_normalization.py` |
| TC-SOURCE-002-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `normalize_text(text, rules) -> NormalizationResult`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_source_chunking.py` |
| TC-SOURCE-002-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `normalize_text(text, rules) -> NormalizationResult`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_source_manifest.py` |
| TC-SOURCE-002-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_source_normalization.py` |

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
python -m pytest --collect-only -q tests/test_source_normalization.py tests/test_source_chunking.py tests/test_source_manifest.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_source_normalization.py tests/test_source_chunking.py tests/test_source_manifest.py
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
