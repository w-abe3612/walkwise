---
spec_id: 13-audio-validation
title: "音声検査の判定基準"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---


# 音声検査の判定基準

> **承認範囲**  
> 本書では検査段階、判定区分、検査項目、レポート形式を確定する。
> LUFS、無音時間、文字数毎秒などの最終数値は
> `../spec-proposals/audio-validation-thresholds.md`で実測後に確定する。

## 1. 目的

破損、無音、異常な長さ、音量不足、clipping、結合順誤りなどを検出し、
不正な音声が正式成果物へ入ることを防ぐ。

## 2. 検査段階

1. セグメントWAV生成直後
2. 章MP3結合後
3. deliverables出力前

## 3. 判定

```text
pass
warning
fail
review_required
```

- `pass`: 自動検査合格
- `warning`: 処理継続可能
- `fail`: 正式出力へ使用不可
- `review_required`: 人間確認まで保留

## 4. 初期必須検査

### ファイル

- 存在する。
- サイズが0ではない。
- 対応ライブラリで開ける。
- WAVはRIFF/WAVEとして読める。
- MP3はffprobe等で読める。

### 音声形式

- channelsが期待値と一致する。
- sample rateが期待値と一致する。
- 結合対象の形式が一致する。

### 長さ

- durationが極端に短い場合はfail。
- 原稿文字数に対して極端に短い・長い場合はwarningまたはreview_required。
- 最大許容時間を設定可能にする。

### 無音

- 先頭・末尾の過剰無音を検出する。
- 長い連続無音を検出する。
- 全体の大半が無音ならfail。

### 音量

- 実効音量不足はwarning。
- clippingはfailまたはreview_required。
- 章間・話者間の音量差はwarning。

## 5. 仮設定例

```yaml
audio_validation:
  minimum_duration_seconds: 0.5
  maximum_silence_seconds: 3.0
  minimum_non_silent_ratio: 0.2
  loudness:
    target_lufs: -18
    warning_tolerance_lu: 4
  peak:
    maximum_dbfs: -0.5
  text_duration_ratio:
    minimum_characters_per_second: 2.0
    maximum_characters_per_second: 12.0
```

上記数値は仮値である。

## 6. 実測対象

最終閾値は、正式候補からVOICEVOXとCOEIROINKの双方を含む代表音声で測定する。

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

全8名を必ず閾値調整へ使うかはタスク4で決める。

最低限:

- VOICEVOXから2名以上
- COEIROINKから1名以上
- 速度差を含む
- 専門用語・英字・数字を含む

## 7. 原稿対応検査

- manifestに全segment IDがある。
- 出力part数が期待値と一致する。
- 各segment durationがある。
- 同じ音声hashが不自然に連続していない。
- 空textの音声がない。
- segment orderが一意である。

完全なASR照合は初期対象外とする。

## 8. 再生成

自動再生成対象:

- API一時失敗
- 0 byte
- WAV破損
- 非音声応答
- 一時的書込失敗

人間レビュー対象:

- 発音
- 声質
- 意味対応
- キャラクター適合
- 聞き疲れ
- 不自然な抑揚

## 9. レポート

```json
{
  "schema_version": "1.0",
  "audio_id": "ch01-seg001-r0003",
  "status": "warning",
  "engine": "voicevox",
  "engine_version": "tested-version",
  "voice_profile_id": "sample-voicevox-profile",
  "duration_seconds": 4.2,
  "sample_rate_hz": 24000,
  "channels": 1,
  "issues": [
    {
      "code": "long_silence",
      "severity": "warning",
      "value": 3.4,
      "threshold": 3.0
    }
  ]
}
```

## 10. 話者差

原則として共通閾値を使用する。
話者別例外が必要な場合は実測根拠を記録し、
コードではなく設定ファイルへ置く。

## 11. 現行実装との関係

- クライアント内: API応答とWAVの最低限検査
- 共通音声検査: 長さ、無音、音量、順序
- packaging後: MP3とmanifest検査

## 12. Error

- 0 byte
- 読込不能
- WAV形式不正
- MP3形式不正
- sample rate不一致
- channel不一致
- manifest順序重複
- 必須segment欠落
- 全体の大半が無音
- 重大clipping

## 13. Warning

- 長い無音
- 音量不足
- 章間音量差
- 文字数毎秒が通常範囲外
- 話者別閾値を使用
- 仮voice profileを使用

## 14. Review required

- 発音不良
- 意味が聞き取れない
- キャラクター表現が不適切
- 不自然な抑揚
- 長時間聴取で疲れやすい
- clipping判定が境界付近
- ASR差分

## 15. テスト観点

- 0秒WAVをfailにする。
- 異なるsample rateの結合を拒否する。
- 長い無音を検出する。
- 正常音声を過剰にfailにしない。
- fail segmentを章MP3へ入れない。
- VOICEVOXとCOEIROINKを同じレポート形式で扱う。
- 話者別例外を設定から解決する。
- 仮閾値と承認済み閾値を区別する。

## 16. 完了条件

壊れた音声、空音声、形式不一致音声を正式成果物から除外し、
原因、使用profile、engine version、測定値を追跡できること。
