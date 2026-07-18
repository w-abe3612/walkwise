---
spec_id: 06-claims-and-sources
title: "技術的主張と出典の管理仕様"
status: approved
version: "1.1"
approved_at: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_235129.txt"
last_updated: "2026-07-19"
---

# 技術的主張と出典の管理仕様

## 1. 目的

教材内の技術的事実を検証可能にし、AI生成の例え話や補足と区別する。

## 2. 基本方針

- 技術的事実には出典をMUSTとする。
- AIによる一般説明、例え話、問いかけはMAYとする。
- AI生成補足を確認済み事実として断定してはならない。
- 出典が確認できない技術的主張は、初期値`block`で完成原稿へ入れない。

## 3. ファイル

```text
project/sources.yaml
chapters/<chapter_id>/claims.yaml
chapters/<chapter_id>/reports/fact-check.json
```

## 4. 出典スキーマ

```yaml
schema_version: "1.0"
sources:
  - source_id: mysql-8-reference
    title: MySQL 8.0 Reference Manual
    source_type: official_documentation
    priority: primary
    publisher: Oracle
    edition_or_version: "8.0"
    locator_base: null
    rights:
      status: unverified
      usage_purpose: personal_learning
```

`rights.status`は資料入力パイプラインが未策定のため、現時点では情報記録に留め、利用可否を自動保証しない。

## 5. 主張スキーマ

```yaml
schema_version: "1.0"
project_id: database-introduction
chapter_id: ch01
claims:
  - claim_id: ch01-claim001
    statement: 主キーはテーブル内の行を一意に識別するために使われます。
    claim_type: technical_fact
    status: verified
    source_evidence:
      - source_id: mysql-8-reference
        locator:
          section: Primary Key Optimization
        support: direct
    verification:
      checked_at: "2026-07-18T21:00:00+09:00"
      checked_by: ai_with_human_approval
      notes: null
```

## 6. claim_type

- `technical_fact`
- `definition`
- `numeric_fact`
- `version_specific_behavior`
- `limitation`
- `comparison`
- `causal_claim`
- `generated_analogy`
- `generated_explanation`
- `opinion`

`generated_analogy`と`generated_explanation`は、事実主張とは別の検査を行う。

## 7. status

- `pending`
- `verified`
- `partially_verified`
- `conflict`
- `unsupported`
- `rejected`
- `human_review_required`

完成原稿へ入れられるのは、原則として`verified`と、人間承認済みの`partially_verified`だけとする。

## 8. 出典優先順位

1. ユーザー指定資料
2. 公式文書・仕様書
3. 査読論文
4. 教科書・専門書
5. 信頼できる解説
6. その他のWeb情報

Wikipediaは調査の入口には使えるが、技術的事実の最終根拠にはしない。

## 9. 資料間の矛盾

```yaml
status: conflict
conflict:
  source_ids:
    - source-a
    - source-b
  resolution: human_review_required
```

システムは黙って一方を選ばない。


## 9.1 AIモデルルーティング

主張処理では、抽出と検証を分離する。

```text
主張候補抽出
＝ economy_structuring
＝ 初期モデル Gemini 2.5 Flash-Lite

通常の出典対応
＝ standard_generation
＝ 初期モデル Gemini 2.5 Flash

出典間矛盾・難しい技術検証
＝ high_assurance_review
＝ 承認済み高性能モデル
```

Flash-Liteが抽出した主張候補は、初期状態を`pending`とする。

高性能モデルを使用しても、AI出力だけで`verified`にしてはならない。
確認可能なsource evidence、locator、人間承認が必要である。

高性能モデルが未設定の場合、conflictや難しい技術検証は
`human_review_required`または`blocked`とする。

## 10. 例え話の検証

AI生成の例え話は次を確認する。

- 同一視しすぎていないか。
- 重要な制約が失われていないか。
- 初心者に誤解を与えないか。
- 例えの限界を補足する必要がないか。

```yaml
analogy_review:
  false_equivalence: pass
  missing_limitations: warning
  misleading_simplification: pass
```

## 11. 出典の粒度

可能な範囲で、章、節、ページ、版、URL内位置を記録する。

```yaml
locator:
  chapter: "13"
  section: "13.1.20"
  page: 312
```

資料全文だけを指定して位置がない場合はwarningとするが、処理を必ず停止する必要はない。

## 12. 現行データとの関係

現行のmindmap `chunks.json`には`source_range`があるが、ページがnullの例もある。この情報は出典位置の候補として取り込めるが、技術的主張の検証済み証拠とはみなさない。

## 13. テスト観点

- 未検証技術主張を完成原稿からブロックする。
- 例え話は出典なしでも許可されるが種別が必要。
- 存在しないsource IDを検出する。
- conflict状態で承認工程を停止する。
- 出典の版が変わった場合に該当主張を再検証対象にする。
- 主張候補抽出だけでstatusをverifiedにできない。
- conflictがhigh assuranceへ昇格する。
- high assurance未設定時にstandardへ黙って降格しない。

## 14. 完了条件

検証済み原稿の各技術的主張について、出典と検証状態を追跡できること。
