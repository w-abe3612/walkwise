---
task_type: specification_decision
status: done
order: 16
title: "カメラ写真・スキャナ画像の資料入力"
depends_on: []
spec_refs:
  - ../../specifications/audiobook-creation-pipeline.md
  - ../../specifications/02-process-input-output.md
  - ../../specifications/17-file-based-data-persistence-policy.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/image-material-ingestion.md"
completed_at: "2026-07-19"
---

# 16. カメラ写真・スキャナ画像の資料入力

## 結果

カメラ写真・スキャナ画像を正式な資料入力形式として策定し、
次へ承認済み仕様を配置した。

```text
docs/specifications/image-material-ingestion.md
```

## 決定内容

- source strategyとmedia typeを分離する。
- camera、flatbed scanner、sheetfed scanner、scan appを識別する。
- original画像はimmutableとする。
- 補正画像を`preprocessed/`へ保存する。
- ページ順、hash、重複、欠番、品質をmanifestへ保存する。
- 見開き分割後も元画像座標へ戻れる。
- EXIF位置情報を既定で後続へexportしない。
- 権利とprivacyを分離して確認する。
- OCRは別工程とし、原画像を上書きしない。

## 完了条件

- [x] 承認済み仕様が存在する。
- [x] `status: approved`、`version: "1.0"`である。
- [x] カメラ写真とスキャナ画像の差が定義されている。
- [x] OCR handoffが定義されている。
- [x] 実装タスクが`docs/tasks/16_image-material-ingestion.md`にある。
