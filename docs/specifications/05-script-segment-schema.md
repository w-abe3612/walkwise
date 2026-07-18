---
spec_id: 05-script-segment-schema
title: "原稿セグメント共通スキーマ"
status: approved
version: "1.1"
approved_at: "2026-07-18"
last_updated: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_231158.txt"
---

# 原稿セグメント共通スキーマ

## 1. 目的

初稿、音声向け原稿、検証済み原稿、TTS入力を同一のセグメント構造で扱い、部分修正・部分再生成・複数話者に対応する。

## 2. セグメントの定義

1セグメントは、1人の話者が連続して読み、単独でTTS再生成できる最小単位とする。

推奨長は、通常説明で80～300文字程度とする。TTSエンジンの制約に合わせた追加分割は音声パイプライン内で行い、原稿セグメントIDは維持する。

## 3. ファイル

```text
chapters/<chapter_id>/<stage>/script.yaml
```

## 4. 推奨スキーマ

```yaml
schema_version: "1.0"
project_id: database-introduction
chapter_id: ch01
stage: verified
content_revision: 3
source_revision: 2
segments:
  - segment_id: ch01-seg001
    order: 1
    speaker:
      character_id: neutral-explainer
      role: explainer
      voice_profile_id: sample-voicevox-profile
    segment_type: introduction
    text: これから、データベースについて説明するのだ。
    tts_text: null
    claim_refs: []
    source_refs: []
    style:
      character_strength: low
    pauses:
      before_ms: 0
      after_ms: 700
    review_status: approved
```

## 5. 必須項目

- `segment_id`
- `order`
- `speaker.character_id`
- `speaker.role`
- `segment_type`
- `text`

`voice_profile_id`は章または作品の既定値を継承できる。

## 6. textとtts_text

- `text`: 正式な原稿内容。
- `tts_text`: 発音、記号、英字読みなどを調整した音声入力。

`tts_text`は意味を変更してはならない。存在しない場合は`text`を使用する。

```yaml
text: MySQLを起動します。
tts_text: マイエスキューエルを起動します。
```

## 7. segment_type

初期列挙値は次とする。

- `heading`
- `introduction`
- `transition`
- `explanation`
- `definition`
- `example`
- `analogy`
- `warning`
- `code`
- `quote`
- `summary`
- `question`

未知の種別を即時拒否せず、`custom:<name>`形式をMAYで許可してもよい。

## 8. 話者と役割

`character_id`は原稿上の人格・説明役を表し、音声エンジンのキャラクター名と一致する必要はない。

音声候補と文章キャラクターを分離する。

話者と役割を分離する。

```yaml
speaker:
  character_id: neutral-learner
  role: learner
  voice_profile_id: sample-learner-voice-profile
```

初期実装は1章1話者だが、各セグメントに話者情報を持たせる。

## 9. 主張と出典

技術的説明は`claim_refs`で主張へ参照し、必要に応じて直接`source_refs`も持てる。

```yaml
claim_refs:
  - ch01-claim001
source_refs:
  - mysql-8-reference
```

通常は主張から出典をたどる。引用や例外的な直接出典だけ`source_refs`を使う。

## 10. 改訂と由来

各セグメントは由来をSHOULDで保持する。

```yaml
provenance:
  previous_segment_id: ch01-seg001
  transformation: audio_adaptation
  previous_text_hash: "..."
```

分割・結合した場合は複数IDを許可する。

## 11. TTS内部分割

VOICEVOXの現行実装は300文字で分割する。本仕様では、原稿セグメントが300文字を超える場合、次の内部IDで分割する。

```text
ch01-seg001-part001
ch01-seg001-part002
```

内部partは音声manifestだけに記録し、原稿YAMLへ恒久追加しない。

## 12. バリデーション

- segment IDとorderの重複はerror。
- text空はerror。
- claim ref欠落はerror。
- speaker参照欠落はerror。
- 負のpauseはerror。
- `definition`でキャラクター強度highはwarning。
- `tts_text`と`text`の意味差が疑われる場合はreview_required。

## 13. 現行テキストとの変換

旧TXTを読む場合、段落または文単位で自動セグメント化し、次を設定する。

```yaml
provenance:
  legacy_input: true
  source_path: text/merged/section1/merged_gemini_fixed.txt
```

自動分割後は人間の承認なしに本番正本として扱わない。

## 14. テスト観点

- 複数話者を順序どおり読み込める。
- 1セグメントだけ変更してハッシュ差分を検出できる。
- 300文字超を内部partへ分割し再結合できる。
- textは不変でtts_textだけを生成できる。
- 旧TXTから決定的にセグメント化できる。

## 15. 完了条件

サンプル章をセグメント配列だけで表現し、1セグメントの修正から対象音声だけを再生成できること。
