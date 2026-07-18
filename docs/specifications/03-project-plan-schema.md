---
spec_id: 03-project-plan-schema
title: "企画書YAMLスキーマ"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_235129.txt"
---


# 企画書YAMLスキーマ

## 1. 目的

作品全体の目的、対象分野、対象読者、難易度、対象範囲、資料戦略、
章構成、話者方針、承認方針を、AIプロンプトへ依存せず定義する。

## 2. ファイル

```text
project/project-plan.yaml
```

## 3. planning stage

```text
registered
curriculum_draft
review_pending
approved
```

- `registered`: 作品登録段階。章0件を許可する。
- `curriculum_draft`: 資料と章構成を検討中。
- `review_pending`: 人間による企画確認待ち。
- `approved`: 企画承認済み。

`review_pending`と`approved`では、章を1件以上必要とする。

## 4. 資料戦略

```text
open_fulltext
hybrid_reconstruction
licensed_reference
```

一作品で複数指定してよい。

## 5. 最小スキーマ

```yaml
schema_version: "1.0"
project_id: database-foundations
content_revision: 1
title: データベース基礎
domain: database
purpose: データベースの基本を耳で学べるようにする
usage_purpose: personal_learning
planning_stage: registered

target_audience:
  description: ITを学び始めた成人

difficulty:
  vocabulary_level: elementary_4
  conceptual_level: adult_beginner

scope:
  included_topics: []
  excluded_topics: []

source_strategy:
  - hybrid_reconstruction

chapters: []

source_policy:
  technical_claims_require_sources: true
  ai_general_knowledge_allowed_for_ideation: true
  ai_generated_analogies_allowed: true
  unsupported_claim_policy: block

ai_policy:
  model_policy_id: default-gemini-routing
  budget_profile_id: personal-learning-default

narration:
  mode: single_speaker_per_chapter
  multi_speaker_schema_supported: true
  voice_selection_status: pending
  default_character_id: null
  default_voice_profile_id: null

approval_policy:
  required:
    - materials_curriculum
    - planning
    - verified_script
    - preview_audio
```

## 6. 完全例

```yaml
schema_version: "1.0"
project_id: database-foundations
content_revision: 2
series_id: hundred-year-knowledge
title: データベース基礎
subtitle: SQLと設計を学ぶための入口
domain: database
purpose: データベースの基本概念を耳で理解できるようにする
usage_purpose: personal_learning
planning_stage: review_pending

learning_outcomes:
  - データベースとRDBMSの役割を説明できる
  - テーブル、行、列の関係を説明できる

target_audience:
  description: ITを学び始めた成人
  assumed_knowledge:
    - パソコンの基本操作

difficulty:
  vocabulary_level: elementary_4
  conceptual_level: adult_beginner

scope:
  included_topics:
    - database
    - rdbms
    - table-row-column
  excluded_topics:
    - 高度な分散データベース設計

estimated_duration_minutes: 180

source_strategy:
  - hybrid_reconstruction
  - open_fulltext

chapters:
  - chapter_id: ch01
    order: 1
    title: データベースとは何か
    purpose: データベースの役割を理解する
    estimated_duration_minutes: 15
    spec_path: chapters/ch01/chapter-spec.yaml

source_policy:
  technical_claims_require_sources: true
  ai_general_knowledge_allowed_for_ideation: true
  ai_generated_analogies_allowed: true
  generated_supplements_must_not_be_presented_as_verified_facts: true
  unsupported_claim_policy: block

narration:
  mode: single_speaker_per_chapter
  multi_speaker_schema_supported: true
  voice_selection_status: pending
  default_character_id: null
  default_voice_profile_id: null

approval_policy:
  required:
    - materials_curriculum
    - planning
    - verified_script
    - preview_audio
```

## 7. 必須項目

すべての段階:

- `schema_version`
- `project_id`
- `content_revision`
- `title`
- `domain`
- `purpose`
- `usage_purpose`
- `planning_stage`
- `target_audience`
- `difficulty`
- `scope`
- `source_strategy`
- `source_policy`
- `narration`
- `approval_policy`

`review_pending`または`approved`:

- `learning_outcomes`
- 1件以上の章
- 4段階承認

## 8. 任意項目

- `series_id`
- `subtitle`
- `estimated_duration_minutes`
- `target_audience.assumed_knowledge`
- `narration.default_character_id`
- `narration.default_voice_profile_id`
- `ai_policy.model_policy_id`
- `ai_policy.budget_profile_id`

## 9. domain

初期想定例:

```text
marketing
philosophy
urban-planning
information-design
biology
game-theory
economics
psychology
database
system-design
```

新分野を追加できるよう固定列挙にはしない。

## 10. 資料方針

AI一般知識は、トピック候補、説明案、例え話、問いかけに使用してよい。

AI一般知識だけを技術的主張の最終根拠にしてはならない。


## 10.1 AIモデル方針

作品企画は物理モデル名を直接必須項目にしない。

```yaml
ai_policy:
  model_policy_id: default-gemini-routing
  budget_profile_id: personal-learning-default
```

`model_policy_id`は`18-ai-model-routing-and-cost-control.md`で定義された
論理層と物理モデルの対応を参照する。

作品ごとに物理モデルを上書きする場合も、
論理層の意味を変更してはならない。

## 11. 話者方針

```text
pending
provisional
selected
```

- `pending`: 未選択
- `provisional`: サンプル検証用
- `selected`: 承認済みprofile選択済み

試聴前には`provisional`または`selected`が必要である。
正式成果物出力前には`selected`をMUSTとする。

## 12. バリデーション

### Error

- 必須項目欠落
- `source_strategy`が空
- 未知の資料戦略
- 未知のplanning stage
- `review_pending|approved`で章0件
- 章IDまたはorder重複
- selectedなのにprofile参照なし
- 4段階承認の欠落

### Warning

- voice selectionがpending
- 再生時間見積もりなし
- 対象外が空
- シリーズ作品なのに`series_id`なし

## 13. 現行設定との関係

`book.json`は実行互換設定、
`project-plan.yaml`は内容企画として分離する。

旧TTS設定はvoice profileへ変換するが、
旧話者を自動的に正式採用扱いにしない。

## 14. テスト観点

- registeredで章0件を許可する。
- review pendingで章0件を拒否する。
- 三つの資料戦略を併用できる。
- 10分野を別projectで表現できる。
- 4段階承認欠落を検出する。
- selectedでprofile欠落を拒否する。
- AI一般知識だけの技術的主張をブロックする。
- ai policy参照先が存在する。
- 高性能モデル未設定時に高リスク検証を自動降格しない。

## 15. 完了条件

作品全体の内容要件、資料戦略、承認方針を、
AIモデル名やプロンプトを知らなくても判断できること。
