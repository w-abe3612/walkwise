---
spec_id: 04-chapter-generation-schema
title: "章単位の原稿生成仕様スキーマ"
status: approved
version: "1.2"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_235129.txt"
---

# 章単位の原稿生成仕様スキーマ

## 1. 目的

各章で何を、どの資料に基づき、どの順序と深さで説明するかを構造化する。

## 2. ファイル

```text
chapters/<chapter_id>/chapter-spec.yaml
```

## 3. 推奨スキーマ

```yaml
schema_version: "1.0"
project_id: database-introduction
chapter_id: ch01
content_revision: 1
order: 1
title: データベースとは何か
purpose: データベースの役割を理解する
learning_outcomes:
  - データとデータベースの違いを説明できる
required_topics:
  - topic_id: data
    title: データとは何か
  - topic_id: database
    title: データベースの役割
explanation_order:
  - data
  - database
required_examples:
  - 住所録
source_ids:
  - mysql-8-reference
  - database-design-for-mere-mortals
inherit:
  difficulty: true
  source_policy: true
overrides: {}
target:
  character_count: 3000
  estimated_duration_minutes: 15
prohibited:
  - 出典のない技術的断定
  - 未説明の専門用語
  - 条件や例外の削除
closing:
  summary_required: true
  review_questions: 2

ai_execution_policy:
  draft_tier: standard_generation
  claim_extraction_tier: economy_structuring
  final_review_tier: high_assurance_review
```

## 4. 継承

作品全体の難易度、資料方針、既定キャラクターと音声プロファイルは企画書から継承する。章ごとの差異だけを`overrides`へ記載する。

```yaml
overrides:
  difficulty:
    conceptual_level: intermediate
  character_id: neutral-explainer
```

何も変更しない場合は空objectとする。

## 5. 必須トピック

各トピックはIDを持ち、説明順から参照する。

```yaml
required_topics:
  - topic_id: primary-key
    title: 主キー
    requirements:
      - 一意性を説明する
      - NULLとの関係を説明する
```

## 6. 資料

章単位で使用可能な出典を明示する。原稿生成AIは、指定された資料外の技術的断定を追加してはならない。外部補足が必要な場合は、主張を`pending`として記録する。

## 7. プロンプトとの分離

`chapter-spec.yaml`は正式要件である。特定AI向けプロンプトは派生物として生成する。

```text
chapter-spec.yaml
  ↓ prompt builder
prompts/ch01-draft.md
```

プロンプト変更によって章要件が失われないよう、プロンプトへスキーマ内容を埋め込む。


## 7.1 AIモデルルーティング

章仕様は物理モデル名ではなく、AIタスクの論理層を指定できる。

```yaml
ai_execution_policy:
  draft_tier: standard_generation
  claim_extraction_tier: economy_structuring
  final_review_tier: high_assurance_review
```

初期割当て:

- 初稿: Gemini 2.5 Flash
- 主張候補抽出: Gemini 2.5 Flash-Lite
- 出典矛盾・難しい技術検証・最終レビュー: 承認済み高性能モデル

生成時は、章に必要なsource chunkだけを渡す。
資料全文を毎回入力してはならない。

## 8. バリデーション

- 企画書に存在しない`chapter_id`はerror。
- `required_topics[].topic_id`重複はerror。
- explanation orderに未知topicがあればerror。
- source_idsの参照先欠落はerror。
- 目標文字数は正の整数。
- 終了時の学習成果が空ならwarning。

## 9. 生成結果の要件

生成された初稿は、次を記録する。

- 使用したchapter spec revision
- 使用したsource revision
- 論理モデル層
- 物理AIモデルとプロンプトバージョン
- 入力source chunk IDとhash
- トークン使用量
- 生成した技術的主張一覧
- 要件を満たせなかった項目

## 10. 現行実装との関係

現行のGeminiプロンプトファイル群は個別処理の指示を保持している。本仕様導入後は、固定プロンプトへ章仕様を追加して生成する。既存プロンプトを直ちに削除しない。

## 11. テスト観点

- 継承と上書きが正しく解決される。
- 未知topic参照を拒否する。
- 章仕様からプロンプトを再現可能に生成できる。
- 同じ章仕様から異なるAIモデル用プロンプトを作れる。
- 章初稿がstandard generationへルーティングされる。
- 主張候補抽出がeconomy structuringへルーティングされる。
- high assurance未設定時に最終レビューを自動降格しない。

## 12. 完了条件

AIモデル名やプロンプト文面を知らなくても、章の完成条件を本スキーマから判断できること。
