---
task_type: specification_decision
status: draft
order: 11
title: "EPUBテキスト抽出"
depends_on:
  - 7_source-storage-and-common-schema.md
output_spec: "docs/specifications/epub-text-extraction.md"
---

# 11. EPUBテキスト抽出

## 1. 目的

EPUBのHTML、目次、ルビ、脚注、画像、メタデータを共通資料形式へ変換する仕様を決める。

## 2. このタスクを今決める理由

このテーマには未決定事項が残っており、現時点では承認済み仕様として
`docs/specifications/`へ置くことができない。

依存タスクを先に完了し、その結果を前提として策定する。

## 3. 決定する事項

- 対応EPUBバージョン
- 目次と本文順序の解決
- ルビの保存方法
- 脚注と注釈の扱い
- 画像・表・CSSの扱い
- DRM付きEPUBの扱い
- 章・節IDの生成

## 4. 推奨する初期回答

- DRM回避は対象外とする
- EPUBの目次情報を章順の第一候補にする
- HTML本文の原形と整形本文を分ける
- ルビは原文情報として保持し、TTS用表記へ変換可能にする

推奨回答は初期案であり、サンプル、実測、公式仕様または既存コードとの
整合性確認で問題が見つかった場合は修正する。

## 5. 策定手順

1. DRMなしEPUBのサンプルを選ぶ
2. 目次、本文、ルビ、脚注の抽出例を作る
3. 章IDとsource locatorの規則を決める
4. 不要な装飾と必要な意味情報を分離する
5. 共通source schemaへ変換する

## 6. 成果物

```text
docs/specifications/epub-text-extraction.md
```

成果物には、目的、対象範囲、対象外、入出力、正常系、異常系、
バリデーション、テスト観点、移行方針、完了条件を含める。

## 7. 完了条件

- 章順を再現できる
- ルビと脚注を失わず保持できる
- 元HTMLへ追跡できる
- DRM対象外方針が明記されている

## 8. 完了後の処理

1. 成果物のフロントマターを`status: review`にする。
2. 人間が内容を確認する。
3. 承認後に`status: approved`、`version: "1.0"`とする。
4. 成果物を`docs/specifications/`へ配置する。
5. 本タスクを`status: done`へ変更する。
6. `INDEX.md`の次タスクへ進む。
