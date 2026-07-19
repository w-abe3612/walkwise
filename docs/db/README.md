---
status: active
version: "1.1"
last_updated: "2026-07-19"
---

# 承認済みDBテーブル仕様

## 1. 役割

このディレクトリには、承認済みのDB方針、ERD、各テーブル定義、制約、index、
migration方針を置く。`docs/db/`は承認済みDB仕様の正本である。

## 2. 格納対象

- DB overview(採用理由、責務分担、ERD、migration方針)
- 各テーブルの論理定義(column、型、null可否、PK/FK/unique/check/index、
  archive/delete規則、正常例、異常例、migration時の注意)

## 3. 格納禁止対象

- 未承認・provisional・blockedなテーブル追加案(→`docs/spec-proposals/`)
- 画面仕様(→`docs/screens/`)
- 実際のmigrationスクリプトやORMコード

## 4. 昇格・削除のライフサイクル

1. テーブル追加・変更案は、まず`docs/spec-proposals/`へ提案として作成する。
2. 検索・制約上の必要性が確認され、既存承認済みテーブルと矛盾しないことを
   人間が確認した場合のみ、本ディレクトリへ昇格する。
3. 昇格後、対応する提案ファイルは削除する。
4. 承認済み後の破壊的変更(列削除・型変更等)は、`00-database-overview.md`の
   migration方針に従い、version番号を更新した上で反映する。

## 5. 正本の優先順位

```text
1. docs/specifications/ (製品全体の方針・アーキテクチャ)
2. docs/db/00-database-overview.md (DB全体方針)
3. docs/db/<NN>-<table>-table.md (個別テーブル定義)
```

個別テーブル定義がoverviewと矛盾する場合、overviewを優先し、個別定義側を修正する。

## 6. ファイル命名規則

```text
00-database-overview.md
01-projects-table.md
02-sources-table.md
03-build-requests-table.md
04-jobs-table.md
05-artifacts-table.md
90-schema-migrations-table.md
```

`<連番2桁>-<table名(snake_case複数形)>-table.md`とする。overviewのみ`00-database-overview.md`
の固定名とする。`90`番台は内部システム管理テーブル用に予約し、製品ドメインテーブル
(`01`〜`05`)の連番とは区別する。

## 7. 最小構成(MVP)

製品ドメインテーブルは次の5つに限定する。

```text
projects
sources
build_requests
jobs
artifacts
```

`job_events`、`source_revisions`、`output_profiles`、`voice_profile_refs`、
`approval_records`、`app_settings`は、MVPでは別テーブルにせず、JSON列・ファイル・
親テーブルの最小列で保持する。検索・制約上の必要性が確認された場合のみ、
5節の昇格手順に従ってテーブルを追加する。

## 8. 製品ドメインテーブルと内部システム管理テーブル

`01`〜`05`(製品ドメインテーブル)と`90`番台(内部システム管理テーブル)は
役割が異なる。

| 区分 | 対象 | 5テーブル制限 | archive/delete規則 | 利用者からの可視性 |
|---|---|---|---|---|
| 製品ドメインテーブル(`01`〜`05`) | projects/sources/build_requests/jobs/artifacts | 対象 | `01-projects-table.md`のarchive規則に従う | 画面から参照される |
| 内部システム管理テーブル(`90`番台) | schema_migrations | 対象外 | 適用しない(追記専用) | 利用者は直接参照しない |

内部システム管理テーブルを追加しても、7節の「製品ドメインテーブルは5つ」という
制限には影響しない。新しい内部システム管理テーブルが必要になった場合も、
5節の昇格手順(まず`docs/spec-proposals/`で提案)に従う。
