---
spec_id: 08-character-profile-schema
title: "キャラクタープロファイルのスキーマ"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---


# キャラクタープロファイルのスキーマ

## 1. 目的

原稿上の一人称、語尾、役割、説明口調、表現強度を定義し、
TTSの声、速度、音高、抑揚とは分離する。

## 2. 基本原則

```text
character profile
＝ 原稿上の話し方

voice profile
＝ 音声合成の声と設定
```

音声候補を使用しただけで、
その音声キャラクター固有の口調を原稿へ自動適用してはならない。

## 3. ファイル

```text
project/characters/<character_id>.yaml
```

## 4. 対象

キャラクタープロファイルの対象を固定列挙しない。

次の場合に作成する。

- 中立ナレーターを定義する
- 特定の説明口調を再利用する
- キャラクター固有の一人称・語尾を使用する
- 複数役割の会話を作る

音声候補8名はvoice profileの候補であり、
全員にcharacter profileを作ることを必須としない。

## 5. 中立例

```yaml
schema_version: "1.0"
character_id: neutral-explainer
display_name: 中立解説者
content_revision: 1
style_enabled: false

speech_style:
  first_person: null
  sentence_endings:
    preferred: []
    prohibited: []
  politeness: polite
  energy: neutral
  explanation_style: clear

character_style:
  default_strength: low
  maximum_consecutive_styled_endings: 0
  apply_to:
    introduction: false
    transition: false
    explanation: false
    definition: false
    analogy: false
    warning: false
    summary: false
  preserve:
    definitions: true
    quotes: true
    code: true
    technical_terms: true

behavior:
  role_defaults:
    - explainer
```

## 6. 強度

- `low`: 導入、話題転換、補足、まとめへ主に適用する。
- `medium`: 通常説明にも適度に適用する。
- `high`: ほぼ全編へ適用する。長時間教材の初期値にしない。

## 7. 変換ルール

MUST:

- 内容、条件、例外、数値を変更しない。
- 技術的主張を追加しない。
- 引用、コード、SQL、定義を保護する。
- 同じ語尾の連続を制限する。
- 変換前hashとprofile revisionを記録する。

MUST NOT:

- 語尾だけを機械的に全置換する。
- 声のキャラクター名から口調を推測する。
- キャラクター性のために事実を誇張する。

## 8. 役割

```text
explainer
learner
reviewer
example_provider
warning_provider
```

`character_id`と`role`を分離する。

## 9. 音声候補との関係

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

上記はvoice profile候補である。
口調を使う場合だけ別途character profileを作成する。

## 10. バリデーション

### Error

- character ID欠落
- 未知のstrength
- 連続語尾上限が負
- preserve key欠落
- style enabledなのにspeech style欠落

### Warning

- definitionへhighを適用
- code保護がfalse
- technical terms保護がfalse
- 特定音声キャラクターの口調を確認なく自動生成
- 長時間教材でhighを既定値に使用

### Review required

- 定義文が変化した疑い
- 技術用語が言い換えられた
- 数値・条件・例外が変化した
- キャラクター表現が教材内容を邪魔する

## 11. 現行実装との関係

- TTSクライアントは文章変換をしない。
- character transformerは音声エンジンを知らない。
- 中立原稿を標準として許可する。
- voice profile変更では原稿を変更しない。

## 12. テスト観点

- 同じ原稿へ複数character profileを適用できる。
- 中立profileで本文が変化しない。
- definitionとcodeが保護される。
- 語尾連続上限を超えない。
- character変更で原稿承認が無効になる。
- voice変更では原稿承認が維持される。
- 音声候補名だけから口調を自動適用しない。

## 13. 完了条件

- 声を変更せず文章キャラクターだけを変更できる。
- 文章を変更せず声だけを変更できる。
- 中立原稿で8名の音声候補を比較できる。
