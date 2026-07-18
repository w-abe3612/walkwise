---
status: active
version: "1.2"
created_at: "2026-07-19"
---

# Claude Code向け仕様ドラフト生成タスク

このディレクトリには、残りの仕様策定をClaude Codeへ依頼するための
一時的な指示書を置く。

## 実行開始

最初に次をClaude Codeへ読ませる。

```text
docs/tasks/00_specification-drafting-master.md
```

続いて、`SPECIFICATION_TASK_INDEX.md`の順序で個別タスクを実行する。

## 注意

これらは未承認仕様のドラフトを生成するタスクである。

- `docs/specifications/`へ自動昇格しない。
- `status: approved`へ自動変更しない。
- 試聴、法的判断、外部サービス確認を完了したことにしない。
- 実装コードを変更しない。

## 承認済み仕様へ昇格したタスク

仕様が承認された項目は、同じファイル名を実装タスクへ切り替えてよい。

- `12_kindle-capture.md`: Kindle画面キャプチャ実装タスク


## 画像資料入力

承認済み仕様に基づく実装タスク:

- `16_image-material-ingestion.md`

動画・授業録音は未承認の将来案であるため、
`docs/tasks/`へ実装タスクを作成しない。
