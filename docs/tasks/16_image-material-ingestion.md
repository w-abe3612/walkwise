---
task_id: implement-image-material-ingestion
task_type: implementation
status: ready
priority: high
spec_refs:
  - ../specifications/image-material-ingestion.md
  - ../specifications/02-process-input-output.md
created_at: "2026-07-19"
---

# カメラ写真・スキャナ画像の資料入力実装

## 1. 目的

承認済み`image-material-ingestion.md`に基づき、
画像ファイル群の登録、順序、hash、品質warning、
派生ページ、OCR handoffを実装する。

## 2. 実装順序

1. image source metadata model
2. image ingestion session model
3. PNG/JPEG/TIFF validator
4. SHA-256
5. natural filename order
6. explicit manifest order
7. duplicate page index validation
8. original immutable save
9. preprocessed path generation
10. EXIF privacy metadata
11. image quality flag interface
12. two-page spread mapping
13. OCR handoff manifest
14. legacy pages import adapter

## 3. テスト先行

最低限次をpytestで作成する。

- PNG、JPEG、TIFF正常入力
- 壊れた画像
- page index重複
- original上書き拒否
- natural sort
- explicit順序優先
- hash
- EXIF location export拒否
- spread locator
- OCR handoff
- legacy path import

画像補正アルゴリズム自体は別タスクへ分割してよい。

## 4. 禁止事項

- 原画像上書き
- blank候補の自動削除
- EXIF位置情報の無断export
- 権利未確認資料の公開用途化
- 画像をAIへ無断送信
- OCR結果を原画像manifestへ上書き

## 5. 完了条件

- 画像群を一つのsourceとして登録できる。
- 順序とhashをmanifestへ保存できる。
- page単位のOCR handoffを生成できる。
- originalを変更しない。
- 通常pytestでカメラ・scanner実機を要求しない。
