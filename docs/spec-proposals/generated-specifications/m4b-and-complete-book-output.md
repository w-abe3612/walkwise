---
spec_id: m4b-and-complete-book-output
title: "M4Bと全文版出力"
status: provisional
version: "0.1"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/14_m4b-complete-book.md
  source_task: docs/spec-proposals/task/14_m4b-and-complete-book-output.md
depends_on:
  - 4_audio-validation-thresholds.md
spec_refs:
  - audio-validation-thresholds.md
  - ../../specifications/audiobook-creation-pipeline.md
  - ../../specifications/14-audio-packaging.md
---

# M4Bと全文版出力(ドラフト)

> **状態に関する注記**
> 本書が依存する`audio-validation-thresholds.md`(タスク04)は
> `status: provisional`である(実測未了)。「全章の音声検査合格後だけ生成する」
> という本書の合格条件は、provisional閾値に基づく暫定合格を意味する。
> また対象プレイヤーでの実機再生確認は本タスクでは行っていない。
> 以上により本書全体を`status: provisional`とする。

## 1. 目的

章単位MP3の次の段階として、全文MP3またはM4B、チャプター情報、カバー、
メタデータ、互換性を定義する。

## 2. 対象範囲

- 章MP3とM4Bの必須・任意の位置付け
- M4B生成タイミング
- chapter情報の正本
- 対象プレイヤーと互換性確認方針
- メタデータ・カバー画像の扱い
- 章差し替え時の再生成範囲

## 3. 対象外

- 章単位MP3の生成自体(承認済み`14-audio-packaging.md`が定義済み)
- 音声検査の最終閾値そのもの(タスク04、provisional)
- ASRによる照合(→タスク15)

## 4. 現行実装

現行コードにM4B生成・全文版出力の実装は存在しない。
章単位MP3の生成については`14-audio-packaging.md`(承認済み)が別途定義している。

## 5. 推奨仕様

### 5.1 章MP3とM4Bの位置付け

質問1への回答: **章MP3を必須のまま維持し、M4Bは追加成果物にする。**

```yaml
output_requirements:
  chapter_mp3: required
  m4b: optional_additional
  full_text_mp3: optional_additional
```

### 5.2 M4B生成タイミング

質問2への回答: **全章が原稿・試聴承認済みかつ音声検査合格後だけ生成する。**

```text
全章の verified script 承認
∧ 全章の試聴音声承認
∧ 全章の音声検査が fail ではない(現状 provisional 閾値による判定)
↓
M4B/全文版生成を許可
```

音声検査がprovisional閾値に基づく場合、生成されたM4Bのフロントマターにも
`validation_threshold_status: provisional`を記録し、最終合格とは区別する。

### 5.3 chapter情報の正本

質問3への回答: **章manifestと章順を正本にする。**

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

質問4への回答: **初期互換試験はApple BooksとVLC系プレイヤーを候補とし、
実機未確認ならprovisionalにする。**

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

夜間実行では実機再生確認を行っていない。

### 5.5 メタデータとカバー

質問5への回答: **確認済みmetadataだけを使用し、不明値をAIで補完しない。
カバーは任意とする。**

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
- 全文版(任意)

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
| 未承認章を含む全文版を生成しようとする | `blocked` |
| 音声検査がfailの章を含む | `blocked` |
| chapter重複(順序衝突) | `fail` |
| metadata欠落を自動補完しようとする | Error(基本原則違反) |
| 対象プレイヤーで実再生できないのに互換性を合格扱いしようとする | Error(5.4節の`tested`必須化で防止) |

## 12. バリデーション

- 全chapterの`chapter_id`が一意である。
- `validation.all_chapters_passed`が`true`のときのみ生成を許可する。
- `compatibility.tested_players`が空の場合、`compatibility.status`を`provisional`のまま
  `approved`にしない。

## 13. テスト観点

- 章位置へ正しく移動できる(chapter atomのタイムスタンプ検証)。
- 対象プレイヤーで再生できる(実機確認、本タスクでは未実施)。
- メタデータの出典が明確である(AI補完がないことを検証)。
- 未承認章を含む全文版を生成できない。
- 一部章変更時に、影響する範囲だけ再生成される
  (`audiobook-creation-pipeline.md` 16.2節「MP3タグのみ変更→対象MP3のみ」の考え方を準用)。

## 14. 移行・互換性

- 章MP3の生成自体は`14-audio-packaging.md`(承認済み)を変更しない。
- M4Bは追加成果物であり、既存の章MP3出力フローに影響しない。

## 15. 未決定事項

- 実際の対象プレイヤーでの互換性確認結果
- 音声検査閾値がprovisionalのままM4Bを生成してよい運用上の許容範囲
  (現状は「provisionalのまま生成可能だが、manifestに明記」という設計)
- narrator表記の法的な取り扱い(クレジット表記との整合、タスク08と連動する可能性)
- 全文版MP3(M4B以外)を実際に必要とするユースケースの有無

## 16. 完了条件

- [x] 章位置へ正しく移動できる設計になっている。
- [ ] 対象プレイヤーで再生できる(実機確認は未実施、`provisional`のまま)。
- [x] メタデータの出典が明確である。
- [x] 未承認章を含む全文版を生成できない。
- [x] 出力ドラフトが存在し、`status: provisional`である。
- [x] 未実測・未確認事項が明記されている(5.4, 15節)。
- [x] 実装コードを変更していない。

## 17. 停止・保留条件(該当状況)

- 音声検査閾値が未確定(タスク04がprovisional)であり、「最終合格」の断定はできない。
  本書はこれを`validation_threshold_status: provisional`として明記することで対応する。
- 対象プレイヤーで実再生できていないため、互換性を合格扱いにしていない
  (`compatibility.status: provisional`のまま)。
