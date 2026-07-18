---
spec_id: 01-common-identifiers-and-versioning
title: "共通ID・バージョン・命名規則"
status: approved
version: "1.0"
approved_at: "2026-07-18"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---


# 共通ID・バージョン・命名規則

## 1. 目的

企画、資料、章、セグメント、主張、出典、音声、承認を安定して関連付けるため、
共通ID、バージョン、ハッシュ、ファイル命名の規則を定義する。

本仕様の目的は、表示名、ファイル名、保存場所が変化しても、
同じ論理データを同じIDで追跡できる状態を維持することである。

---

## 2. 対象範囲

本仕様は次に適用する。

- シリーズ
- 作品プロジェクト
- 資料
- 章
- 節
- 原稿セグメント
- 技術的主張
- キャラクタープロファイル
- 音声プロファイル
- 音声成果物
- 承認
- 構造化ファイルのスキーマバージョン
- 内容改訂番号
- 内容ハッシュ
- ファイル名

---

## 3. 対象外

次は本仕様では決めない。

- UUID生成ライブラリ
- ファイルロック方式
- バックアップ世代数
- データベース主キー
- 外部サービスが返すspeaker IDやUUIDの具体値
- 作品ごとの表示タイトル
- 人間向けファイル名の翻訳

---

## 4. 基本原則

### 4.1 IDと表示名を分ける

IDは内部参照に使用し、表示名は人間向け表示に使用する。

```yaml
character_id: kasukabe-tsumugi
display_name: 春日部つむぎ
```

表示名を変更してもIDを変更してはならない。

### 4.2 IDとファイルパスを分ける

ファイルを移動してもIDを変更してはならない。

### 4.3 IDは再利用しない

削除または廃止したIDを、別の論理データへ再利用してはならない。

### 4.4 旧IDを暗黙変換しない

旧形式から新形式への変換は、互換ルールに従い明示的に行う。

---

## 5. 共通ID

| 対象 | キー | 例 | 一意範囲 |
|---|---|---|---|
| シリーズ | `series_id` | `hundred-year-knowledge` | library全体 |
| 作品 | `project_id` | `database-foundations` | library全体 |
| 資料 | `source_id` | `mysql-8-reference` | library全体 |
| 章 | `chapter_id` | `ch01` | project内 |
| 節 | `section_id` | `ch01-sec01` | chapter内 |
| セグメント | `segment_id` | `ch01-seg001` | project内 |
| 主張 | `claim_id` | `ch01-claim001` | project内 |
| キャラクター | `character_id` | `neutral-explainer` | library全体 |
| 音声プロファイル | `voice_profile_id` | `sample-voicevox-profile` | library全体 |
| 音声成果物 | `audio_id` | `ch01-seg001-r0003` | project内 |
| 承認 | `approval_id` | `approval-script-r0003` | project内 |
| 変更要求 | `request_id` | `cr-0001` | project内 |

`segment_id`と`claim_id`は、章IDを先頭へ含めることをSHOULDとする。

---

## 6. ID形式

新規IDは次の正規表現へ適合しなければならない。

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

許可:

```text
database-foundations
ch01
ch01-seg001
mysql-8-reference
```

不許可:

```text
Database Foundations
database_foundations
データベース
database/foundations
```

旧形式の`section1`、`bookId`由来の値などは、
互換入力として読み込んでよいが、新規出力には使用しない。

---

## 7. unit ID

`unit_id`は処理対象単位を表す互換・実行用の汎用IDである。

```text
章単位: ch01
全文単位: book
旧全文単位: full_book
```

読み込み時:

```text
full_book -> book
book      -> book
```

新形式へ保存するときは`book`を使用する。

---

## 8. スキーマバージョン

各構造化ファイルは`schema_version`をMUSTで持つ。

```yaml
schema_version: "1.0"
```

形式は文字列の`major.minor`とする。

- 後方互換な任意項目追加: minor
- 必須項目追加、意味変更、削除: major
- 未知のmajor: error
- 未知のminor: 読み込み可能な場合はwarning

---

## 9. 内容改訂番号

編集可能な正本は`content_revision`をSHOULDで持つ。

承認対象と生成結果へ影響する正本ではMUSTとする。

```yaml
content_revision: 3
```

規則:

- 1から始める。
- 内容変更ごとに1増加させる。
- 表示順だけの変更でも生成結果へ影響するなら増加させる。
- 単なるファイル移動では増加させない。
- 自動生成物は入力revisionを別途記録する。

---

## 10. 共通メタデータ

### 10.1 MUST

すべての構造化ファイル:

- `schema_version`
- ファイルの主ID

承認対象・キャッシュ対象・生成物:

- `content_revision`
- `content_hash`

### 10.2 SHOULD

```yaml
created_at: "2026-07-18T21:00:00+09:00"
updated_at: "2026-07-18T21:30:00+09:00"
```

AI生成物:

```yaml
generated_by:
  type: ai
  provider: example
  model: example-model
  prompt_id: chapter-draft
  prompt_version: "1.2"
  generated_at: "2026-07-18T21:00:00+09:00"
```

---

## 11. 内容ハッシュ

承認無効化、キャッシュ判定、差分検出にはSHA-256を使用する。

```yaml
content_hash:
  algorithm: sha256
  value: "0123456789abcdef..."
```

### 11.1 正規化

構造化データのハッシュは、次の順で生成する。

1. YAMLまたはJSONをデータ構造へ読み込む。
2. ハッシュ対象外項目を除外する。
3. 文字列をUTF-8、Unicode NFCへ正規化する。
4. 改行をLFへ統一する。
5. mapping keyを辞書順へ並べる。
6. 配列順は保持する。
7. JSON互換のcanonical形式へ変換する。
8. SHA-256を計算する。

### 11.2 原則として除外する項目

- `created_at`
- `updated_at`
- `generated_at`
- 出力先パス
- 実行ログ
- ハッシュ値そのもの
- 承認者コメント

### 11.3 含める項目

- 正式本文
- 表示順
- 参照ID
- 生成結果へ影響する設定
- character profile revision
- voice profile revision
- TTS engine version
- prompt version
- 資料revision

同じ正規化入力からは、同じハッシュが生成されなければならない。

---

## 12. ファイル命名

正式ファイル名:

```text
series-plan.yaml
project-plan.yaml
chapter-spec.yaml
script.yaml
claims.yaml
sources.yaml
approvals.yaml
voice-profile.yaml
character-profile.yaml
manifest.json
validation.json
```

`approval.yaml`は使用せず、複数承認を保持するため`approvals.yaml`へ統一する。

---

## 13. 推奨配置

```text
project/project-plan.yaml
project/sources.yaml
project/approvals.yaml
project/characters/<character_id>.yaml
project/voices/<voice_profile_id>.yaml

chapters/<chapter_id>/chapter-spec.yaml
chapters/<chapter_id>/draft/script.yaml
chapters/<chapter_id>/verified/script.yaml
chapters/<chapter_id>/claims.yaml
```

章のIDをディレクトリ名として使用する。

---

## 14. 外部エンジンID

VOICEVOXやCOEIROINKのIDは、安定した内部IDとは分離する。

```yaml
character_id: lilin-chan
voice_profile_id: lilin-chan-coeiroink-default
engine: coeiroink
speaker:
  id: "<engine-speaker-id>"
  style_id: "<engine-style-id>"
```

エンジンIDを`character_id`へ流用してはならない。

---

## 15. 現行形式との対応

| 現行 | 新仕様 |
|---|---|
| `bookId` | `project_id` |
| `sectionId` | `chapter_id`または互換`unit_id` |
| `fileName` | 表示・互換情報。主IDにはしない |
| `chunk_id` | 必要に応じて`segment_id`へ変換 |
| `schemaVersion: 2` | 旧JSONスキーマとして別系列管理 |
| `full_book` | 読み込み時に`book`へ正規化 |
| `approval.yaml` | `approvals.yaml` |

変換時には元の値をprovenanceへ記録する。

---

## 16. バリデーション

### Error

- 必須IDが空
- 新規IDが正規表現へ不適合
- 一意範囲内でID重複
- 参照先IDが存在しない
- 未知のmajor schema version
- content revisionが1未満
- ハッシュアルゴリズムが未対応

### Warning

- 旧ID形式を読み込んだ
- `full_book`を`book`へ正規化した
- SHOULD項目が欠落
- source locatorが粗い
- 表示名とIDの対応が未確認

---

## 17. 正常例

```yaml
schema_version: "1.0"
project_id: database-foundations
content_revision: 1
content_hash:
  algorithm: sha256
  value: "..."
title: データベース基礎
```

---

## 18. 異常例

```yaml
schema_version: 1
project_id: "データベース 基礎"
content_revision: 0
```

問題:

- `schema_version`が文字列ではない。
- `project_id`がID規則へ適合しない。
- `content_revision`が1未満である。

---

## 19. テスト観点

- 新規IDの正常・異常境界
- IDごとの一意範囲
- タイトル変更後もIDが維持される
- `book`と`full_book`の正規化
- `approval.yaml`から`approvals.yaml`への移行
- 同じ正規化入力から同じハッシュ
- mapping key順が異なっても同じハッシュ
- 配列順が変われば異なるハッシュ
- `bookId`から`project_id`を解決できる
- VOICEVOXとCOEIROINKのエンジンIDを保持できる

---

## 20. 完了条件

- 全仕様サンプルを本書のIDで相互参照できる。
- IDごとの一意範囲が一意に判断できる。
- 同じ入力から同じハッシュを生成できる。
- 旧`book.json`と`sections.json`の識別子を変換できる。
- 外部エンジンIDと内部IDを混同しない。
