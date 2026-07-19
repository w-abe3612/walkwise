---
spec_id: rights-and-license-management
title: "著作権・ライセンス・利用目的の管理"
status: review
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  note: "旧仕様策定タスク(完了・削除済み)により生成。Git履歴を参照。"
depends_on:
  - material-input-pipeline.md
  - source-storage-and-common-schema.md
spec_refs:
  - material-input-pipeline.md
  - source-storage-and-common-schema.md
  - ../specifications/audiobook-creation-pipeline.md
---

# 著作権・ライセンス・利用目的の管理(ドラフト)

> **本書は法律相談ではない。**
> 本書はrights情報の記録方法、状態遷移、公開ゲートの**仕組み**を定義するものであり、
> 個別資料の法的な利用可否を判定・保証するものではない。公開・商用利用の最終判断は
> 常に人間または専門家(弁護士等)に委ねる。夜間自動実行では、実在する特定資料の
> 権利状態確認は一切行っていない。

## 1. 目的

資料の権利情報を記録し、個人学習・社内利用・公開配布などの利用目的ごとに
人間確認を行う方法を定義する。

## 2. 対象範囲

- `rights.status`の状態一覧と遷移
- 利用目的の分類とゲート
- 購入済み資料(購入・閲覧権)と再配布権の分離
- ライセンス証拠(URL、取得日時、ライセンス名・版、確認者)の保存
- 確認不能資料の扱い
- 完成音声の配布ゲート
- クレジット表記生成に必要な情報

## 3. 対象外

- 個別資料の法的利用可否の判定そのもの
- 各国の著作権法・フェアユース規定の解釈
- DRM回避の是非(`audiobook-creation-pipeline.md`により対象外と明記済み)
- 契約書・利用規約の自動解釈

## 4. 現行実装

現行コードにrights管理の実装は存在しない。本書が最初の設計である。

## 5. 推奨仕様

### 5.1 rights.statusの状態一覧

質問1(権利状態をどう分類するか)への回答:

```text
unverified                   初期状態。未確認。
user_asserted_private_use    利用者が個人利用目的であると申告。裏付け未確認。
verified_open_license        オープンライセンス(CC等)を人間が確認済み。
verified_public_domain       パブリックドメインであることを人間が確認済み。
licensed_private_use         購入・契約に基づく私的利用権を人間が確認済み。
restricted                   利用に制限があることが判明。
needs_legal_review           専門家確認が必要と判断された。
rejected                     利用不可と判断された。
```

状態遷移の原則:

```text
unverified
  → user_asserted_private_use (利用者申告)
  → verified_open_license | verified_public_domain | licensed_private_use (人間が証拠確認)
  → restricted | needs_legal_review | rejected (問題発見時、いつでも遷移可)
```

一度`restricted`/`needs_legal_review`/`rejected`になった資料を、
新たな証拠なしに緩い状態へ戻さない。

### 5.2 利用目的の分類

質問2(個人学習と公開配布をどう区別するか)への回答:
利用目的を権利状態とは別の軸として管理する。

```text
personal_learning       個人の学習用途
internal_use            組織内共有(非公開)
public_distribution     不特定多数への公開配布
commercial_distribution 商用配布
```

### 5.3 利用目的別ゲート表

| rights.status \ usage_purpose | personal_learning | internal_use | public_distribution | commercial_distribution |
|---|---|---|---|---|
| `unverified` | 許可(生成過程のみ) | 拒否 | 拒否 | 拒否 |
| `user_asserted_private_use` | 許可 | `review_required` | 拒否 | 拒否 |
| `verified_open_license` | 許可 | 許可 | 許可(ライセンス条件に従う) | ライセンス条件次第(`review_required`) |
| `verified_public_domain` | 許可 | 許可 | 許可 | 許可 |
| `licensed_private_use` | 許可 | `review_required` | 拒否 | 拒否 |
| `restricted` | `review_required` | 拒否 | 拒否 | 拒否 |
| `needs_legal_review` | `review_required` | 拒否 | 拒否 | 拒否 |
| `rejected` | 拒否 | 拒否 | 拒否 | 拒否 |

質問3(購入済み資料をどう扱うか)への回答: **購入・閲覧権と再配布権を分離する。**
`licensed_private_use`は`personal_learning`のみを許可し、
`public_distribution`・`commercial_distribution`は常に拒否または`needs_legal_review`とする。
購入済みであることは公開・再配布の許可を意味しない
(`audiobook-creation-pipeline.md` 6.3節と一致)。

### 5.4 rights metadata例

質問4(ライセンス証拠を何として保存するか)への回答:

```yaml
rights:
  schema_version: "1.0"
  source_id: mysql-8-reference
  status: verified_open_license
  usage_purpose: personal_learning
  evidence:
    license_name: "CC BY-SA 4.0"
    license_version: "4.0"
    source_url: "https://example.invalid/license"
    retrieved_at: "2026-07-19T00:00:00+09:00"
    evidence_file: sources/reports/rights/mysql-8-reference-license.pdf
  confirmed_by:
    type: human
    name: null
    confirmed_at: null
  notes: ""
  history:
    - status: unverified
      changed_at: "2026-07-10T00:00:00+09:00"
      changed_by: system_default
```

`confirmed_by.type`は`human`のみを許可し、`ai`を許可しない
(AIは候補提示のみ行い、状態遷移の実行者にはなれない)。

### 5.5 確認不能資料の扱い

確認できない資料は`unverified`のまま保持し、`personal_learning`以外の
`usage_purpose`では一律`review_required`または拒否とする。
推測で`verified_*`へ格上げしない。

### 5.6 完成音声の配布ゲート

- `public_distribution`または`commercial_distribution`を目的とする成果物は、
  使用した全資料の`rights.status`が5.3節の該当セルで「許可」であることを
  出力前に検査する。
- 1件でも許可されない資料が含まれる場合、正式成果物への出力を`blocked`にする
  (`audiobook-creation-pipeline.md` 15節「未承認成果物の出力要求」と同様の扱い)。

### 5.7 クレジット表記の生成

```yaml
credit:
  source_id: mysql-8-reference
  display_text: "MySQL 8.0 Reference Manual (CC BY-SA 4.0)"
  required_by_license: true
  generated_from:
    - rights.evidence.license_name
    - rights.evidence.license_version
    - source metadata.title
```

クレジット文言は`rights.evidence`が揃っている資料についてのみ機械生成候補を作成し、
最終文言は人間が確認する。

質問5(AIの自動判定をどこまで許可するか)への回答:
AIは次に限定する。

- 権利状態の**候補**分類の提示(例: 「CCライセンスの可能性がある」)
- 不足情報(URL、取得日時、ライセンス名など)の指摘

AIは`rights.status`を`verified_*`や`licensed_private_use`へ確定させない。
状態遷移は常に人間が実行する(5.4節`confirmed_by.type: human`)。


### 5.8 撮影・スキャン資料とプライバシー

利用者が自分で撮影またはスキャンした事実だけでは、
本文の著作権、教材化権、公開権、再配布権を確認したことにならない。

画像資料では次を記録する。

```yaml
capture_or_scan:
  performed_by_user: true
  original_material_type: purchased_book
  ownership_or_access_basis: user_asserted
  public_distribution_allowed: false
  contains_people: unknown
  contains_personal_information: unknown
  exif_location_present: unknown
```

人物、学生名、社員名、住所、個人メモ等が含まれる場合、
権利確認とは別にprivacy reviewを必要とする。

将来の動画・授業録音ではさらに次を分離する。

- 視聴・所持
- 録画・録音
- 文字起こし
- AIへの外部送信
- 教材化
- 公開
- 商用利用

詳細案は`video-source-ingestion.md`と
`audio-recording-source-ingestion.md`へ置く。

## 6. 入力

- 資料metadata(`source-storage-and-common-schema.md`の`rights`項目)
- 利用者が申告する利用目的
- 人間が確認したライセンス証拠

## 7. 出力

- 資料ごとの`rights.yaml`(5.4節形式)
- 配布ゲート判定結果
- クレジット候補リスト

## 8. 正常系

1. 資料登録時に`rights.status: unverified`、`usage_purpose`を記録する。
2. 利用者が私的利用を申告した場合`user_asserted_private_use`へ遷移する。
3. 人間がライセンス証拠を確認し`verified_open_license`等へ遷移する。
4. 公開配布前に5.6節のゲート検査を実行する。
5. 許可された資料についてクレジット候補を生成し、人間が確認して確定する。

## 9. 異常系

| ケース | 状態/扱い |
|---|---|
| 権利未確認資料で公開配布しようとする | `blocked` |
| AIが`verified_*`へ状態遷移しようとする | Error(拒否) |
| ライセンス証拠なしで`verified_open_license`にしようとする | Error |
| `rejected`資料を証拠なしに`unverified`へ戻す | Error |
| 購入資料を`public_distribution`で使おうとする | `blocked`(5.3節ゲート) |
| 資料ごとのrights状態が資料に付随せず紛失 | Warning + `review_required` |

## 10. バリデーション

- `rights.status`が5.1節の列挙値のいずれかである。
- `verified_*`/`licensed_private_use`には`confirmed_by.type: human`と
  `confirmed_by.confirmed_at`が必須。
- `verified_open_license`には`evidence.license_name`が必須。
- `history`に状態変更履歴が追記専用(過去エントリを削除しない)で保持される。

## 11. テスト観点

- 5.3節のゲート表通りに公開可否が判定される。
- AIが状態遷移APIを直接呼んでも`human`確認なしには`verified_*`にならない。
- 購入資料の`personal_learning`は許可、`public_distribution`は拒否される。
- 証拠なしの`rejected`→`unverified`遷移が拒否される。
- クレジット候補が`evidence`不足資料については生成されない。

## 12. 移行・互換性

- 現行実装にrights管理がないため、既存データの移行対象はない。
- `source-storage-and-common-schema.md`の`rights:`項目(5.4節スキーマ)と
  フィールド名を一致させる。

## 13. 未決定事項

- 利用目的分類の粒度(例: `educational_institution_use`等の追加要否)
- 各国法域ごとの著作権例外規定の扱い(本書では意図的に扱わない)
- ライセンス証拠ファイルの保存容量・保持期間
- クレジット表記の自動フォーマット規則の詳細

## 14. 完了条件

- [x] 資料ごとの権利状態と根拠を追跡できる(5.4節)。
- [x] 個人利用と公開利用が区別されている(5.2, 5.3節)。
- [x] 未確認資料から公開成果物を作れない(5.6節)。
- [x] 自動判定を法的保証として表示しない(5.7節、本書冒頭の注記)。
- [x] 出力ドラフトが存在し、`status: review`である。
- [x] 実装コードを変更していない。

## 15. 特記事項

本書はテンプレート・ワークフローの提案であり、法律相談ではない。
実在の資料に本書を適用する際は、公開・商用利用に先立って人間または専門家の確認を
必須とする。
