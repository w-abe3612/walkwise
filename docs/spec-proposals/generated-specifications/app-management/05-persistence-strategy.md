---
spec_id: app-management-05-persistence-strategy
task_id: SPEC-APP-006
title: "ファイルとDBの永続化責務"
status: provisional
version: "0.1"
created_at: "2026-07-19"
depends_on:
  - app-management-00-current-state-and-terminology
  - app-management-02-architecture-and-runtime
  - app-management-04-backend-api-and-service-boundary
spec_refs:
  - 17-file-based-data-persistence-policy.md
  - 02-process-input-output.md
  - 01-common-identifiers-and-versioning.md
---

# ファイルとDBの永続化責務

## 目的

既存ファイル正本と新DBの境界を比較し、DBへ保存するもの、ファイルへ残すもの、
同期・再構築方法を草案化する。本書は`17-file-based-data-persistence-policy.md`が
予告した「DB導入検討」の中核部分にあたる。

## 背景

`00`の監査により、現状は完全にファイルベースであり、DBは一切導入されていない。
`17-file-based-data-persistence-policy.md`は「Web管理画面を実装する場合」を
DB検討条件の一つとして明記しており、本タスク群の実行そのものがこの条件を満たす。
同仕様は同時に「データベース固有のテーブル設計、マイグレーション、接続管理、
バックアップ機能は策定対象外とする」とも述べており、本書と`06`,`13`がこの対象外部分を
今回初めて具体化する。

## 対象

- 3永続化案の比較。
- 正本マトリクス (DBに置くもの/ファイルに置くもの)。
- DB transactionとfile atomic writeの整合方式。
- 再構築・repair方針。
- backup単位、同時実行、DB migration方針。

## 対象外

- DB論理スキーマの詳細 (→ `06`)。
- バックアップ運用の具体手順 (→ `13`)。

## 既存仕様との関係

| 既存仕様 | 関係 |
|---|---|
| `17-file-based-data-persistence-policy.md` | 本書が、同仕様が延期していたDB検討を実施する。承認された場合、同仕様はv2として改訂対象になる (`17-specification-promotion-plan.md`で扱う)。 |
| `02-process-input-output.md` §7 (正本表) | ファイル側に残す対象の一次情報源とする。 |
| `01-common-identifiers-and-versioning.md` | DBの主キーではなく、既存の安定ID (`project_id`等)をDBの論理キーとしてそのまま使う。 |
| `07-approval-workflow.md` | `approvals.yaml`の内容とDBの承認レコードの二重正本を避ける設計とする。 |

## 用語

- **メタデータ正本**: 状態・関連・履歴等、検索・一覧表示に必要な情報の正本。
- **原本正本**: 本文・画像・音声等、大容量またはimmutableなコンテンツの正本。

## 3永続化案の比較

### 案1: ファイル正本 + SQLiteは索引・Job管理のみ

| 項目 | 内容 |
|---|---|
| 概要 | YAML/JSONファイルを唯一の正本とし続け、SQLiteは検索高速化・Job実行履歴のためのキャッシュ/索引として使う。DBを消しても再構築可能。 |
| 利点 | `17-file-based-data-persistence-policy.md`の思想を最も強く維持できる。DB破損時のリスクが最小 (ファイルを読めば復元可能)。 |
| 欠点 | Project/BuildRequest/Job等、ファイルに対応物がない新概念 (`00`参照) の履歴をどこに置くかが曖昧になる。索引の再構築ロジックを常に維持するコストがかかる。 |

### 案2: SQLiteをメタデータ正本、原素材・大型成果物はファイル

| 項目 | 内容 |
|---|---|
| 概要 | Project状態、Source metadata、BuildRequest、Job、Artifact index、Approval、設定等をSQLiteの行として正本管理する。原資料本文、画像、WAV/MP3/EPUB本体、および`project-plan.yaml`等の企画本文は引き続きファイルを正本とする。 |
| 利点 | Job/BuildRequestという新概念に自然な置き場ができる。検索・一覧表示・整合性制約(外部キー等)をDBの機能で保証できる。大型バイナリをDBに入れないため肥大化を避けられる。 |
| 欠点 | ファイルとDBの二重管理点 (例: 承認状態を`approvals.yaml`とDBのどちらで正本にするか) を明確に切り分ける設計が必要。file変更とDB更新のトランザクション不整合リスクがある。 |

### 案3: PostgreSQL等サーバー型を正本とするサーバー型

| 項目 | 内容 |
|---|---|
| 概要 | メタデータ正本をPostgreSQL等のサーバー型RDBMSに置く。 |
| 利点 | 将来の複数利用者・同時アクセス・大規模データに対する拡張性が最も高い。 |
| 欠点 | ローカル単一利用者PCへサーバープロセスの常駐が必要になり、`01`の単一利用者ローカル前提およびインストールの簡便性 (一コマンド起動) と衝突する。バックアップ・移行の運用コストがSQLiteより高い。 |

### 比較まとめ

| 観点 | 案1 ファイル+索引SQLite | 案2 SQLiteメタデータ正本 | 案3 PostgreSQL |
|---|---|---|---|
| 単一利用者ローカル前提との親和性 | 高 | 高 | 低 (サーバー常駐が必要) |
| 新概念(BuildRequest/Job)の自然な置き場 | 低 | 高 | 高 |
| 導入・運用コスト | 低 | 中 | 高 |
| 将来の複数利用者拡張性 | 低 | 中 (移行は必要) | 高 |
| 障害時の復旧しやすさ (ファイルから再構築) | 最高 | 中 (原則ファイルからの再構築を設計する) | 低 |
| `17`の初期方針との連続性 | 最高 | 中 | 低 |

### 採用判断

**MVPでは案2 (SQLiteをメタデータ正本、原素材・大型成果物はファイル) を暫定推奨とする。**

判断条件:
- 案1は新概念の置き場が曖昧になり、`00`で整理したBuildRequest/Jobモデルを一貫して扱えない。
- 案3はローカル単一利用者・一コマンド起動という`01`,`02`の前提と衝突する。
- 案2は`APP_MANAGEMENT_SPEC_DRAFT_DECISIONS.md`の初期仮説とも一致し、既存資料の二重正本を避ける設計 (下記マトリクス) を徹底すれば`17`の懸念にも対応できる。

将来、複数利用者・大規模データの要求が明確化した場合、案3への移行を検討する
(`13-security-backup-migration.md`のmigration方針で移行可能性を残す)。

## 正本マトリクス

| データ | 正本 | 備考 |
|---|---|---|
| Project企画本文 (`project-plan.yaml`の内容) | ファイル | 既存仕様の正本を維持。DBは`project_id`・表示用サマリ・状態のみ保持 |
| Project状態・作成日時・表示メタデータ | DB | 一覧表示・検索用 |
| Source (資料) 本文・原本 | ファイル (immutable) | `image-material-ingestion.md`等の既存原則を維持 |
| Source metadata (一覧表示用: 種類、状態、hash参照) | DB | ファイル側`sources.yaml`とは別に、検索用に複製ではなく「参照」として持つ (下記同期方針) |
| 承認内容 (`approvals.yaml`) | ファイル | 既存仕様の正本を維持。承認ゲート判定はファイルを読んで行う |
| 承認の検索用サマリ (状態、日時) | DB | Dashboard表示専用のキャッシュとして扱い、ファイルと不一致の場合はファイルを正として再同期する |
| BuildRequest (制作依頼) | DB | ファイルに対応物がない新概念のため正本はDBのみ |
| Job / JobEvent (実行履歴・ログ) | DB | 同上 |
| Artifact index (成果物の一覧・パス・hash) | DB | 実体ファイルはfileに置き、DBは索引のみ |
| Artifact本体 (MP3/テキスト/EPUB) | ファイル | 既存`14-audio-packaging.md`の出力方針を維持 |
| VoiceProfile本体 (`voices/<id>.yaml`) | ファイル | 既存仕様の正本を維持 |
| VoiceProfile参照・利用履歴 | DB | どのBuildRequestでどのprofileを使ったかの記録 |
| アプリ全体設定 (起動ポート、engine接続先等) | DB | ファイルではなく設定テーブルとして管理 (次期: エクスポート機能検討) |

**二重正本を避ける原則**: DBに保持する「メタデータの複製」は、常にファイル側の内容から
再構築可能な派生情報として扱い、DB行がファイルの内容そのものを上書きする権限を持たない。
矛盾が検出された場合は、承認・企画本文についてはファイルを正、Job/BuildRequestのようにDBが
唯一の正本であるものはDBを正とする。

## DB transactionとfile atomic writeの整合方式

1. ファイルへの書き込みは、既存方針 (`02-process-input-output.md` §13、`14-audio-packaging.md` §12) の
   通り一時ファイル書き込み後のatomic replaceを維持する。
2. DB側の関連レコード更新は、ファイルのatomic replaceが成功した後にコミットする
   (「ファイル書き込み成功 → DBコミット」の順序を固定し、逆順にしない)。
3. DBコミットが失敗した場合でもファイルは正しい内容のまま残るため、次回起動時の再同期
   (下記repair方針) でDB側を復元できる。
4. 完全な分散トランザクションは導入せず、「ファイルが正、DBは追従」という非対称設計で
   整合性を保証する。

## 再構築・repair方針

- DBファイル (SQLite) が破損・消失した場合、`project-plan.yaml`、`sources.yaml`、
  `approvals.yaml`等の既存ファイルをスキャンして、Project/Source/Approvalのメタデータテーブルを
  再構築できる設計を必須とする。
- BuildRequest/Jobの実行履歴はファイルに対応物がないため、DB消失時は**履歴のみ失われる**ことを
  許容する (実行結果のartifact自体はファイルに残るため、復旧不能な損失にはならない)。
- 起動時に「DBとファイルの整合性チェック」をオプションで実行できるコマンドを用意する
  (詳細は`13`で確定)。

## backup単位

- DB (SQLiteファイル1つ) と、プロジェクトディレクトリ (ファイル群) を、同一世代の
  バックアップ単位として扱う (`13-security-backup-migration.md`で詳細化)。
- DBのみ、またはファイルのみを個別に古い世代へ戻すことを禁止する運用ルールを設ける。

## 同時実行

- MVPは単一利用者・単一プロセス前提のため、SQLiteの同時書き込み制約 (writer1件)は実用上問題にならないと仮定する。
- 複数タブ/複数ウィンドウから同時に同一Projectを操作するケースは、楽観的ロック (content_revision比較) で衝突検出する方針とし、詳細は`06`,`07`で扱う。

## DB migration方針

- スキーマ変更はマイグレーションスクリプトで管理し、起動時に未適用migrationを自動検出・適用する
  (`02`の起動シーケンスと連携)。
- migration失敗時はアプリ起動を中断し、人間へ明示的なエラーを表示する (黙って古いスキーマのまま起動しない)。
- 詳細な移行・ロールバック手順は`13-security-backup-migration.md`に委譲する。

## 採用前提

- SQLiteライブラリ (Python標準の`sqlite3`、またはSQLAlchemy等のORM) の追加導入が必要になるが、
  本タスクでは実際のインストールは行わない (`requirements.txt`は変更しない)。
- 案2の採用は、`06-database-logical-schema.md`でのエンティティ設計が破綻しないことを条件とした
  暫定判断である。

## データ所有者・正本

上記「正本マトリクス」がそのまま本項の内容である。

## バリデーション

### Error

- DBが承認済み企画本文・原稿本文の正本になる設計 (既存ファイル正本の無断DB化)。
- ファイル書き込み前にDBコミットが先行する順序。

### Warning

- DB再構築ロジックが未検証のまま運用に入る。
- 同時アクセス時の楽観的ロックが未実装のまま複数ウィンドウ操作を許可する。

## セキュリティ・プライバシー

DBファイルの保存場所・アクセス権については`13-security-backup-migration.md`に委譲する。

## テスト観点

- DBファイルを削除した状態からファイル群のみでメタデータテーブルを再構築できる。
- ファイル書き込み成功後にDBコミットが行われる順序をコードレベルで確認できる。
- 承認内容 (`approvals.yaml`) とDB側サマリが不一致の場合、ファイル側が優先されることを確認する。
- BuildRequest/Jobのみを持つDBを消失させた場合、artifact自体は失われないことを確認する。

## 移行・互換性

- 既存のファイルベース運用からDB併用への移行は、既存ファイルを一切変更せずDB側へ読み込む
  「一方向の初期同期」として設計する。
- `17-file-based-data-persistence-policy.md`の改訂 (v1.0→v2.0相当) が必要になるが、
  本タスクでは`docs/specifications/`を変更しないため、`17-specification-promotion-plan.md`で
  昇格時の改訂手順として記録するに留める。

## 未決定事項

- SQLiteの具体的なORM/アクセス方式 (生SQL vs SQLAlchemy等) は実装タスクで確定する。
- 同時アクセス制御 (楽観的ロックの粒度) の詳細は`06`,`07`で継続検討。
- 将来PostgreSQLへ移行する場合の具体的な移行ツールは未定。

## 人間レビュー項目

- `human_review_required`: 案2の採用可否、および`17-file-based-data-persistence-policy.md`改訂の方向性。
- `human_review_required`: 「ファイルが正、DBは追従」という非対称設計が十分な整合性を提供するかの技術的検証 (PoC推奨、`17-specification-promotion-plan.md`で計画する)。
- 草案の採否と未決定事項。

## 仕様昇格条件

- 正本マトリクスに矛盾がないことを人間が確認していること。
- DB再構築の実現可能性がPoCで検証されていること (`17`のPoC計画対象)。
- `17-file-based-data-persistence-policy.md`との改訂関係が明記されていること。
