---
spec_id: ocr-and-scanned-pdf
title: "OCRと画像・スキャンPDF"
status: provisional
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/10_ocr-scanned-pdf.md
  source_task: docs/spec-proposals/task/10_ocr-and-scanned-pdf.md
depends_on:
  - 7_source-storage-and-common-schema.md
spec_refs:
  - source-storage-and-common-schema.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
---

# OCRと画像・スキャンPDF(ドラフト)

> **状態に関する注記**
> OCRエンジンの実行・比較(Tesseract等)、画像サンプルでのbenchmarkは
> 夜間実行では行っていない(パッケージインストール・実行の禁止による)。
> エンジン選定・解像度・信頼度閾値は`provisional`とする。

## 1. 目的

カメラ写真・スキャナ画像・スキャンPDFの画像化、OCRエンジン選定、言語対応、信頼度記録、
人間確認フローを定義する。

## 2. 対象範囲

- カメラ写真・スキャナ画像・スキャンPDFの共通OCR入力
- OCRエンジンの初期候補とローカル/クラウドの使い分け
- ページ画像の解像度・形式
- 日本語・英語・縦書きの対応
- 段組み・表・数式・コードの扱い
- 信頼度の記録と再OCR条件
- ページ抜け・重複・回転の検出
- AI補正の範囲とモデル層の使い分け

## 3. 対象外

- テキスト埋め込みPDFの直接抽出(→タスク09)
- 数式・コード・表の意味的な最終確定(人間確認またはhigh assurance支援に限定)
- Kindle画面キャプチャそのもの(→タスク12。本書はOCR処理自体を扱う)

## 4. 現行実装

現行コードにOCR実装は存在しない。

## 5. 推奨仕様

### 5.1 OCRエンジン

質問1・2への回答: **既存利用実績のあるTesseractをMVP基準エンジンとし、
交換可能なadapterを必須にする。クラウドOCRは既定にしない。**

```yaml
ocr_engine_policy:
  status: provisional
  default_engine: tesseract
  adapter_interface_required: true
  cloud_ocr:
    enabled_by_default: false
    allowed_when: explicit_human_permission_and_rights_recorded
  evidence:
    benchmarked: false
```

ローカルOCRを優先し、クラウドOCRは資料を外部送信することを意味するため、
明示許可・rights記録がある場合だけの追加providerとする
(`08_rights-and-license-management`のusage_purposeゲートと連動)。

### 5.2 ページ画像の解像度・形式

質問3への回答: 通常本文は300dpi PNGを初期値とし、小さい文字・コードは
必要時に400dpiを試す。**最終値はbenchmarkで確定する(provisional)。**

```yaml
page_imaging:
  status: provisional
  default_dpi: 300
  high_detail_dpi: 400
  format: png
  evidence:
    benchmarked: false
```

### 5.3 言語・縦書き

質問4への回答: `jpn+eng`を基本とし、縦書きは別モード・別評価にする。

```yaml
ocr_language_modes:
  horizontal_default: jpn+eng
  vertical_writing:
    mode: separate_evaluation
    engine_language: jpn_vert
    status: provisional
```

### 5.4 数式・コード・表・図

質問5への回答: **本文OCRと同じ扱いにしない。** 高リスク領域として別抽出・
人間確認へ送る。

```yaml
high_risk_regions:
  types:
    - formula
    - code
    - table
    - diagram
  handling: separate_extraction_and_human_review
  auto_confirm: false
```

### 5.5 OCR page result例

```json
{
  "chunk_id": "kindle-book-001-page-0042",
  "source_id": "kindle-book-001",
  "locator": {
    "page": 42
  },
  "extraction_method": "ocr",
  "ocr_engine": "tesseract",
  "ocr_engine_version": null,
  "language_mode": "jpn+eng",
  "dpi": 300,
  "confidence": {
    "overall": 0.87,
    "low_confidence_regions": [
      {"bbox": [80, 400, 500, 460], "confidence": 0.42, "type": "formula"}
    ]
  },
  "text_path": "sources/extracted/kindle-book-001/page-0042.md",
  "raw_image_path": "sources/originals/kindle-book-001/page-0042.png",
  "warnings": ["low_confidence_region", "formula_detected"]
}
```

原画像(`raw_image_path`)は`originals/`配下に保持し、OCR結果で上書きしない
(`source-storage-and-common-schema.md` 5.2節「originalsはimmutable」)。

### 5.6 ページ抜け・重複・回転

- 画像hash(exact)とperceptual hashの両方を用いて重複ページを検出する。
- ページ番号の連続性(OCRで読み取ったページ番号 or 手動連番)から抜けを検出する。
- 回転検出は、OCRエンジンのosd(orientation detection)機能があれば利用する候補とし、
  未検証のためprovisionalとする。

### 5.7 AIモデルルーティング

| 処理 | 論理層 |
|---|---|
| 目次整理、形式変換 | `economy_structuring`(Flash-Lite相当) |
| 通常本文の構造復元案 | `standard_generation`(2.5 Flash相当) |
| 数式・コード・表の確認支援 | `high_assurance_review`または人間 |

元画像とOCR原文はAI補正で上書きしない。低リスク箇所のみeconomy層が候補を提示し、
高リスク箇所は人間またはhigh assuranceへ送る(質問9への回答)。

### 5.8 トークン使用量とキャッシュ

質問10への回答: `18-ai-model-routing-and-cost-control.md`のキャッシュキー
(task_type, logical_tier, physical_model, prompt_id, prompt_version, input_hash,
schema_version, generation_parameters)をOCR後処理にもそのまま適用する。
同一ページの再OCRは、画像hashが変わらない限りcache対象とする。


### 5.9 カメラ写真・スキャナ画像の前処理

画像資料の登録と順序管理は
`../../specifications/image-material-ingestion.md`へ従う。

OCRは原画像ではなく、
原画像へ戻れる`preprocessed page`を入力としてよい。

カメラ写真の候補処理:

- EXIF orientation適用
- 本文領域検出
- 回転
- deskew
- perspective correction
- 見開き分割
- 影・反射・ぼけwarning
- ページ端欠落warning

スキャナ画像の候補処理:

- rotation
- deskew
- 余白検出
- duplex順序確認
- blank page候補
- 裏写りwarning

補正後画像でoriginalを上書きしない。

### 5.10 画像形式とOCR派生物

初期必須入力:

- PNG
- JPEG
- TIFF

OCR用標準派生物:

```yaml
format: png
page_unit: true
original_image_locator_required: true
```

HEIC、WebP、複数ページTIFFはadapter候補とし、
decoder未導入時は`unsupported_format`とする。

## 6. 入力

- スキャン画像、または画像化されたPDFページ
- (Kindleの場合)タスク12のキャプチャ結果

## 7. 出力

- ページ単位OCR結果(5.5節形式)
- 信頼度・warningレポート
- benchmark計画(8節)

## 8. Benchmark計画(未実施)

1. 代表ページ(横書き本文、縦書き本文、数式含みページ、表含みページ、
   低解像度スキャン)のbenchmark matrixを作成する。
2. Tesseractを基準に、他のローカルOCR候補と比較する(比較対象は未実施)。
3. 解像度(300dpi/400dpi)による認識率の差を比較する。
4. 信頼度閾値と人間確認要否の境界を調整する。

夜間実行ではOCRエンジンのインストール・実行を行っていない。

## 9. 正常系

1. スキャン画像/ページ画像を`originals/`へ保存する。
2. OCRを実行し、page単位でtext・confidence・warningを記録する。
3. 低信頼領域と高リスク領域(数式/コード/表/図)を分離して記録する。
4. 重複・抜け・回転を検出する。
5. 通常本文の低リスク補正候補をeconomy/standard層で生成する(原文は保持)。
6. 高リスク箇所をreview-requiredレポートへ集約する。

## 10. 異常系

| ケース | 扱い |
|---|---|
| OCR結果が空 | `fail`、当該ページをreview対象 |
| confidence全体が閾値未満 | `review_required` |
| 数式・コード・表を検出 | 自動確定せず`review_required` |
| ページ重複検出 | warning、重複候補を提示 |
| ページ番号の不連続(抜け疑い) | warning、`review_required` |
| クラウドOCRへ資料送信が必要だが許可なし | `blocked` |

## 11. バリデーション

- 原画像とOCR結果が1対1で対応付けられている。
- `confidence`情報が欠落したままpage resultを確定しない。
- 高リスク領域を含むページが、人間確認なしに`structured`へ昇格しない。

## 12. テスト観点

- OCR結果を元画像へ追跡できる。
- 低品質ページを自動検出できる。
- ページ単位で再実行できる。
- 人間が確認すべき箇所が一覧化される(review-required.yaml)。
- AI補正のモデル、prompt、input hashを追跡できる。
- 低リスク処理と高リスク処理を同じモデルで自動確定しない。

## 13. 移行・互換性

- 現行実装からの移行対象なし。
- 出力formatは`source-storage-and-common-schema.md`のchunk形式に準拠する。

## 14. 未決定事項

- 最終採用OCRエンジン(Tesseract以外の比較候補含む)
- 解像度の最終値(300dpi/400dpi)
- 縦書きOCRの具体的なエンジン設定
- 信頼度閾値の実測による調整
- クラウドOCR利用時のデータ保持・削除ポリシー

## 15. 完了条件

- [x] OCR結果を元画像へ追跡できる設計になっている。
- [x] 低品質ページを自動検出できる。
- [x] ページ単位で再実行できる。
- [x] 人間が確認すべき箇所が一覧化される。
- [x] AI補正のモデル、prompt、input hashを追跡できる。
- [x] 低リスク処理と高リスク処理を同じモデルで自動確定しない。
- [x] 出力ドラフトが存在し、`status: provisional`である。
- [x] 実装コードを変更していない。

## 16. 停止・保留条件(該当状況)

- 画像サンプルなしで最終OCRエンジンを確定する必要がある → 未確定のまま`provisional`とする。
- クラウドへ資料を送信する必要があるが許可がない → 既定でクラウドOCRを無効化する設計とした。
- 数式・コードをAIだけで確定しそうになる → 5.4節で高リスク領域として分離済み。
