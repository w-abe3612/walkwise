---
spec_id: kindle-capture
title: "Kindle画面キャプチャ仕様"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
current_source_dump: "audio_book_creation_dump_2026-07-19_005824.txt"
legacy_source_dump: "audio_book_creation_dump_2026-07-18_193603.txt"
---

# Kindle画面キャプチャ仕様

## 1. 目的

利用者が正当に閲覧できるKindle書籍の表示画面を、
Windows上でページ単位の画像として取得し、再開可能なmanifestを作成して、
後続のOCR処理へ安全に引き渡す仕様を定義する。

旧版オーディオブック作成ツールに存在したKindle操作、
画面キャプチャ、ページ送り、試し撮り、設定読込の実装を
移行元として再利用する。

旧版の座標や待機時間を全環境共通値として固定せず、
環境別のcapture profileとして扱う。

## 2. 対象範囲

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
- OCR処理へのmanifest引渡し
- 旧版実装・設定・出力の段階移行

## 3. 対象外

- DRMの解除、回避、解析
- Kindleコンテンツファイルの直接抽出
- Amazonアカウントへの自動ログイン
- 書籍の購入や取得の自動化
- 利用規約や著作権上の利用可否をシステムが保証すること
- キャプチャした本文や音声の自動公開
- macOS、Linux、Web版Kindleへの初期対応
- OCR精度、OCRエンジン、AI補正の最終仕様
- ページ画像から得た内容の事実確認

## 4. 現行実装と移行元実装

### 4.1 現行リポジトリ

現行リポジトリにはKindleキャプチャ実装が存在しない。

本仕様の承認後、旧版実装を参照して現行の資料入力パイプラインへ移植する。

### 4.2 旧版リポジトリ

旧版には次が存在する。

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

旧版の実装および生成済みページ群は、
方式の採用根拠と回帰テスト資材として使用する。

ただし、旧版の動作実績だけを根拠に、
現在のWindows、Kindleアプリ、モニター構成でも動作するとみなしてはならない。

## 5. 基本原則

### 5.1 利用者操作を開始条件とする

利用者は次を実施しなければならない。

- 自分が利用できるKindleアカウントでログインする。
- 対象書籍を自分で開く。
- キャプチャ開始ページを表示する。
- 利用目的を記録する。
- 権利・規約上の確認が必要な場合は自分で確認する。

本機能は、利用者が開いた表示画面に対する操作だけを行う。

### 5.2 DRM回避を行わない

本機能は画面キャプチャ方式だけを対象とする。

Kindle内部ファイルの復号、抽出、保護機構の回避を行ってはならない。

### 5.3 キャプチャとOCRを分離する

正式な処理順は次とする。

```text
Kindle画面
↓
ページ画像
↓
capture manifest
↓
OCR
↓
OCR raw
↓
normalized
↓
structured
```

キャプチャ工程は、ページ画像とcapture manifestを作成した時点で終了する。

OCR、文字補正、AI補正をキャプチャ成功条件へ含めてはならない。

### 5.4 原画像を上書きしない

確認済みのページ画像は原資料相当の成果物として扱う。

OCR結果、画像前処理結果、AI補正結果でページ画像を上書きしてはならない。

### 5.5 内部連番と表示ページを分ける

`page_index`はキャプチャセッション内の安定した連番である。

Kindle画面に表示されるページ番号、位置番号、章名と同一視してはならない。

```yaml
page_index: 42
displayed_page_label: "35"
kindle_location: null
chapter_label: "第2章"
```

## 6. 初期対象環境

初期実装は次に限定する。

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

Kindleアプリの特定バージョンは固定しない。

実行時にアプリのバージョンを取得できる場合はmanifestへ記録する。
取得できない場合は`null`を許可する。

## 7. Capture profile

### 7.1 正本

環境別capture profileの正本はYAMLとする。

推奨保存先:

```text
data/library/<project_id>/sources/manifests/capture-profiles/<profile_id>.yaml
```

### 7.2 必須項目

- `schema_version`
- `profile_id`
- `target.os`
- `target.application`
- `capture_region`
- `page_turn.method`
- `page_turn.wait_seconds`
- `verification.smoke_test_status`

### 7.3 任意項目

- ウィンドウタイトルの検索語
- 表示倍率
- フォント
- テーマ
- Kindleアプリバージョン
- モニター情報
- OCRで読み取るページ番号領域
- キー入力設定
- クリック位置
- focus用クリック位置

### 7.4 旧版profile

旧版の設定値は`kindle-win-legacy-2200x1900`という
参考profileへ変換してよい。

```yaml
capture_region:
  left: 0
  top: 0
  width: 2200
  height: 1900

page_turn:
  method: click
  click:
    offset_x_from_right: 80
    offset_y_from_center: 80
```

この値は旧環境の参考値であり、
現在環境での1ページ試し撮りに合格するまで使用可能状態にしてはならない。

## 8. 実行前確認

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

権利・利用目的に関する記録がない場合、
capture sessionを`ready`または`in_progress`へ遷移させてはならない。

## 9. Capture session

### 9.1 正本

capture sessionの正本はJSONとする。

推奨保存先:

```text
data/library/<project_id>/sources/manifests/<source_id>-capture-session.json
```

### 9.2 状態

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

### 9.3 状態遷移

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

### 9.4 checkpoint

セッションは、最後に確認済みのページを保持する。

```yaml
last_confirmed_page_index: 41
next_page_index: 42
```

未確認ページが存在する場合、
単純に`last_confirmed_page_index + 1`から開始せず、
未確認ページを再取得する。

## 10. ページ取得処理

1ページの取得は次の順序で行う。

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

正式なページファイルが存在する場合、
確認なしに上書きしてはならない。

## 11. ページ送り

### 11.1 対応方式

初期実装は次をサポートする。

- `click`
- `key`

旧版との互換性のため、`click`を初期候補とする。

環境によってクリックが不安定な場合は、profileで`key`へ変更できる。

### 11.2 ページ送り成功確認

ページ送り後、待機時間だけを根拠に成功扱いしてはならない。

最低限、ページ送り前後の画像について次を比較する。

- SHA-256
- perceptual hash
- 必要に応じて低解像度差分

完全一致の場合はページ送り失敗候補とする。

近似一致の場合は、
固定ヘッダーやアニメーションの影響を考慮してwarningとする。

### 11.3 再試行

ページ送り失敗時はprofileの上限まで再試行できる。

```yaml
retry:
  max_attempts: 3
  backoff_seconds: 1.0
```

上限超過時は`paused`または`review_required`へ遷移する。

自動的に次の`page_index`へ進めてはならない。

## 12. 重複・抜け検出

### 12.1 重複候補

次のいずれかに該当した場合、重複候補とする。

- 連続ページのSHA-256が一致する。
- perceptual hashの距離がprofileの閾値以下である。
- OCRされた表示ページ番号が連続していない。
- 前後ページの本文連続性が著しく不自然である。

SHA-256一致は強い証拠として扱う。

perceptual hash、OCRページ番号、本文連続性だけでは
自動削除または自動確定してはならない。

### 12.2 抜け候補

次を抜け候補とする。

- 表示ページ番号に飛びがある。
- 章・節見出しの連続性が失われている。
- OCR後の前後本文が接続しない。
- セッションmanifestに`page_index`の欠番がある。
- ページ送り時に複数ページ進んだ可能性がある。

抜け候補は`review_required`へ送り、
人間確認または対象範囲の再キャプチャを要求する。

## 13. 出力

### 13.1 ページ画像

```text
data/library/<project_id>/sources/originals/<source_id>/pages/page-000001.png
```

ファイル名は内部`page_index`に基づく。

### 13.2 Capture manifest

各ページには最低限次を記録する。

```json
{
  "page_index": 1,
  "image_path": "sources/originals/book-001/pages/page-000001.png",
  "image_hash": {
    "algorithm": "sha256",
    "value": "..."
  },
  "perceptual_hash": null,
  "captured_at": "2026-07-19T00:00:00+09:00",
  "capture_profile_id": "kindle-win-legacy-2200x1900",
  "displayed_page_label": null,
  "kindle_location": null,
  "chapter_label": null,
  "page_turn_attempts": 1,
  "status": "confirmed",
  "warnings": []
}
```

### 13.3 OCRへの引渡し

OCRへ渡すのは次だけとする。

- `source_id`
- `capture_session_id`
- `page_index`
- `image_path`
- `image_hash`
- 表示ページ情報
- warning

OCR結果をcapture manifestのページ画像情報へ上書きしてはならない。

## 14. エラーと警告

### 14.1 Error

- profileが不正
- キャプチャ領域が画面外
- 出力先へ書き込めない
- PNG保存または読込検証失敗
- manifestのJSONが不正
- 同じ`page_index`へ異なる画像を無断上書き
- 利用目的がない状態で開始
- DRM回避を要求する処理
- checkpointとページ記録が矛盾

### 14.2 Warning

- Kindleウィンドウの自動検出失敗
- Kindleアプリバージョン不明
- perceptual hashが近似
- 表示ページ番号を取得できない
- OCRによる本文連続性確認が未実施
- legacy profileを現在環境で未確認
- 画面テーマやフォントがprofileと一致しない可能性

### 14.3 Review required

- 重複候補
- ページ抜け候補
- ページ送り失敗が再試行上限へ到達
- 同じ表示ページ番号に異なる画像がある
- 章境界で本文連続性を判断できない
- 権利・利用目的の確認内容に疑義がある

## 15. 正常例

1. 利用者がKindle書籍を開く。
2. 利用目的を`personal_learning`として記録する。
3. legacy profileを読み込む。
4. 1ページ試し撮りを行う。
5. 利用者が領域と文字の視認性を確認する。
6. capture sessionを開始する。
7. ページをPNGとして保存する。
8. hashを計算してmanifestへ記録する。
9. ページ送り後の画面変化を確認する。
10. 中断時はcheckpointを保存する。
11. 再開時に未確認ページから再取得する。
12. 終端を利用者が確認して`completed`にする。
13. manifestをOCR工程へ渡す。

## 16. 異常例

### 16.1 ページ送り失敗

クリック後の画像が直前ページと完全一致した。

```text
再試行
↓
上限到達
↓
paused
```

同じ画面を次ページとして保存してはならない。

### 16.2 中断中の不完全ファイル

一時PNGだけが残り、manifestに記録されていない。

再開時に一時ファイルを検出し、
正式ページとして採用せず再取得する。

### 16.3 既存ページとの衝突

`page-000042.png`が存在し、
新しい画像のSHA-256が異なる。

自動上書きせず`review_required`とする。

### 16.4 権利記録なし

利用目的が未記録である。

sessionを`ready`へ進めず`blocked`相当として停止する。

## 17. テスト観点

### 17.1 通常pytest

画面操作を実行せず、次をテストする。

- capture profileの読込
- camelCase旧設定からsnake_caseへの変換
- 座標計算
- 画面外判定
- ページ送り位置計算
- session状態遷移
- checkpoint
- SHA-256比較
- perceptual hash判定
- manifest追加
- duplicate候補
- gap候補
- atomic保存失敗
- 既存ページ衝突
- OCR handoff生成
- 旧CLI wrapperのimport

### 17.2 手動スモークテスト

- Kindleウィンドウ検出
- 1ページ試し撮り
- カーソル位置確認
- 1ページ送り
- 10ページ連続取得
- 中断・再開
- クリック方式
- キー方式

### 17.3 回帰テスト

旧版で使用した次を回帰資材にする。

- `config/capture_settings.json`
- 旧ページ画像
- 旧ページ単位OCRテキスト
- Kindle操作モジュールのimportテスト

旧版の実データを新しい出力先へ自動移動してはならない。

## 18. 移行・互換性

### 18.1 旧設定

旧設定のcamelCaseを互換入力として読む。

```text
captureRegion
→ capture_region

nextPageClick
→ page_turn.click
```

新規保存はsnake_case YAMLとする。

### 18.2 旧コマンド

旧コマンドは移行期間中、薄いwrapperとして維持してよい。

新しい実体を呼び出し、
旧保存形式への書込みは互換オプションが明示された場合だけ許可する。

### 18.3 旧キャプチャ・OCR一体処理

旧版の`capture_ocr_tts.py`をそのまま移植してはならない。

次へ分割する。

```text
capture
→ image + capture manifest

ocr
→ OCR raw

normalization
→ normalized

AI correction
→ structured candidate
```

旧版の`clean_text`相当処理は、
キャプチャ工程ではなく正規化工程へ移す。

### 18.4 旧出力

旧版の次の出力は移行元として読み取ってよい。

```text
data/library/<book_id>/pages/<section>/page_XXXX.png
data/library/<book_id>/text/raw/<section>/page_XXXX.txt
```

移行時は次を行う。

- `source_id`を付与する。
- ページ画像のSHA-256を算出する。
- `page_index`を付与する。
- capture manifestを生成する。
- 旧ファイルを移動・削除しない。
- OCRテキストはページ画像とは別の派生物として登録する。

## 19. 未決定事項

仕様確定を妨げる未決定事項はない。

次は環境別profileまたは実装時の検証値であり、
本仕様の変更を必要としない。

- 現在環境の具体的な画面座標
- Kindleアプリバージョン
- monitor scale
- 表示倍率・フォント・テーマ
- ページ送り待機時間
- perceptual hashの閾値
- クリック方式とキー方式の優先順位

これらは1ページ試し撮りとスモークテストで決定し、
capture profileへ保存する。

## 20. 完了条件

- Windows版Kindleを初期対象としている。
- 旧版実装を移行元として再利用する範囲が明確である。
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
- 通常pytestと実画面スモークテストが分離されている。
- 旧出力を削除せず段階移行できる。
