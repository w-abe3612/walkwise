---
task_type: specification_validation
status: draft
order: 1
title: "サンプル1章による仕様間整合性確認"
depends_on: []
spec_refs:
  - ../../specifications/audiobook-creation-pipeline.md
  - ../../specifications/01-common-identifiers-and-versioning.md
  - ../../specifications/02-process-input-output.md
  - ../../specifications/03-project-plan-schema.md
  - ../../specifications/04-chapter-generation-schema.md
  - ../../specifications/05-script-segment-schema.md
  - ../../specifications/06-claims-and-sources.md
  - ../../specifications/07-approval-workflow.md
  - ../../specifications/09-voice-profile-schema.md
  - ../../specifications/10-tts-client-common-interface.md
  - ../../specifications/11-voicevox-client.md
  - ../../specifications/13-audio-validation.md
  - ../../specifications/14-audio-packaging.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
output_spec: "docs/specifications/examples/sample-book/ および仕様修正版"
last_updated: "2026-07-19"
---

# 1. サンプル1章による仕様間整合性確認

## 1. 目的

承認済み仕様をサンプル1章へ適用し、
ID、資料、主張、出典、4段階承認、AIモデルルーティング、
TTS、音声manifest、部分再生成を検証する。

## 2. 作業正本

```text
docs/spec-proposals/examples/sample-book/
```

検証完了後だけ次へ昇格する。

```text
docs/specifications/examples/sample-book/
```

## 3. サンプル規模

- 1作品
- 1章
- 8〜10セグメント
- 技術的主張4件以上
- AI生成例え話1件以上
- 資料3件以上
- 1キャラクター
- 暫定voice profile 1件
- 章MP3
- audio manifest
- AI execution report
- validation report

## 4. 資料

最低限次を含める。

1. factual evidenceとなる公式資料
2. factual evidenceとcurriculum structureを持つ無料教材
3. curriculum structureだけを持つ公開目次

公開目次を技術的主張の証拠に使用しない。

## 5. AIモデルルーティング

最低限次を検証する。

| 処理 | 期待する論理層 |
|---|---|
| 目次整理 | economy structuring |
| topic抽出 | economy structuring |
| 主張候補抽出 | economy structuring |
| 形式変換 | economy structuring |
| 章初稿 | standard generation |
| 分かりやすさ変換 | standard generation |
| 音声向け変換 | standard generation |
| source conflict fixture | high assurance review |
| 最終意味レビュー | high assurance review |

初期モデル:

```text
economy
→ Gemini 2.5 Flash-Lite

standard
→ Gemini 2.5 Flash

high assurance
→ テスト用に設定した高性能モデルまたはmock
```

high assurance未設定時に、standardへ黙って降格しないことを確認する。

## 6. 資料構築成果物

```text
source-summary.yaml
topic-index.yaml
coverage-map.yaml
source-requirements.yaml
chunk-manifest.json
```

coverage mapに一つの`missing`を用意し、
追加資料提案へ戻れることを検証する。

## 7. 承認

```text
materials_curriculum
planning
verified_script
preview_audio
```

## 8. 必須変更シナリオ

- source revision変更
- curriculum変更
- 原稿text変更
- tts_textのみ変更
- voice profile変更
- MP3タグのみ変更
- prompt version変更
- physical model変更
- budget stop
- cache hit
- cache invalidation

## 9. AI固有シナリオ

### 9.1 主張候補抽出

Flash-Lite相当のeconomy結果は`pending`とする。
そのまま`verified`へ変更できない。

### 9.2 source conflict

高性能モデルまたは人間確認へ進む。
モデル未設定時は`blocked`または`human_review_required`とする。

### 9.3 必要chunkだけの入力

章と無関係なsource chunkがAIリクエストへ入らないことを確認する。

### 9.4 cache

同じtask、model、prompt version、input hashでAPI再実行しない。

### 9.5 usage

model、prompt、input hash、token usageを記録する。
usage取得不能時はwarningとし、推測値を実測として保存しない。

## 10. 音声

VOICEVOXで1〜3分の試聴音声を生成する。

- segment WAV
- chapter MP3
- audio manifest
- validation report

話者は暫定profileとし、正式採用を意味しない。

## 11. 異常fixture

```text
fixtures/
├─ unsupported-claim.yaml
├─ source-conflict.yaml
├─ invalid-reference.yaml
├─ high-assurance-unconfigured.yaml
├─ budget-stop.yaml
├─ cache-invalidation.yaml
└─ unapproved-output-request.yaml
```

## 12. 完了条件

- 参照先のないIDがない。
- 4件以上の技術的主張を出典まで追跡できる。
- 公開目次を事実根拠にしていない。
- 4段階承認が機能する。
- economy、standard、high assuranceが正しく選択される。
- high assurance未設定時に黙って降格しない。
- 全資料ではなく必要chunkだけを送る。
- cacheと無効化が機能する。
- usage記録がある。
- coverage不足から資料追加へ戻れる。
- 未検証主張が本番TTSを通過しない。
- 章MP3とmanifestを生成できる。
- 未承認音声がdeliverablesへ入らない。
- validation reportがある。

## 13. 完了後の処理

1. 全シナリオを実行する。
2. validation reportを確認する。
3. 不整合を該当仕様へ差し戻す。
4. 再検証する。
5. サンプルを承認済み側へ昇格する。
6. 本タスクを`done`へ変更する。
