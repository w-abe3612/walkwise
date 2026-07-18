---
spec_id: kindle-capture
title: "Kindle画面キャプチャ"
status: human_review_required
version: "0.1"
last_updated: "2026-07-19"
generated_by:
  type: ai
  task: docs/tasks/12_kindle-capture.md
  source_task: docs/spec-proposals/task/12_kindle-capture.md
depends_on:
  - 7_source-storage-and-common-schema.md
  - 10_ocr-and-scanned-pdf.md
  - 8_rights-and-license-management.md
spec_refs:
  - source-storage-and-common-schema.md
  - ocr-and-scanned-pdf.md
  - rights-and-license-management.md
---

# Kindle画面キャプチャ(ドラフト)

> **特記事項**
> 夜間自動実行では、ブラウザ・Kindleアプリ・画面操作を一切行っていない。
> 本書は仕様(状態機械、schema、検出ロジック)のドラフトのみであり、
> 自動操作の実行、Kindleアプリの起動、画面キャプチャの取得は行っていない。
> 権利・利用規約確認(タスク08)が完了しない限り、本機能を正式処理へ進めない
> 方針そのものを本書の中核要件とする。

## 1. 目的

Kindle画面のキャプチャ、ページ送り、重複・抜け検出、画像保存、
利用上の確認事項(権利・規約)を策定する。

## 2. 対象範囲

- 初期対応OS・アプリ
- 画面設定の固定方法(profile化)
- ページ送りと保存の再開可能性
- 重複・抜けの検出
- 権利・規約確認をどこに位置付けるか

## 3. 対象外

- 実際の自動操作の実行(本タスクでは行わない)
- DRM回避
- Kindleアプリ以外の電子書籍リーダーへの対応
- OCR処理そのもの(→タスク10、本書はOCRへの受け渡しまでを扱う)

## 4. 現行実装

現行コードにKindle画面キャプチャの実装は存在しない。

## 5. 推奨仕様

### 5.1 初期対応OSとアプリ

質問1への回答: **初期はWindows上の利用者が操作可能なKindleアプリ環境に限定する。**

```yaml
kindle_capture_target:
  os: windows
  app: kindle_for_pc
  scope: user_operated_only
```

「利用者が操作可能」とは、利用者が自分のアカウントで正当にログインし、
自分が購入・利用権を持つ書籍のみを対象とすることを意味する。

### 5.2 画面設定の固定

質問2への回答: **固定する。** ウィンドウ位置、表示倍率、フォント、テーマ、
キャプチャ範囲をprofile化する。

```yaml
capture_profile:
  schema_version: "1.0"
  profile_id: kindle-win-default
  window:
    position: null        # 実環境確認後に確定
    size: null
  display:
    zoom_level: null
    font: null
    theme: light
  capture_region:
    x: null
    y: null
    width: null
    height: null
  page_turn:
    method: null           # 例: キーボード右矢印、クリック等(実環境確認後に確定)
```

具体的な座標・倍率値は実環境での確認が必要であり、本書では`null`のまま
構造だけを定義する(evidence_gap)。

### 5.3 ページ送りと再開可能性

質問3への回答: **ページ単位manifestとcheckpointを保存し、
最後に確認済みのページから再開する。**

```yaml
capture_session:
  schema_version: "1.0"
  source_id: kindle-book-001
  profile_id: kindle-win-default
  status: in_progress
  last_confirmed_page: 41
  pages:
    - page_index: 41
      image_path: sources/originals/kindle-book-001/page-0041.png
      image_hash: "..."
      captured_at: "2026-07-19T00:00:00+09:00"
      confirmed: true
```

再開時は`last_confirmed_page + 1`から処理を継続し、
未確認ページ(`confirmed: false`)は再取得候補とする。

### 5.4 重複・抜けの検出

質問4への回答: **画像hash・perceptual hash・OCRされたページ番号・
前後テキストの連続性を組み合わせ、疑いは人間確認にする。**

```yaml
duplicate_and_gap_detection:
  exact_hash: sha256
  perceptual_hash: phash
  page_number_ocr: enabled
  text_continuity_check: enabled
  on_suspected_duplicate: flag_for_review
  on_suspected_gap: flag_for_review
```

自動削除・自動スキップは行わず、疑いのあるページは`review-required.yaml`へ記録する。

### 5.5 権利・規約確認の位置付け

質問5への回答: **処理開始前に利用目的と権利確認を必須にし、
DRM回避・本文配布を対象外とする。**

```text
capture開始条件
= rights.status が rights-and-license-management.md の
  「personal_learning」ゲートを満たしていること
かつ 利用者が当該Kindle書籍の正当な利用者であることの申告があること
```

権利確認が未完了の状態でキャプチャセッションを`in_progress`にしない
(`rights-and-license-management.md`の`unverified`状態では
`personal_learning`のみ許可、それ以外は拒否のゲートに従う)。

### 5.6 状態遷移(Markdown表現)

```text
[not_started]
   ↓ (rights確認完了 + profile設定完了)
[ready]
   ↓ (キャプチャ開始)
[in_progress] --(ページ取得)--> [in_progress]
   ↓ (最終ページ確認)          ↓ (重複/抜け疑い検出)
[completed]                  [review_required]
   ↓ (中断/エラー)                 ↓ (人間確認)
[paused] --(resume)--> [in_progress]
```

`[review_required]`からは、人間確認後に`[in_progress]`または`[paused]`へ戻る。
`rights`未確認のまま`[ready]`へは遷移できない。

### 5.7 OCRタスクへの受け渡し

キャプチャ済みページ画像は、`ocr-and-scanned-pdf.md`の入力形式
(`sources/originals/<source_id>/page-XXXX.png`)へそのまま渡せる構成にする。

```json
{
  "source_id": "kindle-book-001",
  "capture_session_ref": "kindle-win-default-2026-07-19",
  "pages": [
    {"page_index": 41, "image_path": "sources/originals/kindle-book-001/page-0041.png"}
  ],
  "handoff_to": "ocr-and-scanned-pdf"
}
```

## 6. 入力

- 利用者が正当な権利を持つKindle書籍
- rights確認結果(`rights-and-license-management.md`のゲート判定)
- キャプチャprofile

## 7. 出力

- capture profile例(5.2節)
- page manifest例(5.3節)
- 状態遷移(5.6節)
- OCRタスクへの受け渡しmanifest(5.7節)

## 8. 正常系

1. 利用目的・権利確認を完了する(rights.statusゲート通過)。
2. キャプチャprofileを設定する。
3. ページ単位でキャプチャし、manifestとcheckpointを更新する。
4. 重複・抜けを検出し、疑いがあれば人間確認へ送る。
5. 最終ページまで完了したら`completed`にする。
6. OCRタスクへページ画像manifestを渡す。

## 9. 異常系

| ケース | 扱い |
|---|---|
| rights未確認のままキャプチャ開始しようとする | `blocked` |
| DRM回避を要求される | `blocked`(対象外) |
| ページ送り失敗 | 現在ページで一時停止(`paused`)、再開可能 |
| 重複ページ疑い | `review_required` |
| ページ抜け疑い | `review_required` |
| キャプチャ範囲設定が画面と一致しない | `blocked`、profile再設定要求 |

## 10. バリデーション

- `capture_session.status`が`in_progress`のとき、対応する`rights.status`が
  `personal_learning`許可状態である。
- 全ページの`image_hash`が記録されている。
- `last_confirmed_page`が実際に確認済みのページを指している。

## 11. テスト観点

- ページ順を保って画像を保存できる(mock環境での状態機械テストとして検証可能)。
- 重複と抜けを検出できる(hash比較ロジックの単体テスト)。
- 途中から安全に再開できる(checkpoint復元テスト)。
- 権利確認なしに`in_progress`へ遷移しない。
- DRM検出時に`blocked`のまま進まない。

これらはロジック(状態機械・hash比較・manifest検証)の単体テストとして
実装可能であり、実際のKindleアプリ操作を必要としない。
実機での自動操作テストは、本タスクでは実施しない別タスクとする。

## 12. 移行・互換性

- 現行実装からの移行対象なし。
- 出力(page画像)は`ocr-and-scanned-pdf.md`の入力形式と互換にする。

## 13. 未決定事項

- 実際のウィンドウ座標・zoom・キャプチャ範囲の値(実環境確認が必要)
- ページ送り方法の具体的な実装(キーボード操作かクリックか)
- Kindleアプリのバージョン依存による表示崩れへの対応
- macOS/他プラットフォーム対応の要否
- 自動操作ツール(該当する場合)の選定

## 14. 完了条件

- [x] ページ順を保って画像を保存できる設計になっている。
- [x] 重複と抜けを検出できる設計になっている。
- [x] 途中から安全に再開できる設計になっている。
- [x] 権利確認なしに正式処理へ進まない(5.5, 5.6節)。
- [x] 出力ドラフトが存在する。
- [x] 未実測・未確認事項が明記されている(5.2, 13節)。
- [x] 人間承認済みと偽っていない。
- [x] 実装コードを変更していない。
- [x] 夜間はブラウザ・Kindle・画面操作を行っていない。

## 15. 停止・保留条件(該当状況、本書の状態を`human_review_required`とする理由)

- 利用目的・権利確認の運用が(タスク08ドラフトの人間承認を経て)確定していない。
- 実環境の画面・操作条件が不明であり、profileの具体値を断定できない。

これらの理由により、本書は`review`ではなく`human_review_required`として提出する。
自動操作の実装・実行には、権利確認プロセスの人間承認と実環境確認が必要である。
