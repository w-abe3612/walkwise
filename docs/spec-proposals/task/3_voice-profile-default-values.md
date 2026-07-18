---
task_type: specification_decision
status: draft
order: 3
title: "話者別音声プロファイル初期値"
depends_on:
  - 1_sample-book-end-to-end-validation.md
output_spec: "docs/specifications/voice-profile-default-values.md"
last_updated: "2026-07-18"
---

# 3. 話者別音声プロファイル初期値

## 1. 目的

正式な候補話者について、学習用オーディオブックの長時間聴取に適した
速度、音高、抑揚、音量、無音時間、採用スタイルを試聴によって決定する。

本タスクでは、すべての候補を必ず正式採用することや、
全作品で一人の共通既定話者を使用することは要求しない。

作品ごとに異なる話者を選択できることを前提とする。

---

## 2. 正式な候補話者

### 2.1 VOICEVOX

| character_id | 表示名 | voice_profile_id候補 |
|---|---|---|
| `kasukabe-tsumugi` | 春日部つむぎ | `kasukabe-tsumugi-voicevox-default` |
| `ouka-miko` | 櫻歌ミコ | `ouka-miko-voicevox-default` |
| `chugoku-usagi` | 中国うさぎ | `chugoku-usagi-voicevox-default` |
| `nekotsuka-bi` | 猫使ビィ | `nekotsuka-bi-voicevox-default` |
| `tohoku-kiritan` | 東北きりたん | `tohoku-kiritan-voicevox-default` |

### 2.2 COEIROINK

| character_id | 表示名 | voice_profile_id候補 |
|---|---|---|
| `lilin-chan` | リリンちゃん | `lilin-chan-coeiroink-default` |
| `tsukuyomi-chan` | つくよみちゃん | `tsukuyomi-chan-coeiroink-default` |
| `dia-chan` | ディアちゃん | `dia-chan-coeiroink-default` |

表示名と内部IDを分離する。

内部IDは一度採用した後、表示名や表記方針が変わっても原則変更しない。

---

## 3. このタスクを今決める理由

音声プロファイルの構造は承認済みだが、
話者ごとの最終値と採用スタイルはまだ確定していない。

また、従来のタスク文書では、
ずんだもん、四国めたん、りりんちゃんを中心に想定していた。

正式候補を今回の8名へ変更し、
VOICEVOXとCOEIROINKを同じ評価基準で比較できるようにする必要がある。

---

## 4. 決定する事項

候補話者ごとに次を決定する。

- 使用するTTSエンジン
- 話者ID
- スタイルID
- エンジン上での表示名
- `speed_scale`
- `pitch_scale`
- `intonation_scale`
- `volume_scale`
- 文末無音
- 段落間無音
- 節間無音
- 章間無音
- 専門用語やコード読み上げ時の上書き
- 長時間聴取への適性
- 採用用途
- 不採用または保留理由
- エンジンバージョン
- キャラクターまたは音声ライブラリのクレジット情報

話者IDとスタイルIDはコードへ固定値として直接埋め込まず、
使用するエンジンの話者一覧から確認してプロファイルへ保存する。

---

## 5. 評価を二段階に分ける

8名すべてについて4種類以上の速度を最初から比較すると、
音声数と確認量が大きくなる。

そのため、次の二段階で評価する。

### 5.1 第一次試聴

8名すべてを同一原稿、同一評価項目で比較する。

第一次試聴では、原則として次を使用する。

```yaml
trial_stage: screening
candidate_speed_scales:
  - 1.00
  - 1.10
```

エンジン間で同名パラメータの意味が異なる場合、
数値を単純比較せず、聴感上の読み速度と実測時間も記録する。

第一次試聴の目的は、次を確認することである。

- 内容を聞き取りやすい
- 長時間聴いて疲れにくい
- 専門用語が聞き分けやすい
- 数字、英字、SQL、コードを認識しやすい
- 声質が教材内容を邪魔しない
- 不自然な抑揚が少ない
- エンジンを安定して再現できる

### 5.2 第二次試聴

第一次試聴で残った候補だけについて、詳細値を比較する。

```yaml
trial_stage: detailed
candidate_speed_scales:
  - 1.00
  - 1.05
  - 1.10
  - 1.15
```

必要に応じて話者別に候補範囲を変更してよい。

第二次試聴では、速度だけでなく次も調整する。

- pitch
- intonation
- volume
- sentence pause
- paragraph pause
- section pause
- chapter pause
- 採用スタイル

---

## 6. 共通試聴原稿

同一原稿をすべての候補へ使用する。

原稿は2〜5分程度とし、最低限次を含める。

1. 短い導入
2. 技術的な定義
3. やや長い通常説明
4. 数字
5. 英字
6. MySQLなどの専門用語
7. SQLまたはコード
8. 箇条書き相当の列挙
9. 注意事項
10. まとめ
11. 疑問文
12. 固有名詞

候補ごとに内容を変更してはならない。

発音調整のために`tts_text`を変更した場合は、
変更内容を話者別に記録する。

---

## 7. 評価項目

各候補を次の5段階で評価する。

```text
1 = 不適
2 = やや不適
3 = 利用可能
4 = 良好
5 = 非常に良好
```

| 評価項目 | 内容 |
|---|---|
| clarity | 単語と文を聞き分けやすい |
| fatigue | 長時間聴取で疲れにくい |
| terminology | 専門用語を識別しやすい |
| code_reading | 英字、SQL、記号の読みを理解しやすい |
| pace | 遅すぎず速すぎない |
| intonation | 不自然な抑揚が少ない |
| neutrality | 教材内容を邪魔しない |
| character_fit | 作品の雰囲気に合う |
| engine_stability | 同じ条件で再生成しやすい |
| correction_cost | `tts_text`修正量が少ない |

自由記述として次も記録する。

- 良かった点
- 気になった点
- 向いている分野
- 向いていない分野
- 必要な読み辞書
- 推奨スタイル
- 再試聴の要否

---

## 8. 採用状態

候補ごとに次の状態を持つ。

```text
candidate
screening_passed
screening_rejected
detailed_review
approved
approved_for_limited_use
on_hold
rejected
```

意味:

- `candidate`: 未試聴
- `screening_passed`: 第一次試聴を通過
- `screening_rejected`: 第一次試聴で不採用
- `detailed_review`: 詳細調整中
- `approved`: 標準利用可能
- `approved_for_limited_use`: 特定作品・用途だけ利用可能
- `on_hold`: エンジン、規約、音質などの理由で保留
- `rejected`: 正式不採用

不採用になっても候補履歴を削除しない。

---

## 9. 作品ごとの話者選択

全作品で一人の共通話者を使用する必要はない。

`project-plan.yaml`では、作品ごとに次を指定できるものとする。

```yaml
narration:
  mode: single_speaker_per_chapter
  default_character_id: kasukabe-tsumugi
  default_voice_profile_id: kasukabe-tsumugi-voicevox-default
```

分野ごとに異なる話者を採用してよい。

例:

```text
哲学
＝ 落ち着きと聞き疲れしにくさを重視

生物学
＝ 用語の明瞭さを重視

データベース
＝ 英字、SQL、数字の聞き分けを重視

マーケティング
＝ 明るさとテンポを重視
```

上記は評価方針の例であり、特定話者の割り当てを確定するものではない。

---

## 10. 音声とキャラクター表現の分離

音声候補であることと、原稿へキャラクター口調を適用することは別の設定とする。

```text
voice profile
＝ 声、速度、音高、抑揚、音量、無音

character profile
＝ 一人称、語尾、説明口調、役割
```

候補話者の声を使用しても、
原稿へそのキャラクター特有の語尾や人格表現を必ず適用する必要はない。

学習教材では、最初に中立原稿で音声を比較し、
キャラクター表現は別の試聴として評価する。

---

## 11. VOICEVOX候補の扱い

VOICEVOX候補は話者一覧APIから実際のspeaker/style情報を取得する。

固定する情報:

```yaml
engine: voicevox
speaker:
  id: "<resolved-style-id>"
  style_id: "<resolved-style-id-or-null>"
engine_identity:
  speaker_uuid: "<resolved-speaker-uuid>"
  engine_version: "<tested-version>"
```

実際に合成へ渡すIDと、
表示用キャラクターIDを分離する。

---

## 12. COEIROINK候補の扱い

COEIROINK候補は、タスク5で確定するAPIと起動方式を使用する。

対象:

- リリンちゃん
- つくよみちゃん
- ディアちゃん

候補ごとに次を確認する。

- 音声ライブラリが導入済みか
- speaker UUIDまたは識別子
- style ID
- 利用可能なスタイル
- エンジンバージョン
- クレジット要件
- 利用条件
- 最大入力長
- パラメータ対応状況

COEIROINKのIDをVOICEVOXのIDへ変換してはならない。

---

## 13. 推奨する初期回答

- 正式候補は本書記載の8名とする。
- VOICEVOX 5名、COEIROINK 3名へ分類する。
- 全候補を第一次試聴する。
- 第一次試聴は速度1.00と1.10を基本とする。
- 第一次試聴を通過した候補だけ詳細調整する。
- 現行互換値1.6は新規候補の既定値にしない。
- 旧値1.6が必要な場合は互換プロファイルとして分離する。
- 話者ID、UUID、style IDをコードへ直書きしない。
- 最終値にはエンジンバージョンを記録する。
- 音声候補とキャラクター口調を分離して評価する。
- 一人のグローバル既定話者を必須にしない。
- 作品ごとに承認済み候補から選択できるようにする。

---

## 14. 策定手順

1. 8名の候補一覧を確定する。
2. エンジン別に話者・スタイル一覧を取得する。
3. 各候補の利用条件とクレジット情報を記録する。
4. 共通試聴原稿を作成する。
5. 中立原稿で第一次試聴音声を生成する。
6. 評価表へ採点とコメントを記録する。
7. 第二次試聴へ進む候補を決める。
8. 詳細な速度、音高、抑揚、音量、無音を比較する。
9. 作品分野ごとの適性を記録する。
10. 採用状態と採用理由を確定する。
11. 承認済みvoice profileを作成する。
12. エンジンバージョンと話者識別子をmanifestへ記録する。
13. プロファイル変更時の試聴承認無効化を確認する。

---

## 15. 成果物

```text
docs/specifications/voice-profile-default-values.md
```

付属成果物:

```text
docs/specifications/voice-profiles/
├─ kasukabe-tsumugi-voicevox-default.yaml
├─ ouka-miko-voicevox-default.yaml
├─ chugoku-usagi-voicevox-default.yaml
├─ nekotsuka-bi-voicevox-default.yaml
├─ tohoku-kiritan-voicevox-default.yaml
├─ lilin-chan-coeiroink-default.yaml
├─ tsukuyomi-chan-coeiroink-default.yaml
└─ dia-chan-coeiroink-default.yaml

docs/specifications/voice-profile-evaluations/
├─ common-audition-script.md
├─ screening-results.yaml
└─ detailed-results.yaml
```

不採用候補のプロファイルは、`status: rejected`または`on_hold`として
評価結果側へ残し、正式利用可能なprofileとしては登録しない。

---

## 16. バリデーション

- 候補IDが重複していない。
- 表示名と内部IDが分離されている。
- engineが`voicevox`または`coeiroink`である。
- speaker IDが試聴時に解決済みである。
- 使用style IDが実際に存在する。
- speedとvolumeが0より大きい。
- pauseが0以上である。
- engine versionが記録されている。
- 試聴原稿のcontent hashが候補間で同一である。
- 採用プロファイルに人間の試聴承認がある。
- 利用条件・クレジット確認が記録されている。

---

## 17. テスト観点

- 8名を候補一覧として読み込める。
- VOICEVOXとCOEIROINKのID形式を同じ文字列型で保持できる。
- エンジンごとの固有IDを混同しない。
- 同一原稿・同一候補値から試聴を再生成できる。
- voice profile変更で試聴承認だけが無効になる。
- character profileを変更せず声だけ変更できる。
- 声を変更せずcharacter profileだけ変更できる。
- 不採用候補をproject planから選択できない。
- `approved_for_limited_use`を許可された作品だけで選択できる。
- エンジン未起動時に対象候補だけを`blocked`として扱える。

---

## 18. 完了条件

- 8名の候補と使用エンジンが明示されている。
- 各候補の話者・スタイル識別子を再現可能に取得できる。
- 共通試聴原稿がある。
- 第一次試聴結果が記録されている。
- 詳細試聴へ進む候補が決定している。
- 採用候補の最終パラメータが明示されている。
- 互換値と新規推奨値が混同されない。
- 同じ条件で試聴を再生成できる。
- 値変更時の試聴承認無効化が定義されている。
- 作品ごとに承認済み話者を選択できる。
- 音声とキャラクター表現が分離されている。

---

## 19. 完了後の処理

1. 成果物のフロントマターを`status: review`にする。
2. 人間が内容を確認する。
3. 承認後に`status: approved`、`version: "1.0"`とする。
4. 成果物を`docs/specifications/`へ配置する。
5. 承認済みvoice profileを付属成果物として配置する。
6. 本タスクを`status: done`へ変更する。
7. `INDEX.md`の次タスクへ進む。
