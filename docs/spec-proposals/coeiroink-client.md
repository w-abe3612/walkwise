---
spec_id: coeiroink-client
title: "COEIROINKクライアント固有仕様(ドラフト・blocked)"
status: blocked
version: "0.4"
last_updated: "2026-07-19"
merged_from:
  - "docs/spec-proposals/12-coeiroink-client.md (v0.1、初期ドラフト、削除済み)"
  - "docs/spec-proposals/generated-specifications/12-coeiroink-client.md (v0.2、削除済み)"
depends_on:
  - task/3_voice-profile-default-values.md
spec_refs:
  - ../specifications/10-tts-client-common-interface.md
  - ../specifications/11-voicevox-client.md
  - ../specifications/09-voice-profile-schema.md
  - ../specifications/01-common-identifiers-and-versioning.md
  - ../specifications/19-application-scope-and-mvp.md
---

# COEIROINKクライアント固有仕様(ドラフト・blocked)

> **状態に関する注記**
> `19-application-scope-and-mvp.md`により、COEIROINKはpost-MVPの追加TTS engineと
> して製品方針が確定している。初期対象話者はリリンちゃんだけとし、つくよみちゃん・
> ディアちゃんは初期対象として列挙しない(利用者確定方針)。一方、COEIROINK公式サイト・
> 公式リポジトリ・公式APIドキュメントへのアクセス、およびCOEIROINKサービスへの
> 実接続はまだ行っていない。そのため、次の事実確認が必要な項目は**すべて`evidence_gap`**
> として未確定のまま残し、本書は`status: blocked`を維持する。
>
> - 採用COEIROINKバージョンおよびAPI世代
> - 既定URL、health checkエンドポイント
> - リリンちゃんのspeaker UUID/style ID
> - 音声ライブラリの利用条件・必須クレジット文言
> - 公式配布・同梱可否

## 1. 目的

COEIROINKを、承認済みTTS共通インターフェース(`10-tts-client-common-interface.md`)へ
適合させるためのクライアント固有仕様を定義する。post-MVPの追加TTS engineであり、
Walkwise本体には同梱しない。利用者が別途COEIROINKをインストール・起動していることを
前提に、Walkwiseがそれへ接続する。

初期対象話者は次の1名のみとする。

- リリンちゃん (`lilin-chan`)

## 2. 対象範囲

- COEIROINK API呼び出しの共通TTSインターフェースへのマッピング
- speaker/style識別子の解決方法(値そのものではなく、解決の**手順**)
- capabilitiesの表現方法
- エラー変換表
- 起動方式の決定条件(Walcwise非同梱、利用者が別途起動する前提)
- テスト観点

## 3. 対象外

- 採用COEIROINKバージョンの確定(evidence_gap)
- 実際のspeaker UUID/style IDの値(evidence_gap)
- 利用条件・クレジット文言の確定(evidence_gap)
- 話者別の音声パラメータ最終値
- DRM回避や非公式配布物の利用
- MVPへの組み込み(`19-application-scope-and-mvp.md`によりMVP対象外、post-MVP機能)
- COEIROINK自体のWalkwise配布物への同梱(利用者が別途用意する前提)
- つくよみちゃん・ディアちゃんの初期対応(将来、利用者が追加確定した場合に再検討)

## 4. 現行実装

- `script/tts_clients/coeiroink/client.py`は`CoeiroinkNotImplementedError`を送出する
  予約実装のみを持つ(`synthesize_text_to_wav`)。実装は本書では変更していない。
- `docker-compose.yml`にCOEIROINKサービス定義は存在しない。COEIROINKはWalkwiseに
  同梱せず、利用者が別途インストール・起動する前提であるため、非公式Docker imageを
  前提にした同梱は行わない。

## 5. 推奨仕様(構造のみ確定、値はblocked)

### 5.1 話者解決モデル

`01-common-identifiers-and-versioning.md`の「外部エンジンID」原則に従い、
安定IDとエンジンIDを分離する。

```yaml
voice_profile_id: lilin-chan-coeiroink-default
character_id: lilin-chan
display_name: リリンちゃん
engine: coeiroink

speaker:
  id: null            # evidence_gap: 起動中の公式APIから解決する
  style_id: null       # evidence_gap

engine_identity:
  engine_version: null       # evidence_gap
  speaker_uuid: null         # evidence_gap
  engine_display_name: null  # evidence_gap
```

`character_id`と`voice_profile_id`は、エンジンの表示名やUUIDが変わっても変更しない
(`01-common-identifiers-and-versioning.md` 14節)。speaker/style IDをコードへ
直書きせず、起動中のCOEIROINK APIの話者一覧から解決する。

### 5.2 音声ライブラリ未導入時の扱い

リリンちゃんの音声ライブラリが導入されていない、またはCOEIROINK自体が
起動していない場合、COEIROINKエンジンまたは該当話者だけを利用不可とし、
VOICEVOXや他のアプリ機能全体を停止しない。

### 5.3 capabilities(値は未確認)

```yaml
supports:
  speed_scale: true          # 既存ドラフトの記載を仮採用、要実機確認
  pitch_scale: conditional
  intonation_scale: conditional
  volume_scale: true
  speaker_listing: true
  style_selection: true
limits:
  recommended_max_text_length: null   # evidence_gap: VOICEVOXの300文字を流用しない
```

`conditional`項目は、実機の`/speakers`相当の応答を確認するまで`true`へ固定しない。

### 5.4 共通パラメータ変換の方針

`text`, `speaker_id`, `style_id`, `speed`, `pitch`, `intonation`, `volume`, `無音`,
`出力形式`のそれぞれについて、VOICEVOXと同名でも数値の意味・範囲が同一であると
仮定せず、個別の変換関数を設ける(`11-voicevox-client.md` 4節と対称の構造)。

具体的な変換係数・範囲は、実機の`audio_query`相当API応答を確認してからでなければ
確定できないため、本書では関数のシグネチャ方針のみ示す。

```python
def to_coeiroink_parameters(common: SynthesisRequest) -> "CoeiroinkParameters":
    """共通パラメータをCOEIROINK固有パラメータへ変換する。
    変換係数は未確定(evidence_gap)。
    """
```

### 5.5 エラー変換表(共通インターフェースへの対応方針)

| COEIROINK側(想定) | 共通エラー |
|---|---|
| 接続不能 | `connection_error` |
| health check失敗 | `health_check_failed` |
| 話者一覧取得失敗 | `query_failed` |
| 話者不在 | `speaker_not_found` |
| スタイル不在 | `speaker_not_found` |
| 音声ライブラリ未導入 | `speaker_not_found`(または新設`voice_library_not_installed`。要検討) |
| 不正パラメータ | `invalid_parameter` |
| 未対応パラメータ | `unsupported_parameter` |
| text空 | `text_empty` |
| text長超過 | `text_too_long` |
| 合成失敗 | `synthesis_failed` |
| 非音声応答 | `invalid_audio_response` |
| timeout | `timeout` |
| 出力書き込み失敗 | `output_write_failed` |

`voice_library_not_installed`を共通エラー一覧(`10-tts-client-common-interface.md` 7節)へ
新設するかどうかは、同仕様の変更管理下にあるため、本書だけでは決定しない。

### 5.6 起動方式

COEIROINKはWalkwiseに同梱せず、利用者が別途インストール・起動していることを
前提に、WalkwiseはローカルAPI(例: `http://localhost:<port>`)へ接続するクライアントと
してのみ振る舞う。docker-composeサービスとしての同梱、非公式Dockerイメージの
前提利用は行わない。具体的な既定URL・ポートは、公式インストールガイド確認後に
確定する(evidence_gap)。

`script/tts_clients/coeiroink/client.py`の正式実装は、上記evidence_gapが解消してから
着手する(現行の予約実装は変更しない)。

## 6. 入力

- COEIROINK公式ドキュメント・公式配布情報(未取得)
- 起動中のCOEIROINK `/speakers`相当APIの応答(未取得)
- `09-voice-profile-schema.md`、`10-tts-client-common-interface.md`

## 7. 出力

- 本ドラフト(`status: blocked`)
- evidence gap一覧(9節)
- 話者プロファイル雛形(5.1節、値は`null`)

## 8. 正常系(将来、evidence解消後)

1. 公式ドキュメントからバージョンとAPI世代を確認し、確認日とともに記録する。
2. 起動中のCOEIROINKへhealth checkを行う。
3. `/speakers`相当APIからリリンちゃんの識別子を解決する。
4. リリンちゃんの疎通確認を行う。
5. 共通試聴原稿で確認する(試聴自体は人間が実施)。

## 9. Evidence gap一覧

| 項目 | 状態 | 解消に必要な行動 |
|---|---|---|
| 採用COEIROINKバージョン | evidence_gap | 公式サイト・公式リリースノートの確認 |
| API世代・エンドポイント仕様 | evidence_gap | 公式APIドキュメントの確認 |
| 既定URL | evidence_gap | 公式インストールガイドの確認 |
| リリンちゃんのspeaker UUID/style ID | evidence_gap | 音声ライブラリ導入後、起動中APIから取得 |
| 利用条件・クレジット文言 | evidence_gap | 音声ライブラリ配布元の利用規約確認 |
| 公式配布・同梱可否 | evidence_gap | 公式配布チャネル・ライセンスの確認 |
| 最大入力長・timeout推奨値 | evidence_gap | 公式ドキュメントまたは実機確認 |

## 10. 異常系

| ケース | 扱い |
|---|---|
| 公式資料にアクセスできない | `blocked`のまま保持(本書の状態) |
| COEIROINKが起動していない、または音声ライブラリ未導入 | COEIROINKまたは該当話者だけ利用不可とし、VOICEVOX・アプリ全体は継続動作する |
| 利用条件を確認できない | 当該候補を権利未確認として扱い、公開用途を禁止 |

## 11. バリデーション

- `speaker.id`/`speaker.style_id`が`null`の間、当該voice profileの`status`は
  `provisional`を超えて`approved`にできない。
- `engine_identity.engine_version`が未記録のまま音声manifestへ出力しない。
- 表示名だけで話者を一意に決定するロジックを実装へ持ち込まない。

## 12. テスト観点

- `character_id`/`voice_profile_id`とエンジンIDが分離して保持できる
  (値未確定でも構造テスト可能)。
- エラー変換表に列挙した想定COEIROINKエラーが、対応する共通エラーコードへ
  マップされる(mock前提)。
- `voice_library_not_installed`相当の未導入状態を検出できる設計になっている。
- COEIROINK・リリンちゃんが利用不可でも、VOICEVOXおよびアプリ全体が継続動作する。

これらはmockベースの単体テストとして定義可能であり、実サービスへの接続を
必要としない。実サービス統合テスト・手動試聴は、evidence解消後の別タスクとする。

## 13. 移行・互換性

- `10-tts-client-common-interface.md`のクライアント選択(`registry.get(profile.engine)`)
  機構を変更せず、`coeiroink`エンジンを追加登録する形で組み込む。
- post-MVPの追加候補であり、`19-application-scope-and-mvp.md`のMVP範囲には含めない。

## 14. 未決定事項

- 採用COEIROINKバージョンとAPI世代
- 既定URL、health check、話者一覧APIの実仕様
- リリンちゃんのspeaker/style識別子
- 利用条件と必須クレジット
- `voice_library_not_installed`を共通エラーへ新設するか
- 最大入力長・timeout・リトライの推奨値
- 公式配布・同梱可否

## 15. 昇格条件

- 公式ドキュメントによりバージョン・API世代・既定URLが確認されている。
- 音声ライブラリ導入環境でリリンちゃんのspeaker UUID/style IDが実機確認されている。
- 利用条件・クレジット文言が確認されている。
- 公式配布・同梱可否が確認されている。
- 上記解消後、`docs/specifications/`側のTTSクライアント仕様として提案する。
