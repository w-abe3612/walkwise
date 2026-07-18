---
document_type: future_spec_proposal
proposal_id: audio-recording-source-ingestion
title: "授業録音・音声ファイルを資料とする入力パイプライン案"
status: draft
version: "0.1"
last_updated: "2026-07-19"
target_release: post_mvp
required_for_mvp: false
---

# 授業録音・音声ファイルを資料とする入力パイプライン案

## 1. 目的

授業、講義、勉強会、インタビュー、会議、個人メモ等を録音した音声ファイルを、
将来オーディオブック作成の資料として扱うための検討案を記録する。

本書は未承認の将来案であり、
録音・外部送信・自動文字起こしを許可する仕様ではない。

## 2. 想定入力

- WAV
- MP3
- M4A / AAC
- FLAC
- OGG
- 利用者が用意したtranscript
- speakerメモ
- 授業資料との対応表

録音context候補:

```text
lecture
classroom
seminar
meeting
interview
field_note
personal_voice_memo
```

## 3. 基本処理案

```text
原音声
↓
immutable保存・hash
↓
音声品質検査
↓
必要に応じて派生ノイズ低減音声
↓
ASR raw
↓
speaker / timestamp alignment
↓
normalized transcript
↓
structured chunks
↓
source summary / topic index
```

ノイズ低減音声や音量調整音声を原音声として扱わない。

## 4. 同意・プライバシー

授業を録音できることと、
録音内容をAIへ送信・教材化・公開できることは別である。

最低限次を確認する。

- 録音が許可されている
- 講師の利用条件
- 受講者・参加者の発話
- 個人名、学生番号、住所、健康、勤務先等の個人情報
- 外部ASRへの送信許可
- 公開・商用利用の許可
- 要配慮情報の有無
- 保存期間

複数話者または第三者の発話を含む場合、
既定で`privacy_review_required`とする。

## 5. Source locator案

```yaml
locator:
  type: audio_time_range
  start_ms: 360000
  end_ms: 392500
  speaker_id: lecturer-01
```

主張、引用、要約は元音声の時間範囲へ戻れるようにする。

## 6. ASR案

初期方針案:

```yaml
asr:
  preferred: local_provider
  cloud_default: disabled
  raw_transcript_immutable: true
  normalized_transcript_separate: true
  automatic_factual_verification: prohibited
```

専門用語、固有名詞、数式、コード、英字、
複数話者の重なりは`review_required`とする。

## 7. 話者分離

speaker diarizationを利用する場合でも、
話者名を自動的に実名へ結び付けてはならない。

```text
speaker-01
speaker-02
unknown-speaker
```

実名対応は人間が許可した場合だけ別metadataとして保存する。

## 8. 音声品質

検査候補:

- duration
- sample rate
- channels
- clipping
- 無音
- background noise
- reverberation
- speaker overlap
- microphone drop
- 分割ファイルの欠番
- 同一区間の重複

品質が低くても原音声を削除せず、
ASR confidenceとreview範囲を記録する。

## 9. 授業資料との関連付け

授業録音だけでは、
スライド・板書・配布資料に依存する内容が欠落する可能性がある。

```yaml
companion_materials:
  - source_id: lecture-slide-01
    relationship: synchronized_material
```

「この図」「前の式」等の発話は、
対応資料がない限り自動確定しない。

## 10. 権利・利用目的

最低限次を記録する。

- 録音者
- 録音日時
- 授業・講義名
- 講師
- 録音許可
- 教材化許可
- 外部送信許可
- 公開・商用利用可否
- 第三者発話の有無
- 人間確認者

録音ファイルを持っていることだけを理由に、
公開・再配布可能と判断してはならない。

## 11. 未決定事項

- 初期ASR provider
- diarization provider
- 音声品質閾値
- 長時間音声の分割
- realtime録音対応
- transcript修正UI
- 個人情報マスキング
- companion material同期
- 複数録音機器の同期
- 外部API利用時の削除保証

## 12. 仕様策定前の検証

- 一人の講義
- 教室の遠距離録音
- 複数話者
- 雑音あり
- スライド参照あり
- 数式・コードを含む授業
- 途中停止・複数ファイル
- 一時間以上
- 個人情報を含むfixture

## 13. 昇格条件

- 録音・教材化・外部送信の許可を分離して記録できる。
- 原音声と加工音声が分離されている。
- timestamp locatorが確定している。
- ASR rawとnormalized transcriptが分離されている。
- 複数話者と個人情報を人間確認へ送れる。
- companion materialとの関係を保存できる。
- ASRだけで事実をverifiedにしない。
