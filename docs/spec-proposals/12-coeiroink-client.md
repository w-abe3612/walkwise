---
status: draft
version: "0.1"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_193603(1).txt"
---

# COEIROINKクライアント固有仕様

## 1. 目的

現在未実装のCOEIROINKクライアントを、TTS共通インターフェースへ適合させる。

## 2. 現行実装

`script/tts_clients/coeiroink/client.py`は、`CoeiroinkNotImplementedError`を送出する予約実装だけを持つ。docker-composeにはCOEIROINKサービスがない。

したがって、実装前に利用するCOEIROINKのバージョン、API仕様、配布・利用条件、Dockerまたはホスト起動方法を確定する必要がある。

## 3. 初期対象

- りりんちゃんの利用を優先対象とする。
- 他話者は話者一覧取得により追加可能とする。
- 固定のspeaker UUIDやstyle IDをコードへ直書きしない。

## 4. 接続先

```text
CLIまたは依存注入
> COEIROINK_URL
> ローカル既定URL
```

既定URLは採用するCOEIROINKバージョンの公式APIに基づき、実装時に確定する。本提案書では未確定値を断定しない。

## 5. APIマッピング

共通リクエストを次へ変換する。

- text
- speaker UUIDまたは話者ID
- style ID
- speed
- pitch
- intonationまたは感情表現
- volume

VOICEVOXと同名でも意味・範囲が異なる値は、単純コピーせず変換関数を設ける。

## 6. capabilities

COEIROINK実装は、利用バージョンで対応している機能を明示する。

```yaml
supports:
  speed_scale: true
  pitch_scale: conditional
  intonation_scale: conditional
  volume_scale: true
  speaker_listing: true
  style_selection: true
```

未対応値は黙って無視せずwarningを返す。

## 7. 話者情報

```yaml
speaker_id: "speaker-uuid-or-id"
style_id: "style-id"
display_name: りりんちゃん
engine: coeiroink
```

speakerとstyleを分けて保存する。

## 8. 分割

エンジンの入力制限を実測・公式仕様で確認し、capabilitiesへ設定する。VOICEVOXの300文字をそのまま流用しない。

## 9. エラー変換

COEIROINK固有エラーを共通TTSエラーへ変換する。少なくとも次を実装する。

- 接続不能
- 話者不在
- スタイル不在
- 不正パラメータ
- 合成失敗
- 非音声応答
- timeout

## 10. Docker・起動方法

次のいずれかを仕様確定する。

1. docker-composeサービスとして起動する。
2. ホストOSで起動し、コンテナからhostへ接続する。
3. 開発時だけ手動起動し、統合テストを別profileにする。

推奨は、再現可能な公式または信頼できるコンテナイメージがある場合のみdocker-composeへ追加する。非公式イメージを無断採用しない。

## 11. テスト

### 単体テスト

- 共通パラメータ変換
- 話者・style選択
- エラー変換
- capabilities

### mock統合テスト

- 話者一覧
- 合成成功
- style不在
- 非音声応答

### 手動テスト

- りりんちゃんの5分試聴
- 速度・抑揚差
- 長文分割
- VOICEVOXとの音量差

## 12. 完了条件

- 共通TTSインターフェースから音声生成できる。
- りりんちゃんのvoice profileを保存・再利用できる。
- 上位処理にCOEIROINK固有分岐がない。
- 利用エンジンバージョンと起動方法がdocsに固定されている。
