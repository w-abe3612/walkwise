---
task_type: specification_decision
status: draft
order: 4
title: "音声検査の最終閾値"
depends_on:
  - 3_voice-profile-default-values.md
output_spec: "docs/specifications/audio-validation-thresholds.md"
---

# 4. 音声検査の最終閾値

## 1. 目的

話者別の実測音声をもとに、無音、音量、ピーク、文字数毎秒、warningとfailの境界を確定する。

## 2. このタスクを今決める理由

このテーマには未決定事項が残っており、現時点では承認済み仕様として
`docs/specifications/`へ置くことができない。

依存タスクを先に完了し、その結果を前提として策定する。

## 3. 決定する事項

- 最小再生時間
- 連続無音のwarningとfail閾値
- LUFS目標と許容差
- ピーク値とclipping判定
- 文字数毎秒の正常範囲
- 自動再生成対象
- 話者別閾値を許可するか

## 4. 推奨する初期回答

- 現在の数値は仮値として扱い、最低3話者で実測する
- 破損、0秒、形式不一致は常にfailとする
- 発音、声質、意味対応は自動failにせずreview_requiredとする
- 文字数毎秒はwarning用途とし、単独でfailにしない

推奨回答は初期案であり、サンプル、実測、公式仕様または既存コードとの
整合性確認で問題が見つかった場合は修正する。

## 5. 策定手順

1. 正常音声と意図的異常音声のセットを作る
2. ffprobe等で測定値を収集する
3. 誤検出と見逃しを比較する
4. warning、review_required、failの境界を決める
5. 設定ファイルとテストケースへ反映する

## 6. 成果物

```text
docs/specifications/audio-validation-thresholds.md
```

成果物には、目的、対象範囲、対象外、入出力、正常系、異常系、
バリデーション、テスト観点、移行方針、完了条件を含める。

## 7. 完了条件

- すべての閾値に根拠となる実測がある
- 正常音声を過剰にfailにしない
- 壊れた音声が完成版へ入らない
- 閾値変更のバージョン管理方法が決まっている

## 8. 完了後の処理

1. 成果物のフロントマターを`status: review`にする。
2. 人間が内容を確認する。
3. 承認後に`status: approved`、`version: "1.0"`とする。
4. 成果物を`docs/specifications/`へ配置する。
5. 本タスクを`status: done`へ変更する。
6. `INDEX.md`の次タスクへ進む。
