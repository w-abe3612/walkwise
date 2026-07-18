---
status: active
version: "1.2"
last_updated: "2026-07-18"
---

# 仕様提案・仕様策定タスク

## 1. 役割

このディレクトリには、未承認の仕様、検討事項、
仕様を確定するためのタスク、検証中サンプルを置く。

承認済み仕様は`../specifications/`へ置く。

## 2. 正本

```text
承認済み仕様
＝ docs/specifications/

未承認仕様
＝ docs/spec-proposals/

仕様策定タスク
＝ docs/spec-proposals/task/

検証中サンプル
＝ docs/spec-proposals/examples/
```

## 3. 現在残す未承認仕様

- `12-coeiroink-client.md`
- `material-input-pipeline-unplanned.md`
- `video-source-ingestion.md`
- `audio-recording-source-ingestion.md`

01〜03および仕様書作成ガイドラインは承認済みへ昇格したため、
本ディレクトリから削除する。

音声候補変更提案は、関連仕様とタスクへ反映後に削除する。

## 4. 一覧

- [仕様策定タスク一覧](task/INDEX.md)
- [仕様策定タスクの運用](task/README.md)


## 5. 将来のmultimedia資料

次はMVP必須ではなく、未承認の将来案として保持する。

- [動画・YouTube等の資料入力案](video-source-ingestion.md)
- [授業録音・音声ファイルの資料入力案](audio-recording-source-ingestion.md)

カメラ写真・スキャナ画像は承認済み仕様へ昇格済みである。

```text
docs/specifications/image-material-ingestion.md
```
