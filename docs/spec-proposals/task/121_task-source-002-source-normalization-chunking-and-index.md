---
task_type: implementation_preparation
status: draft
order: 121
implementation_task_id: "TASK-SOURCE-002"
title: "資料正規化・chunk・index・manifest"
phase: "2. 資料入力"
release_scope: "MVP"
depends_on:
  - "TASK-INGEST-001"
  - "TASK-PDF-001"
  - "TASK-OCR-001"
spec_refs:
  - ../../specifications/source-preprocessing.md
  - ../../specifications/source-storage-and-common-schema.md
planned_outputs:
  test_case_contract: "docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md"
  executable_task: "docs/tasks/TASK-SOURCE-002-source-normalization-chunking-and-index.md"
  test_scaffolds:
    - "tests/test_source_normalization.py"
    - "tests/test_source_chunking.py"
    - "tests/test_source_manifest.py"
  source_scaffolds:
    - "script/source_processing/normalize.py"
    - "script/source_processing/chunking.py"
    - "script/source_processing/manifests.py"
  command_documents:
    - "docs/commands/source-processing.md"
    - "docs/commands/testing.md"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
last_updated: "2026-07-19"
---
# TASK-SOURCE-002 資料正規化・chunk・index・manifest

> この文書は**STEP1の実装タスク切り出し案**である。Claude Codeへ直接実装させる契約書ではない。
> STEP2〜STEP6で契約、テストケース、テスト空実装、ソース空実装、コマンド文書を作成し、
> 人間承認後のSTEP7で`docs/tasks/`へ実行可能なタスク契約書を作成する。

## 1. 単一責務

immutable extracted/rawから低リスク正規化、構造化、約2000文字soft chunk、typed locator、topic検索用indexを生成する。

## 2. このタスクで扱う範囲

- Unicode/改行/空白の決定的正規化
- 繰返しheader/footer除去
- diff/hash
- footnote分離
- structured Markdown/YAML/JSON
- soft chunk
- chunk manifest
- typed locators
- 重複hash warning

## 3. 対象外

- AIによる高リスク本文修正
- Project間共通library
- 自動dedup merge

## 4. 先行タスク

- TASK-INGEST-001
- TASK-PDF-001
- TASK-OCR-001

## 5. 根拠仕様

- docs/specifications/source-preprocessing.md
- docs/specifications/source-storage-and-common-schema.md

## 6. STEP2で固定する契約

次の事項を`docs/test-cases/TASK-SOURCE-002-source-normalization-chunking-and-index.md`で具体化する。

- 公開クラス、関数、Protocol、dataclass、enum、公開例外
- Given／When／Then形式のテストケースID
- 正常系、異常系、境界値、入力不変、再実行時の挙動
- 外部サービスをmockする境界
- 許可ファイル、変更禁止ファイル
- STEP3・STEP4で作る空実装の正確なファイルパス

## 7. STEP3で予定するテスト空実装

- tests/test_source_normalization.py
- tests/test_source_chunking.py
- tests/test_source_manifest.py

テスト空実装は`pytest.mark.xfail(strict=True)`と明示的な`pytest.fail`を使用し、
`pass`、無条件`skip`、成功を装う仮assertionを使用しない。

## 8. STEP4で予定するソース空実装

- script/source_processing/normalize.py
- script/source_processing/chunking.py
- script/source_processing/manifests.py

ここに記載したパスはSTEP1時点の推奨配置である。STEP2の契約作成時に、
責務が1〜3主要ソースへ収まるよう最終確定する。

## 9. STEP6で予定するコマンド文書

- docs/commands/source-processing.md
- docs/commands/testing.md

## 10. 推奨前提・未確定事項の扱い

- なし

## 11. 準備継続条件

- 根拠仕様と矛盾しない。
- 主要責務が一つである。
- STEP2で3〜10件程度のテストケースへ落とせる。
- 公開契約を空実装として固定できる。
- 外部サービスの実呼び出しを通常テストから分離できる。

上記を満たせない場合は、STEP2で子タスクへ分割し、元のtask IDを親追跡IDとして維持する。

## 12. STEP7で作成する実行タスク

```text
docs/tasks/TASK-SOURCE-002-source-normalization-chunking-and-index.md
```

この実行タスクには、Claude Codeが次を順番どおり行う指示を含める。

```text
テスト本実装
↓
未実装によるRed確認
↓
ソースコード本実装
↓
対象テスト
↓
全体テスト
↓
文書記載コマンド
↓
実装完了報告
↓
ChatGPTまたは人間による仕様適合レビュー
```

## 13. STEP1完了条件

- 安定したtask IDが割り当てられている。
- 依存関係とrelease scopeが明記されている。
- 根拠仕様、対象、対象外が区別されている。
- STEP2〜STEP7の成果物予定が追跡できる。
- この文書だけを根拠にClaude Codeへ本実装を依頼しないことが明記されている。
