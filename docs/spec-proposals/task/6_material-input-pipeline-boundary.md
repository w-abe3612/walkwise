---
task_type: specification_decision
status: draft
order: 6
title: "資料入力パイプラインの責務と境界"
depends_on: []
spec_refs:
  - ../../specifications/audiobook-creation-pipeline.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/material-input-pipeline.md"
last_updated: "2026-07-19"
---

# 6. 資料入力パイプラインの責務と境界

## 1. 目的

無料公開資料、複数資料による再構築、購入済みKindle・PDF・OCRを、
独立した資料入力パイプラインとして定義し、
コンテンツ作成側へ検索可能・引用可能・章へ割当て可能な資料セットを渡す。

---

## 2. 開始点

次のいずれかから開始する。

1. テーマと対象範囲だけがある。
2. URLや資料候補がある。
3. PDF、EPUB、テキストがある。
4. カメラ写真・スキャナ画像がある。
5. Kindle等の購入済み資料がある。
6. 既存OCR結果がある。
7. 人間が作成した構造化資料がある。

資料入力パイプラインの完成を待たず、
手動構造化資料から後続処理を開始できる。

---

## 3. 終了点

次を満たした資料セットをコンテンツ作成側へ渡す。

- source IDがある。
- 原資料または確認可能な参照先がある。
- versionまたは取得日時がある。
- source roleがある。
- source locatorを保持できる。
- normalizedまたはstructured本文がある。
- chunk manifestがある。
- source summaryがある。
- topic indexがある。
- coverage mapがある。
- rightsとusage purposeが記録されている。
- 低信頼箇所とwarningが明示されている。
- materials curriculum承認の対象にできる。

---

## 4. 共通処理

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

一回で資料収集を完了することを前提にしない。

---

## 5. 資料戦略別の経路

## 5.1 open_fulltext

対象:

- 無料教科書
- パブリックドメイン原典
- 大学公開教材
- オープンアクセス論文
- 公的機関・学会資料

処理:

1. AIが候補、検索語、資料役割案を提示する。
2. 人間が資料を選択・取得する。
3. 本文と目次を抽出する。
4. AIが章構造、topic、用語を整理する。
5. 複数資料のcoverageを作る。
6. 不足topicの追加資料を提案する。
7. カリキュラムを再構築する。

原典と解説資料を同じ役割にしない。

## 5.2 hybrid_reconstruction

対象:

- データベース
- 資格試験
- 公式マニュアルと教科書を組み合わせる分野

処理:

1. シラバスと公開目次を収集する。
2. topic requirement matrixを作る。
3. topicごとに必要な資料役割を決める。
4. 公式資料、無料教科書、専門資料を登録する。
5. coverage mapを作る。
6. 不足topicを追加探索する。
7. 根拠資料が揃うまで反復する。
8. 独自カリキュラムを作る。

公開目次とシラバスを技術的事実の最終根拠にしてはならない。

## 5.3 licensed_reference

対象:

- 購入済みKindle
- 購入済みPDF
- 市販書籍
- 人間が利用権を確認した資料

処理:

1. 利用目的とrights状態を登録する。
2. 人間が原資料を用意する。
3. 直接抽出または画面キャプチャを行う。
4. OCRを行う。
5. raw、normalized、structuredを分離する。
6. 低信頼箇所を人間が確認する。
7. topic indexとcoverage mapを作る。

DRM回避や市販本文の自動取得は対象外とする。

---

## 6. AIモデルルーティング

`18-ai-model-routing-and-cost-control.md`へ従う。

### economy structuring

初期モデル:

```text
Gemini 2.5 Flash-Lite
```

用途:

- 目次整理
- topic抽出
- source summary
- coverage map一次作成
- 形式変換
- 主張候補抽出
- 低リスクなOCR整形候補

### standard generation

初期モデル:

```text
Gemini 2.5 Flash
```

用途:

- カリキュラム統合
- 章構成案
- 資料に基づく説明案

### high assurance review

用途:

- 出典間の矛盾
- 難しい技術検証
- OCRされた数式、コード、表の確認支援
- 最終意味レビュー

高性能モデル未設定時は、人間確認へ差し戻す。

---

## 7. AIに許可すること

- 資料候補と検索語の提案
- 目次・見出し整理
- topic候補抽出
- source role候補
- source summary
- coverage map
- 不足topic検出
- OCR修正候補
- 構造化候補
- 矛盾論点の整理

---

## 8. AIに許可しないこと

- 資料の利用可否を法的に保証する。
- 存在しない引用位置を作る。
- OCR原文を上書きする。
- 出典のない技術的主張をverifiedにする。
- 公開目次を事実根拠へ昇格する。
- source conflictを黙って解消する。
- 数式、コード、図表の不確かな復元を自動承認する。
- 購入資料を自動公開する。

---

## 9. 正本と派生物

| 段階 | 正本または位置付け |
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

---

## 10. コスト制御

- 資料全文は原則として一度だけ構造化する。
- 後続工程では必要なchunkだけを使用する。
- 同じinput hashとprompt versionの結果を再利用する。
- 大量の目次整理、topic抽出、形式変換はBatch候補とする。
- 再試行を含めたusageを記録する。
- 高性能モデルの自動昇格可否を設定する。
- project予算上限を超えたら人間確認へ停止する。

---

## 11. 決定する事項

- 自動資料候補提案の範囲
- URL取得を自動化するか
- source requirement matrixのschema
- coverage状態の詳細
- 何件の資料で「充足」とするか
- 低信頼OCRの閾値
- 人間確認画面またはレポート
- Batch実行の単位
- token budget初期値

---

## 12. 下位仕様への分割

- 資料保存構成と共通schema
- rightsとlicense
- PDF直接抽出
- OCR（カメラ写真・スキャナ画像・スキャンPDF）
- 画像ファイル取り込み
- EPUB
- Kindle capture
- source preprocessing

---

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

---

## 14. 成果物

```text
docs/specifications/material-input-pipeline.md
```

---

## 15. 完了条件

- 3種類の資料構築パターンが定義されている。
- 資料収集とcoverage分析を反復できる。
- コンテンツ作成側への終了条件が一意である。
- 資料入力未完成でも手動データで開始できる。
- 原資料とAI加工結果が混在しない。
- AIモデルの役割と昇格条件が明示されている。
- 資料全文の繰り返し送信を避けられる。
- 人間承認を省略しない。

---

## 16. 完了後の処理

1. 成果物を`status: review`で作成する。
2. open fulltext、hybrid、licensedのサンプルを確認する。
3. 人間が内容を確認する。
4. 承認後に`status: approved`、`version: "1.0"`とする。
5. `docs/specifications/`へ配置する。
6. 本タスクを`done`へ変更する。
