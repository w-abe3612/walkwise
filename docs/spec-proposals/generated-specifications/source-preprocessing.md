---
spec_id: source-preprocessing
title: "書籍データ前処理"
status: review
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/13_source-preprocessing.md
  source_task: docs/spec-proposals/task/13_source-preprocessing.md
depends_on:
  - 9_pdf-direct-text-extraction.md
  - 10_ocr-and-scanned-pdf.md
  - 11_epub-text-extraction.md
  - 12_kindle-capture.md
spec_refs:
  - pdf-direct-text-extraction.md
  - ocr-and-scanned-pdf.md
  - epub-text-extraction.md
  - kindle-capture.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
---

# 書籍データ前処理(ドラフト)

## 1. 目的

PDF直接抽出・カメラ写真OCR・スキャナ画像OCR・EPUB抽出・Kindleキャプチャ経由OCRのいずれから得た抽出本文からも、
ヘッダー、ページ番号、不自然な改行、重複を除去し、章・節・図表・コード・数式を、
原文へ戻れる形で構造化する処理を定義する。

## 2. 対象範囲

- raw/normalized/structuredの境界
- 決定的なルール処理とAI補正の分担
- 改行結合、ハイフン修正、header/footer/ページ番号除去
- 重複・抜けの扱い
- 章・節・目次の構造化
- 図表、脚注、コード、数式の分離
- AIモデルルーティングとコスト制御
- 人間確認条件

## 3. 対象外

- 抽出そのもの(PDF/OCR/EPUB/Kindleは各タスク09〜12で定義済み)
- 技術的主張の検証(コンテンツ作成パイプラインの責務)
- 音声向け変換(`tts_text`生成。コンテンツ作成パイプラインの責務)

## 4. 現行実装

現行コードに前処理の実装は存在しない。

## 5. 推奨仕様

### 5.1 raw/normalized/structuredの境界

質問2への回答:

```text
raw          = 抽出結果そのもの(タスク09〜12の出力)。原文相当。不変。
normalized   = 表記・改行・header/footer補正済み。rawとの差分を追跡可能。
structured   = 章節・要素分類済み。コンテンツ作成パイプラインへの後続入力。
```

### 5.2 処理順

質問1・3への回答: **決定的なルール処理を先に行い、AIは候補生成と
複雑な構造化に使う。**

```text
raw
↓
決定的なルール処理(header/footer既知パターン、単純改行結合)
↓
normalized candidate
↓
差分検査
↓
AIによる低リスク構造化(economy)
↓
高リスク箇所の抽出(数式/コード/表/図/固有名詞/ページ跨ぎ欠落)
↓
人間またはhigh assurance review
↓
structured
```

### 5.3 economy_structuring

初期モデル: Gemini 2.5 Flash-Lite

許可:

- 目次整理
- 見出し階層候補
- 不自然な改行の結合候補
- header・footer候補
- 段落分類
- JSON・YAML・Markdown変換
- 通常本文のtopic抽出
- 主張候補抽出

単独確定不可:

- 数式
- コード
- 表
- 図
- 固有名詞の不確かな復元
- ページをまたぐ欠落文
- 技術的意味を変える補正

### 5.4 standard_generation

初期モデル: Gemini 2.5 Flash

用途:

- 複数ページから章構造を統合する。
- 読み順候補を比較する。
- 通常本文の自然な段落復元案を作る。
- 人間確認用の差分説明を作る。

原文を上書きしてはならない。

### 5.5 high_assurance_review

用途:

- 数式、コード、表の復元候補比較
- 技術的意味が変わる可能性のある補正
- 複数候補が競合する読み順
- 最終意味レビュー

高性能モデルの結果も、人間確認なしにoriginal相当へ昇格しない。

### 5.6 図表・コード・数式

質問4への回答: **独立要素として保存し、本文へ推測で埋め込まない。**

```json
{
  "element_id": "ch01-formula-0001",
  "type": "formula",
  "locator": {"page": 12},
  "raw_reference": "sources/extracted/example/page-0012.png#region1",
  "candidate_transcription": null,
  "status": "requires_human_review",
  "auto_confirmed": false
}
```

`auto_confirmed`は常に`false`から開始し、人間確認後にのみ`true`へ変更する。

### 5.7 AI通信量の削減

質問5への回答:

- 変更がないページをAIへ送らない。
- header/footerの繰り返し除去はルール化して再利用する(AIへ毎回依頼しない)。
- source summaryとtopic indexを再利用する。
- 大量の単純変換はBatch候補とする(`18-ai-model-routing-and-cost-control.md` 14節)。
- usageと再試行回数を記録する。

### 5.8 差分記録

```yaml
transformation:
  type: line_break_normalization
  input_hash: "..."
  output_hash: "..."
  changed_ranges:
    - locator:
        page: 12
      before: "..."
      after: "..."
  ai_execution_ref: ai-run-0001
```

### 5.9 review required条件

- OCR confidenceが閾値未満(`ocr-and-scanned-pdf.md`の信頼度と連動)
- 数式、コード、表、UML・アーキテクチャ図
- 脚注参照が不明
- ページ欠落
- 固有名詞候補が複数
- 数字または単位が変化
- 否定、条件、例外が変化
- economyとstandardの結果が不一致
- high assuranceが必要だが未設定

これらはいずれも自動でstructuredへ昇格させない(質問3「どの変更を人間確認にするか」への回答)。


### 5.10 画像由来本文の追加provenance

カメラ写真・スキャナ画像由来の本文では、
各text blockから次へ戻れるようにする。

- source ID
- page index
- original image ID
- preprocessed image ID
- crop座標
- OCR engine
- OCR confidence
- image quality flags

台形補正、見開き分割、回転等の画像処理は、
本文正規化とは別のprovenanceとして保存する。

手書き文字、反射、ページ湾曲、欠け、
図表内文字は`review_required`候補とする。

## 6. 入力

- タスク09〜12いずれかの抽出結果(raw)
- `source-storage-and-common-schema.md`のchunk manifest

## 7. 出力

- normalized本文
- structured本文(章・節・要素分類済み)
- transformation log
- review-required report

## 8. 正常系

1. rawをルールベース処理へ通す(header/footer既知パターン除去、単純改行結合)。
2. normalized candidateを作る。
3. rawとの差分を検査する。
4. 低リスク箇所をeconomy層で構造化候補として生成する。
5. 高リスク箇所(数式/コード/表/図/固有名詞/ページ跨ぎ欠落)を抽出し、
   human_reviewまたはhigh_assurance_reviewへ送る。
6. 人間確認後、structuredへ昇格する。

## 9. 異常系

| ケース | 扱い |
|---|---|
| normalizedがoriginalを置き換えようとする設計 | Error(基本原則違反、5.1節) |
| 数式・コード・表を根拠なく復元 | Error、`auto_confirmed`のまま人間確認へ |
| economyとstandardの結果が不一致 | `review_required` |
| ページ欠落を検出 | `review_required` |
| 数字・単位・否定・条件が変化する補正 | `review_required` |
| high assuranceが必要だが未設定 | `blocked`または`human_review_required`(降格しない) |

## 10. バリデーション

- `structured`の全要素が`raw`のlocatorへ追跡可能である。
- `auto_confirmed: true`は人間確認記録を伴う。
- transformation logに`input_hash`/`output_hash`が記録されている。

## 11. テスト観点

- originalが変更されない。
- rule処理とAI処理を区別できる。
- 改行修正前後を比較できる。
- 数字、否定、条件の変更をreview requiredにする。
- 目次整理がeconomyへルーティングされる。
- 高リスク補正がhigh assuranceまたは人間へ進む。
- 問題ページだけを再実行できる。
- 同一input hashでcache hitになる。
- structuredから元pageへ戻れる。

## 12. 移行・互換性

- 現行実装からの移行対象なし。
- 入力形式はタスク09〜12それぞれの出力(chunk/page result)と互換にする。

## 13. 未決定事項

- header/footerの既知パターンルールの具体的な実装(正規表現辞書等)
- 固有名詞候補が複数ある場合の優先順位付け方法
- AI実行単位(ページ単位/章単位)の最終的な粒度調整

## 14. 完了条件

- [x] 原文と補正後本文を比較できる。
- [x] 変換処理とAIモデルを追跡できる。
- [x] 章・節単位で後続処理へ渡せる。
- [x] 意味変更の可能性がある補正を自動承認しない。
- [x] 必要箇所だけを再処理できる。
- [x] AI通信量を抑える構造になっている。
- [x] 出力ドラフトが存在し、`status: review`である。
- [x] 実装コードを変更していない。

## 15. 停止・保留条件(該当状況)

- normalizedがoriginalを置き換える設計にはなっていない(5.1節で明確に分離)。
- 数式・コード・表を根拠なしで復元する要求はなく、5.6節で常に人間確認対象とした。
