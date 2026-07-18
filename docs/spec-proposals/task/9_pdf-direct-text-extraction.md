---
task_type: specification_decision
status: draft
order: 9
title: "PDF直接テキスト抽出"
depends_on:
  - 7_source-storage-and-common-schema.md
spec_refs:
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/pdf-direct-text-extraction.md"
last_updated: "2026-07-19"
---

# 9. PDF直接テキスト抽出

## 1. 目的

テキスト埋め込みPDFから、読み順、見出し、ページ位置を保持して本文を抽出する仕様を決める。

## 2. このタスクを今決める理由

このテーマには未決定事項が残っており、現時点では承認済み仕様として
`docs/specifications/`へ置くことができない。

依存タスクを先に完了し、その結果を前提として策定する。

## 3. 決定する事項

- 採用ライブラリ
- テキスト埋め込み判定
- 複数段組みの読み順
- ヘッダー・フッター・ページ番号の除去
- 表、図、脚注の扱い
- 文字化けとOCR切替条件
- パスワード付きPDFの扱い

## 4. 推奨する初期回答

- 直接抽出を最初に試し、品質基準を下回る場合だけOCRへ切り替える
- ページ番号と座標情報を可能な範囲で保持する
- 原文と補正後本文を分離する
- 抽出失敗ページをページ単位で再実行できるようにする
- 直接抽出は決定的ツールを優先し、AIは見出し整理・形式変換へ限定する
- 目次整理と形式変換はeconomy層を使用する
- 読み順の重大な競合はstandardまたは人間確認へ送る

推奨回答は初期案であり、サンプル、実測、公式仕様または既存コードとの
整合性確認で問題が見つかった場合は修正する。

## 5. 策定手順

1. 複数種類のPDFサンプルを選ぶ
2. 抽出ライブラリを比較する
3. 読み順と不要部分除去のルールを決める
4. OCRへ切り替える判定を決める
5. 共通source schemaへの変換例を作る

## 6. 成果物

```text
docs/specifications/pdf-direct-text-extraction.md
```

成果物には、目的、対象範囲、対象外、入出力、正常系、異常系、
バリデーション、テスト観点、移行方針、完了条件を含める。

## 7. 完了条件

- 通常PDFの本文をページ位置付きで抽出できる
- 読み順異常と文字化けを検出できる
- 失敗ページだけを再処理できる
- OCR経路への切替条件が明確である

## 8. 完了後の処理

1. 成果物のフロントマターを`status: review`にする。
2. 人間が内容を確認する。
3. 承認後に`status: approved`、`version: "1.0"`とする。
4. 成果物を`docs/specifications/`へ配置する。
5. 本タスクを`status: done`へ変更する。
6. `INDEX.md`の次タスクへ進む。
