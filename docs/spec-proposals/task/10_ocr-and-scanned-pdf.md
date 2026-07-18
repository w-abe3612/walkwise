---
task_type: specification_decision
status: draft
order: 10
title: "OCRと画像・スキャンPDF"
depends_on:
  - 7_source-storage-and-common-schema.md
spec_refs:
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/ocr-and-scanned-pdf.md"
last_updated: "2026-07-19"
---

# 10. OCRと画像・スキャンPDF

## 1. 目的

カメラ写真・スキャナ画像・スキャンPDFの画像化、OCRエンジン、言語、縦書き、信頼度、人間確認を策定する。

## 2. このタスクを今決める理由

このテーマには未決定事項が残っており、現時点では承認済み仕様として
`docs/specifications/`へ置くことができない。

依存タスクを先に完了し、その結果を前提として策定する。

## 3. 決定する事項

- カメラ写真とスキャナ画像の前処理差
- 見開き、台形歪み、影、反射、ぼけ、duplex順序
- OCRエンジンとローカル・クラウドの使い分け
- ページ画像の解像度と形式
- 日本語、英語、縦書きの対応
- 段組み、表、数式、コードの扱い
- 信頼度の記録と再OCR条件
- ページ抜け・重複・回転の検出
- 人間確認の対象
- OCR後のAI補正範囲
- economy、standard、high assuranceの使い分け
- token usageとcache

## 4. 推奨する初期回答

- 原画像を保持し、OCR結果を上書きしない
- ページ単位で処理・再実行する
- 低信頼度箇所をreview_requiredとして残す
- 表、数式、コードは本文OCRと別の扱いにする
- 目次整理・形式変換はFlash-Lite相当のeconomy層を使用する
- 通常本文の構造復元案は2.5 Flash相当のstandard層を使用できる
- 数式・コード・表は高性能モデルまたは人間確認へ送る
- 元画像とOCR原文をAI補正で上書きしない

推奨回答は初期案であり、サンプル、実測、公式仕様または既存コードとの
整合性確認で問題が見つかった場合は修正する。

## 5. 策定手順

1. 代表的なページサンプルを用意する
2. OCRエンジン候補を比較する
3. 画像化設定を決める
4. 信頼度と警告の形式を決める
5. 共通source schemaへの変換を確認する

## 6. 成果物

```text
docs/specifications/ocr-and-scanned-pdf.md
```

成果物には、目的、対象範囲、対象外、入出力、正常系、異常系、
バリデーション、テスト観点、移行方針、完了条件を含める。

## 7. 完了条件

- OCR結果を元画像へ追跡できる
- 低品質ページを自動検出できる
- ページ単位で再実行できる
- 人間が確認すべき箇所が一覧化される
- AI補正のモデル、prompt、input hashを追跡できる
- 低リスク処理と高リスク処理を同じモデルで自動確定しない

## 8. 完了後の処理

1. 成果物のフロントマターを`status: review`にする。
2. 人間が内容を確認する。
3. 承認後に`status: approved`、`version: "1.0"`とする。
4. 成果物を`docs/specifications/`へ配置する。
5. 本タスクを`status: done`へ変更する。
6. `INDEX.md`の次タスクへ進む。
