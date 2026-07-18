---
task_type: specification_decision
status: draft
order: 13
title: "書籍データ前処理"
depends_on:
  - 9_pdf-direct-text-extraction.md
  - 10_ocr-and-scanned-pdf.md
  - 11_epub-text-extraction.md
  - 12_kindle-capture.md
spec_refs:
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/source-preprocessing.md"
last_updated: "2026-07-19"
---

# 13. 書籍データ前処理

## 1. 目的

抽出本文からヘッダー、ページ番号、不自然な改行、重複を除去し、
章・節・図表・コード・数式を、原文へ戻れる形で構造化する。

## 2. 決定する事項

- raw、normalized、structuredの境界
- 決定的なルール処理
- AI補正を許可する範囲
- 改行結合とhyphen修正
- header、footer、page number
- 重複・抜け
- 章・節・目次
- 図表、脚注、コード、数式
- AIモデルルーティング
- 差分、hash、usage
- 人間確認条件

## 3. 処理順

```text
raw
↓
決定的なルール処理
↓
normalized candidate
↓
差分検査
↓
AIによる低リスク構造化
↓
高リスク箇所の抽出
↓
人間またはhigh assurance review
↓
structured
```

ルールベース処理を先に行う。

## 4. economy structuring

初期モデル:

```text
Gemini 2.5 Flash-Lite
```

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

## 5. standard generation

初期モデル:

```text
Gemini 2.5 Flash
```

用途:

- 複数ページから章構造を統合する。
- 読み順候補を比較する。
- 通常本文の自然な段落復元案を作る。
- 人間確認用の差分説明を作る。

原文を上書きしてはならない。

## 6. high assurance review

用途:

- 数式、コード、表の復元候補比較
- 技術的意味が変わる可能性のある補正
- 複数候補が競合する読み順
- 最終意味レビュー

高性能モデルの結果も、人間確認なしにoriginal相当へ昇格しない。

## 7. AI実行単位

- ページ単位でrawとlocatorを保持する。
- 通常本文は複数ページをまとめてもよい。
- 長い資料を全ページまとめて送らない。
- 同じheader/footer判定はルール化して再利用する。
- 問題ページだけを再実行する。
- 同じinput hashの成功結果をcacheする。

## 8. 差分

各変換は次を記録する。

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

## 9. review required

- OCR confidenceが閾値未満
- 数式
- コード
- 表
- UML・アーキテクチャ図
- 脚注参照が不明
- ページ欠落
- 固有名詞候補が複数
- 数字または単位が変化
- 否定、条件、例外が変化
- economyとstandardの結果が不一致
- high assuranceが必要だが未設定

## 10. コスト制御

- 決定的処理をAIより先に行う。
- 変更がないページをAIへ送らない。
- header/footerの繰り返し除去をAIへ毎回依頼しない。
- source summaryとtopic indexを再利用する。
- 大量の単純変換はBatch候補とする。
- usageと再試行回数を記録する。

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

## 12. 成果物

```text
docs/specifications/source-preprocessing.md
```

## 13. 完了条件

- 原文と補正後本文を比較できる。
- 変換処理とAIモデルを追跡できる。
- 章・節単位で後続処理へ渡せる。
- 意味変更の可能性がある補正を自動承認しない。
- 必要箇所だけを再処理できる。
- AI通信量を抑える構造になっている。
