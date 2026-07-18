---
spec_id: 10-tts-client-common-interface
title: "TTSクライアント共通インターフェース"
status: approved
version: "1.0"
approved_at: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_220811.txt"
---

# TTSクライアント共通インターフェース

## 1. 目的

上位処理がVOICEVOXとCOEIROINKのAPI差異を意識せず、同じリクエスト・レスポンス・エラー形式で利用できるようにする。

## 2. 現行実装

- `voicevox/client.py`は関数群で実装され、接続確認、分割、audio query、設定適用、合成、WAV結合を行う。
- `coeiroink/client.py`は未実装例外だけを持つ。
- `batch_tts_sections.py`はVOICEVOX関数を直接importし、engineがVOICEVOX以外なら停止する。

## 3. 推奨インターフェース

```python
class TTSClient(Protocol):
    engine_name: str

    def health_check(self) -> HealthCheckResult: ...
    def get_capabilities(self) -> TTSCapabilities: ...
    def list_speakers(self) -> list[SpeakerInfo]: ...
    def synthesize(self, request: SynthesisRequest) -> SynthesisResult: ...
```

実装形式はProtocol、ABC、抽象基底クラスのいずれでもよいが、上位が具体クライアントを直接importしないことをMUSTとする。

## 4. リクエスト

```yaml
request_id: synth-ch01-seg001-r0003
engine: voicevox
text: マイエスキューエルを起動します。
speaker_id: "3"
parameters:
  speed_scale: 1.05
  pitch_scale: 0.0
  intonation_scale: 1.0
  volume_scale: 1.0
output:
  path: audio/cache/wav/segments/ch01-seg001.wav
  format: wav
metadata:
  project_id: database-introduction
  chapter_id: ch01
  segment_id: ch01-seg001
```

## 5. レスポンス

```yaml
status: success
engine: voicevox
engine_version: "0.25.0"
speaker_id: "3"
output_path: audio/cache/wav/segments/ch01-seg001.wav
duration_seconds: 4.2
sample_rate_hz: 24000
channels: 1
parts:
  - part_id: ch01-seg001-part001
    character_count: 20
warnings: []
```

## 6. capabilities

```yaml
supports:
  speed_scale: true
  pitch_scale: true
  intonation_scale: true
  volume_scale: true
  speaker_listing: true
  accent_phrase_editing: false
  streaming: false
limits:
  recommended_max_text_length: 300
```

上位処理は、クライアントの対応能力を確認してからパラメータを渡す。

## 7. 共通エラー

- `connection_error`
- `health_check_failed`
- `speaker_not_found`
- `unsupported_parameter`
- `invalid_parameter`
- `text_empty`
- `text_too_long`
- `query_failed`
- `synthesis_failed`
- `invalid_audio_response`
- `audio_format_mismatch`
- `timeout`
- `output_write_failed`

各エンジン固有例外は、共通`TTSClientError`へ変換し、`code`と`engine_detail`を保持する。

## 8. 分割責務

文章の意味単位分割はセグメント作成工程が担当する。エンジン制限のための内部part分割はTTS共通層が担当してよい。

分割関数は外部APIに依存しない純粋関数として実装する。

## 9. クライアント選択

```python
client = registry.get(profile.engine)
```

登録されていないengineは`unsupported_engine`とする。

## 10. リトライ

- 接続エラー、timeout、5xxは限定回数の再試行対象。
- 4xx、speaker not found、invalid parameterは自動再試行しない。
- 初期値は最大3回、指数バックオフとする。
- 同じrequest IDの重複出力を避ける。

## 11. ファイル出力

合成結果のbytesを直接ファイルへ保存してもよいが、失敗時に半端なファイルを残さないよう一時ファイルへ書き、検査後にatomic renameする。

## 12. 現行コードの移行

1. 現行VOICEVOX関数を壊さず、`VoicevoxClient`クラスからラップする。
2. `batch_tts_sections.py`にregistryを導入する。
3. COEIROINKを共通インターフェースで実装する。
4. 既存関数はdeprecated warning後に段階廃止する。

## 13. テスト観点

- 2クライアントを同じmock requestで呼べる。
- 固有エラーが共通エラーへ変換される。
- unsupported parameterがcapabilityに従って処理される。
- 分割・再結合の順序が維持される。
- 書込失敗時に壊れた最終ファイルが残らない。

## 14. 完了条件

`batch_tts_sections.py`相当の上位処理からVOICEVOX固有importを除去し、engine名の切替だけで両エンジンを利用できること。
