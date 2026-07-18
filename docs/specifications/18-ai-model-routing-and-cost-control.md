---
spec_id: 18-ai-model-routing-and-cost-control
title: "AIモデルルーティング・資料構築・コスト制御仕様"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_235129.txt"
---

# AIモデルルーティング・資料構築・コスト制御仕様

## 1. 目的

資料候補の提案、資料抽出後の構造化、トピック整理、原稿生成、
主張検証、最終レビューで使用するAIモデルを、処理の難易度とリスクに応じて
選択する方法を定義する。

本仕様は、次を同時に満たすことを目的とする。

- 単純な処理へ高価なモデルを使用しない。
- 難しい技術検証を低コストモデルだけで確定しない。
- 資料全文を工程ごとに繰り返し送信しない。
- モデル名変更がコンテンツ仕様へ波及しない。
- AI処理の入力、出力、モデル、プロンプト、トークン使用量を追跡できる。
- 無料原典型、資料群構築型、購入資料OCR型を同じ上位フローで扱う。

---

## 2. 対象範囲

- 無料公開資料候補の提案
- シラバス、目次、索引の整理
- トピック抽出
- 資料要求表とcoverage mapの作成
- OCR・抽出結果の低リスクな形式変換
- 主張候補抽出
- 章初稿
- 分かりやすさ変換
- 音声向け変換
- 出典間の矛盾検出
- 難しい技術検証
- 意味保存の最終レビュー
- キャッシュ
- Batch処理
- 使用量・概算費用の記録
- モデルの昇格と差し戻し

---

## 3. 対象外

- AIの出力を法的判断として保証すること
- AIの自己申告したconfidenceだけで正確性を確定すること
- 人間承認の省略
- 利用者が取得していない市販資料の自動取得
- DRM回避
- モデル価格を仕様へ固定すること
- 一つのモデルを全工程へ強制すること

---

## 4. 基本原則

### 4.1 論理モデル層を使用する

処理仕様は物理モデル名ではなく、次の論理層を参照する。

```text
economy_structuring
standard_generation
high_assurance_review
```

物理モデルは設定で解決する。

### 4.2 技術的主張の根拠は資料である

高性能モデルを使用しても、その出力自体を出典にしてはならない。

AIは次を担当する。

- 主張候補の抽出
- 関連資料候補の提示
- 資料間差分の整理
- 検証報告の作成

技術的主張の承認には、確認可能な資料とlocatorが必要である。

### 4.3 高性能モデルは例外経路とする

高性能モデルを、全資料・全章・全セグメントへ常時使用しない。

次の場合だけ昇格する。

- 出典が矛盾する。
- 版や条件によって挙動が異なる。
- 数式、コード、標準仕様などの難しい検証である。
- 低コストモデルの出力がschema検証を繰り返し失敗する。
- 意味保存の最終検査で重大な差分候補がある。
- 人間が明示的に指定する。

### 4.4 資料全文を繰り返し送らない

資料は一度、チャンク化・構造化・索引化する。

後続処理には、対象章に必要なチャンクだけを渡す。

### 4.5 AI出力を上書きしない

AI処理前後の成果物を分離し、input hashとoutput hashを記録する。

---

## 5. 論理モデル層

## 5.1 economy_structuring

初期物理モデル:

```text
gemini-2.5-flash-lite
```

主な用途:

- 目次整理
- 見出し階層の正規化
- トピック抽出
- 用語候補抽出
- 主張候補抽出
- source summaryの作成
- topic indexの作成
- coverage mapの一次作成
- JSON、YAML、Markdown間の形式変換
- 既に内容が確定した文章の機械的構造化
- 低リスクなOCR改行修正候補
- 章・ページ・節の分類

禁止または単独確定不可:

- 出典間の矛盾解決
- 難しい技術的主張の最終判定
- OCRされた数式・コード・表の意味確定
- 検証済み原稿の最終承認判定

## 5.2 standard_generation

初期物理モデル:

```text
gemini-2.5-flash
```

主な用途:

- 章初稿
- 資料に基づく通常説明
- 分かりやすさ変換
- 音声向け変換
- 例え話案
- 復習問題案
- カリキュラム案の統合
- 複数チャンクを用いた章単位の説明生成
- 軽度な意味保存検査

禁止または単独確定不可:

- 矛盾資料の黙示的な採択
- 出典なしの技術的断定
- 最終レビューの自動承認
- 利用権の法的確定

## 5.3 high_assurance_review

物理モデル:

```text
利用時点で承認した高性能モデル
```

環境変数例:

```text
GEMINI_MODEL_HIGH_ASSURANCE
```

主な用途:

- 出典間の矛盾分析
- 難しい技術検証
- 版依存・条件依存の挙動確認
- 数式、コード、標準仕様を含む高リスク確認
- 変換前後の最終意味保存レビュー
- 人間レビュー用の論点整理

高性能モデルが未設定の場合:

- 該当処理を`blocked`または`human_review_required`にする。
- `standard_generation`へ黙って降格しない。
- 技術的主張を`verified`へ変更しない。

---

## 6. モデル解決設定

```yaml
schema_version: "1.0"
ai_model_policy_id: default-gemini-routing
content_revision: 1

provider: google

tiers:
  economy_structuring:
    model: gemini-2.5-flash-lite
    env_override: GEMINI_MODEL_ECONOMY
  standard_generation:
    model: gemini-2.5-flash
    env_override: GEMINI_MODEL_STANDARD
  high_assurance_review:
    model: null
    env_override: GEMINI_MODEL_HIGH_ASSURANCE
    required_when_invoked: true

fallback:
  economy_to_standard: allowed_with_warning
  standard_to_high_assurance: explicit_escalation_only
  high_assurance_to_standard: prohibited

execution:
  prefer_batch_for_non_interactive_bulk: true
  cache_enabled: true
  record_usage_metadata: true
```

保存候補:

```text
project/ai/model-policy.yaml
```

プロジェクト固有設定がない場合は、システム既定policyを使用する。

---

## 7. 資料構築の共通ループ

```text
作品目的・対象範囲を登録
↓
必要トピックの仮説を作る
↓
資料候補または既存資料を登録
↓
抽出・OCR・正規化
↓
source summaryとtopic indexを作る
↓
coverage mapを作る
↓
不足・重複・矛盾を検出
↓
追加資料の提案または再処理
↓
必要範囲が満たされるまで反復
↓
資料・カリキュラム承認
```

AIが資料候補を提案しても、取得と採用は人間が確認する。

---

## 8. 資料戦略別フロー

## 8.1 open_fulltext

対象例:

- 無料教科書
- パブリックドメイン原典
- 大学公開教材
- オープンアクセス論文
- 公的機関・学会資料

処理:

```text
AIが候補と検索語を提案
↓
人間が選択・取得
↓
本文抽出
↓
章構造・用語・topicをeconomy層で整理
↓
複数資料のcoverageを作成
↓
不足を追加探索
↓
カリキュラム統合
```

原典と解説資料は役割を分ける。

```text
原典
＝ 著者自身の記述の根拠

解説・研究資料
＝ 歴史的位置付け、解釈、比較の根拠
```

## 8.2 hybrid_reconstruction

対象例:

- データベース
- 資格試験
- 公式マニュアルと複数教科書を組み合わせる分野

処理:

```text
シラバス・公開目次を整理
↓
topic requirement matrixを作る
↓
各topicに必要な資料役割を定義
↓
公式資料・無料教科書・専門資料を登録
↓
coverage mapを作る
↓
不足topicの資料を追加提案
↓
資料が充足するまで反復
↓
独自カリキュラムを作る
```

公開目次やシラバスは`curriculum_structure`として使用し、
技術的事実の最終根拠にしない。

## 8.3 licensed_reference

対象例:

- 購入済みKindle
- 購入済みPDF
- 市販書籍の個人学習利用

処理:

```text
利用目的・権利情報を登録
↓
人間が原資料を用意
↓
直接抽出または画面キャプチャ
↓
OCR
↓
rawを保存
↓
normalizedを作る
↓
structuredを作る
↓
低信頼箇所を人間確認
↓
topic indexとcoverage mapを作る
```

次は高リスクとして自動確定しない。

- 数式
- コード
- UML・アーキテクチャ図
- 表
- 脚注
- 固有名詞
- ページをまたぐ文
- 英数字が混在する箇所

---

## 9. 資料構築成果物

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
└─ manifests/
   └─ chunk-manifest.json
```

### source-summary.yaml

資料ごとの目的、範囲、役割、版、注意点を記録する。

### topic-index.yaml

topicとsource chunkの対応を記録する。

### coverage-map.yaml

必要topicごとの充足状態を記録する。

```text
covered
partially_covered
conflict
missing
not_applicable
```

### chunk-manifest.json

チャンク順、source locator、input hash、生成物を記録する。

---

## 10. 工程別ルーティング

| 工程 | 論理層 | 備考 |
|---|---|---|
| 資料候補の検索語・候補案 | economy | 実際の取得・採用は人間 |
| 目次整理 | economy | schema検証必須 |
| トピック抽出 | economy | topic重複を機械検査 |
| source summary | economy | locatorを保持 |
| coverage map一次作成 | economy | 不足判定を人間確認 |
| 主張候補抽出 | economy | `verified`へしない |
| 形式変換 | economy | 意味変更禁止 |
| カリキュラム統合 | standard | 元topicとsourceを参照 |
| 章初稿 | standard | 指定資料外の断定禁止 |
| 分かりやすさ変換 | standard | 条件・例外を保持 |
| 音声向け変換 | standard | `text`を正本として保持 |
| 出典間矛盾分析 | high assurance | 人間確認必須 |
| 難しい技術検証 | high assurance | 証拠locator必須 |
| 最終意味保存レビュー | high assurance | 承認自体は人間 |

---

## 11. 昇格条件

economyまたはstandardの結果をhigh assuranceへ送る条件:

- source statusが`conflict`
- claim typeが`version_specific_behavior`
- claim typeが`numeric_fact`かつ資料差がある
- 重要な条件・例外が失われた疑い
- OCR warningに`formula`、`code`、`table`が含まれる
- schema修復を2回以上行っても不正
- 引用位置を一意に決められない
- 人間が`escalate`を指定

昇格時は、元入力全部ではなく、関連チャンクと差分だけを渡す。

---

## 12. キャッシュ

キャッシュキーは最低限次を含む。

```text
task_type
logical_tier
physical_model
prompt_id
prompt_version
input_hash
schema_version
generation_parameters
```

同じキーの成功結果は再利用してよい。

次の場合は再利用しない。

- source revision変更
- prompt major version変更
- schema major version変更
- model変更を再検証条件に指定した場合
- 過去結果がwarningまたはreview required
- 人間が再生成を指定

---

## 13. チャンクとコンテキスト

- 章原稿は原則として章単位で生成する。
- 資料は必要なチャンクだけを取得する。
- 通常生成をセグメントごとの全工程に分割しない。
- 問題箇所の修正だけをセグメント単位で行う。
- チャンクには前後関係を復元できるlocatorを持たせる。
- 大きな資料のsummaryだけで技術的主張を検証しない。
- 引用・事実確認時は原資料チャンクを使用する。

---

## 14. Batch処理

即時応答が不要な次の処理はBatch候補とする。

- 大量ページの目次・見出し整理
- source summary
- topic extraction
- claim candidate extraction
- 複数章の形式変換
- coverage mapの再計算

人間の対話が必要な次は通常リクエストとする。

- 企画レビュー
- source conflict review
- 最終レビュー
- 差し戻し対応

Batch利用有無を生成記録へ残す。

---

## 15. 使用量・費用記録

各AI実行は次を記録する。

```yaml
ai_execution:
  task_type: chapter_draft
  logical_tier: standard_generation
  provider: google
  model: gemini-2.5-flash
  api_version: v1beta
  prompt_id: chapter-draft
  prompt_version: "1.0"
  input_hashes:
    - "..."
  output_hash: "..."
  batch: false
  usage:
    input_tokens: 0
    output_tokens: 0
    total_tokens: 0
  cost:
    currency: USD
    estimated_amount: null
    pricing_snapshot_id: null
```

価格はコードへ固定せず、取得日付きのpricing snapshotから概算する。

usage情報が取得できない場合は`null`とし、推測値を実測値として保存しない。

---

## 16. 予算制御

設定例:

```yaml
budget:
  project_warning_usd: 5.0
  project_stop_usd: 20.0
  single_request_warning_tokens: 200000
  allow_high_assurance_auto_escalation: false
```

- warning到達後も処理継続は可能。
- stop到達後は人間承認が必要。
- 高性能モデルの自動昇格可否を設定可能にする。
- 再試行も使用量へ含める。
- cache hitは新しいAPI使用量へ含めない。

---

## 17. エラー・警告

### Error

- 論理層が未知
- high assuranceが必要なのにモデル未設定
- 必須source chunk欠落
- input hash欠落
- 出力schema不正かつ修復上限超過
- budget stop超過
- 技術検証をsummaryだけで確定しようとした
- source conflictを自動解消して`verified`にした

### Warning

- economyからstandardへfallback
- Batch非対応により通常実行
- usage metadata欠落
- pricing snapshot欠落
- contextが大きい
- cache miss
- OCR低信頼箇所を含む
- 高性能モデルを単純形式変換へ使用

### Human review required

- 出典矛盾
- 難しい技術検証
- OCRされた数式・コード・表
- 最終意味保存レビューの重大差分
- budget stop解除
- 利用目的・権利状態の変更

---

## 18. 現行実装への影響

現在のGeminiクライアントは、単一の`GEMINI_MODEL`を既定値として使用している。

実装時は次へ拡張する。

```text
GEMINI_MODEL_ECONOMY
GEMINI_MODEL_STANDARD
GEMINI_MODEL_HIGH_ASSURANCE
```

必要な追加責務:

- logical tier resolver
- task typeとtierの対応表
- model override
- usage metadata取得
- input/output hash記録
- cache
- budget counter
- Batch adapter
- escalation result

既存`GEMINI_MODEL`は移行期間中、
`GEMINI_MODEL_STANDARD`の互換入力として扱ってよい。

---

## 19. テスト観点

- 目次整理がeconomyへルーティングされる。
- 章初稿がstandardへルーティングされる。
- conflictがhigh assuranceへ昇格する。
- high assurance未設定時に黙って降格しない。
- 同一入力でcache hitになる。
- source revision変更でcache missになる。
- 全資料ではなく必要チャンクだけが入力になる。
- 形式変換で入力内容が失われない。
- AI実行記録にモデルとprompt versionが残る。
- usage metadata欠落をwarningにする。
- budget stopで処理を停止する。
- Batchと通常実行の結果schemaが同じになる。
- 技術的主張をAI出力だけでverifiedにできない。

---

## 20. 完了条件

- 全AI工程が論理モデル層へ分類されている。
- Flash-Lite、2.5 Flash、高性能モデルの役割が明示されている。
- 無料原典型、資料群構築型、購入資料OCR型のフローが定義されている。
- 資料収集とcoverage分析を反復できる。
- 資料全文を各工程で再送しない。
- モデル変更が章仕様や原稿schemaを変更しない。
- 高リスク処理を低コストモデルだけで自動確定しない。
- AI実行履歴と使用量を追跡できる。
- キャッシュと予算上限を設定できる。
- 人間承認を省略しない。
