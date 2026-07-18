---
task_type: specification_decision
status: draft
order: 5
title: "COEIROINKのバージョン・API・起動方式"
depends_on:
  - 3_voice-profile-default-values.md
output_spec: "docs/specifications/12-coeiroink-client.md"
last_updated: "2026-07-18"
---

# 5. COEIROINKのバージョン・API・起動方式

## 1. 目的

COEIROINKの採用バージョン、公式API、接続先、話者・スタイル識別子、
起動方式、利用条件を確定し、次の候補話者を共通TTSインターフェースから
利用できるようにする。

- リリンちゃん
- つくよみちゃん
- ディアちゃん

---

## 2. 正式な初期対象

| character_id | 表示名 | engine |
|---|---|---|
| `lilin-chan` | リリンちゃん | `coeiroink` |
| `tsukuyomi-chan` | つくよみちゃん | `coeiroink` |
| `dia-chan` | ディアちゃん | `coeiroink` |

従来の「リリンちゃんを優先し、他話者は追加可能」という方針を変更し、
3名を同じ初期対象として扱う。

ただし、実装順は次を推奨する。

```text
1. COEIROINK共通接続
2. 話者・スタイル一覧取得
3. 3名の識別子解決
4. リリンちゃんで最初の疎通確認
5. つくよみちゃんで疎通確認
6. ディアちゃんで疎通確認
7. 共通試聴原稿による比較
```

---

## 3. 決定する事項

- 採用するCOEIROINKのバージョン
- 参照する公式API仕様
- Docker起動かホスト起動か
- 既定URLと環境変数
- health check
- 話者一覧取得方法
- speaker UUIDまたは識別子
- style ID
- 3名それぞれの利用可能スタイル
- 共通TTSパラメータとの変換
- 最大入力長
- timeout
- リトライ
- 出力音声形式
- 利用条件
- 必須クレジット
- 音声ライブラリ導入方法
- エンジン更新時の回帰試聴

---

## 4. 推奨する初期回答

- 最初は一つのCOEIROINK API世代へ固定する。
- 非公式コンテナを根拠なく採用しない。
- 再現可能な公式起動方法がない場合はホスト起動とする。
- 接続URLは依存注入、環境変数、既定値の順で解決する。
- speaker UUIDとstyle IDをコードへ直書きしない。
- 起動後の話者・スタイル一覧から3名を解決する。
- 表示名だけで一意に決めず、UUID等も保存する。
- VOICEVOXの最大300文字設定を流用しない。
- 未対応パラメータを黙って無視しない。
- 利用条件とクレジットを候補ごとに記録する。
- エンジンバージョンを音声manifestへ記録する。
- 3名を同一の共通試聴原稿で評価する。

---

## 5. 話者解決

プロファイルには、利用者向けの安定IDと
エンジンが返す識別子を分けて保存する。

```yaml
voice_profile_id: lilin-chan-coeiroink-default
character_id: lilin-chan
display_name: リリンちゃん
engine: coeiroink

speaker:
  id: "<resolved-speaker-id-or-uuid>"
  style_id: "<resolved-style-id>"

engine_identity:
  engine_version: "<tested-version>"
  speaker_uuid: "<resolved-uuid>"
  engine_display_name: "<returned-display-name>"
```

表示名変更や表記差があっても、
`character_id`と`voice_profile_id`を自動変更しない。

---

## 6. capabilities

採用バージョンで実際に確認した能力を返す。

```yaml
supports:
  speed_scale: true
  pitch_scale: conditional
  intonation_scale: conditional
  volume_scale: true
  speaker_listing: true
  style_selection: true
limits:
  recommended_max_text_length: null
```

`conditional`の項目は、
話者、スタイル、API世代によって差がある可能性を明示する。

未確認の値を`true`として固定しない。

---

## 7. 共通パラメータ変換

次を個別の変換関数で処理する。

- text
- speaker ID
- style ID
- speed
- pitch
- intonationまたは感情
- volume
- 無音
- 出力形式

VOICEVOXと同名のパラメータであっても、
数値の意味や範囲が同じであると仮定しない。

最終的に解決された値をmanifestへ記録する。

---

## 8. 起動方式

次のいずれかを一つ選ぶ。

1. docker-composeサービス
2. ホストOS上で起動しコンテナから接続
3. 開発時に手動起動し外部統合テストだけで利用

選定条件:

- 再現性
- 公式サポート
- Windows上での扱いやすさ
- Dockerからの接続
- 音声ライブラリの保存方法
- バージョン固定
- 更新作業
- ライセンスと配布条件

起動方式を決めるまでは、
`script/tts_clients/coeiroink/client.py`を正式実装へ進めない。

---

## 9. エラー変換

最低限、次を共通TTSエラーへ変換する。

- 接続不能
- health check失敗
- 話者一覧取得失敗
- 話者不在
- スタイル不在
- 音声ライブラリ未導入
- 不正パラメータ
- 未対応パラメータ
- text空
- text長超過
- 合成失敗
- 非音声応答
- timeout
- 出力書き込み失敗

一人の候補が利用不能でも、
他のエンジンや候補まで一律に停止しない。

---

## 10. テスト

### 10.1 単体テスト

- URL解決
- 話者情報変換
- style選択
- パラメータ変換
- capabilities
- エラー変換
- 3名の安定IDとエンジンIDの分離

### 10.2 mock統合テスト

- health check
- 話者一覧
- 3名の識別子解決
- 合成成功
- style不在
- 音声ライブラリ未導入
- 非音声応答
- timeout

### 10.3 実サービス統合テスト

各候補について短い固定文を合成する。

- リリンちゃん
- つくよみちゃん
- ディアちゃん

出力WAVが読めること、
manifestにengine version、speaker ID、style IDが記録されることを確認する。

### 10.4 手動試聴

タスク3の共通試聴原稿を使用する。

確認項目:

- 専門用語
- 数字
- 英字
- SQLまたはコード
- 速度
- 抑揚
- 音量
- 長時間聴取
- VOICEVOX候補との音量差

---

## 11. 成果物

```text
docs/specifications/12-coeiroink-client.md
```

付属する確認結果:

```text
docs/specifications/voice-profiles/
├─ lilin-chan-coeiroink-default.yaml
├─ tsukuyomi-chan-coeiroink-default.yaml
└─ dia-chan-coeiroink-default.yaml
```

話者ごとの最終パラメータはタスク3の成果物とし、
本タスクではAPI接続、識別子解決、起動方式、利用条件を確定する。

---

## 12. 完了条件

- 使用バージョンが固定されている。
- 起動方法が一つに決まっている。
- 公式APIまたは採用APIの根拠が記録されている。
- 共通TTSインターフェースとの対応が定義されている。
- リリンちゃんを再現可能に選択できる。
- つくよみちゃんを再現可能に選択できる。
- ディアちゃんを再現可能に選択できる。
- 各候補のstyleを再現可能に選択できる。
- 3名の音声ライブラリ導入状態を検出できる。
- 利用条件と必要なクレジットを記録できる。
- エンジンバージョンをmanifestへ記録できる。
- 上位処理にCOEIROINK固有の候補名分岐がない。
- 3名を同じ試聴手順へ通せる。

---

## 13. 完了後の処理

1. 成果物を`status: review`で作成する。
2. 実サービスで3名の疎通確認を行う。
3. 利用条件とクレジットを人間が確認する。
4. 承認後に`status: approved`、`version: "1.0"`とする。
5. `docs/specifications/12-coeiroink-client.md`へ配置する。
6. 提案側の旧`12-coeiroink-client.md`を削除する。
7. 本タスクを`status: done`へ変更する。
