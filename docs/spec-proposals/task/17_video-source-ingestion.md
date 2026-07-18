---
task_type: specification_decision
status: draft
order: 17
title: "動画・YouTube等の資料入力"
depends_on:
  - 7_source-storage-and-common-schema.md
  - 8_rights-and-license-management.md
spec_refs:
  - ../video-source-ingestion.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/video-source-ingestion.md"
last_updated: "2026-07-19"
---

# 17. 動画・YouTube等の資料入力

## 目的

ローカル動画、YouTube等のURL、字幕、transcriptを
資料として扱う将来仕様を策定する。

## 決定する事項

- URLをlocatorだけにするか
- 自動downloadを許可する条件
- 公式字幕、利用者字幕、ASRの優先順位
- timestamp locator
- 映像依存箇所
- slide・frame抽出
- 外部ASR送信
- 権利・プライバシー
- 長時間動画のcost control

## 推奨初期回答

- URLだけで自動downloadしない。
- 利用者提供字幕・transcript・許可済みlocal fileを優先する。
- transcriptだけでは分からない図・実演を`visual_context_required`にする。
- ASR rawとnormalized transcriptを分離する。
- 外部送信は既定で無効にする。
- 映像確認なしに技術的主張をverifiedへ進めない。

## 完了条件

- 取得経路と権利が明確である。
- timestamp locatorがある。
- 映像依存情報を人間確認へ送れる。
- downloadやplatform回避を暗黙に許可しない。
