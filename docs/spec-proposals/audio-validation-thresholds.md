---
spec_id: audio-validation-thresholds
title: "音声検査の最終閾値"
status: provisional
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  note: "旧仕様策定タスク(完了・削除済み)により生成。Git履歴を参照。"
depends_on:
  - task/3_voice-profile-default-values.md
spec_refs:
  - ../specifications/13-audio-validation.md
  - ../specifications/09-voice-profile-schema.md
  - ../specifications/audiobook-creation-pipeline.md
  - ../specifications/18-ai-model-routing-and-cost-control.md
  - ../specifications/19-application-scope-and-mvp.md
---

# 音声検査の最終閾値(ドラフト)

> **状態に関する注記**
> 本書は`docs/specifications/13-audio-validation.md`が仮値として保持しているLUFS、無音、
> 文字数毎秒などの数値を「最終確定」させるための下書きである。
> 依存タスク`3_voice-profile-default-values.md`(話者別初期値の試聴確定)が未完了であり、
> かつ本書自体も実測(MVP対象のVOICEVOX話者2名以上・正常音声/異常音声fixtureでの測定)を
> 行っていないため、数値は**すべてprovisionalのまま**とする。`status: approved`へは
> 進めない。COEIROINKはpost-MVPのため、MVPの閾値確定条件には含めない
> (`19-application-scope-and-mvp.md`)。

## 1. 目的

`13-audio-validation.md`が定義する検査段階・判定区分・検査項目に対して、
具体的な数値閾値(LUFS目標値、許容差、ピーク上限、無音秒数、文字数毎秒範囲など)を
実測に基づいて確定するための手順とprovisional値を定義する。

## 2. 対象範囲

- 共通閾値と話者別例外閾値の関係
- 破損・0秒・形式不一致の扱い
- LUFS、ピーク、無音、文字数毎秒のprovisional初期値
- 発音・聞き疲れなど主観品質の自動fail可否
- 正常/異常音声fixtureの要件
- 測定コマンドとレポートschema
- 閾値の根拠欄とsample数の必須化

## 3. 対象外

- 話者別の最終音声プロファイル値そのもの(タスク3で確定)
- 発音・声質・キャラクター適合の最終合否判定(常に人間が行う)
- ASRによる自動照合(タスク15)
- VOICEVOX/COEIROINK以外のエンジンの閾値

## 4. 現行実装

- `13-audio-validation.md`が判定区分(`pass`/`warning`/`fail`/`review_required`)と
  検査段階(セグメントWAV直後、章MP3結合後、deliverables出力前)を承認済みで定義している。
- 同仕様の「仮設定例」(`target_lufs: -18`、`peak.maximum_dbfs: -0.5`、
  `characters_per_second: 2.0〜12.0`、`maximum_silence_seconds: 3.0`など)は
  明示的に「上記数値は仮値である」と記載されており、未実測である。
- 実測対象話者候補(VOICEVOX 5名、COEIROINK 3名)は`13-audio-validation.md`で列挙済みだが、
  実際の音声ファイルは本リポジトリに存在しない(`dumps/`配下はテキストダンプのみ)。
  MVPの閾値承認にはVOICEVOX話者2名以上の実測で足り、COEIROINKの実測は
  post-MVP対応時まで不要である(`19-application-scope-and-mvp.md`)。

## 5. 推奨仕様

### 5.1 共通閾値を基本とする

質問1(共通閾値と話者別閾値のどちらを使うか)への回答:
**共通閾値を基本とし、実測根拠がある場合だけ話者別例外を設定する。**

```yaml
audio_validation_thresholds:
  schema_version: "1.0"
  scope: common
  status: provisional
  evidence:
    measured_speakers: []          # 実測前は空
    minimum_required_speakers: 2  # MVP: VOICEVOXから2名以上
    sample_count: 0
```

話者別例外は次の形で共通設定を上書きする。

```yaml
audio_validation_thresholds:
  schema_version: "1.0"
  scope: speaker_override
  voice_profile_id: sample-voicevox-profile
  status: provisional
  evidence:
    sample_count: 0
    rationale_required: true
  overrides:
    loudness:
      target_lufs: null
```

`rationale_required: true`のexample override は、根拠(sample数、測定条件、測定日)が
記入されるまで有効化しない。

### 5.2 破損・0秒・形式不一致

質問2への回答: **常に`fail`とする。**

対象:

- ファイルが存在しない、または0 byte
- WAVがRIFF/WAVEとして読めない
- MP3がffprobe等で読めない
- 期待するchannels/sample rateと一致しない
- 結合対象間で形式が不一致

これらは`13-audio-validation.md`の`Error`区分と一致させ、warningへ格下げしない。

### 5.3 数値のprovisional初期値

質問3への回答: **`13-audio-validation.md`の仮値をそのまま引き継ぎ、最終確定しない。**

```yaml
audio_validation:
  schema_version: "1.0"
  status: provisional
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
  evidence:
    measured: false
    measured_speakers: []
    sample_count: 0
    measurement_tool: null
    measured_at: null
```

これらの数値は`13-audio-validation.md`からの転記であり、本ドラフト独自の実測値ではない。

### 5.4 発音・疲れやすさの自動fail

質問4への回答: **自動failにしない。`review_required`とする。**

該当項目(`13-audio-validation.md`の`Review required`区分と同一):

- 発音不良
- 意味が聞き取れない
- キャラクター表現が不適切
- 不自然な抑揚
- 長時間聴取での聞き疲れ
- clipping境界付近

### 5.5 実測がない値の最終化可否

最終値にしない。MVPの閾値承認は、VOICEVOX話者の実測後にのみ`status: approved`へ
進める。COEIROINKはpost-MVPの追加TTS engine(`19-application-scope-and-mvp.md`)
であるため、MVPの閾値確定をCOEIROINK実測で停止させない。

MVPでの昇格条件:

```text
measured == true
かつ measured_speakers の人数 >= 2 (VOICEVOXから2名以上)
かつ 誤検出(false fail)と見逃し(false pass)を人間が比較確認済み
```

将来COEIROINK対応時は、COEIROINK向け閾値または共通閾値の適用可否を
別途実測し、そのタイミングで閾値仕様を追加改訂する。

## 6. 入力

- 正常音声fixtureセット(各話者・速度差・専門用語/英字/数字を含む)
- 意図的異常音声fixtureセット(0秒、破損WAV、極端な無音、clipping、極端な音量)
- `13-audio-validation.md`の仮設定値
- `09-voice-profile-schema.md`のvoice profile一覧(候補8名)
- ffprobe等の測定ツール出力(存在する場合のみ)

## 7. 出力

- 本ドラフト(`status: provisional`)
- provisional threshold YAML(5.3節)
- 実測計画(8節)
- 測定結果を記録するレポートschema(9節)

## 8. 実測計画(未実施)

本タスクの実行時点では、音声ファイル・TTSエンジンへのアクセスがなく、
音声生成や試聴は行っていない。次を実測前の計画としてのみ記録する。

1. fixture要件を確定する。
   - 正常: MVP対象のVOICEVOXから最低2話者、通常文/専門用語文/数字文/英字文をそれぞれ1件以上
   - 異常: 0秒WAV、ヘッダ破損WAV、90%以上無音、+3dBFS相当のclipping、sample rate不一致
2. `ffprobe`(またはPython `soundfile`/`pydub`等、インストールはしない)でLUFS、
   peak、duration、無音区間を測定するコマンド仕様を定義する(10節)。
3. 誤検出率(正常音声をfailにした割合)と見逃し率(異常音声をpassにした割合)を比較する。
4. warning/review_required/failの境界値を調整する。
5. 結果を`docs/specifications/audio-validation-thresholds.md`への昇格案としてまとめ、
   人間レビューへ提出する。

夜間実行では、音声ファイルの生成・再生・試聴を一切行っていない。

## 9. レポートschema(最小例)

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
  "measurements": {
    "lufs": -19.4,
    "peak_dbfs": -1.2,
    "silence_ratio": 0.05,
    "characters_per_second": 5.1
  },
  "issues": [
    {
      "code": "long_silence",
      "severity": "warning",
      "value": 3.4,
      "threshold": 3.0,
      "threshold_status": "provisional"
    }
  ]
}
```

`threshold_status`は常に`provisional`または`approved`のいずれかを記録し、
provisional閾値による判定結果であることを追跡可能にする。

## 10. 測定コマンド仕様(例、未実行)

```text
ffprobe -v error -show_entries format=duration -of json <input.wav>
```

音量・LUFS測定は`ffmpeg`の`loudnorm`フィルタ(dry-run/measure mode)を候補とするが、
本ドラフト作成時点ではインストール・実行していない。採用ツールは実測タスクで確定する。

## 11. 正常系

1. fixture一式を用意する(実測タスクで実施)。
2. 各fixtureを測定し、`measurements`を記録する。
3. provisional閾値と比較し、`pass`/`warning`/`fail`/`review_required`を判定する。
4. 正常音声が誤ってfailにならないことを確認する。
5. 異常音声が確実にfailまたはreview_requiredになることを確認する。

## 12. 異常系

| ケース | 判定 |
|---|---|
| 0秒WAV | `fail`(常時) |
| 破損WAV(RIFFヘッダ不正) | `fail`(常時) |
| sample rate不一致での結合 | `fail`(常時) |
| 90%以上無音 | `fail`(常時) |
| 発音不良の疑い | `review_required` |
| 文字数毎秒が範囲外 | `warning`(単独ではfailにしない) |
| 話者別override未確認 | `evidence`不足として`review_required` |

## 13. バリデーション

- `status: provisional`の閾値をdeliverables検査へ使用する場合、レポートへ
  `threshold_status: provisional`を必ず記録する。
- `evidence.measured == false`の閾値セットを`status: approved`として保存できない。
- 話者別overrideは`rationale_required`を満たさない限り無効とする。

## 14. テスト観点

- provisional閾値でも判定ロジック自体は正しく動作する(fixtureなしでも単体テスト可能)。
- 破損・0秒・形式不一致が常にfailになる。
- 発音関連項目がfailではなくreview_requiredになる。
- `evidence.sample_count`が2未満の場合、`status`を`approved`へ変更する処理が拒否される。
- 話者別overrideに根拠が無い場合、共通閾値にフォールバックする。

## 15. 移行・互換性

- `13-audio-validation.md`の仮設定例と数値を完全一致させ、無断で変更しない。
- 将来、実測後に`docs/specifications/audio-validation-thresholds.md`として承認する際は、
  `13-audio-validation.md`側の「承認範囲」の記述も合わせて更新する(別タスク)。

## 16. 未決定事項

- 各項目の最終数値(LUFS目標、許容差、ピーク上限、無音秒数、文字数毎秒範囲)
- 話者別exceptionが実際に必要になる話者の有無
- 採用する測定ツール(ffmpeg loudnormか、他の非商用ツールか)
- 文字数毎秒の言語依存性(日本語以外の混在テキストの扱い)
- warningからfailへ格上げする累積条件の有無

## 17. 完了条件(本ドラフトの完了条件)

- [x] 出力ドラフトが存在する。
- [x] フロントマターが`status: provisional`である。
- [x] 未実測・未確認事項が明記されている(8, 16節)。
- [x] 人間承認済みと偽っていない。
- [x] 主要な正常例・異常例・テスト観点がある(11, 12, 14節)。
- [x] 参照した仕様と根拠が記録されている(spec_refs、4節)。
- [x] 実装コードを変更していない。

## 18. 停止・保留条件(該当状況)

次はいずれも本タスク実行時点で未解消であり、`docs/specifications/`への昇格は保留する。

- 代表音声ファイルがリポジトリ内に存在しない。
- MVP対象のVOICEVOX話者2名以上の実測が行われていない。
- 人間による聴感評価が行われていない。
