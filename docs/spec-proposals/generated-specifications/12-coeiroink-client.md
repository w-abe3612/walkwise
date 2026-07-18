---
spec_id: 12-coeiroink-client
title: "COEIROINKクライアント固有仕様(ドラフト)"
status: blocked
version: "0.2"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/05_coeiroink-runtime-api.md
  source_task: docs/spec-proposals/task/5_coeiroink-client-runtime-api.md
depends_on:
  - 3_voice-profile-default-values.md
spec_refs:
  - ../../specifications/10-tts-client-common-interface.md
  - ../../specifications/11-voicevox-client.md
  - ../../specifications/09-voice-profile-schema.md
  - ../../specifications/01-common-identifiers-and-versioning.md
  - ../12-coeiroink-client.md
---

# COEIROINKクライアント固有仕様(ドラフト・blocked)

> **状態に関する注記**
> 本タスクの実行class は`official_evidence_required`である。
> 夜間自動実行では、COEIROINK公式サイト・公式リポジトリ・公式APIドキュメントへの
> アクセス、およびCOEIROINKサービスへの実接続を行っていない。
> そのため、次の事実確認が必要な項目は**すべて`evidence_gap`**として未確定のまま残す。
>
> - 採用COEIROINKバージョンおよびAPI世代
> - 既定URL、health checkエンドポイント
> - リリンちゃん・つくよみちゃん・ディアちゃんのspeaker UUID/style ID
> - 音声ライブラリの利用条件・必須クレジット文言
> - Docker公式イメージの有無
>
> 本書は、既存の未承認ドラフト(`docs/spec-proposals/12-coeiroink-client.md`)と
> 承認済み`10-tts-client-common-interface.md`・`11-voicevox-client.md`から導出できる
> **構造・インターフェース・命名規則の部分だけ**を`review`相当の完成度で記述し、
> 事実確認が必要な部分は空欄・placeholderのまま`blocked`とする。

## 1. 目的

COEIROINKを、承認済みTTS共通インターフェース(`10-tts-client-common-interface.md`)へ
適合させるためのクライアント固有仕様を定義する。対象話者は次の3名。

- リリンちゃん (`lilin-chan`)
- つくよみちゃん (`tsukuyomi-chan`)
- ディアちゃん (`dia-chan`)

## 2. 対象範囲

- COEIROINK API呼び出しの共通TTSインターフェースへのマッピング
- speaker/style識別子の解決方法(値そのものではなく、解決の**手順**)
- capabilitiesの表現方法
- エラー変換表
- 起動方式の決定条件(方式そのものの断定はしない)
- テスト観点

## 3. 対象外

- 採用COEIROINKバージョンの確定(evidence_gap)
- 実際のspeaker UUID/style IDの値(evidence_gap)
- 利用条件・クレジット文言の確定(evidence_gap)
- 話者別の音声パラメータ最終値(タスク3で確定)
- DRM回避や非公式配布物の利用

## 4. 現行実装

- `script/tts_clients/coeiroink/client.py`は`CoeiroinkNotImplementedError`を送出する
  予約実装のみを持つ(`synthesize_text_to_wav`)。実装は本タスクでは変更していない。
- `docker-compose.yml`は空ファイルであり、COEIROINKサービス定義は存在しない。
- 既存の未承認ドラフト`docs/spec-proposals/12-coeiroink-client.md`は
  「りりんちゃん優先、他話者は追加可能」としていたが、
  `docs/spec-proposals/task/5_coeiroink-client-runtime-api.md`はこれを変更し、
  3名を同格の初期対象とする方針へ更新済みである。本書はこの更新後の方針を正とする。

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
(`01-common-identifiers-and-versioning.md` 14節)。

同様に`tsukuyomi-chan`・`dia-chan`用のプロファイル雛形を用意する。

### 5.2 capabilities(値は未確認)

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

### 5.3 共通パラメータ変換の方針

`text`, `speaker_id`, `style_id`, `speed`, `pitch`, `intonation`, `volume`, `無音`, `出力形式`の
それぞれについて、VOICEVOXと同名でも数値の意味・範囲が同一であると仮定せず、
個別の変換関数を設ける(`11-voicevox-client.md` 4節と対称の構造)。

具体的な変換係数・範囲は、実機の`audio_query`相当API応答を確認してからでなければ
確定できないため、本書では関数のシグネチャ方針のみ示す。

```python
def to_coeiroink_parameters(common: SynthesisRequest) -> "CoeiroinkParameters":
    """共通パラメータをCOEIROINK固有パラメータへ変換する。
    変換係数は未確定(evidence_gap)。
    """
```

### 5.4 エラー変換表(共通インターフェースへの対応方針)

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
新設するかどうかは、`10-tts-client-common-interface.md`の変更管理下にあるため、
本書だけでは決定しない(未決定事項として記録)。

### 5.5 起動方式(決定条件のみ、選択はblocked)

`5_coeiroink-client-runtime-api.md`が挙げる3案(docker-composeサービス/ホスト起動/
開発時手動起動)のいずれを採用するかは、次が確認できるまで決定しない。

- 再現可能な公式Dockerイメージの有無
- Windows上でのホスト起動の実運用性
- 音声ライブラリのライセンス上、コンテナ配布が許容されるか

いずれの場合も、`script/tts_clients/coeiroink/client.py`の正式実装は
起動方式確定後に着手する(現行の予約実装は変更しない)。

## 6. 入力

- COEIROINK公式ドキュメント・公式配布情報(本タスクでは未取得)
- 起動中のCOEIROINK `/speakers`相当APIの応答(本タスクでは未取得)
- `09-voice-profile-schema.md`、`10-tts-client-common-interface.md`

## 7. 出力

- 本ドラフト(`status: blocked`)
- evidence gap一覧(9節)
- 話者プロファイル雛形(5.1節、値は`null`)

## 8. 正常系(将来、evidence解消後)

1. 公式ドキュメントからバージョンとAPI世代を確認し、確認日とともに記録する。
2. 起動中のCOEIROINKへhealth checkを行う。
3. `/speakers`相当APIから3名の識別子を解決する。
4. リリンちゃん→つくよみちゃん→ディアちゃんの順に疎通確認する。
5. 3名を同一の共通試聴原稿で比較する(試聴自体は人間が実施)。

## 9. Evidence gap一覧

| 項目 | 状態 | 解消に必要な行動 |
|---|---|---|
| 採用COEIROINKバージョン | evidence_gap | 公式サイト・公式リリースノートの確認(人間または許可されたセッションでのWeb確認) |
| API世代・エンドポイント仕様 | evidence_gap | 公式APIドキュメントの確認 |
| 既定URL | evidence_gap | 公式インストールガイドの確認 |
| 3名のspeaker UUID/style ID | evidence_gap | 音声ライブラリ導入後、起動中APIから取得 |
| 利用条件・クレジット文言 | evidence_gap | 各音声ライブラリ配布元の利用規約確認 |
| Docker公式イメージの有無 | evidence_gap | 公式配布チャネルの確認 |
| 最大入力長・timeout推奨値 | evidence_gap | 公式ドキュメントまたは実機確認 |

## 10. 異常系

| ケース | 扱い |
|---|---|
| 公式資料にアクセスできない | `blocked`のまま保持(本書の状態) |
| 音声ライブラリ未導入で識別子を確認できない | 該当話者だけ`evidence_gap`、他候補は継続検討可 |
| 利用条件を確認できない | 当該候補を`licensed_reference`相当の権利未確認として扱い、公開用途を禁止 |
| 1候補だけ利用不能 | 他の候補・エンジンまで一律停止しない(`5_coeiroink-client-runtime-api.md` 9節) |

## 11. バリデーション

- `speaker.id`/`speaker.style_id`が`null`の間、当該voice profileの`status`は
  `provisional`を超えて`approved`にできない(`09-voice-profile-schema.md`のstatus規則を準用)。
- `engine_identity.engine_version`が未記録のまま音声manifestへ出力しない。
- 表示名だけで話者を一意に決定するロジックを実装へ持ち込まない。

## 12. テスト観点

- 3名の`character_id`/`voice_profile_id`とエンジンIDが分離して保持できる(値未確定でも構造テスト可能)。
- エラー変換表に列挙した想定COEIROINKエラーが、対応する共通エラーコードへマップされる(mock前提)。
- `voice_library_not_installed`相当の未導入状態を検出できる設計になっている。
- 1候補の利用不能が他候補の処理を止めない。

これらはmockベースの単体テストとして定義可能であり、実サービスへの接続を必要としない。
実サービス統合テスト・手動試聴は、evidence解消後の別タスクとする。

## 13. 移行・互換性

- `10-tts-client-common-interface.md`のクライアント選択(`registry.get(profile.engine)`)機構を
  変更せず、`coeiroink`エンジンを追加登録する形で組み込む。
- 既存の未承認ドラフト`docs/spec-proposals/12-coeiroink-client.md`は、本書が
  `docs/specifications/12-coeiroink-client.md`として承認されるまで削除しない
  (`8_rights...`と同様、本タスクでは既存ファイルを削除しない)。

## 14. 未決定事項

- 採用COEIROINKバージョンとAPI世代
- Docker起動かホスト起動か
- 既定URL、health check、話者一覧APIの実仕様
- 3候補のspeaker/style識別子
- 利用条件と必須クレジット
- `voice_library_not_installed`を共通エラーへ新設するか
- 最大入力長・timeout・リトライの推奨値

## 15. 完了条件(本ドラフトの完了条件)

- [x] 出力ドラフトが存在する。
- [x] フロントマターが`status: review`または`provisional`(本書は`blocked`、より保守的な状態)である。
- [x] 未実測・未確認事項が明記されている(9, 14節)。
- [x] 人間承認済みと偽っていない。
- [x] 主要な正常例・異常例・テスト観点がある(8, 10, 12節)。
- [x] 参照した仕様と根拠が記録されている(spec_refs)。
- [x] 実装コードを変更していない。

## 16. 停止・保留条件(該当状況)

- 公式資料へアクセスしていない(方針により未実施)。
- 採用バージョンを特定できていない。
- 話者ライブラリが導入されておらず識別子を確認できない。
- 利用条件を公式根拠で確認できていない。

以上により、本書の状態は`review`ではなく`blocked`とする。
`docs/specifications/`への昇格には、人間または明示的に許可されたセッションによる
公式情報確認と実機疎通確認が必要である。
