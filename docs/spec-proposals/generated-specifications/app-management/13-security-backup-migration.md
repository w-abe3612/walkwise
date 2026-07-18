---
spec_id: app-management-13-security-backup-migration
task_id: SPEC-APP-014
title: "セキュリティ・権利・バックアップ・移行"
status: provisional
version: "0.1"
created_at: "2026-07-19"
depends_on:
  - app-management-05-persistence-strategy
  - app-management-06-database-logical-schema
  - app-management-08-material-import-workflow
notes:
  - "タスク指示書 34_spec-draft-app-security-migration.md の depends_on に SPEC-APP-014 (自分自身) が含まれており、自己参照と判断した。おそらく別タスクIDの誤記であるため evidence_gap として記録し、依存関係は SPEC-APP-006/007/009 のみを実際の前提として扱った。"
---

# セキュリティ・権利・バックアップ・移行

## 目的

ローカル管理画面とDB導入で増えるpath操作、file upload、個人情報、backup、schema migration、
既存data移行の危険を整理する。

## 背景

`evidence_gap`: 本タスクの指示書 (`34_spec-draft-app-security-migration.md`)は
`depends_on`に自分自身 (`SPEC-APP-014`)を含めており、タスク定義上の誤記と考えられる。
本書は実質的な依存対象である`SPEC-APP-006`(`05-persistence-strategy`)、
`SPEC-APP-007`(`06-database-logical-schema`)、`SPEC-APP-009`(`08-material-import-workflow`)を
前提として作成した。この不整合は`app-management-overnight-report.md`で人間へ報告する。

## 対象

- loopback限定方針。
- path traversal対策。
- secret管理。
- DB+fileのバックアップ整合。
- 既存data移行。
- rollback。

## 対象外

- 具体的な暗号化アルゴリズムの実装コード (実装タスクで確定)。

## 既存仕様との関係

`image-material-ingestion.md` §15、`kindle-capture.md`の権利・利用目的記録方針を
バックアップ・移行対象データの取り扱いにもそのまま適用する。

## 用語

`00`の用語集を使用する。

## threat model

| 脅威 | 対象 | 対策方針 |
|---|---|---|
| 外部ネットワークからの不正アクセス | Backend API | loopback限定バインド (`02`参照)、既定で外部公開しない |
| path traversal (`../`等) によるファイルシステム外アクセス | 素材アップロード、成果物ダウンロード | サーバー側で新規決定したパスのみ使用し、利用者指定パスを直接結合しない (`04`のpath安全性方針) |
| secret (Gemini APIキー等) の平文漏洩 | `.env`、DB | DBへ平文保存しない、`.env`はリポジトリ管理外のまま維持 (現状どおり) |
| DB/ファイルの不整合によるデータ損失 | バックアップ・復元 | 同一世代でのbackup/restoreを強制 (下記) |
| 個人情報・肖像を含む素材の意図しない外部送信 | AI adapterへの画像送信等 | `image-material-ingestion.md` §16の既存方針 (権利・プライバシー確認済みのみ送信)を維持 |
| 未承認出力の正式成果物への混入 | deliverables相当の出力 | `07-approval-workflow.md`の`--force`分離方針を画面経由でも維持 |

## loopback外から接続可能にするか

初期は`127.0.0.1`限定とし、認証機構は設けない。これは単一利用者ローカル利用を条件とした
判断であり、外部公開が必要になった場合は認証機構の追加を前提条件とする
(`human_review_required`として次項に記録)。

## path policy

- アップロードされたファイルは、サーバー側で新規採番した`source_id`ベースのパスへ保存し、
  利用者が送信したファイル名・パスの文字列をディレクトリ構造の一部として直接使用しない。
- 成果物ダウンロードAPIは、DBの`artifacts.file_path`を参照して配信し、利用者からの
  任意パス指定を受け付けない。
- 将来「サーバー側ファイルシステムブラウザ」(`04`の次期候補)を実装する場合、
  許可されたroot配下 (プロジェクトディレクトリ)のみを列挙・参照可能にし、
  `..`を含むパスやroot外シンボリックリンクの参照を拒否する。

## secret management

- Gemini APIキー等の秘密情報は、現状どおり`.env`ファイル (リポジトリ管理外)で管理し、
  DBやフロントへ平文で送信・保存しない。
- 画面の「設定・診断」画面 (`03`)では、キーが設定されているかどうかの真偽値のみ表示し、
  値そのものは表示しない。

## backup/restore

- DB (SQLiteファイル)とプロジェクトディレクトリ (ファイル群)を同一タイムスタンプの
  世代としてまとめてバックアップする単位を定義する。
- 片方だけを別世代から復元することを手順上禁止する (`05`のbackup単位方針を継承)。
- バックアップの保存先・世代数はMVPでは利用者の手動操作 (エクスプローラでのコピー等)を
  基本とし、自動バックアップスケジューリングは次期候補とする。

## DB migration

- `05-persistence-strategy.md`のmigration方針 (起動時自動検出・適用、失敗時は起動中断)を
  そのまま踏襲する。
- migration実行前に、対象DBファイルの自動バックアップコピーを作成することを必須とする。

## legacy import

現状`data/library/`等の実データが存在しないため (`00`の監査参照)、本タスク時点では
「移行すべき既存データ」は存在しない。将来、旧`book.json`/`sections.json`形式のデータが
作成された場合の一方向インポート手順 (ファイル→DB、ファイル自体は変更しない)を
`05`の初期同期方針として踏襲する。

## rollback

- DB migrationのロールバックは、migration適用前の自動バックアップへの復元として提供する。
- Build Request/Jobの「取り消し」は`07`の方針どおり、既存履歴を書き換えず新規作成で表現する
  (データのロールバックとJob実行のロールバックは別概念として扱う)。

## privacy/rights

`image-material-ingestion.md` §15,§16の権利・プライバシー確認方針をそのまま踏襲し、
バックアップファイルにも同じ権利状態の情報が保持される (バックアップによって
権利確認記録が失われないようにする)。

## 故障注入ケース

| ケース | 期待動作 |
|---|---|
| DB migration中に電源断 | 次回起動時、migration前バックアップから安全に再試行できる |
| バックアップ処理中にディスク容量不足 | エラーで停止し、不完全なバックアップを正式バックアップとして扱わない |
| 素材アップロード時に`../../etc/passwd`のようなファイル名を送信 | サーバー側で無視し、新規パスのみ使用 |

## 実行前確認 (画面)

migration実行前、バックアップ未取得状態でのmigration実行はUIから警告し、
「バックアップを先に取得しますか」の確認を挟む (次期: 自動バックアップ)。

## UIまたはAPIの入出力

`GET /api/system/backup-status`,`POST /api/system/backup`等を次期APIとして候補に挙げる
(MVPでは手動運用のため必須APIではない)。

## 状態遷移

バックアップ・移行自体に状態遷移はないが、DB migrationは「未適用→適用中→適用済み/失敗」の
単純な状態を持つ。

## データ所有者・正本

本書は既存の正本方針 (`05`)を変更しない。バックアップは正本のコピーであり、
それ自体が新たな正本にはならない。

## バリデーション

### Error

- path traversal文字列を含むファイル名がそのままファイルシステムパスとして使われる設計。
- secretがDBやログへ平文出力される設計。
- migration失敗時に黙って古いスキーマのまま起動を継続する設計。

### Warning

- バックアップ未取得のままmigrationを実行しようとする。

## セキュリティ・プライバシー

上記threat modelがそのまま本項の内容である。

## テスト観点

- path traversal文字列を含むアップロードファイル名がサーバー側パスに影響しないことを確認する。
- migration失敗時にアプリ起動が中断し、人間向けエラーが表示される。
- DBとファイルの世代不一致バックアップからの復元を試みた場合に警告が出る。
- `.env`のAPIキーがAPIレスポンス・ログに含まれないことを確認する。

## 移行・互換性

既存データが存在しないため (`00`の監査参照)、現時点での移行対象はない。将来データが
蓄積された段階で、本書のlegacy import方針を適用する。

## 未決定事項

- 自動バックアップスケジューリングの要否・頻度。
- 将来の認証機構導入 (外部公開要求が生じた場合)。
- 暗号化 (DBファイル自体の暗号化)要否。

## 人間レビュー項目

- `human_review_required`: タスク指示書の依存関係自己参照 (誤記の可能性) の確認。
- `human_review_required`: loopback限定・認証なしという方針を維持し続けてよい期間の判断。
- `human_review_required`: 自動バックアップ機能をMVPに含めるかどうか。
- 草案の採否と未決定事項。

## 仕様昇格条件

- threat modelに人間の承認が得られていること。
- path traversal対策がPoCまたは実装レビューで実証されていること。
- バックアップ/移行手順が`05`,`06`の正本・スキーマ設計と矛盾しないこと。
