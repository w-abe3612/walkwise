---
task_type: specification_decision
status: draft
order: 18
title: "授業録音・音声ファイルの資料入力"
depends_on:
  - 7_source-storage-and-common-schema.md
  - 8_rights-and-license-management.md
  - 15_asr-script-audio-verification.md
spec_refs:
  - ../audio-recording-source-ingestion.md
output_spec: "docs/specifications/audio-recording-source-ingestion.md"
last_updated: "2026-07-19"
---

# 18. 授業録音・音声ファイルの資料入力

## 目的

授業、講義、勉強会、インタビュー、音声メモ等を録音したファイルを
資料として扱う将来仕様を策定する。

## 決定する事項

- 対応音声形式
- 録音許可、教材化、公開、外部送信の分離
- timestamp locator
- ASR provider
- speaker diarization
- 個人情報
- noise・reverberation・重複・欠番
- companion slideとの同期
- 長時間音声の分割

## 推奨初期回答

- 原音声をimmutableにする。
- 加工音声、ASR raw、normalized transcriptを分離する。
- local ASRを初期候補にし、cloudは既定無効にする。
- 複数話者と第三者発話はprivacy reviewへ送る。
- speaker IDを自動的に実名へ結び付けない。
- ASRだけで技術的事実をverifiedにしない。

## 完了条件

- 録音・文字起こし・教材化・公開・外部送信を別々に承認できる。
- timestamp locatorがある。
- 複数話者と個人情報を扱える。
- companion materialとの関係を保存できる。
