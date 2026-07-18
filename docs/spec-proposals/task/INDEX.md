---
status: active
version: "1.4"
last_updated: "2026-07-19"
---

# 仕様策定タスク一覧

## 1. 実行規則

- 原則として番号順に進める。
- `depends_on`が未完了のタスクには着手しない。
- 承認済み仕様は`spec_refs`で参照する。
- 完成した仕様は`docs/specifications/`へ移す。
- 仕様承認後にのみ`docs/tasks/`へ実装タスクを作成する。

## 2. 承認済みの横断仕様

- [オーディオブック作成全体パイプライン](../../specifications/audiobook-creation-pipeline.md)
- [AIモデルルーティング・資料構築・コスト制御](../../specifications/18-ai-model-routing-and-cost-control.md)

## 3. タスク状態

| 状態 | 意味 |
|---|---|
| `draft` | 未着手または検討中 |
| `review` | 仕様案の確認中 |
| `blocked` | 依存事項や外部条件により停止 |
| `done` | 仕様が承認され、正本へ反映済み |

## 4. 一覧

| 順序 | テーマ | 状態 | 依存 | 出力仕様 |
|---:|---|---|---|---|
| 0 | [オーディオブック作成全体パイプライン](../../specifications/audiobook-creation-pipeline.md) | done | なし | `docs/specifications/audiobook-creation-pipeline.md` |
| 1 | [サンプル1章による仕様間整合性確認](1_sample-book-end-to-end-validation.md) | draft | 承認済み上位仕様 | `docs/specifications/examples/sample-book/` |
| 2 | [ファイル保存運用の詳細](2_file-persistence-operations.md) | draft | 1 | `docs/specifications/file-persistence-operations.md` |
| 3 | [話者別音声プロファイル初期値](3_voice-profile-default-values.md) | draft | 1 | `docs/specifications/voice-profile-default-values.md` |
| 4 | [音声検査の最終閾値](4_audio-validation-thresholds.md) | draft | 3 | `docs/specifications/audio-validation-thresholds.md` |
| 5 | [COEIROINKのバージョン・API・起動方式](5_coeiroink-client-runtime-api.md) | draft | 3 | `docs/specifications/12-coeiroink-client.md` |
| 6 | [資料入力パイプラインの責務と境界](6_material-input-pipeline-boundary.md) | draft | 承認済み上位仕様 | `docs/specifications/material-input-pipeline.md` |
| 7 | [資料保存構成と共通資料スキーマ](7_source-storage-and-common-schema.md) | draft | 6、2 | `docs/specifications/source-storage-and-common-schema.md` |
| 8 | [著作権・ライセンス・利用目的の管理](8_rights-and-license-management.md) | draft | 6、7 | `docs/specifications/rights-and-license-management.md` |
| 9 | [PDF直接テキスト抽出](9_pdf-direct-text-extraction.md) | draft | 7 | `docs/specifications/pdf-direct-text-extraction.md` |
| 10 | [OCRとスキャンPDF](10_ocr-and-scanned-pdf.md) | draft | 7 | `docs/specifications/ocr-and-scanned-pdf.md` |
| 11 | [EPUBテキスト抽出](11_epub-text-extraction.md) | draft | 7 | `docs/specifications/epub-text-extraction.md` |
| 12 | [Kindle画面キャプチャ](12_kindle-capture.md) | done | 承認済み上位仕様・旧版実装証拠 | `docs/specifications/kindle-capture.md` |
| 13 | [書籍データ前処理](13_source-preprocessing.md) | draft | 9、10、11、12 | `docs/specifications/source-preprocessing.md` |
| 14 | [M4Bと全文版出力](14_m4b-and-complete-book-output.md) | draft | 4 | `docs/specifications/m4b-and-complete-book-output.md` |
| 15 | [ASRによる原稿と音声の照合](15_asr-script-audio-verification.md) | draft | 4、14 | `docs/specifications/asr-script-audio-verification.md` |
| 16 | [カメラ写真・スキャナ画像の資料入力](16_image-material-ingestion.md) | done | 承認済み横断仕様 | `docs/specifications/image-material-ingestion.md` |
| 17 | [動画・YouTube等の資料入力](17_video-source-ingestion.md) | draft | 7、8 | `docs/specifications/video-source-ingestion.md` |
| 18 | [授業録音・音声ファイルの資料入力](18_audio-recording-source-ingestion.md) | draft | 7、8、15 | `docs/specifications/audio-recording-source-ingestion.md` |
