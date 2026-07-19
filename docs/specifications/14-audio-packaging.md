---
spec_id: 14-audio-packaging
title: "MP3結合と出力ファイルの仕様"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_220811.txt"
---

# MP3結合と出力ファイルの仕様

> **承認範囲**  
> 章単位MP3、音声マニフェスト、部分再生成、atomic outputを確定する。M4Bの詳細は、`m4b-output.md`で別途規定する(全文MP3は本製品では作成しない、`19-application-scope-and-mvp.md`参照)。


## 1. 目的

検査済みセグメント音声を順序どおり結合し、章単位MP3、deliverablesを再現可能に生成する。

## 2. 現行実装

- `batch_tts_sections.py`はunitごとのWAVを作り、MP3へ変換する。
- `wav_to_mp3.py`はffmpeg、libmp3lame、`-q:a 2`を使用する。
- 本内の`audio/exports/`と`deliverables/<title>/audio/`へコピーする。
- 出力名はunit IDを中心にしている。

## 3. 出力単位

### MUST

- セグメントWAV
- 章単位MP3
- 音声manifest

### SHOULD

- 全章MP3一覧
- M4B(`m4b-output.md`、post-MVP)
- deliverablesコピー

M4Bは初期実装の必須にはしない。全文MP3は本製品の成果物として作成しない
(`19-application-scope-and-mvp.md`)。

## 4. ディレクトリ

```text
audio/
├── cache/wav/segments/<chapter_id>/
├── chapters/
│   └── 01_ch01.mp3
├── exports/
│   ├── chapters/
│   ├── complete/        # M4B(post-MVP、m4b-output.md)。全文MP3は置かない
│   └── manifest.json
├── preview/
├── manifests/
└── reports/
```

現行`audio/cache/wav/<unit>.wav`と`audio/exports/<unit>.mp3`は互換出力として当面維持してよい。

## 5. 結合順

ファイル名の文字列順ではなく、manifestの`order`を使用する。

```yaml
segments:
  - segment_id: ch01-seg001
    order: 1
    wav_path: audio/cache/wav/segments/ch01/ch01-seg001.wav
```

order重複、欠番はerrorまたはwarningとする。欠番を許容する場合でも順序は一意でなければならない。

## 6. 無音挿入

原稿segmentの`pauses.after_ms`を優先し、未指定時はvoice profileの既定値を使う。

```text
セグメント後無音
> segment override
> segment type default
> voice profile default
```

VOICEVOXが生成する内部無音と二重にならないよう、結合前の実測を行う。

## 7. MP3設定

初期推奨:

```yaml
mp3:
  codec: libmp3lame
  mode: vbr
  quality: 2
  channels: 1
  sample_rate_hz: 44100
```

現行の`-q:a 2`を維持する。WAV sample rateからMP3用sample rateへ変換する場合はffmpeg commandとmanifestへ記録する。

## 8. メタデータ

章MP3:

- title
- album
- artistまたはnarrator
- track number
- chapter ID
- project ID
- generated revision

完成版:

- title
- album
- author（権利情報が確定している場合）
- narrator
- cover image（任意）
- year

不明な著者情報をAIで推測して埋めない。

## 9. ファイル名

```text
01_ch01_データベースとは何か.mp3
02_ch02_SQLの基本.mp3
```

内部処理はIDを使い、表示タイトルはsanitizeして付加する。Windows禁止文字の除去には現行`sanitize_filename`を再利用できる。

## 10. manifest

```json
{
  "schema_version": "1.0",
  "project_id": "database-introduction",
  "content_revision": 3,
  "voice_profile_revision": 2,
  "outputs": [
    {
      "audio_id": "ch01-r0003",
      "type": "chapter_mp3",
      "chapter_id": "ch01",
      "path": "audio/chapters/01_ch01.mp3",
      "duration_seconds": 620.4,
      "source_segments": ["ch01-seg001", "ch01-seg002"],
      "content_hash": "..."
    }
  ]
}
```

## 11. 部分再生成

1セグメント変更時:

1. 対象セグメントWAVを再生成する。
2. 対象章を再結合する。
3. 完成版がある場合だけ完成版を再結合する。
4. 変更のない章MP3は再生成しない。

## 12. atomic output

ffmpeg出力は一時パスへ生成し、検査合格後に最終パスへ置換する。失敗時に既存の正常ファイルを削除しない。

## 13. deliverables

正式承認済み成果物だけを`deliverables/`へコピーする。未承認・強制実行・検査failの成果物はコピーしない。

## 14. テスト観点

- manifest orderで結合される。
- 出力名の禁止文字が除去される。
- 1セグメント変更時に対象章だけ再結合される。
- ffmpeg失敗時に既存完成ファイルが保持される。
- 未承認音声がdeliverablesへ入らない。

## 15. 完了条件

同じ承認済み原稿、プロファイル、エンジンバージョンから、同じ章順とメタデータ構成の成果物を再生成できること。
