---
spec_id: app-management-09-review-and-approval-workflow
task_id: SPEC-APP-010
title: "原稿・出典・承認・編集画面"
status: provisional
version: "0.1"
created_at: "2026-07-19"
depends_on:
  - app-management-03-frontend-information-architecture
  - app-management-07-project-task-job-workflow
spec_refs:
  - 07-approval-workflow.md
  - 01-common-identifiers-and-versioning.md
---

# 原稿・出典・承認・編集画面

## 目的

OCR結果、正規化text、主張と出典、原稿、音声を人間が確認・差し戻し・承認する管理画面の
範囲を草案化する。

## 背景

`07-approval-workflow.md`は4段階承認 (資料・カリキュラム/企画/検証済み原稿/試聴音声) と
差し戻しカテゴリを既に定義している。本書はこれをUIとしてどこまで作り込むかを決定する。

## 対象

- MVPでの編集画面範囲。
- 4段階承認の画面表示。
- diff・version履歴の要否。
- 一括承認の可否。
- AI生成箇所と人間編集の追跡。

## 対象外

- 承認の状態機械そのもの (既存仕様のまま、変更しない)。
- 出力設定・声選択 (→ `10`,`11`)。

## 既存仕様との関係

`07-approval-workflow.md`の状態・遷移・無効化規則・差し戻しカテゴリをそのまま画面へ反映する。
新たな承認状態や遷移を追加しない。

## 用語

`00`の用語集、`07-approval-workflow.md`の差し戻しカテゴリ用語をそのまま使用する。

## MVPでの編集画面範囲

| 機能 | MVP/次期 | 理由 |
|---|---|---|
| 承認待ち一覧・個別確認・承認/差し戻し操作 | MVP | `07-approval-workflow.md`のゲートを画面から動かせないと`01`のMVP導線が完結しない |
| 差し戻し理由の入力 (カテゴリ選択+コメント) | MVP | 既存仕様の`change_requests`スキーマをそのまま利用 |
| 原稿本文の読み取り専用プレビュー | MVP | 承認判断に必要な最低限の閲覧機能 |
| 原稿本文の直接編集 (WYSIWYG的な書き換え) | 次期 | 実装量が大きく、MVPの完成を遅らせるリスクが`01`で指摘されている |
| diff表示 (改訂間の差分) | 次期 | 閲覧だけなら現行内容の確認で足りるため優先度を下げる |
| 一括承認 (複数章まとめて承認) | 次期・条件付き | 誤承認のリスクがあるため、まずは個別確認を徹底する |

## 4段階承認の表示

```mermaid
flowchart LR
    G1[資料・カリキュラム承認] --> G2[企画承認]
    G2 --> G3[検証済み原稿承認]
    G3 --> G4[試聴音声承認]
```

画面は`07-approval-workflow.md`の状態値 (`draft`/`review_pending`/`approved`/
`changes_requested`/`revised`/`rejected`/`invalidated`)をそのままバッジ表示する。

## diffとversion履歴

MVPでは`content_revision`の数値のみを表示し (「revision 3」等)、詳細な行単位diffは
次期機能とする。理由: 既存仕様は`content_hash`とrevisionの整合性検証を要求するが、
diff表示自体はUI実装コストが高く、MVPの完成 (承認ゲートの迂回不可という必須要件)を
優先するため。

## 一括承認

一括承認はMVPでは提供せず、常に個別確認・個別承認を要求する。
理由: `07-approval-workflow.md`が要求する「試聴対象」(導入・技術的定義・数字・専門用語等)の
確認粒度を、一括承認は損ないやすい。次期で「章単位一括」等の限定的な一括承認を検討する余地を残す。

## AI生成箇所と人間編集の追跡

`01-common-identifiers-and-versioning.md` §10の`generated_by`メタデータ (type: ai, provider,
model, prompt_id, prompt_version, generated_at) を、原稿プレビュー画面で
「AI生成 (モデル: xxx, 生成日時: xxx)」として表示する。人間編集が入った場合は
編集前後、編集者、日時、理由を記録する (`00`の初期推奨回答どおり、単一利用者でも監査列を持つ)。

## 権限は単一利用者でも監査列を持つ案

現状は単一利用者のため、権限分離機能は実装しないが、
「誰が承認したか」を`approved_by`として記録するカラムを`07`の`approval_records`に
既に含めている (`06-database-logical-schema.md`参照)。既定値は固定の利用者識別子とする。

## 未承認出力の隔離

`07-approval-workflow.md` §12の`--force`実行時の`unapproved/`分離出力方針を、
画面上でも「未承認出力」として明確に区別されたセクションに表示し、
正式成果物一覧 (`10`)とは混在させない。ただし前述のとおり`--force`自体はCLI限定機能である。

## 画面一覧

| 画面 | 内容 |
|---|---|
| 承認一覧 | 4ゲートの状態バッジ、対象、更新日時 |
| 承認詳細 | 対象ファイル/bundleの内容プレビュー、hash、承認/差し戻しボタン |
| 差し戻し入力 | カテゴリ選択 (`07-approval-workflow.md` §9の列挙値)、対象segment/箇所、コメント必須 |

## approval gate

`07-approval-workflow.md` §11の実行ゲートをそのまま踏襲し、画面のJob起動ボタンは
ゲート未充足の場合disabledにする (`04`のJob起動API 403との対応)。

## 編集・diff

MVPは読み取り専用プレビューのみ。次期でdiff表示・簡易編集を追加する。

## 差し戻しreason

`07-approval-workflow.md` §9のカテゴリ (`source_missing`〜`other`) をドロップダウンで選択し、
コメントを必須入力とする。

## 異常系

| 状況 | 扱い |
|---|---|
| 承認対象のhashが現在のファイルhashと不一致 | 画面は`invalidated`バッジを表示し、承認操作を無効化する |
| 差し戻し理由未入力で差し戻しを確定しようとする | フォームバリデーションで停止 |
| 未検証の技術的主張が残ったまま原稿承認しようとする | Warning表示 (`audiobook-creation-pipeline.md` §11.3の確認事項を画面上でチェックリスト表示) |

## UIまたはAPIの入出力

`04`のAPI一覧の `/approvals/{gate}/approve`,`/approvals/{gate}/request-changes` を使用する。

## 状態遷移

`07-approval-workflow.md` §4の基本遷移をそのまま参照。本書はUI操作からの遷移トリガーのみ追加する。

## データ所有者・正本

承認内容そのものは`approvals.yaml`がファイル正本。DBは検索・一覧表示用サマリのみ保持する
(`05`の正本マトリクスと一致)。

## バリデーション

### Error

- hash不一致 (`invalidated`)のまま承認操作を許可する画面設計。
- 差し戻し理由なしでの差し戻し確定。

### Warning

- 未検証主張が残ったまま承認しようとする操作 (ブロックはしないが警告表示)。

## セキュリティ・プライバシー

承認記録の監査列 (`approved_by`,`approved_at`)は改ざん防止のためAPI経由のみで更新可能にし、
DB直接編集を想定しない (詳細は`13`)。

## テスト観点

- hash不一致状態で承認ボタンがdisabledになる。
- 差し戻し理由未入力で確定できない。
- AI生成メタデータ (`generated_by`)がプレビュー画面に表示される。
- 一括承認機能がMVP画面に存在しないことを確認する。

## 移行・互換性

`07-approval-workflow.md`のスキーマ・状態値を変更しない。画面は既存ファイルを読み書きする
操作レイヤーとして追加される。

## 未決定事項

- 次期のdiff表示方式 (行単位/segment単位)。
- 監修者ロール分離の要否 (`01`の未決定事項と同じ)。
- 一括承認を将来提供する場合の粒度。

## 人間レビュー項目

- `human_review_required`: 原稿編集をMVPから完全に除外する判断の妥当性。
- `human_review_required`: 一括承認を将来的にも提供しない方針でよいか。
- 草案の採否と未決定事項。

## 仕様昇格条件

- `07-approval-workflow.md`の状態・遷移と矛盾しないこと。
- MVP範囲 (読み取り専用プレビュー+承認/差し戻し) が`01-product-scope-and-mvp.md`と一致すること。
- 未承認出力の隔離方針が`13-security-backup-migration.md`と整合すること。
