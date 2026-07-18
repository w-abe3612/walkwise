---
spec_id: 09-voice-profile-schema
title: "音声プロファイルのスキーマ"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---


# 音声プロファイルのスキーマ

> **承認範囲**  
> 本書では音声プロファイルの構造、継承、上書き、互換変換を確定する。
> 話者ごとの最終速度、音量、無音時間、採用スタイルは
> `../spec-proposals/task/3_voice-profile-default-values.md`で試聴後に確定する。

## 1. 目的

TTSエンジン、話者、スタイル、速度、音高、抑揚、音量、無音、
出力形式を再利用可能な設定として定義する。

## 2. ファイル

```text
project/voices/<voice_profile_id>.yaml
```

## 3. 推奨スキーマ

```yaml
schema_version: "1.0"
voice_profile_id: sample-voicevox-profile
character_id: null
display_name: サンプルVOICEVOX音声
content_revision: 1
status: provisional
engine: voicevox

speaker:
  id: "<resolved-style-id>"
  style_id: "<resolved-style-id-or-null>"

engine_identity:
  speaker_uuid: "<resolved-speaker-uuid>"
  engine_version: "<tested-version>"
  engine_display_name: "<engine-display-name>"

parameters:
  speed_scale: 1.05
  pitch_scale: 0.0
  intonation_scale: 1.0
  volume_scale: 1.0

pause:
  sentence_ms: 250
  paragraph_ms: 600
  section_ms: 1000
  chapter_ms: 1500

output:
  sample_rate_hz: 24000
  channels: 1
  intermediate_format: wav

engine_options: {}
```

`character_id`は、音声と原稿キャラクターを明示的に関連付ける場合だけ指定する。
中立原稿で試聴する場合は`null`でよい。

## 4. status

```text
provisional
approved
approved_for_limited_use
on_hold
rejected
deprecated
```

正式成果物に使用できるのは原則として次である。

- `approved`
- 使用条件を満たす`approved_for_limited_use`

サンプル検証では`provisional`を許可するが、
deliverablesへ出力してはならない。

## 5. 現行設定との対応

現行`book.json`:

```json
{
  "tts": {
    "engine": "voicevox",
    "speaker": 3,
    "speedScale": 1.6,
    "pitchScale": 0.0,
    "intonationScale": 1.0,
    "volumeScale": 1.0
  }
}
```

変換:

```text
speaker            -> speaker.id
speedScale          -> parameters.speed_scale
pitchScale          -> parameters.pitch_scale
intonationScale     -> parameters.intonation_scale
volumeScale         -> parameters.volume_scale
```

既存値1.6は互換移行時に保持する。
新規プロファイルは1.0〜1.15を中心に試聴して決める。
旧値1.6を新規候補の暗黙既定値にしない。

## 6. 共通項目と固有項目

共通パラメータ:

- speed
- pitch
- intonation
- volume
- pause
- output

エンジン固有値:

```yaml
engine_options:
  voicevox:
    enable_interrogative_upspeak: true
```

COEIROINK固有のスタイル、感情、モードなども`engine_options`へ置く。

## 7. 既定値

再現性のため、エンジン暗黙値に依存しない。
使用したengine versionをmanifestへ記録する。

## 8. 上書き優先順位

```text
CLI明示値
> セグメント単位上書き
> 章単位上書き
> voice profile
> book.json旧tts
> ツール既定値
```

最終解決値をmanifestへ記録する。

## 9. speaker ID

共通スキーマでは文字列で保持する。

- VOICEVOX呼出時: 整数style IDへ変換
- COEIROINK呼出時: UUIDまたは採用APIのIDを使用

内部`character_id`へ外部speaker IDを流用してはならない。

## 10. 正式候補

### VOICEVOX

- 春日部つむぎ
- 櫻歌ミコ
- 中国うさぎ
- 猫使ビィ
- 東北きりたん

### COEIROINK

- リリンちゃん
- つくよみちゃん
- ディアちゃん

候補一覧は最終パラメータを意味しない。
最終値はタスク3で確定する。

## 11. バリデーション

### Error

- profile ID欠落
- 未登録engine
- speaker ID欠落
- speedまたはvolumeが0以下
- pauseが負
- sample rateが0以下
- approvedなのにengine version欠落
- approvedなのに試聴承認欠落

### Warning

- statusがprovisional
- unsupported parameter
- character IDと音声候補の対応が未確認
- engine暗黙値に依存
- 互換値1.6を新規profileへ使用

## 12. 承認との関係

voice profile revisionまたはengine versionが変わった場合、
試聴承認を無効化する。

原稿承認は原則維持する。
character profileを変更しない限り、原稿textを変更しない。

## 13. テスト観点

- 旧book.jsonから変換できる。
- CLI上書き優先順位が正しい。
- VOICEVOXとCOEIROINKのID形式を保持できる。
- 未対応パラメータが共通処理を壊さない。
- provisional profileをdeliverablesへ使用できない。
- voice変更で原稿が変化しない。
- engine version変更で試聴承認が無効になる。

## 14. 完了条件

同じプロファイル、同じエンジンバージョン、同じ入力から、
同じ合成条件を再現できること。
