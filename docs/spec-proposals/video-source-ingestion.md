---
document_type: future_spec_proposal
proposal_id: video-source-ingestion
title: "動画・YouTube等を資料とする入力パイプライン案"
status: draft
version: "0.1"
last_updated: "2026-07-19"
target_release: post_mvp
required_for_mvp: false
---

# 動画・YouTube等を資料とする入力パイプライン案

## 1. 目的

動画ファイル、利用者が参照するYouTube等の動画、
講義動画、ウェビナー、画面録画等を、
将来オーディオブック作成の資料として扱うための検討案を記録する。

本書は未承認の将来案であり、
動画取得や文字起こし機能の実装を許可する仕様ではない。

## 2. 想定入力

- 利用者が用意したローカル動画
- 利用者が用意した字幕ファイル
- 利用者が用意したtranscript
- 動画URLと人間が確認したmetadata
- 利用条件を確認済みの講義動画
- 自作動画
- 公開ライセンス動画

候補形式:

- MP4
- WebM
- MOV
- MKV
- SRT
- VTT
- TXT / Markdown transcript

## 3. YouTube等の扱い

URLは資料のlocatorであり、
ダウンロードまたは再利用の許可を意味しない。

初期案では次を既定とする。

```yaml
platform_video:
  automatic_download: false
  platform_bypass: prohibited
  preferred_inputs:
    - user_supplied_caption
    - user_supplied_transcript
    - permitted_local_file
  reference_url_only: allowed
```

動画プラットフォームからの自動取得は、
公式な取得方法、利用条件、権利、実装方式を別途確認するまで行わない。

## 4. 処理段階案

```text
動画または字幕
↓
原動画・原字幕をimmutable保存
↓
許可されたローカル動画から音声派生物を生成
↓
字幕またはASR raw
↓
話者・時間位置付きnormalized transcript
↓
visual context requirement
↓
structured chunks
↓
source summary / topic index
```

動画から取り出した音声は派生物であり、
原動画を置き換えない。

## 5. Source locator案

```yaml
locator:
  type: media_time_range
  start_ms: 125000
  end_ms: 148500
  video_frame_ref:
    start_frame_path: null
    end_frame_path: null
```

主張や引用は、動画全体ではなく時間範囲へ戻れるようにする。

## 6. 映像依存情報

次はtranscriptだけでは確定できない。

- スライドにだけ表示された文字
- 図、グラフ、数式
- 実演
- 画面操作
- 指差しや「ここ」「これ」等の参照
- 字幕と発話の不一致

```yaml
visual_context:
  required: true
  reason: "speaker refers to diagram"
  review_status: human_review_required
```

映像確認なしに技術的主張をverifiedへ進めてはならない。

## 7. 文字起こし案

優先順位案:

1. 人間が確認済みの公式字幕
2. 利用者提供字幕
3. 利用者提供transcript
4. ローカルASR
5. 明示許可されたクラウドASR

自動字幕またはASR結果は事実根拠ではなく抽出候補である。

## 8. 権利・利用目的

最低限次を記録する。

- URLまたは原動画の入手元
- 投稿者・講師
- 利用条件
- 字幕の権利
- 録画の権利
- 個人学習、組織内、公開、商用の区別
- 動画内の人物・個人情報
- 外部ASRへの送信許可

公開されていることだけを理由に、
全文取得・再配布・音声化を許可してはならない。

## 9. 未決定事項

- 動画プラットフォームごとの公式取得方法
- 字幕取得adapter
- ローカル動画からの音声抽出tool
- keyframe・slide抽出
- speaker diarization
- ASR provider
- 時間単位chunk
- 映像依存箇所の自動検出
- 長時間動画のコスト制御
- URL更新・削除時の扱い

## 10. 仕様策定前の検証

- 自作動画
- 公開ライセンス動画
- 字幕あり動画
- 字幕なし動画
- スライド中心の講義
- 実演中心の動画
- 複数話者
- 一時間以上の動画

## 11. 昇格条件

- 権利と取得経路が整理されている。
- URLだけで自動downloadしない。
- timestamp locatorが確定している。
- 映像依存箇所を人間確認へ送れる。
- ASR rawとnormalized transcriptが分離されている。
- 外部送信が既定で無効である。
- サンプルで欠落・誤認識・映像依存を検証している。
