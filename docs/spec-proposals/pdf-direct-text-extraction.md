---
spec_id: pdf-direct-text-extraction
title: "PDF直接テキスト抽出"
status: provisional
version: "0.1"
last_updated: "2026-07-19"
generated_by:
  type: ai
  note: "旧仕様策定タスク(完了・削除済み)により生成。Git履歴を参照。"
depends_on:
  - source-storage-and-common-schema.md
spec_refs:
  - source-storage-and-common-schema.md
  - ../specifications/18-ai-model-routing-and-cost-control.md
---

# PDF直接テキスト抽出(ドラフト)

> **状態に関する注記**
> ライブラリ選定(PyMuPDF/pypdf等)はサンプル評価による比較が必要であり、
> 夜間実行ではパッケージのインストール・実行を行っていないため、
> ライブラリ確定・閾値確定は`provisional`とする。構造(schema、判定フロー、
> 異常系)は既存承認済み仕様から導出可能なため`review`相当の完成度で記述する。

## 1. 目的

テキスト埋め込みPDFから、読み順・見出し・ページ位置を保持して本文を抽出する
仕様を定義する。

## 2. 対象範囲

- 直接抽出とOCRの優先順位
- 抽出ライブラリの候補と選定方針(値は未確定)
- 読み順・座標の保持方法
- 文字化け・低品質判定とOCR切替条件
- パスワード付きPDFの扱い

## 3. 対象外

- スキャンPDF・画像PDFのOCR処理そのもの(→タスク10)
- パスワード解除・DRM回避
- 図表・数式の意味的な復元(前処理タスク13で扱う)

## 4. 現行実装

現行コードにPDF抽出の実装は存在しない。

## 5. 推奨仕様

### 5.1 直接抽出とOCRの優先順位

質問1への回答: **直接抽出を先に試し、品質基準を満たさないページだけOCRへ送る。**

```text
PDFページ
↓
テキスト埋め込み判定
↓ (embedded text あり)          ↓ (embedded text なし/低品質)
直接抽出                          OCRへ送る(タスク10)
↓
ページ単位品質評価
↓ (基準未満)
OCRへフォールバック
```

### 5.2 採用ライブラリ

質問2への回答: **PyMuPDFを座標・block取得の第一候補、pypdfをmetadataや
単純抽出の比較候補とし、サンプル評価後に確定する。**

```yaml
extraction_library_candidates:
  status: provisional
  primary_candidate: pymupdf
  secondary_candidate: pypdf
  selection_criteria:
    - coordinate_extraction_accuracy
    - reading_order_accuracy
    - table_of_contents_extraction
    - performance_on_large_pdf
  evidence:
    benchmarked: false
    sample_count: 0
```

本タスクでは、いずれのライブラリもインストール・実行していない。
選定は代表的なPDFサンプル(テキストPDF、複数段組み、表あり、画像混在PDF)での
比較評価後に確定する。

### 5.3 読み順と座標

質問3への回答: **ページ番号、block座標、読み順候補を保持する。**

```json
{
  "source_id": "example-pdf",
  "chunk_id": "example-pdf-chunk-0001",
  "locator": {
    "page": 12,
    "coordinates": {
      "blocks": [
        {"bbox": [72.0, 100.2, 520.0, 140.5], "reading_order": 1}
      ]
    }
  },
  "extraction_method": "direct_text",
  "extractor": "pymupdf",
  "extractor_version": null,
  "text_path": "sources/extracted/example-pdf/page-0012.md",
  "quality": {
    "printable_char_ratio": 0.98,
    "duplicate_ratio": 0.0,
    "reading_order_anomaly": false,
    "mojibake_detected": false
  },
  "warnings": []
}
```

複数段組みの読み順は、block座標のx/y位置から列を推定する方式を初期候補とするが、
競合が生じた場合は`standard_generation`または人間確認へ送る(5.5節)。

### 5.4 文字化け・低品質判定とOCR切替条件

質問4への回答: 抽出文字数、印字可能文字率、重複率、読み順異常、文字化けを
ページ単位で評価する。閾値は`provisional`とする。

```yaml
page_quality_thresholds:
  status: provisional
  minimum_printable_char_ratio: 0.85
  maximum_duplicate_ratio: 0.3
  minimum_extracted_chars_per_page: 20
  evidence:
    measured: false
```

いずれかの基準を下回るページは、直接抽出を採用せず`ocr_fallback_required`として
タスク10のOCR経路へ渡す。

### 5.5 AIの役割

直接抽出は決定的ツールを優先し、AIは見出し整理・形式変換へ限定する
(`18-ai-model-routing-and-cost-control.md`に従う)。

| 処理 | 論理層 |
|---|---|
| 目次整理、形式変換 | `economy_structuring` |
| 読み順の重大な競合の解消案 | `standard_generation`または人間確認 |

AIは抽出テキストの内容そのものを生成・補完しない(決定的抽出結果を正とする)。

### 5.6 パスワード付きPDF

質問5への回答: **復号・回避を自動化せず、利用者が正当に開ける入力だけを対象とする。**
利用者がパスワードを明示的に入力・提供した場合のみ処理対象とし、
パスワードクラッキングやDRM回避は行わない。

## 6. 入力

- テキスト埋め込みPDF(利用者が正当に開けるもの)
- `source-storage-and-common-schema.md`の`sources/originals/`配置

## 7. 出力

- ページ単位の抽出結果(5.3節JSON形式)
- page-level品質レポート
- OCR切替判定結果

## 8. 正常系

1. PDFのテキスト埋め込みを判定する。
2. 直接抽出を実行し、ページ単位で座標・読み順候補を保持する。
3. ページ品質を評価する。
4. 基準を満たすページは`extracted/`へ保存する。
5. 基準未満のページはOCR経路(タスク10)へフラグを立てて渡す。
6. 失敗ページだけを再実行できるようにする。

## 9. 異常系

| ケース | 扱い |
|---|---|
| テキスト埋め込みなし(画像PDF) | 全ページをOCR経路へ |
| 文字化け検出 | 該当ページを`ocr_fallback_required`、warning記録 |
| 読み順異常(競合) | `standard_generation`または人間確認 |
| パスワード付きで利用者からパスワード未提供 | `blocked`(処理しない) |
| DRM保護PDF | 対象外、`blocked` |
| 抽出ライブラリが例外を送出 | 該当ページのみ`fail`、他ページは継続 |

## 10. バリデーション

- 各抽出chunkに`extraction_method: direct_text`が記録されている。
- `quality`情報が欠落したまま`extracted/`へ確定しない。
- OCRへフォールバックしたページを直接抽出結果と混同しない。

## 11. テスト観点

- テキストPDF、複数段組み、表あり、画像混在PDFのサンプルで抽出できる(サンプル未取得のため設計のみ)。
- 低品質ページが正しくOCR経路へフラグ付けされる。
- 失敗ページだけを再実行できる。
- パスワード付きPDFが未提供時に処理されない。
- 抽出結果が共通source schema(`source-storage-and-common-schema.md`)へ変換できる。

## 12. 移行・互換性

- 現行実装からの移行対象なし。
- 出力formatは`source-storage-and-common-schema.md`の chunk 形式に準拠する。

## 13. 未決定事項

- 採用ライブラリの最終確定(PyMuPDF vs pypdf、サンプル評価後)
- page-level品質閾値の実測による調整
- 複数段組み読み順推定の具体的アルゴリズム
- 表・図・脚注の抽出方法(前処理タスク13との責務分担)

## 14. 完了条件

- [x] 通常PDFの本文をページ位置付きで抽出できる設計になっている。
- [x] 読み順異常と文字化けを検出できる。
- [x] 失敗ページだけを再処理できる。
- [x] OCR経路への切替条件が明確である。
- [x] 出力ドラフトが存在し、`status: provisional`である。
- [x] 未実測・未確認事項が明記されている(5.2, 5.4, 13節)。
- [x] 実装コードを変更していない。

## 15. 停止・保留条件(該当状況)

- サンプルなしで特定ライブラリを最終確定する必要がある → 未確定のまま`provisional`とする。
- パスワード回避・DRM回避は要求されておらず、対象外として扱う。
