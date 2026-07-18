---
spec_id: 17-file-based-data-persistence-policy
title: "17-file-based-data-persistence-policy.md"
status: approved
version: "1.0"
approved_at: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_220811.txt"
---

## データ永続化に関する初期方針

初期実装では、MySQL、SQLiteなどのデータベースを使用しない。

設定、状態、原稿、検証結果、タスク、音声生成情報は、YAML、JSON、Markdownおよび通常のファイルとして管理する。

データベースの導入は、次のような必要性が生じた時点で改めて検討する。

* 管理対象の作品や章が大幅に増えた場合
* 複雑な検索や集計が必要になった場合
* 複数ユーザーによる同時利用が必要になった場合
* Web管理画面を実装する場合
* 並列処理やジョブ管理が必要になった場合
* ファイルベースの状態管理では整合性の維持が難しくなった場合

将来のデータベース移行を妨げないため、ファイルベースの段階でも、各データには安定したIDとスキーマバージョンを付与する。

```yaml
schema_version: "1.0"
project_id: mysql_beginner
chapter_id: ch01
segment_id: ch01-seg001
```

ファイルパスは識別子そのものとして扱わず、IDに関連付けられた保存場所として扱う。

初期段階では、データ構造と各工程の責務を確定することを優先し、データベース固有のテーブル設計、マイグレーション、接続管理、バックアップ機能は策定対象外とする。
