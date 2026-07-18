---
spec_id: 11-voicevox-client
title: "VOICEVOXクライアント固有仕様"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---


# VOICEVOXクライアント固有仕様

## 1. 目的

TTS共通インターフェースをVOICEVOX Engine APIへ変換する。

## 2. 現行実装

現行クライアントは次を実装済みである。

- `VOICEVOX_URL`または`http://localhost:50021`
- `/speakers`による接続確認
- `/audio_query`
- `speedScale`
- `pitchScale`
- `intonationScale`
- `volumeScale`
- `/synthesis`
- 既定最大300文字の分割
- WAV形式一致確認と結合
- 接続10秒、読取300秒のtimeout

基本処理は再利用する。

## 3. 正式な試聴候補

VOICEVOX側の候補:

- 春日部つむぎ
- 櫻歌ミコ
- 中国うさぎ
- 猫使ビィ
- 東北きりたん

候補名をクライアントへハードコードしてはならない。

`/speakers`からspeaker UUID、表示名、style IDを取得し、
voice profileへ保存する。

## 4. APIマッピング

| 共通項目 | VOICEVOX |
|---|---|
| `speaker_id` | `speaker` query parameterへ整数変換 |
| `text` | `/audio_query`の`text` |
| `speed_scale` | `speedScale` |
| `pitch_scale` | `pitchScale` |
| `intonation_scale` | `intonationScale` |
| `volume_scale` | `volumeScale` |

## 5. 接続先

```text
CLIまたは依存注入
> VOICEVOX_URL
> http://localhost:50021
```

Docker内は環境変数で`http://voicevox:50021`を設定する。

## 6. health check

`GET /speakers`を使用する。

成功条件:

- HTTP成功
- JSON配列
- 1件以上のspeaker
- 各speakerに必要な識別情報がある

## 7. 話者一覧

`/speakers`応答を共通`SpeakerInfo`へ変換する。

保持:

- speaker UUID
- speaker表示名
- style ID
- style表示名
- engine name
- engine version

表示名だけで話者を再現しない。

## 8. 分割

- 最大文字数をprofileまたはcapabilitiesから指定可能にする。
- 句読点と段落境界を優先する。
- 固定文字数分割時はwarningを出す。
- 原稿segment IDと内部part IDをmanifestへ記録する。
- 候補話者によって原稿segmentを変更しない。

## 9. 音声合成

1. textを検査する。
2. speaker/style IDを解決する。
3. `/audio_query`を呼ぶ。
4. 共通パラメータを適用する。
5. engine optionsを適用する。
6. `/synthesis`を呼ぶ。
7. RIFFヘッダとWAV読込を検査する。
8. partを順序どおり結合する。
9. 一時ファイルから最終パスへ移動する。
10. engine versionと解決済み設定をmanifestへ記録する。

## 10. WAV結合

次が一致しない場合は`audio_format_mismatch`とする。

- channels
- sample width
- sample rate
- compression type

暗黙の再サンプリングは行わない。

## 11. エラー変換

| VOICEVOX側 | 共通エラー |
|---|---|
| connection error | `connection_error` |
| timeout | `timeout` |
| speaker/style不在 | `speaker_not_found` |
| `/audio_query`失敗 | `query_failed` |
| `/synthesis`失敗 | `synthesis_failed` |
| 非音声応答 | `invalid_audio_response` |
| WAV不一致 | `audio_format_mismatch` |
| 書込失敗 | `output_write_failed` |

## 12. Docker

VOICEVOX image versionを固定し、
manifestへengine versionを記録する。

更新時は共通試聴セットを再生成して回帰確認する。

## 13. テスト

### 単体テスト

- 文章分割
- URL正規化
- speaker一覧変換
- style ID解決
- audio query設定適用
- WAV結合
- エラー変換

### mock統合テスト

- `/speakers`
- `/audio_query`
- `/synthesis`
- 2 part結合
- speaker不在
- style不在
- 非音声応答

### 手動試聴

対象:

- 春日部つむぎ
- 櫻歌ミコ
- 中国うさぎ
- 猫使ビィ
- 東北きりたん

同じ共通試聴原稿で、専門用語、数字、英字、SQL、速度、抑揚、
音量、疲れにくさを確認する。

## 14. バリデーション

- 指定style IDがspeaker一覧に存在する。
- profileのengineが`voicevox`である。
- speaker IDを整数へ変換できる。
- engine versionが記録される。
- 合成結果をWAVとして読める。
- 候補名をコード分岐に使用していない。

## 15. 完了条件

現行VOICEVOX出力を維持しつつ、
共通TTSインターフェースと音声manifestを利用でき、
正式候補5名を同じ処理経路で試聴できること。
