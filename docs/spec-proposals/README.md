---
status: active
version: "3.0"
last_updated: "2026-07-19"
---

# 仕様提案・仕様策定タスク

## 1. 役割

このディレクトリには、未承認・provisional・blockedな仕様提案、検討事項、
仕様を確定するためのタスク、検証中サンプルだけを置く。

承認済み仕様は`../specifications/`、承認済みDBテーブル仕様は`../db/`、
承認済み画面仕様は`../screens/`へ置く。承認済み仕様と同じ内容を
本ディレクトリへ重複して残さない。

## 2. 正本

```text
承認済み仕様
＝ docs/specifications/

承認済みDBテーブル仕様
＝ docs/db/

承認済み画面仕様
＝ docs/screens/

未承認仕様
＝ docs/spec-proposals/ (flat配置)

仕様策定タスク
＝ docs/spec-proposals/task/

検証中サンプル
＝ docs/spec-proposals/examples/
```

## 3. flat配置と禁止階層

`docs/spec-proposals/`直下は、個々の提案書をflatに置く。`task/`・`examples/`
以外の新しいサブディレクトリ(`generated-specifications/`等)を作らない。

## 4. 現在残す未承認仕様(flat)

- [`coeiroink-client.md`](coeiroink-client.md) — `status: blocked`。post-MVPの追加TTS engine。公式API・実機情報が未確認。
- [`audio-validation-thresholds.md`](audio-validation-thresholds.md) — `status: provisional`。実測未了。

各提案は、昇格条件(既存承認済み仕様と矛盾しない、`evidence_gap`が解消している等)を
満たし、人間が承認した時点で対応する承認済みディレクトリへ移し、
本ディレクトリから削除する。

## 5. 一覧

- [仕様策定タスク一覧](task/INDEX.md)
- [仕様策定タスクの運用](task/README.md)

## 6. 恒久的対象外(未承認提案として保持しない)

次は製品の恒久的対象外であり、未承認提案としても保持しない
(`docs/specifications/19-application-scope-and-mvp.md` 5.5節)。

- Kindle画面キャプチャ・Kindle専用ツールの開発
- 動画・YouTube等の資料入力
- 授業録音・音声ファイルの資料入力

カメラ写真・スキャナ画像は承認済み仕様へ昇格済みである。

```text
docs/specifications/image-material-ingestion.md
```

## 7. 昇格済みの参考(履歴)

次のテーマは、資料入力パイプラインの下位仕様として承認済み仕様へ昇格済みであり、
本ディレクトリには重複して残していない。

- 資料入力パイプラインの責務と境界 → `docs/specifications/material-input-pipeline.md`
- 資料保存構成と共通資料スキーマ → `docs/specifications/source-storage-and-common-schema.md`
- 著作権・ライセンス・利用目的の管理 → `docs/specifications/rights-and-license-management.md`
- PDF直接テキスト抽出 → `docs/specifications/pdf-direct-text-extraction.md`
- OCRとスキャンPDF → `docs/specifications/ocr-and-scanned-pdf.md`
- EPUBテキスト抽出 → `docs/specifications/epub-text-extraction.md`
- 書籍データ前処理 → `docs/specifications/source-preprocessing.md`
- M4B出力 → `docs/specifications/m4b-output.md`
- ASRによる原稿と音声の照合 → `docs/specifications/asr-script-audio-verification.md`
