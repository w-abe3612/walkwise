---
spec_id: 17-local-data-persistence-policy
title: "ローカルデータ永続化方針"
status: approved
version: "2.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
supersedes: "17-file-based-data-persistence-policy.md (v1.0)"
spec_refs:
  - 01-common-identifiers-and-versioning.md
  - 19-application-scope-and-mvp.md
  - 20-electron-desktop-architecture.md
  - 23-distribution-and-platform-policy.md
---

# ローカルデータ永続化方針

## 1. 目的

Electronデスクトップアプリ本体において、SQLiteとファイルシステムの責務を分離し、
metadataの検索性と実行状態の追跡性を確保しつつ、原資料・原稿・音声などの
大型コンテンツをファイル正本として保持する方針を定義する。

本書はv1.0(ファイルのみを正本とする方針)を置き換える。DB導入は
「Web管理画面を実装する場合に改めて検討する」というv1.0の条件が、
Electron本体アプリの採用によって満たされたことに伴う改訂である。

## 2. 対象範囲

- SQLiteとファイルの責務分担
- fileとDBの正本境界
- file writeとDB transactionの順序
- backup単位
- migration方針
- DB破損時の復旧範囲
- 利用者データの保存場所の方針

## 3. 対象外

- 具体的なテーブル定義(→`docs/db/`)
- 画面からの操作手順(→`docs/screens/`)
- Electron側の実装コード

## 4. 現行実装

現行コードにDB・永続化層の実装は存在しない。本書は新規導入方針である。

## 5. 推奨仕様

### 5.1 責務分担

```yaml
persistence:
  metadata_and_execution_state: sqlite
  large_content: filesystem
```

- SQLiteは、Project・Source・BuildRequest・Job・Artifactのmetadataと実行状態の正本とする(`docs/db/00-database-overview.md`参照)。
- 原資料本文、画像、生成原稿、WAV、MP3等の大型コンテンツはファイルを正本とする。
- SQLiteへ大型バイナリを保存しない。

### 5.2 DBとfileの責務を重複させない

同じ内容をDBの列とファイルの両方に正本として持たない。ファイルパスは
DB側から相対パスとして参照し、内容そのものの複製をDBへ持たない。

### 5.3 file writeとDB transactionの順序

1. ファイルへ一時パスで書き込む。
2. 書き込み内容を検証する。
3. 正式パスへatomic replaceする。
4. atomic replaceの成功後にDB transactionをcommitする。

ファイル書き込みが失敗した場合、DB側のcommitを行わない。この順序により、
DBとファイルが不整合になった場合でも「ファイルが存在しないのにDBに記録がある」
状態を避け、「ファイルは存在するがDB記録がない」状態(再スキャンで復元可能)に留める。

### 5.4 backup単位

SQLiteファイルと、Projectデータを保持するディレクトリ一式を、同一世代の
バックアップ単位として扱う。DBファイルのみ、またはProjectディレクトリのみを
別世代から復元することを禁止する。

### 5.5 migration方針

- migrationはアプリ起動時に未適用分を自動検出・適用する。
- migration適用前にDBファイルの自動バックアップコピーを作成する。
- migration失敗時はアプリ起動を中断し、人間向けエラーを表示する。古いスキーマのまま黙って起動しない。

### 5.6 DB破損時の復旧範囲

- Project・Source・Artifactのmetadataは、対応するファイル(企画本文、素材原本、成果物ファイル)を
  再スキャンすることで再構築できる設計とする。
- BuildRequest・Jobの実行履歴は、対応するファイルが存在しないため、DB破損時は
  この履歴のみ失われることを許容する。Artifact本体(生成済みファイル)自体は
  ファイルシステムに残るため、復旧不能な損失にはならない。

### 5.7 利用者データの保存場所

- Projectデータ(SQLiteファイル、Project別ディレクトリ)は、Electronアプリの
  install先ディレクトリへ保存しない。
- 具体的な保存先パス(WindowsのAppData配下等)は、実装時にElectronの
  `app.getPath('userData')`相当の標準的な利用者データ領域を用いて確定する。
- uninstall時、アプリ本体は削除されるが、利用者データ領域は自動削除しない
  (詳細は`23-distribution-and-platform-policy.md`)。

## 6. 入力

- Electron mainプロセスからのDB接続要求
- Python workerが生成するartifact・進捗イベント

## 7. 出力

- SQLiteファイル(metadata・実行状態の正本)
- ファイルシステム上のProjectデータ一式

## 8. 必須項目

- 全構造化データの`schema_version`(`01-common-identifiers-and-versioning.md`準拠)
- DBの各エンティティにおける安定ID(`project_id`等の既存ID体系をそのまま使用し、DB固有のsurrogate IDへ置き換えない)

## 9. 任意項目

- backupの自動スケジューリング設定

## 10. バリデーション

### Error

- 大型バイナリ(音声・画像本体)をSQLiteの列へ保存する設計。
- ファイル書き込み前にDB commitが先行する順序。
- migration失敗時に古いスキーマのまま起動を継続する設計。

### Warning

- backupがDBとファイルで別世代になっている状態を検出した場合。

## 11. 状態・エラー・警告

DB接続・migration自体の状態遷移は次のとおりとする。

```text
not_migrated -> migrating -> migrated
migrating -> migration_failed (人間確認まで起動を停止)
```

## 12. 正常例

1. アプリ起動時、SQLiteファイルの存在を確認する。
2. 未適用のmigrationがあれば、バックアップ作成後に適用する。
3. Project一覧をDBから取得し、対応するファイルの存在を検証する。
4. 新規Source登録時、ファイルをimmutable領域へ書き込み、成功後にDBへmetadataを記録する。

## 13. 異常例

| 状況 | 扱い |
|---|---|
| SQLiteファイルが存在しない(初回起動) | 新規作成し、初期migrationを適用する |
| SQLiteファイルが破損している | 起動を中断し、バックアップからの復元またはfileからの再構築を人間へ提示する |
| ファイル書き込みは成功したがDB commitに失敗した | 次回起動時の再スキャンでDB側を復元できる状態を維持する |
| migration適用中にアプリが強制終了した | 次回起動時、バックアップから安全に再試行する |

## 14. テスト観点

- ファイル書き込み成功後にDB commitが行われる順序をコードレベルで確認できる。
- DBファイルを削除した状態から、ファイル群のみでProject/Source/Artifactのmetadataを再構築できる。
- migration失敗時にアプリ起動が中断される。
- Projectデータがアプリのinstall先ディレクトリへ保存されない。

## 15. 移行・互換性

- 本書はv1.0を置き換える。v1.0が定義していた「DBを使用しない」という制約は撤回する。
- 本書へのリンク更新が必要な参照元は次のとおりであり、すべて更新済みである。
  - `docs/specifications/README.md`
  - `docs/db/00-database-overview.md`

## 16. 未決定事項

なし。実装時に確定するWindows上の具体的な保存先パス(5.7節)は、
`app.getPath('userData')`相当の標準領域を使うという方針自体は確定しており、
実装時のパス確定はこの方針の範囲内の詳細作業である。

## 17. 完了条件

- SQLiteとfileの責務分担が明示されている。
- file writeとDB transactionの順序が定義されている。
- backup単位が定義されている。
- migration方針が定義されている。
- DB破損時の復旧範囲が明示されている。
- 利用者データがinstall先に保存されない方針が明示されている。
- v1.0からの改訂理由が記録されている。
