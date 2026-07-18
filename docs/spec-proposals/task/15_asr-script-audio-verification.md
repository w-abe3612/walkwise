---
task_type: specification_decision
status: draft
order: 15
title: "ASRによる原稿と音声の照合"
depends_on:
  - 4_audio-validation-thresholds.md
  - 14_m4b-and-complete-book-output.md
output_spec: "docs/specifications/asr-script-audio-verification.md"
---

# 15. ASRによる原稿と音声の照合

## 1. 目的

将来機能として、音声認識結果と原稿を比較し、読み飛ばし、重複、欠落をreview候補として検出する仕様を決める。

## 2. このタスクを今決める理由

このテーマには未決定事項が残っており、現時点では承認済み仕様として
`docs/specifications/`へ置くことができない。

依存タスクを先に完了し、その結果を前提として策定する。

## 3. 決定する事項

- 採用するASR
- 照合単位
- 日本語専門用語の正規化
- 誤差指標
- warningとreview_requiredの境界
- 自動failを許可するか
- 外部APIへ音声を送る場合の取り扱い

## 4. 推奨する初期回答

- 初期段階では必須機能にしない
- ASR差分だけで自動failにしない
- セグメント単位で照合する
- 専門用語辞書とtts_textを正規化に利用する

推奨回答は初期案であり、サンプル、実測、公式仕様または既存コードとの
整合性確認で問題が見つかった場合は修正する。

## 5. 策定手順

1. 正常音声と欠落・重複音声を用意する
2. ASR候補を比較する
3. 原稿とのアラインメント方法を決める
4. 誤検出率を測定する
5. review reportの形式を決める

## 6. 成果物

```text
docs/specifications/asr-script-audio-verification.md
```

成果物には、目的、対象範囲、対象外、入出力、正常系、異常系、
バリデーション、テスト観点、移行方針、完了条件を含める。

## 7. 完了条件

- 欠落・重複をreview候補として提示できる
- 正常な言い換えや発音差を過剰検出しない
- 外部送信の有無とデータ取り扱いが明示されている
- ASRなしでも基本パイプラインが動作する

## 8. 完了後の処理

1. 成果物のフロントマターを`status: review`にする。
2. 人間が内容を確認する。
3. 承認後に`status: approved`、`version: "1.0"`とする。
4. 成果物を`docs/specifications/`へ配置する。
5. 本タスクを`status: done`へ変更する。
6. `INDEX.md`の次タスクへ進む。
