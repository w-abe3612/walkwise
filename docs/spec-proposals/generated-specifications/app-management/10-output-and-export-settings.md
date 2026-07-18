---
spec_id: app-management-10-output-and-export-settings
task_id: SPEC-APP-011
title: "出力形式・出力プロファイル・成果物管理"
status: provisional
version: "0.1"
created_at: "2026-07-19"
depends_on:
  - app-management-01-product-scope-and-mvp
  - app-management-03-frontend-information-architecture
  - app-management-07-project-task-job-workflow
spec_refs:
  - 14-audio-packaging.md
  - 00-specification-guidelines.md
---

# 出力形式・出力プロファイル・成果物管理

## 目的

MP3、テキスト、EPUBを中心に、出力選択、単位、品質、保存先、再生成、成果物一覧を草案化する。

## 背景

`00-specification-guidelines.md` §4のデータ形式表はMP3を「章単位または配布用音声」と定め、
M4Bを「初期必須出力には含めない」としている。`14-audio-packaging.md`は章MP3・manifestの
生成を確定済み。EPUB出力についてはリポジトリ内に承認済み仕様が存在しない
(`evidence_gap`: EPUB関連は`docs/spec-proposals/generated-specifications/epub-text-extraction.md`が
未承認の抽出仕様として存在するのみで、EPUB *出力* についての仕様は本監査では確認できなかった)。

## 対象

- 出力形式の複数選択。
- 出力profileの保存・複製。
- 成果物のversion管理。
- 再生成・ダウンロード。

## 対象外

- 声・音声プロファイルの選択自体 (→ `11`)。
- Job監視の詳細 (→ `12`)。

## 既存仕様との関係

| 既存仕様 | 関係 |
|---|---|
| `14-audio-packaging.md` | 章MP3・manifest生成をMVPの主要出力とする。M4Bは対象外のまま維持。 |
| `00-specification-guidelines.md` §4 | MP3=章/配布用音声、TXT=既存互換入力という形式定義を出力選択肢の設計根拠とする。 |

## 用語

`00`の用語集を使用する。「出力プロファイル (Output Profile)」を本書で新規定義する:
出力形式・対象範囲・品質設定の組み合わせをテンプレートとして保存したもの。

## 出力形式は複数同時選択か

複数選択を可能にする。1回のBuild Requestで「MP3+テキスト」等の組み合わせをまとめて指定できる。

## format capability表

| 形式 | 状態 | 理由 |
|---|---|---|
| MP3 (章単位) | MVP・有効 | `14-audio-packaging.md`で確定済み |
| テキスト (検証済み原稿のtxt/md出力) | MVP・有効 | 既存の`text/`互換出力方針を踏襲 |
| EPUB | 次期・disabled | EPUB出力の承認済み仕様が存在しないため (`evidence_gap`) |
| MP3 (全文版) | 次期・disabled | `14-audio-packaging.md`が「SHOULD」止まりで確定していない |
| M4B | 対象外 | `audiobook-creation-pipeline.md`が明示的に初期対象外と規定 |

## 章別・全文をどう選ぶか

出力設定画面で「章単位」「全文まとめ」をチェックボックスで選べるようにするが、
全文まとめはformat capability表のとおり次期disabledとする。

## EPUBはどの仕様確定後に有効化するか

EPUB出力の承認済み仕様 (抽出ではなく生成側)が`docs/specifications/`に追加された時点で
有効化する。それまでは`10`のUI選択肢としては表示するが、理由付きdisabledとする
(`03-frontend-information-architecture.md`のdisabled状態方針と一致)。

## 出力profileを保存・複製できるか

出力プロファイルはプロジェクト単位で複数保存・複製できる設計とする。

```yaml
output_profile_id: mp3-and-text-default
project_id: database-foundations
formats:
  - mp3_chapter
  - text_verified_script
quality:
  mp3:
    codec: libmp3lame
    mode: vbr
    quality: 2
scope: all_chapters
```

## 同名成果物のversionと上書き

`06-database-logical-schema.md`の`artifacts.version_number`をそのまま使用し、
既存artifactを上書きしない。再生成のたびに新versionを作成し、UI上は最新versionを
既定表示しつつ過去versionへのアクセスも提供する (次期: 一覧の詳細表示)。

## output profile schema案

上記YAML例のとおり。`content_revision`を持ち、変更のたびに増加させる
(`01-common-identifiers-and-versioning.md`の一般原則に従う)。

## 画面項目

| 項目 | 型 | 備考 |
|---|---|---|
| 出力形式 (複数選択) | チェックボックス | capability表に従いdisabled制御 |
| 対象範囲 | 選択式 (全章/特定章) | MVP範囲 |
| 出力先を開く | ボタン | OSのファイルエクスプローラを開く (Windows: `explorer`起動) |

## disabled理由

disabled項目には常にツールチップで理由 (例: 「EPUB出力の仕様が未確定のため準備中です」)を
表示する (`03`のdisabled状態方針を継承)。

## artifact一覧

| 列 | 内容 |
|---|---|
| 種類 | mp3_chapter / text等 |
| version | `version_number` |
| 生成日時 | `created_at` |
| 生成元Job | `job_id`リンク |
| 操作 | ダウンロード / フォルダを開く / 再生成 |

## 再生成・download/open folder

再生成ボタンは新しいBuild Request/Jobを作成する (`07`のJob設計どおり)。ダウンロードは
静的ファイル配信、フォルダを開くはOS統合機能 (Windows Explorer起動)として次期実装候補とする
(MVPでは「保存先パスをコピー」で代替してもよい、実装コストとのトレードオフ)。

## 上書き禁止

`14-audio-packaging.md` §12のatomic output原則、および本書のversion管理方針により、
既存の正常な成果物ファイルが上書きされることはない。

## 異常系

| 状況 | 扱い |
|---|---|
| disabled形式を選択しようとする | UIレベルで選択不可 |
| 出力先ディスク容量不足 | Jobがfailedとなり、エラーメッセージで容量不足を明示 (`12`と連携) |
| 未承認試聴音声のまま本番出力を要求 | `09`の承認ゲートにより403で拒否 |

## UIまたはAPIの入出力

`GET /api/projects/{id}/artifacts`、出力プロファイルCRUD APIを`04`の一覧に追加する
(本書時点でのAPI一覧拡張として記録)。

## 状態遷移

Artifact自体に状態遷移はなく、生成元Jobの状態 (`07`)に従属する。

## データ所有者・正本

Artifact本体はファイル正本、索引はDB正本 (`05`のマトリクスどおり)。

## バリデーション

### Error

- disabled形式のJobが起動できてしまう設計。
- 既存artifactを新規生成が上書きする設計。

### Warning

- 出力プロファイルのcontent_revisionが更新時に増加しない。

## セキュリティ・プライバシー

出力先パスの安全性は`04`のpath安全性方針、`13`のセキュリティ草案に従う。

## テスト観点

- EPUBチェックボックスがdisabledであり、理由ツールチップが表示される。
- 同一出力を2回実行すると`version_number`が2つ存在し、旧versionが消えない。
- 未承認試聴音声のまま本番出力Jobが起動できない。

## 移行・互換性

`14-audio-packaging.md`のディレクトリ構成・manifest構造を変更しない。

## 未決定事項

- EPUB出力仕様の確定時期 (`evidence_gap`、人間が別途仕様策定を計画する必要がある)。
- 全文版MP3をいつMVPへ組み込むか。
- 「フォルダを開く」機能のOS統合実装方法。

## 人間レビュー項目

- `human_review_required`: EPUB出力を今後どのタイミングで仕様化するか。
- `human_review_required`: 出力プロファイルの複製機能をMVPに含めるかの最終判断。
- 草案の採否と未決定事項。

## 仕様昇格条件

- `14-audio-packaging.md`のversion・atomic output方針と矛盾しないこと。
- format capability表がEPUB仕様確定状況を正しく反映していること。
- artifact一覧のAPIが`04`のAPI一覧に統合されていること。
