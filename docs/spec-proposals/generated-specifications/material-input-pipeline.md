---
spec_id: material-input-pipeline
title: "資料入力パイプラインの責務と境界"
status: review
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/06_material-input-pipeline.md
  source_task: docs/spec-proposals/task/6_material-input-pipeline-boundary.md
depends_on: []
spec_refs:
  - ../../specifications/audiobook-creation-pipeline.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
  - ../../specifications/01-common-identifiers-and-versioning.md
  - ../material-input-pipeline-unplanned.md
---

# 資料入力パイプラインの責務と境界(ドラフト)

## 1. 目的

無料公開資料(`open_fulltext`)、複数資料の組み合わせによる再構築
(`hybrid_reconstruction`)、購入済みKindle・PDF・カメラ写真・スキャナ画像・OCR(`licensed_reference`)を、
上位仕様`audiobook-creation-pipeline.md`が定義する資料入力パイプラインとして具体化し、
コンテンツ作成パイプラインへ検索可能・引用可能・章へ割当て可能な資料セットを渡す
責務と境界を定義する。

## 2. 対象範囲

- 資料入力パイプラインの開始点・終了点
- `open_fulltext`/`hybrid_reconstruction`/`licensed_reference`の共通終了形式への収束
- AIが担当してよい範囲・担当してはならない範囲
- 資料収集の反復構造(一度で完了としない)
- 手動資料からの後続処理開始
- カメラ写真・スキャナ画像からの画像取り込み経路
- AIモデルルーティングの適用

## 3. 対象外

- 資料保存の物理ディレクトリ構成と共通schemaの詳細(→タスク07)
- 権利・ライセンス状態の詳細な分類(→タスク08)
- PDF/OCR/EPUB/Kindleそれぞれの抽出仕様の詳細(→タスク09〜12)
- 前処理の詳細な変換ルール(→タスク13)
- 資料の法的利用可否の最終判断(常に人間または専門家)

## 4. 現行実装

現行コードには専用の資料入力パイプライン実装は存在しない
(`docs/spec-proposals/material-input-pipeline-unplanned.md`が示す通り、全項目が未策定)。
`dumps/`配下には資料入力の元となったテキストダンプが手動で置かれているのみである。
本書は、この未着手状態に対する最初の責務境界の確定を行う。

## 5. 推奨仕様

### 5.1 開始点

質問1(資料入力の開始点と終了点)への回答: 次のいずれからも開始できる。

1. テーマ・対象範囲だけがある。
2. URLや資料候補がある。
3. PDF、EPUB、テキストがある。
4. Kindle等の購入済み資料がある。
5. 既存OCR結果がある。
6. 人間が作成した構造化資料がある。

資料入力パイプラインの完成を待たず、手動構造化資料から後続処理(コンテンツ作成)を
開始できる。これは上位仕様`audiobook-creation-pipeline.md` 4.4節「資料入力方式を固定しない」
と一致する。

### 5.2 終了点

次を満たした資料セットをコンテンツ作成側へ渡す。

- `source_id`がある。
- 原資料または確認可能な参照先がある。
- versionまたは取得日時がある。
- source roleがある(`audiobook-creation-pipeline.md` 7節の役割一覧を使用)。
- source locatorを保持できる。
- normalizedまたはstructured本文がある。
- chunk manifestがある。
- source summaryがある。
- topic indexがある。
- coverage mapがある。
- rightsとusage purposeが記録されている(タスク08で詳細化)。
- 低信頼箇所とwarningが明示されている。
- 資料・カリキュラム承認の対象にできる。

### 5.3 共通処理フロー

質問2(3種類の資料戦略をどう統一するか)への回答:
3戦略を次の共通処理へ収束させ、終了時点の資料schemaを共通化する
(schemaの詳細はタスク07)。

```text
作品目的・対象範囲を登録
↓
資料戦略を選択
↓
必要topicの仮説を作る
↓
資料候補または原資料を登録
↓
利用目的・権利情報を記録
↓
直接抽出またはOCR
↓
rawを保存
↓
normalizedを作る
↓
structuredを作る
↓
source summaryとtopic indexを作る
↓
coverage mapを作る
↓
不足・重複・矛盾を分析
↓
必要に応じて資料追加または再処理
↓
資料・カリキュラム承認
```

質問4(資料収集を一回で完了とするか)への回答: **しない。**
coverage不足の検出から資料追加または再処理へ戻る反復ループとして設計する。

質問5(手動資料から後続処理を開始できるか)への回答: **できる。**
資料入力機能の完成をコンテンツ作成側の前提条件にしない。

### 5.4 戦略別の経路

#### 5.4.1 open_fulltext

対象: 無料教科書、パブリックドメイン原典、大学公開教材、オープンアクセス論文、
公的機関・学会資料。

```text
AIが候補・検索語・資料役割案を提示
↓
人間が資料を選択・取得
↓
本文と目次を抽出
↓
AIが章構造・topic・用語を整理(economy)
↓
複数資料のcoverageを作成
↓
不足topicの追加資料を提案
↓
カリキュラムを再構築(standard)
```

原典(著者自身の記述の根拠)と解説・研究資料(歴史的位置付け・解釈・比較の根拠)は
役割を分ける。

#### 5.4.2 hybrid_reconstruction

対象: データベース、資格試験、公式マニュアルと複数教科書を組み合わせる分野。

```text
シラバス・公開目次を収集
↓
topic requirement matrixを作成
↓
topicごとに必要な資料役割を決定
↓
公式資料・無料教科書・専門資料を登録
↓
coverage mapを作成
↓
不足topicを追加探索
↓
根拠資料が揃うまで反復
↓
独自カリキュラムを作成
```

公開目次・シラバスは`curriculum_structure`役割として使用し、
技術的事実の最終根拠にはしない(`audiobook-creation-pipeline.md` 7.1節と一致)。

#### 5.4.3 licensed_reference

対象: 購入済みKindle、購入済みPDF、市販書籍、人間が利用権を確認した資料。

```text
利用目的とrights状態を登録
↓
人間が原資料を用意
↓
直接抽出または画面キャプチャ
↓
OCR
↓
raw、normalized、structuredを分離
↓
低信頼箇所を人間が確認
↓
topic indexとcoverage mapを作成
```

DRM回避や市販本文の自動取得は対象外とする。

### 5.5 AIモデルルーティング

`18-ai-model-routing-and-cost-control.md`に従う。

| 論理層 | 初期モデル | 用途 |
|---|---|---|
| `economy_structuring` | Gemini 2.5 Flash-Lite | 目次整理、topic抽出、source summary、coverage map一次作成、形式変換、主張候補抽出、低リスクOCR整形候補 |
| `standard_generation` | Gemini 2.5 Flash | カリキュラム統合、章構成案、資料に基づく説明案 |
| `high_assurance_review` | 利用時点で承認した高性能モデル | 出典間の矛盾、難しい技術検証、OCRされた数式・コード・表の確認支援、最終意味レビュー |

高性能モデル未設定時は、`standard_generation`へ黙って降格せず人間確認へ差し戻す。

### 5.6 AIに許可すること

- 資料候補と検索語の提案
- 目次・見出し整理
- topic候補抽出
- source role候補の提示
- source summary作成
- coverage map作成
- 不足topic検出
- OCR修正候補の提示
- 構造化候補の提示
- 矛盾論点の整理

### 5.7 AIに許可しないこと

- 資料の利用可否を法的に保証する。
- 存在しない引用位置を作る。
- OCR原文を上書きする。
- 出典のない技術的主張を`verified`にする。
- 公開目次を事実根拠へ昇格する。
- source conflictを黙って解消する。
- 数式、コード、図表の不確かな復元を自動承認する。
- 購入資料を自動公開する。

質問3(AIが担当してよい範囲)への回答: 5.6/5.7節の通り、
候補提案・構造化・topic/coverage分析・不足検出に限定し、
権利・事実・意味の最終確定は行わない。


### 5.8 資料戦略とmedia typeの分離

資料の収集・利用戦略と、入力ファイルの物理形式を分ける。

```yaml
source_strategy:
  - licensed_reference

media:
  type: image_sequence
  acquisition_method: camera_photo
```

`source_strategy`候補:

- `open_fulltext`
- `hybrid_reconstruction`
- `licensed_reference`

`media.type`候補:

- `text`
- `pdf`
- `epub`
- `image_sequence`
- `kindle_capture`
- `manual_structured`

`acquisition_method`候補:

- `camera_photo`
- `flatbed_scanner`
- `sheetfed_scanner`
- `mobile_scan_app`
- `existing_image_file`
- `kindle_capture`

カメラ写真・スキャナ画像は
`../../specifications/image-material-ingestion.md`へ従う。

動画・録音は現在の正式対象へ含めず、
`../video-source-ingestion.md`と
`../audio-recording-source-ingestion.md`で将来案として管理する。

## 6. 正本と派生物

| 段階 | 位置付け |
|---|---|
| 原資料 | 不変の正本 |
| extracted | 抽出ツールの派生物 |
| normalized | 補正済み派生物 |
| structured | コンテンツ作成向け派生物 |
| source summary | 索引用派生物 |
| topic index | 検索用派生物 |
| coverage map | 計画用派生物 |
| curriculum | 人間承認対象 |

AI生成物だけを原資料の代替にしない。

## 7. コスト制御

- 資料全文は原則として一度だけ構造化する。
- 後続工程では必要なchunkだけを使用する。
- 同じinput hashとprompt versionの結果を再利用する。
- 大量の目次整理、topic抽出、形式変換はBatch候補とする。
- 再試行を含めたusageを記録する。
- 高性能モデルの自動昇格可否を設定する。
- project予算上限を超えたら人間確認へ停止する。

詳細は`18-ai-model-routing-and-cost-control.md`の予算制御(16節)に従う。

## 8. 入力

- 作品目的・対象範囲・資料戦略(`project-plan.yaml`初期版相当)
- 資料候補、URL、原資料ファイル、既存OCR結果、手動構造化資料のいずれか
- 利用目的・権利情報(タスク08確定前は暫定的に`unverified`扱い)

## 9. 出力

- 6.1節の終了条件を満たす資料セット
- source summary、topic index、coverage map
- 人間確認待ちのreview-requiredレポート

## 10. 正常系

1. 資料戦略を1件以上選択して作品へ登録する。
2. 選択した戦略の経路(5.4節)に従って資料を登録・抽出・正規化・構造化する。
3. source summaryとtopic indexを作成する。
4. coverage mapを作成し、不足topicを検出する。
5. 不足があれば資料追加または再処理を行い、4〜5を繰り返す。
6. coverageが充足したら、資料・カリキュラム承認へ提出する。

## 11. 異常系

| 問題 | 状態 | 差し戻し先 |
|---|---|---|
| 資料不足 | `blocked` | 資料一覧作成(5.3節) |
| 資料の利用目的不明 | `review_required` | 資料登録・権利情報記録 |
| 重要topic欠落 | `changes_requested` | coverage map・追加資料提案 |
| 資料間の矛盾 | `human_review_required` | high_assurance_reviewまたは人間確認 |
| 公開目次のみを事実根拠に使用しようとした | `blocked` | AIに許可しないこと(5.7節)違反として拒否 |
| 資料全文を毎回AIへ送ろうとした | `warning` | チャンク化の見直し |

## 12. バリデーション

- 資料戦略が1件以上指定されている。
- `curriculum_structure`のみの資料役割を`factual_evidence`として使用していない。
- 同一資料を複数作品から参照できる(資料自体は複製しない)。
- coverage状態が`missing`のtopicに`next_action`が設定されている。
- AI生成summaryだけで技術的主張が`verified`になっていない。

## 13. テスト観点

- 3資料戦略を同じ終了形式へ変換できる。
- coverage不足から資料追加へ戻れる。
- 手動資料だけでも終了条件を満たせる。
- originalが変更されない。
- AI補正前後を比較できる。
- 目次整理がeconomyへルーティングされる。
- conflictがhigh assuranceまたは人間確認へ進む。
- 全文ではなく必要chunkだけを後続へ渡す。
- AI生成summaryだけで主張をverifiedにできない。
- budget stopで処理を停止できる。

## 14. 移行・互換性

- 現行コードに資料入力パイプライン実装がないため、破壊的な移行対象はない。
- `docs/spec-proposals/material-input-pipeline-unplanned.md`に記載された未策定事項一覧は、
  本書と後続タスク(07〜13)で段階的に解消する。同ファイルは全項目解消後に削除を検討する
  (本タスクでは削除しない)。

## 15. 未決定事項

- 自動資料候補提案の範囲(検索エンジン利用の可否・範囲)
- URL取得を自動化するか
- source requirement matrixの詳細schema(→タスク07)
- coverage状態の粒度の詳細
- 「充足」と判断する資料件数の目安
- 低信頼OCRの閾値(→タスク10)
- 人間確認画面またはレポートの形式
- Batch実行の単位
- token budget初期値

## 16. 完了条件

- [x] 3種類の資料構築パターンが定義されている。
- [x] 資料収集とcoverage分析を反復できる構造になっている。
- [x] コンテンツ作成側への終了条件が一意に定義されている。
- [x] 資料入力未完成でも手動データで開始できる。
- [x] 原資料とAI加工結果が混在しない設計になっている。
- [x] AIモデルの役割と昇格条件が明示されている。
- [x] 資料全文の繰り返し送信を避ける方針が明示されている。
- [x] 人間承認を省略しない設計になっている。
- [x] 出力ドラフトが存在し、`status: review`である。
- [x] 参照した承認済み仕様が記録されている。
- [x] 実装コードを変更していない。

## 17. 下位仕様への分割

- 資料保存構成と共通資料スキーマ(タスク07)
- 著作権・ライセンス・利用目的の管理(タスク08)
- PDF直接抽出(タスク09)
- OCRとスキャンPDF(タスク10)
- EPUBテキスト抽出(タスク11)
- Kindle画面キャプチャ(タスク12)
- 書籍データ前処理(タスク13)
