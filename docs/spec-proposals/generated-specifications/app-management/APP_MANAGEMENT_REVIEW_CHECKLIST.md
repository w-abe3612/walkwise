---
status: provisional
version: "0.1"
created_at: "2026-07-19"
task_id: SPEC-APP-019
---

# app-management 草案 人間レビューチェックリスト

このチェックリストは、`docs/spec-proposals/generated-specifications/app-management/`配下の
全草案 (00〜17、決定マトリクス含む)を人間がレビューする際に使う。
未チェック項目は `docs/specifications/` への昇格条件を満たさない。

## 全体

- [ ] 全17個別草案 + 決定マトリクス + 本チェックリストが存在し、`status`が`review`/`provisional`/
      `blocked`のいずれかである (`approved`になっていない)。
- [ ] `docs/specifications/`配下が一切変更されていない。
- [ ] `script/`,`tests/`,`requirements.txt`,`Dockerfile`,`docker-compose.yml`が変更されていない。
- [ ] 各草案に「対象外」「未決定事項」「人間レビュー項目」が明記されている。

## 00 現状・用語

- [ ] 「タスク」の二義性 (制作依頼 vs 開発タスク)整理に同意する。
- [ ] `evidence_gap` (04,05,06,08,10,11,13,15番仕様の未精読)を認識し、必要なら精読を指示する。

## 01 製品範囲・MVP

- [ ] MVP/次期/将来の区分に同意する。
- [ ] EPUB出力を次期送りにする判断に同意する。

## 02 アーキテクチャ・起動方式

- [ ] 技術スタック案A (FastAPI+Vue SPA)の暫定採用に同意する、または代替案を指示する。
- [ ] Windowsホスト直接実行を正式経路、Dockerを開発・テスト用途とする方針に同意する。
- [ ] PoC-1 (一コマンド起動)の実施を承認する。

## 03 フロント情報設計

- [ ] 画面一覧・MVP範囲に同意する。

## 04 バックエンドAPI

- [ ] SSE採用、multipart upload方式に同意する。
- [ ] path安全性方針に同意する。

## 05 永続化戦略

- [ ] 永続化案2 (SQLiteメタデータ正本)の暫定採用に同意する、または代替案を指示する。
- [ ] PoC-2 (ファイルからのDB再構築)の実施を承認する。
- [ ] `17-file-based-data-persistence-policy.md`改訂の必要性に同意する。

## 06 DB論理スキーマ

- [ ] entity一覧・ERDに同意する。
- [ ] soft delete/archive方針に同意する。

## 07 Project/Job状態遷移

- [ ] Build Request/Job分解粒度に同意する。
- [ ] rollback非提供 (新規作成のみ)方針に同意する。

## 08 素材インポート

- [ ] copy方式既定 (reference方式は次期)に同意する。
- [ ] PDF/EPUB下位仕様未確定のままUI選択肢に含める判断に同意する。

## 09 承認・編集画面

- [ ] MVPで原稿編集を含めない判断に同意する。
- [ ] 一括承認を提供しない方針に同意する。

## 10 出力設定

- [ ] EPUB・全文版MP3をdisabledとする判断に同意する。

## 11 声選択

- [ ] COEIROINKをdisabledとする判断 (未実装のため)に同意する。
- [ ] クレジット表記の最終確認が必要であることを認識する。

## 12 Job監視

- [ ] 直列実行制限 (MVP)に同意する。
- [ ] ログ無期限保存方針に同意する、または保存期間を指示する。

## 13 セキュリティ・バックアップ・移行

- [ ] loopback限定・認証なし方針に同意する。
- [ ] タスク34番の依存関係自己参照 (誤記の可能性)を認識し、必要なら指示元タスクを修正する。
- [ ] 自動バックアップをMVPに含めるか判断する。

## 14 テスト戦略

- [ ] test pyramid・acceptance scenarioに同意する。
- [ ] E2Eフレームワーク採用可否を判断する (未決定事項)。

## 15 追加機能提案

- [ ] 25件の提案分類・Top5採用推奨に同意する。

## 16 統合草案

- [ ] 全体構成図・MVP対応表に矛盾がないことを確認する。
- [ ] 実装分割案 (TASK-APP-001〜015)の順序に同意する。

## 17 仕様昇格計画

- [ ] 分割昇格方針・昇格順序に同意する。
- [ ] PoC-1, PoC-2の実施担当・スケジュールを決定する。

## 最終確認

- [ ] `docs/tasks/app-management-overnight-report.md`を読み、blocked/evidence_gap/
      human_review_required項目をすべて把握した。
- [ ] 次に着手する項目 (PoCまたは個別仕様レビュー)を決定した。
