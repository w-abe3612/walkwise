---
spec_id: source-storage-and-common-schema
title: "資料保存構成と共通資料スキーマ"
status: review
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  note: "旧仕様策定タスク(完了・削除済み)により生成。Git履歴を参照。"
depends_on:
  - material-input-pipeline.md
  - task/2_file-persistence-operations.md
spec_refs:
  - ../specifications/18-ai-model-routing-and-cost-control.md
  - ../specifications/01-common-identifiers-and-versioning.md
  - ../specifications/17-local-data-persistence-policy.md
  - material-input-pipeline.md
---

# 資料保存構成と共通資料スキーマ(ドラフト)

> **依存関係の注記**
> 本書は`docs/spec-proposals/task/2_file-persistence-operations.md`
> (ファイル保存運用の詳細: atomic write、ファイルロック、バックアップ世代数)への
> 依存を宣言しているが、同タスクは本書作成時点で未着手のまま残っている
> (`docs/spec-proposals/task/INDEX.md`参照)。
> このため、ファイルロック・atomic write・バックアップ世代数といった
> **書き込み手順の詳細**は本書の対象外・未決定事項として残し、
> `17-local-data-persistence-policy.md`(承認済み・方針レベル)と
> `01-common-identifiers-and-versioning.md`(承認済み・ID/ハッシュ規則)から
> 導出できる範囲でのみ、資料保存構成とschemaを定義する。

## 1. 目的

原資料、抽出本文、補正本文、構造化資料、source locator、信頼度、rights、
AI実行情報、索引を共通形式で保存するための、ディレクトリ構成とスキーマを定義する。

## 2. 対象範囲

- source IDと版の管理方法
- original/extracted/normalized/structuredの配置
- source locator(page/chapter/section/座標)
- chunk IDと順序
- source summary、topic index、terminology、coverage map、source requirements
- AI実行provenance
- コンテンツ作成側へのexport形式

## 3. 対象外

- ファイルロック方式、atomic write手順、バックアップ世代数
  (`2_file-persistence-operations.md`未着手のため未決定事項へ送る)
- PDF/OCR/EPUB/Kindleそれぞれの抽出アルゴリズム(→タスク09〜12)
- 権利状態の詳細な遷移(→タスク08)
- データベースへの移行(`17-local-data-persistence-policy.md`により初期対象外)

## 4. 現行実装

現行コードには資料保存の共通schemaは存在しない。`dumps/`配下に手動配置された
テキストダンプがあるのみで、`sources/`ディレクトリ構成も未実装である。

## 5. 推奨仕様

### 5.1 推奨ディレクトリ

`audiobook-creation-pipeline.md` 20節の推奨ディレクトリと整合させる。

```text
data/library/<project_id>/sources/
├─ originals/
│  └─ <source_id>/...
├─ extracted/
│  └─ <source_id>/...
├─ normalized/
│  └─ <source_id>/...
├─ structured/
│  └─ <source_id>/chunk-0001.md ...
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

質問1(original/extracted/normalized/structuredをどう配置するか)への回答:
プロジェクト配下の`sources/`に段階別ディレクトリを置き、`originals/`は
**immutable**とする(基本原則5.2節)。

### 5.2 基本原則

- `originals/`はimmutableとする。AIまたは前処理は`original`を上書きしない。
- `normalized`は`extracted`との差分を追跡できる(タスク13の`transformation`記録を使用)。
- `structured`はlocatorを失わない。
- `source summary`と`topic index`を技術的事実の最終証拠にしない
  (`audiobook-creation-pipeline.md` 7.2節と一致)。
- 事実検証時は必ず元source chunkへ戻る。
- 同じsourceを別projectから参照できる(参照であり複製ではない)。
- source revision変更で関連cache(topic index、coverage map、claim検証結果)を無効化する。

### 5.3 データ形式の使い分け

`00-specification-guidelines.md` 4節に従う。

| 内容 | 形式 |
|---|---|
| source metadata、source summary、topic index、coverage map、source requirements | YAML |
| chunk manifest、AI実行ログ | JSON/JSONL |
| structured本文 | Markdown |
| 互換入力(既存TXTダンプ) | TXT |

質問2(metadata、chunk、AI実行履歴の保存形式)への回答: 上表の通り。

### 5.4 共通資料metadata

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
  content_hash:
    algorithm: sha256
    value: "..."

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

`source_id`の命名規則は`01-common-identifiers-and-versioning.md` 6節の
`^[a-z0-9]+(?:-[a-z0-9]+)*$`に従う。`content_hash`の算出方法は同仕様11節に従う。

### 5.5 source locator

質問3(source locatorの粒度)への回答: ページ、章、節、座標、元ファイルhashを
可能な範囲で保持する。すべての抽出方式が座標を提供できるわけではないため、
`page`/`chapter`/`section`/`coordinates`はすべて任意項目とし、
**locatorが完全に空である状態だけをwarning対象**とする。

```json
{
  "chunk_id": "mysql-8-reference-chunk-0001",
  "source_id": "mysql-8-reference",
  "order": 1,
  "locator": {
    "chapter": "13",
    "section": "13.1.20",
    "page": null,
    "coordinates": null
  },
  "text_path": "sources/structured/mysql-8-reference/chunk-0001.md",
  "input_hash": "...",
  "warnings": []
}
```

### 5.6 chunk分割の原則

質問4(chunk分割の原則)への回答: 見出し・段落など意味境界を優先する。
初期目安は**2,000〜6,000日本語文字**とし、locatorをまたぐ場合は分割する。
この数値目安は実測に基づくものではなく、後続タスクでの調整対象とする。

### 5.7 source summary / topic index / coverage map / source requirements

```yaml
# source-summary.yaml (要素例)
source_id: mysql-8-reference
summary: MySQLの公式リファレンスマニュアル。DDL/DML/インデックス設計を含む。
scope_notes: バージョン8.0時点の挙動。旧バージョンとの差異は別途確認要。
roles:
  - factual_evidence
  - terminology_reference
```

```yaml
# topic-index.yaml (要素例)
topics:
  - topic_id: normalization
    chunk_refs:
      - mysql-8-reference-chunk-0001
```

```yaml
# coverage-map.yaml
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

状態の列挙値: `covered` / `partially_covered` / `conflict` / `missing` / `not_applicable`

```yaml
# source-requirements.yaml
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

`minimum_independent_sources`を満たすことだけで資料品質を自動保証しない
(人間による資料・カリキュラム承認が必須、`audiobook-creation-pipeline.md` 11.1節)。

質問5(source summaryやtopic indexを事実根拠にしてよいか)への回答:
**してはいけない。** 検証時は必ず元source chunkへ戻る。

### 5.8 AI実行記録

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

AI実行情報はsource contentと分離して`reports/ai-execution.jsonl`へ記録する
(`18-ai-model-routing-and-cost-control.md` 15節と整合)。


### 5.9 media・取得方法・画像manifest

`source_type`を媒体形式と資料の意味分類へ兼用しない。

推奨:

```yaml
source_category: textbook
media:
  type: image_sequence
  acquisition_method: flatbed_scanner
  original_mime_types:
    - image/tiff
  page_representation: single_page

privacy:
  exif_location_present: false
  contains_people: false
  contains_personal_information: unknown
```

画像資料では次を追加で保持する。

- image ID
- original path
- original hash
- page index
- original imageと派生pageの対応
- crop座標
- rotation
- spread side
- quality flags
- EXIF privacy flags
- OCR handoff status

```text
sources/originals/<source_id>/images/
sources/preprocessed/<source_id>/pages/
sources/manifests/<source_id>-image-ingestion-session.json
sources/reports/<source_id>-image-quality-report.json
```

動画・録音の将来対応を妨げないよう、
locatorは`page`だけに固定せず、
将来`media_time_range`を追加可能なunion構造とする。
現時点では動画・録音を正式schemaの必須対象にしない。

## 6. 入力

- 原資料ファイル、または資料入力パイプラインの抽出・OCR結果
- 資料戦略とsource role(`material-input-pipeline.md`より)

## 7. 出力

- 5.1節のディレクトリ構成に従って保存された`sources/`一式
- source summary、topic index、coverage map、source requirements
- chunk manifest

## 8. 正常系

1. 原資料を`originals/<source_id>/`へ保存し、`content_hash`を記録する。
2. 抽出結果を`extracted/`へ保存する。
3. 正規化結果を`normalized/`へ保存し、`extracted`との差分を追跡可能にする。
4. 構造化結果を`structured/`へchunk単位で保存し、locatorを保持する。
5. source summary、topic index、coverage mapを生成する。
6. 別プロジェクトから同じ`source_id`を参照する(複製しない)。

## 9. 異常系

| ケース | 扱い |
|---|---|
| source ID重複 | Error |
| original hash欠落 | Error |
| structuredからlocatorへ戻れない | Error |
| chunk order重複 | Error |
| 未知のcoverage status | Error |
| AI出力がoriginalを上書き | Error(基本原則5.2節違反) |
| coverageが`conflict`なのに`next_action`が`none` | Error |
| AI summaryだけをfactual evidenceに指定 | Error |
| locatorが資料全体だけを指す | Warning |
| OCR confidence欠落 | Warning |
| usage metadata欠落 | Warning |
| rights unverified | Warning |
| source summaryがsource revisionより古い | Warning |
| coverage mapがsource revisionより古い | Warning |

## 10. バリデーション

- `source_id`が`01-common-identifiers-and-versioning.md` 6節のID形式に適合する。
- `content_hash`が11節の正規化手順で算出されている。
- `schema_version`が全構造化ファイルに存在する。
- chunk manifestの`order`が資料内で一意である。

## 11. AIモデル方針

- source summary、topic index、形式変換: `economy_structuring`
- coverage統合: `economy_structuring`または`standard_generation`
- source conflict: `high_assurance_review`
- 技術的事実の承認: source evidenceと人間

## 12. テスト観点

- PDF、OCR、EPUB、Kindleを同じsource ID体系で扱える。
- originalからclaim locatorまで追跡できる。
- source revision変更でindexとcacheが古くなる(warning検出)。
- coverage missingから追加資料へ戻れる。
- topic indexから必要chunkだけを取得できる。
- AI実行モデルとpromptを追跡できる。
- summaryだけでclaim verificationできない。
- 同じsourceを複数projectから参照しても複製が発生しない。

## 13. 移行・互換性

- 現行実装に資料保存schemaがないため、既存データからの変換対象はない。
- `17-local-data-persistence-policy.md`の方針(DB非使用、YAML/JSON/Markdown中心、
  安定ID + schema_versionの付与)と整合させている。

## 14. 未決定事項

- ファイルロック方式、atomic write手順、バックアップ世代数
  (`2_file-persistence-operations.md`が夜間実行対象外のため未着手)
- chunk分割サイズ(2,000〜6,000文字)の実測による調整
- 大容量ファイル(画像・PDF原本)の重複排除・保存上限
- coverage状態`partially_covered`の定量的な充足率定義

## 15. 完了条件

- [x] すべての入力形式(PDF/OCR/EPUB/Kindle)を同じschemaへ変換できる構造になっている。
- [x] original、extracted、normalized、structuredが分離されている。
- [x] source locatorを維持できる。
- [x] source summary、topic index、coverage mapを保存できる。
- [x] AI実行履歴とusageを追跡できる。
- [x] 必要chunkだけを後続へ渡せる構造になっている。
- [x] 出力ドラフトが存在し、`status: review`である。
- [x] 実装コードを変更していない。

## 16. 停止・保留条件(該当状況の確認)

- 01番のID規則と矛盾しない(5.4節で明示的に整合)。
- originalをAIが上書きする設計にしていない(5.2節)。
- structuredから元位置へ戻れる(5.5節のlocator必須化)。

いずれの停止条件にも該当しないため、本書は`status: review`として提出する。
ただし、依存タスク2(ファイル保存運用)未着手分は14節の未決定事項として残す。
