---
status: active
version: "2.0"
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
過去に存在した`docs/spec-proposals/generated-specifications/`は、内容を
本ディレクトリ直下または承認済み仕様へ統合したうえで削除済みである。

## 4. 現在残す未承認仕様(flat)

- [`coeiroink-client.md`](coeiroink-client.md)
- [`material-input-pipeline.md`](material-input-pipeline.md)
- [`source-storage-and-common-schema.md`](source-storage-and-common-schema.md)
- [`rights-and-license-management.md`](rights-and-license-management.md)
- [`pdf-direct-text-extraction.md`](pdf-direct-text-extraction.md)
- [`ocr-and-scanned-pdf.md`](ocr-and-scanned-pdf.md)
- [`epub-text-extraction.md`](epub-text-extraction.md)
- [`source-preprocessing.md`](source-preprocessing.md)
- [`audio-validation-thresholds.md`](audio-validation-thresholds.md)
- [`m4b-and-complete-book-output.md`](m4b-and-complete-book-output.md)
- [`asr-script-audio-verification.md`](asr-script-audio-verification.md)
- [`kindle-capture-separate-tool.md`](kindle-capture-separate-tool.md)(本体対象外・専用ツール案)
- [`video-source-ingestion.md`](video-source-ingestion.md)(post-MVP将来案)
- [`audio-recording-source-ingestion.md`](audio-recording-source-ingestion.md)(post-MVP将来案)

各提案は、昇格条件(既存承認済み仕様と矛盾しない、`evidence_gap`/
`human_review_required`が解消している等)を満たし、人間が承認した時点で
対応する承認済みディレクトリへ移し、本ディレクトリから削除する。

## 5. 一覧

- [仕様策定タスク一覧](task/INDEX.md)
- [仕様策定タスクの運用](task/README.md)

## 6. 将来のmultimedia資料

次はMVP必須ではなく、未承認の将来案として保持する。

- [動画・YouTube等の資料入力案](video-source-ingestion.md)
- [授業録音・音声ファイルの資料入力案](audio-recording-source-ingestion.md)

カメラ写真・スキャナ画像は承認済み仕様へ昇格済みである。

```text
docs/specifications/image-material-ingestion.md
```
