---
task_type: specification_decision
status: done
order: 12
title: "Kindle画面キャプチャ"
depends_on: []
spec_refs:
  - ../../specifications/audiobook-creation-pipeline.md
  - ../../specifications/00-specification-guidelines.md
  - ../../specifications/01-common-identifiers-and-versioning.md
  - ../../specifications/15-migration-and-compatibility.md
  - ../../specifications/17-file-based-data-persistence-policy.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/kindle-capture.md"
completed_at: "2026-07-19"
legacy_evidence: "audio_book_creation_dump_2026-07-18_193603.txt"
---

# 12. Kindle画面キャプチャ

## 1. 結果

旧版オーディオブック作成ツールのKindle操作実装、
capture settings、ページ画像、OCR結果、互換テストを根拠に、
Kindle画面キャプチャ仕様を策定し、承認済み仕様へ昇格した。

承認済み仕様:

```text
docs/specifications/kindle-capture.md
```

## 2. 依存関係の整理

従来は次の未承認タスクへ依存していた。

- 資料保存・共通スキーマ
- OCR
- 権利・ライセンス管理

仕様昇格時に責務を分離した。

- Kindle仕様はページ画像とcapture manifestまでを自己完結して定義する。
- OCRの詳細は後続工程とし、OCR未確定でもキャプチャ仕様を承認できる。
- 利用目的記録、DRM回避禁止、人間確認を本仕様内の開始条件として定義する。
- 詳細な権利判定は別仕様で後から追加できる。
- 保存先は承認済み上位仕様の`sources/originals`・`sources/manifests`を使用する。

## 3. 採用した旧版要素

- Windows版Kindle
- `pyautogui`
- `pygetwindow`
- capture settings
- 1ページ試し撮り
- ページ送り位置確認
- Kindle操作モジュール
- 旧CLI wrapper
- ページ画像・OCR結果を回帰資材として利用する方針

## 4. 新たに追加した要件

- キャプチャとOCRの分離
- capture profile
- capture session
- checkpoint・再開
- SHA-256
- perceptual hash
- ページ送り成功確認
- 重複・抜け候補
- atomicなページ・manifest保存
- 既存ページの無断上書き禁止
- 内部`page_index`とKindle表示ページの分離
- 利用目的記録
- DRM回避禁止
- 実画面操作と通常pytestの分離

## 5. 完了条件

- [x] ページ順を保って画像を保存できる仕様がある。
- [x] 重複と抜けを検出できる仕様がある。
- [x] 途中から安全に再開できる仕様がある。
- [x] 権利・利用目的の記録なしに処理を開始しない。
- [x] DRM回避を対象外としている。
- [x] 旧版実装の移行方法が定義されている。
- [x] `status: approved`、`version: "1.0"`で正本へ配置されている。
