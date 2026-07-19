---
spec_id: m4b-output
title: "M4B出力"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
generated_by:
  type: ai
  note: "旧仕様策定タスク(完了・削除済み)により生成。Git履歴を参照。旧ファイル名 m4b-and-complete-book-output.md から改名。"
depends_on:
  - audio-validation-thresholds.md
spec_refs:
  - audio-validation-thresholds.md
  - audiobook-creation-pipeline.md
  - 14-audio-packaging.md
  - 19-application-scope-and-mvp.md
---

# M4B出力

> **状態に関する注記**
> `19-application-scope-and-mvp.md`により、M4Bはpost-MVPの追加成果物として
> 承認済みである。正式な基本成果物は章単位MP3であり、**全文MP3は作成しない**。
> 本書が依存する`docs/spec-proposals/audio-validation-thresholds.md`は
> `status: provisional`である(実測未了)。「全章の音声検査合格後だけ生成する」
> という本書の合格条件は、provisional閾値に基づく暫定合格を意味する。
> 対象プレイヤーでの実機再生確認も未実施であり、`compatibility.status`は
> `provisional`のまま扱う。

## 1. 目的

章単位MP3の次の段階として、M4B、チャプター情報、カバー、メタデータ、
互換性を定義する。全文MP3は本製品の成果物として作成しない。

## 2. 対象範囲

- 章MP3とM4Bの必須・任意の位置付け
- M4B生成タイミング
- chapter情報の正本
- 対象プレイヤーと互換性確認方針
- メタデータ・カバー画像の扱い
- 章差し替え時の再生成範囲

## 3. 対象外

- 章単位MP3の生成自体(承認済み`14-audio-packaging.md`が定義済み)
- 音声検査の最終閾値そのもの(`docs/spec-proposals/audio-validation-thresholds.md`、provisional)
- ASRによる照合(→`asr-script-audio-verification.md`)
- 全文MP3の生成(本製品では作成しない)

## 4. 現行実装

現行コードにM4B生成の実装は存在しない。章単位MP3の生成については
`14-audio-packaging.md`(承認済み)が別途定義している。

## 5. 推奨仕様

### 5.1 章MP3とM4Bの位置付け

章MP3を必須のまま維持し、M4Bはpost-MVPの追加成果物にする。全文MP3は作成しない。

```yaml
output_requirements:
  chapter_mp3: required
  m4b: optional_additional_post_mvp
```

### 5.2 M4B生成タイミング

全章が原稿・試聴承認済みかつ音声検査合格後だけ生成する。

```text
全章の verified script 承認
∧ 全章の試聴音声承認
∧ 全章の音声検査が fail ではない(現状 provisional 閾値による判定)
↓
M4B生成を許可
```

音声検査がprovisional閾値に基づく場合、生成されたM4Bのフロントマターにも
`validation_threshold_status: provisional`を記録し、最終合格とは区別する。

### 5.3 chapter情報の正本

章manifestと章順を正本にする。

```yaml
m4b_chapter_source:
  primary: chapter_manifest
  fields_used:
    - chapter_id
    - order
    - title
    - start_time_offset
```

M4Bのchapter atomは、この章manifestから生成し、M4B側で手動編集しない。

### 5.4 対象プレイヤー

初期互換試験はApple BooksとVLC系プレイヤーを候補とし、実機未確認なら
provisionalにする。

```yaml
compatibility_targets:
  status: provisional
  candidates:
    - apple_books
    - vlc
  evidence:
    tested: false
    tested_players: []
```

実機再生確認は実装時のacceptance testとして実施する。

### 5.5 メタデータとカバー

確認済みmetadataだけを使用し、不明値をAIで補完しない。カバーは任意とする。

```yaml
m4b_metadata:
  title: null            # project-plan.yamlのtitleから取得、AI補完しない
  author: null            # 人間が明示的に入力した場合のみ設定
  narrator: null           # voice profileのdisplay_nameから取得可能だが、
                            # 表示用途に限定し法的なnarrator表記と混同しない
  year: null
  cover_image:
    required: false
    format: [jpeg, png]
    recommended_size: "1400x1400"
    source: human_provided
```

不明な著者・年などのフィールドは`null`のまま出力し、AIが推測で埋めない。

## 6. 入力

- 全章の承認済みverified script
- 全章の承認済み試聴音声
- 全章のセグメントWAV/章MP3、音声検査レポート(provisional閾値基準)
- 章manifest

## 7. 出力

- M4B manifest例(8節)
- 互換性確認表(5.4節)

## 8. M4B manifest例

```yaml
schema_version: "1.0"
project_id: database-foundations
output_type: m4b
content_revision: 1
chapters:
  - chapter_id: ch01
    order: 1
    title: データベース基礎とは
    start_time_offset_seconds: 0.0
    duration_seconds: 480.5
source_chapter_mp3s:
  - chapters/ch01/audio.mp3
metadata:
  title: データベース基礎
  author: null
  narrator: null
  year: null
validation:
  all_chapters_passed: true
  validation_threshold_status: provisional
compatibility:
  status: provisional
  tested_players: []
```

## 9. ffmpegコマンド(例、環境依存値は固定しない)

```text
ffmpeg -i concat_list.txt -i chapters.txt -map_metadata 1 -c copy output.m4b
```

具体的なコマンドオプション・エンコード設定は環境・ffmpegバージョンに依存するため、
本書では例として示すのみで、値を固定しない。

## 10. 正常系

1. 全章の原稿承認・試聴承認・音声検査結果(provisional基準)を確認する。
2. 章manifestからchapter atomを生成する。
3. 確認済みmetadataのみを設定する。
4. カバー画像が提供されていれば添付する(任意)。
5. M4Bを生成し、manifestへ`validation_threshold_status`を記録する。
6. 対象プレイヤーでの再生確認は人間が実施し、結果を`compatibility`へ反映する。

## 11. 異常系

| ケース | 扱い |
|---|---|
| 未承認章を含むM4Bを生成しようとする | `blocked` |
| 音声検査がfailの章を含む | `blocked` |
| chapter重複(順序衝突) | `fail` |
| metadata欠落を自動補完しようとする | Error(基本原則違反) |
| 対象プレイヤーで実再生できないのに互換性を合格扱いしようとする | Error(5.4節の`tested`必須化で防止) |
| 全文MP3を生成しようとする | Error(3節・5.1節の対象外方針違反) |

## 12. バリデーション

- 全chapterの`chapter_id`が一意である。
- `validation.all_chapters_passed`が`true`のときのみ生成を許可する。
- `compatibility.tested_players`が空の場合、`compatibility.status`を`provisional`のまま
  `approved`にしない。
- `output_type`が`m4b`以外(全文MP3等)の生成物を本仕様の対象として扱わない。

## 13. テスト観点

- 章位置へ正しく移動できる(chapter atomのタイムスタンプ検証)。
- 対象プレイヤーで再生できる(実機確認は実装時のacceptance test)。
- メタデータの出典が明確である(AI補完がないことを検証)。
- 未承認章を含むM4Bを生成できない。
- 一部章変更時に、影響する範囲だけ再生成される
  (`audiobook-creation-pipeline.md` 16.2節「MP3タグのみ変更→対象MP3のみ」の考え方を準用)。
- 全文MP3が生成されないことを確認する。

## 14. 移行・互換性

- 章MP3の生成自体は`14-audio-packaging.md`(承認済み)を変更しない。
- M4Bは追加成果物であり、既存の章MP3出力フローに影響しない。

## 15. 未決定事項

- 実際の対象プレイヤーでの互換性確認結果(実装時に実施)
- narrator表記の法的な取り扱い(クレジット表記との整合、`rights-and-license-management.md`と連動する可能性)

## 16. 完了条件

- [x] 章位置へ正しく移動できる設計になっている。
- [x] メタデータの出典が明確である。
- [x] 未承認章を含む成果物を生成できない。
- [x] post-MVPの追加成果物として承認されている。
- [x] 全文MP3を作成しない方針が明示されている。
- [x] 未実測の音声検査閾値・プレイヤー互換性は`provisional`として区別されている。
- [x] 実装コードを変更していない。
