---
spec_id: asr-script-audio-verification
title: "ASRによる原稿と音声の照合"
status: provisional
version: "0.1"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/15_asr-verification.md
  source_task: docs/spec-proposals/task/15_asr-script-audio-verification.md
depends_on:
  - 4_audio-validation-thresholds.md
  - 14_m4b-and-complete-book-output.md
spec_refs:
  - audio-validation-thresholds.md
  - m4b-and-complete-book-output.md
  - ../../specifications/13-audio-validation.md
  - ../../specifications/18-ai-model-routing-and-cost-control.md
---

# ASRによる原稿と音声の照合(ドラフト)

> **状態に関する注記**
> 本機能はASRエンジンの選定・benchmarkを必要とし、夜間実行では音声サンプルへの
> ASR実行、外部APIへの音声送信のいずれも行っていない。閾値・誤検出率は未測定であり
> `status: provisional`とする。

## 1. 目的

将来機能として、音声認識(ASR)結果と原稿を比較し、読み飛ばし、重複、欠落を
review候補として検出する仕様を定義する。

## 2. 対象範囲

- ASRを必須工程にするか
- 照合単位
- 採用ASRの候補選定方針(値は未確定)
- 誤差指標
- warning/review_required/自動failの境界
- 外部APIへ音声を送る場合の取り扱い

## 3. 対象外

- ASRの実行・benchmark(本タスクでは未実施)
- 発音・声質・キャラクター適合の最終判定(常に人間、`13-audio-validation.md`と同様)
- ASR単独での正式成果物の自動合否判定

## 4. 現行実装

現行コードにASR照合の実装は存在しない。

## 5. 推奨仕様

### 5.1 必須工程にするか

質問1への回答: **必須にせず、追加のreview支援機能にする。**

```yaml
asr_verification:
  required: false
  role: additional_review_support
```

ASRなしでも基本パイプライン(原稿承認→試聴承認→本番TTS→音声検査→章MP3)は
完結する(`audiobook-creation-pipeline.md`の正式な処理順序を変更しない)。

### 5.2 照合単位

質問2への回答: **原則として原稿segment単位とする。**

```yaml
alignment_unit: segment
fallback_unit: chapter   # segment単位のアラインメントが失敗した場合の代替
```

### 5.3 採用ASR

質問3への回答: **provider interfaceを定義し、初期候補はローカルWhisper互換エンジンと
する。benchmark前に物理実装を最終固定しない。**

```python
class ASRProvider(Protocol):
    provider_name: str

    def transcribe(self, request: "ASRRequest") -> "ASRResult": ...
```

```yaml
asr_provider_policy:
  status: provisional
  initial_candidate: local_whisper_compatible
  cloud_provider:
    enabled_by_default: false
    allowed_when: explicit_permission_and_rights_recorded
  evidence:
    benchmarked: false
```

### 5.4 誤差指標

質問4への回答: **文字誤り率(CER)、単語誤り率(WER)、欠落・重複・順序差を使い、
専門用語辞書とtts_textで正規化する。**

```yaml
metrics:
  - character_error_rate
  - word_error_rate
  - missing_segment_ratio
  - duplicate_segment_ratio
  - order_mismatch_count
normalization:
  terminology_dictionary: enabled
  use_tts_text_as_reference: true   # textではなくtts_textと比較(意図的な読み変換を誤検出しない)
```

### 5.5 自動fail可否

質問5への回答: **しない。** 明確な空音声・順序欠落など、ASR以外でも
確認できる場合を除き`review_required`にする。

```yaml
auto_fail_policy:
  allowed: false
  exceptions:
    - empty_audio_detected_independently_of_asr
    - segment_order_missing_detected_independently_of_asr
  default_result: review_required
```

これは`13-audio-validation.md` 14節「Review required」区分の「ASR差分」の
扱いと一致させている。

### 5.6 外部API送信

質問6への回答: **既定では送らない。外部送信は明示許可、rights、privacy記録が
ある場合だけにする。**

```yaml
external_transmission:
  default: disabled
  requires:
    - explicit_human_permission
    - rights_status_recorded
    - privacy_notice_acknowledged
```

`rights-and-license-management.md`のusage_purposeゲートと連動させ、
権利未確認資料の音声を無断でクラウドASRへ送らない。

## 6. 入力

- セグメントWAVまたは章MP3
- 検証済み原稿の`tts_text`
- 専門用語辞書

## 7. 出力

- ASR照合report(8節)
- benchmark matrix(9節、未実施)

## 8. ASR report例

```json
{
  "schema_version": "1.0",
  "audio_id": "ch01-seg001-r0003",
  "asr_provider": "local_whisper_compatible",
  "asr_provider_version": null,
  "status": "review_required",
  "metrics": {
    "character_error_rate": 0.08,
    "word_error_rate": 0.12,
    "missing_segment_ratio": 0.0,
    "duplicate_segment_ratio": 0.0,
    "order_mismatch_count": 0
  },
  "issues": [
    {
      "code": "possible_mispronunciation",
      "severity": "review_required",
      "segment_id": "ch01-seg001"
    }
  ],
  "threshold_status": "provisional"
}
```

## 9. Benchmark計画(未実施)

1. 正常音声と、意図的に欠落・重複させた音声のfixtureを用意する。
2. ASR候補(ローカルWhisper互換エンジン等)を比較する(本タスクでは未実施)。
3. 原稿とのアラインメント方法(動的計画法によるsegmentマッチング等)を検証する。
4. 誤検出率(正常な言い換え・発音差を誤ってreview_requiredにする割合)を測定する。
5. review reportの形式を確定する。

夜間実行ではASRエンジンのインストール・実行・音声の外部送信は行っていない。

## 10. 正常系

1. セグメントWAVと`tts_text`を用意する。
2. ASRを実行し、テキストを取得する(ローカル実行、外部送信は既定で行わない)。
3. 専門用語辞書で正規化する。
4. `tts_text`とASR結果をsegment単位でアラインメントする。
5. 誤差指標を計算する。
6. 閾値(provisional)と比較し、`pass`/`warning`/`review_required`を判定する。
   自動`fail`は5.5節の例外を除き使用しない。

## 11. 異常系

| ケース | 扱い |
|---|---|
| ASRエンジン未設定 | ASR照合をスキップ(基本パイプラインは継続、5.1節) |
| セグメント欠落をASRが検出 | `review_required` |
| セグメント重複をASRが検出 | `review_required` |
| 順序差をASRが検出 | `review_required` |
| 外部API送信の許可がない状態で送信しようとする | `blocked` |
| ASR差分だけで正式成果物を自動failにしようとする | Error(5.5節ポリシー違反) |

## 12. バリデーション

- `auto_fail_policy.allowed`が`false`の間、ASR単独の結果で`status: fail`を
  設定できない。
- 外部送信フラグが立っていない状態で、クラウドASRへのリクエストを生成しない。
- `threshold_status`が常に`provisional`または`approved`のいずれかで記録される。

## 13. テスト観点

- 欠落・重複をreview候補として提示できる。
- 正常な言い換えや発音差を過剰検出しない(専門用語辞書・tts_text正規化の効果測定、未実施)。
- 外部送信の有無とデータ取り扱いが明示されている。
- ASRなしでも基本パイプラインが動作する。
- ASR差分だけで自動failにならない。

## 14. 移行・互換性

- 現行実装からの移行対象なし。
- `13-audio-validation.md`の音声検査フローとは独立した追加検査として位置付け、
  既存の`pass`/`warning`/`fail`/`review_required`区分をそのまま流用する。

## 15. 未決定事項

- 最終採用ASRエンジン(ローカルWhisper互換の具体的な実装候補を含む)
- CER/WERの具体的な閾値
- アラインメントアルゴリズムの詳細
- 専門用語辞書の管理方法(既存の用語辞書との統合可否)

## 16. 完了条件

- [x] 欠落・重複をreview候補として提示できる設計になっている。
- [x] 正常な言い換えや発音差を過剰検出しない方針が明示されている(実測は未了)。
- [x] 外部送信の有無とデータ取り扱いが明示されている。
- [x] ASRなしでも基本パイプラインが動作する。
- [x] 出力ドラフトが存在し、`status: provisional`である。
- [x] 未実測・未確認事項が明記されている(9, 15節)。
- [x] 実装コードを変更していない。

## 17. 停止・保留条件(該当状況)

- 音声サンプルなしで最終ASRを固定する必要がある → 未確定のまま`provisional`とする。
- 外部API送信の許可は本タスクでは確認していない → 既定で無効化(5.6節)。
- ASR差分だけで正式成果物を自動failにしそうになる → 5.5節で明示的に禁止した。
