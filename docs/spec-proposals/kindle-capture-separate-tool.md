---
spec_id: kindle-capture-separate-tool
title: "Kindle画面キャプチャ(専用ツール案・本体対象外)"
status: draft
version: "0.3"
last_updated: "2026-07-19"
superseded_specs:
  - "docs/specifications/kindle-capture.md (旧v1.0、本体承認済み仕様として撤回)"
merged_from:
  - "docs/specifications/kindle-capture.md (v1.0)"
  - "docs/spec-proposals/generated-specifications/kindle-capture.md (v0.1, status: human_review_required)"
spec_refs:
  - ../specifications/19-application-scope-and-mvp.md
  - ../specifications/image-material-ingestion.md
---

# Kindle画面キャプチャ(専用ツール案・本体対象外)

## 0. 位置付け(最重要)

- **本機能はWalkwise本体(Electronデスクトップアプリ)の対象外である。**
  `docs/specifications/19-application-scope-and-mvp.md` 5.4節・5.6節のとおり、
  本体はKindleアプリの操作、座標、ページ送りを一切認識しない。
- 本機能は、将来的に**専用ツールまたは別ブランチ・別リポジトリへ移管予定**である。
  ブランチ名・リポジトリ名は本書時点で未確定であり、断定しない。
- 本タスク(docs再編)では、別ブランチやリポジトリの作成・checkoutを行っていない。
- 本体との接続点は、専用ツールが生成する**ページ画像sequenceとcapture manifestのみ**である。
  本体は`image-material-ingestion.md`の一般的な画像入力契約(`acquisition_method: kindle_capture`)
  としてこれを受け取るだけであり、専用ツールの内部実装・状態機械・画面操作を関知しない。
- DRMの解除、回避、解析は、本体・専用ツールのいずれにおいても対象外である。

本書は、旧`docs/specifications/kindle-capture.md`(v1.0、承認済みだった本体機能仕様)と、
`docs/spec-proposals/`側で生成されていた同名ドラフト(`status: human_review_required`)を
統合し、専用ツール側で今後検討する未承認案としてまとめたものである。

## 1. 目的

利用者が正当に閲覧できるKindle書籍の表示画面を、Windows上でページ単位の画像として
取得し、再開可能なmanifestを作成して、後続のOCR処理へ安全に引き渡す**専用ツール**の
仕様候補を記録する。

旧版オーディオブック作成ツールに存在したKindle操作、画面キャプチャ、ページ送り、
試し撮り、設定読込の実装を移行元として再利用する候補とするが、座標や待機時間を
全環境共通値として固定せず、環境別のcapture profileとして扱う方針は維持する。

## 2. 対象範囲(専用ツール側)

- Windows上のKindle for PC
- 利用者が最前面へ表示した書籍画面
- キャプチャ範囲とページ送り方法のprofile化
- 1ページ試し撮り
- ページ単位PNG保存
- capture sessionとcheckpoint
- 中断後の再開
- ページ送り成功確認
- 完全一致・近似一致による重複候補検出
- ページ抜け候補の記録
- 本体(Walkwise)のOCR処理へのmanifest引渡し
- 旧版実装・設定・出力の段階移行(専用ツール側での検討)

## 3. 対象外

- DRMの解除、回避、解析
- Kindleコンテンツファイルの直接抽出
- Amazonアカウントへの自動ログイン
- 書籍の購入や取得の自動化
- 利用規約や著作権上の利用可否をシステムが保証すること
- キャプチャした本文や音声の自動公開
- macOS、Linux、Web版Kindleへの初期対応
- OCR精度、OCRエンジン、AI補正の最終仕様(本体`image-material-ingestion.md`側の対象)
- ページ画像から得た内容の事実確認
- **Walkwise本体への統合、本体コードへの組み込み**

## 4. 現行実装と移行元実装

### 4.1 現行リポジトリ

現行リポジトリ(本体Walkwise)にKindleキャプチャ実装は存在しない。今後、
専用ツールを別リポジトリまたは別ブランチとして作成する場合、旧版実装を
参照して移植することを検討する(本タスクではブランチ作成・checkoutを行っていない)。

### 4.2 旧版リポジトリ

旧版には次が存在する(移行元候補としての記録)。

- `config/capture_settings.json`
- `script/utility/capture_settings.py`
- `script/utility/kindle_operation/get_kindle_region.py`
- `script/utility/kindle_operation/goto_page_step.py`
- `script/utility/kindle_operation/move_cursor_to_next_page_click.py`
- `script/utility/kindle_operation/test_capture_page.py`
- `script/utility/kindle_operation/check_mouse_position.py`
- `script/capture_ocr_tts.py`
- `tests/test_kindle_operation_imports.py`
- ページ単位の画像・OCR結果・補正済みテキスト

旧版実装は次の技術を使用する。

- `pyautogui`
- `pygetwindow`
- Pillow
- Tesseract OCR

旧版実装および生成済みページ群は、方式の採用根拠と回帰テスト資材の候補として
使用できるが、旧版の動作実績だけを根拠に、現在のWindows、Kindleアプリ、
モニター構成でも動作するとみなしてはならない。

## 5. 基本原則(専用ツール側で維持すべき原則)

### 5.1 利用者操作を開始条件とする

利用者は次を実施しなければならない。

- 自分が利用できるKindleアカウントでログインする。
- 対象書籍を自分で開く。
- キャプチャ開始ページを表示する。
- 利用目的を記録する。
- 権利・規約上の確認が必要な場合は自分で確認する。

専用ツールは、利用者が開いた表示画面に対する操作だけを行う。

### 5.2 DRM回避を行わない

専用ツールは画面キャプチャ方式だけを対象とする。Kindle内部ファイルの復号、
抽出、保護機構の回避を行ってはならない。

### 5.3 キャプチャとOCRを分離する

正式な処理順は次のとおりとする。

```text
Kindle画面 (専用ツール)
↓
ページ画像 (専用ツール)
↓
capture manifest (専用ツール)
↓
=== 本体Walkwiseとの境界 ===
↓
OCR (本体、image-material-ingestion.md経由)
↓
OCR raw
↓
normalized
↓
structured
```

専用ツール側のキャプチャ工程は、ページ画像とcapture manifestを作成した時点で
終了する。OCR、文字補正、AI補正は本体側の責務であり、専用ツールの
キャプチャ成功条件へ含めない。

### 5.4 原画像を上書きしない

確認済みのページ画像は原資料相当の成果物として扱う。OCR結果、画像前処理結果、
AI補正結果でページ画像を上書きしてはならない。

### 5.5 内部連番と表示ページを分ける

`page_index`はキャプチャセッション内の安定した連番である。Kindle画面に
表示されるページ番号、位置番号、章名と同一視してはならない。

```yaml
page_index: 42
displayed_page_label: "35"
kindle_location: null
chapter_label: "第2章"
```

## 6. 初期対象環境(専用ツール側)

```yaml
target_environment:
  os: windows
  application: kindle_for_pc
  interaction:
    - mouse_click
    - keyboard
  capture_library: pyautogui
  window_detection_library: pygetwindow
```

Kindleアプリの特定バージョンは固定しない。実行時にアプリのバージョンを
取得できる場合はmanifestへ記録する。取得できない場合は`null`を許容する。

## 7. Capture profile

環境別capture profileの正本は専用ツール側のYAMLとする(本体のDB・ファイル正本には含めない)。

必須項目候補: `schema_version`、`profile_id`、`target.os`、`target.application`、
`capture_region`、`page_turn.method`、`page_turn.wait_seconds`、
`verification.smoke_test_status`。

旧版設定値は`kindle-win-legacy-2200x1900`という参考profileへ変換してよいが、
現在環境での1ページ試し撮りに合格するまで使用可能状態にしてはならない。
実際の座標・zoom・キャプチャ範囲の値は、専用ツールの実環境確認が必要であり、
本書時点では`null`のまま構造だけを示す(未確定値を断定しない)。

## 8. 実行前確認(専用ツール側)

キャプチャ開始前に次を確認する。

1. 利用目的が記録されている。
2. DRM回避を行わない方式である。
3. capture profileが読み込める。
4. キャプチャ領域が画面内に収まる。
5. ページ送り位置が画面内に収まる。
6. Kindleウィンドウが検出できる、または利用者が手動で最前面へ移動した。
7. 1ページ試し撮りが成功した。
8. 試し撮り画像を利用者が確認した。
9. 出力先に書き込み可能である。
10. 既存セッションへ上書きしない。

権利・利用目的に関する記録がない場合、capture sessionを`ready`または
`in_progress`へ遷移させてはならない。

## 9. Capture session(専用ツール側)

### 9.1 状態

```text
not_started
ready
in_progress
paused
review_required
completed
failed
cancelled
```

### 9.2 状態遷移

```text
not_started
  ↓ 実行前確認完了
ready
  ↓ 開始
in_progress
  ├─ 中断 → paused
  ├─ 重複・抜け疑い → review_required
  ├─ 復旧不能エラー → failed
  ├─ 利用者中止 → cancelled
  └─ 終端確認 → completed

paused
  └─ checkpoint確認 → in_progress

review_required
  ├─ 再取得 → in_progress
  ├─ 問題なしと人間確認 → in_progress
  └─ 中止 → cancelled
```

### 9.3 checkpoint

セッションは、最後に確認済みのページを保持する。未確認ページが存在する場合、
単純に`last_confirmed_page_index + 1`から開始せず、未確認ページを再取得する。

## 10. ページ取得処理(専用ツール側)

```text
画面をキャプチャ
↓
一時ファイルへPNG保存
↓
PNGとして読めることを検証
↓
SHA-256を計算
↓
直前ページと比較
↓
正式ページパスへatomic replace
↓
page recordをmanifestへ追加
↓
manifestをatomic replace
↓
ページ送り
↓
画面変化を確認
```

正式なページファイルが存在する場合、確認なしに上書きしてはならない。

## 11. ページ送りと重複・抜け検出(専用ツール側)

初期実装候補は`click`と`key`の2方式とする。ページ送り後、待機時間だけを
根拠に成功扱いせず、SHA-256・perceptual hash・必要に応じた低解像度差分で
画面変化を確認する。完全一致はページ送り失敗候補、近似一致は
固定ヘッダーやアニメーションの影響を考慮したwarningとする。

重複候補: 連続ページのSHA-256一致、perceptual hash距離が閾値以下、
OCR表示ページ番号の不連続、前後本文連続性の不自然さ。SHA-256一致は
強い証拠として扱うが、他の兆候だけでは自動削除・自動確定しない。

抜け候補: 表示ページ番号の飛び、章・節見出しの連続性喪失、OCR後の
前後本文非接続、`page_index`欠番、複数ページ進んだ可能性。
抜け候補は`review_required`へ送り、人間確認または再キャプチャを要求する。

## 12. 本体WalkwiseへのOCR引渡し(境界の定義)

専用ツールが本体へ渡すのは次だけとする。

- `source_id`
- `capture_session_id`(専用ツール側の識別子。本体のJob/Source IDとは独立)
- `page_index`
- `image_path`
- `image_hash`
- 表示ページ情報
- warning

本体は、この引渡し情報を`image-material-ingestion.md`の一般的な画像sequence
契約(`acquisition_method: kindle_capture`)として受け取り、専用ツールの
内部状態・座標・操作ログを一切保持しない。OCR結果は専用ツール側の
capture manifestのページ画像情報を上書きしない。

## 13. エラーと警告(専用ツール側)

### Error

- profileが不正
- キャプチャ領域が画面外
- 出力先へ書き込めない
- PNG保存または読込検証失敗
- manifestのJSONが不正
- 同じ`page_index`へ異なる画像を無断上書き
- 利用目的がない状態で開始
- DRM回避を要求する処理
- checkpointとページ記録が矛盾

### Warning

- Kindleウィンドウの自動検出失敗
- Kindleアプリバージョン不明
- perceptual hashが近似
- 表示ページ番号を取得できない
- OCRによる本文連続性確認が未実施
- legacy profileを現在環境で未確認
- 画面テーマやフォントがprofileと一致しない可能性

## 14. テスト観点(専用ツール側)

- capture profileの読込、camelCase旧設定からsnake_caseへの変換
- 座標計算、画面外判定、ページ送り位置計算
- session状態遷移、checkpoint
- SHA-256比較、perceptual hash判定
- manifest追加、duplicate候補、gap候補
- atomic保存失敗、既存ページ衝突
- OCR handoff生成(本体との境界契約)
- 旧CLI wrapperのimport

実機でのKindleウィンドウ検出・試し撮り・連続取得・中断再開・クリック/キー方式は
手動スモークテストとする。

## 15. 未決定事項

- 実際の運用主体(専用ツールとして独立配布するか、別ブランチとして本体リポジトリ内に
  留めるか)
- ブランチ名・リポジトリ名(未確定であり本書では断定しない)
- 現在環境の具体的な画面座標、Kindleアプリバージョン、monitor scale
- 表示倍率・フォント・テーマ、ページ送り待機時間
- perceptual hashの閾値
- クリック方式とキー方式の優先順位
- 権利・利用規約確認プロセスの最終運用(旧ドラフトが`human_review_required`とした理由)

これらは専用ツール側の実環境確認・1ページ試し撮り・スモークテスト、および
運用主体の人間判断によって解消される。

## 16. 昇格条件(専用ツールとして仕様化する場合)

- 運用主体(別リポジトリ/別ブランチ/独立配布)が人間により決定されている。
- Windows版Kindleを対象とし、旧版実装の移行元範囲が明確である。
- 旧版設定を環境別profileへ変換できる。
- キャプチャとOCRが分離されている。
- 原画像が上書きされない。
- ページ順をmanifestで管理できる。
- ページ送り成功を画像変化で確認する。
- 重複・抜け候補を記録できる。
- 中断後にcheckpointから再開できる。
- 既存ページを無断上書きしない。
- 権利・利用目的の記録なしに処理を開始しない。
- DRM回避を対象外としている。
- 本体Walkwiseとの接続が画像sequenceとmanifestのみに限定されている。
- 本体側のコード・仕様に依存を作らない(本体は専用ツールの存在を知らなくても動作する)。

## 17. 人間レビュー項目

- `human_review_required`: 専用ツールの運用主体(独立リポジトリか別ブランチか)。
- `human_review_required`: 権利・利用規約確認プロセスの最終運用。
- `human_review_required`: 実環境確認前の座標・profile値。
