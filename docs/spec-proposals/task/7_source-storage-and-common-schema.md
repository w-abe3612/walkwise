---
task_type: specification_decision
status: draft
order: 7
title: "資料保存構成と共通資料スキーマ"
depends_on:
  - 6_material-input-pipeline-boundary.md
  - 2_file-persistence-operations.md
spec_refs:
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/source-storage-and-common-schema.md"
last_updated: "2026-07-19"
---

# 7. 資料保存構成と共通資料スキーマ

## 1. 目的

原資料、ページ画像、抽出本文、補正本文、構造化資料、
source locator、信頼度、rights、AI実行情報、索引を共通形式で保存する。

## 2. 決定する事項

- source IDと版
- source strategy、media type、acquisition methodの分離
- カメラ写真・スキャナ画像のimage sequence manifest
- original、extracted、normalized、structuredの配置
- page、chapter、section、座標のlocator
- OCR信頼度とwarning
- chunk IDと順序
- source summary
- topic index
- terminology
- coverage map
- source requirements
- AI実行provenance
- 大容量ファイルのhashと重複
- コンテンツ作成側へのexport

## 3. 推奨ディレクトリ

```text
sources/
├─ originals/
├─ extracted/
├─ normalized/
├─ structured/
├─ indexes/
│  ├─ source-summary.yaml
│  ├─ topic-index.yaml
│  ├─ terminology.yaml
│  ├─ coverage-map.yaml
│  └─ source-requirements.yaml
├─ manifests/
│  └─ chunk-manifest.json
└─ reports/
   ├─ extraction-report.json
   ├─ ai-execution.jsonl
   └─ review-required.yaml
```

## 4. 基本原則

- originalsはimmutableとする。
- AIはoriginalを上書きしない。
- normalizedはextractedとの差分を追跡できる。
- structuredはlocatorを失わない。
- summaryとindexを技術的事実の最終証拠にしない。
- 事実検証では元source chunkへ戻る。
- 同じsourceを別projectから参照できる。
- source revision変更で関連cacheを無効化する。

## 5. 共通資料例

```yaml
schema_version: "1.0"
source_id: mysql-8-reference
content_revision: 1
title: MySQL 8.0 Reference Manual
source_type: official_documentation
source_strategy: hybrid_reconstruction
roles:
  - factual_evidence
  - terminology_reference

version:
  edition_or_version: "8.0"
  retrieved_at: "2026-07-19T00:00:00+09:00"

original:
  path: sources/originals/mysql-8-reference/
  content_hash: "..."

processing:
  extraction_method: direct_text
  extractor: "<tool>"
  extractor_version: "<version>"

rights:
  status: unverified
  usage_purpose: personal_learning

indexes:
  source_summary: sources/indexes/source-summary.yaml
  topic_index: sources/indexes/topic-index.yaml
  coverage_map: sources/indexes/coverage-map.yaml
```

## 6. chunk例

```json
{
  "chunk_id": "mysql-8-reference-chunk-0001",
  "source_id": "mysql-8-reference",
  "order": 1,
  "locator": {
    "chapter": "13",
    "section": "13.1.20",
    "page": null
  },
  "text_path": "sources/structured/mysql-8-reference/chunk-0001.md",
  "input_hash": "...",
  "warnings": []
}
```

## 7. AI実行記録

```yaml
ai_execution:
  task_type: topic_extraction
  logical_tier: economy_structuring
  provider: google
  model: gemini-2.5-flash-lite
  prompt_id: source-topic-extraction
  prompt_version: "1.0"
  input_hashes:
    - "..."
  output_hash: "..."
  usage:
    input_tokens: 0
    output_tokens: 0
    total_tokens: 0
```

AI実行情報は、source contentとは分離して記録する。

## 8. coverage map

```yaml
schema_version: "1.0"
project_id: database-foundations
topics:
  - topic_id: normalization
    status: missing
    required_roles:
      - factual_evidence
      - curriculum_structure
    source_refs: []
    next_action: propose_sources
```

状態:

```text
covered
partially_covered
conflict
missing
not_applicable
```

## 9. source requirements

```yaml
topics:
  - topic_id: normalization
    required_source_roles:
      - factual_evidence
      - curriculum_structure
    preferred_source_types:
      - textbook
      - official_documentation
    minimum_independent_sources: 1
```

minimum数だけで品質を自動保証しない。

## 10. AIモデル方針

- source summary、topic index、形式変換: economy
- coverage統合: economyまたはstandard
- source conflict: high assurance
- 技術的事実の承認: source evidenceと人間

## 11. バリデーション

### Error

- source ID重複
- original hash欠落
- structuredからlocatorへ戻れない
- chunk order重複
- unknown coverage status
- AI出力がoriginalを上書き
- conflictなのにnext actionがnone
- AI summaryだけをfactual evidenceに指定

### Warning

- locatorが資料全体だけ
- OCR confidence欠落
- usage metadata欠落
- rights unverified
- source summaryが古い
- coverage mapがsource revisionより古い

## 12. テスト観点

- PDF、カメラ写真、スキャナ画像、OCR、EPUB、Kindleを同じsource ID体系で扱える。
- originalからclaim locatorまで追跡できる。
- source revision変更でindexとcacheが古くなる。
- coverage missingから追加資料へ戻れる。
- topic indexから必要chunkだけを取得できる。
- AI実行モデルとpromptを追跡できる。
- summaryだけでclaim verificationできない。

## 13. 成果物

```text
docs/specifications/source-storage-and-common-schema.md
```

## 14. 完了条件

- すべての入力形式を同じschemaへ変換できる。
- original、extracted、normalized、structuredが分離される。
- source locatorを維持できる。
- source summary、topic index、coverage mapを保存できる。
- AI実行履歴とusageを追跡できる。
- 必要chunkだけを後続へ渡せる。
