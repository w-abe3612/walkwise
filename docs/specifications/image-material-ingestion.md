---
spec_id: image-material-ingestion
title: "カメラ写真・スキャナ画像の資料入力仕様"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
requested_source_dump: "audio_book_creation_dump_2026-07-19_012222.txt"
available_baseline_dump: "audio_book_creation_dump_2026-07-19_005824.txt"
spec_refs:
  - 00-specification-guidelines.md
  - 01-common-identifiers-and-versioning.md
  - 02-process-input-output.md
  - 17-file-based-data-persistence-policy.md
  - 18-ai-model-routing-and-cost-control.md
---

# カメラ写真・スキャナ画像の資料入力仕様

## 1. 目的

カメラで撮影した書籍・ノート・配布資料・ホワイトボード等の写真、
およびフラットベッドスキャナ、シートフィードスキャナ、
スキャンアプリ等で保存した画像ファイルを、
資料入力パイプラインの正式な原資料として登録する方法を定義する。

本仕様は画像から本文を認識するOCRエンジンの最終選定ではなく、
画像を失わず、順序・出所・品質・権利・加工履歴を追跡可能な状態で
OCR工程へ渡すまでを確定する。

## 2. 重要な区別

資料の使い方と物理形式を分離する。

```text
source_strategy
＝ open_fulltext / hybrid_reconstruction / licensed_reference

media_type
＝ text / pdf / epub / image_sequence / kindle_capture / ...

acquisition_method
＝ camera_photo / flatbed_scanner / sheetfed_scanner /
   mobile_scan_app / existing_image_file
```

カメラ写真やスキャナ画像は新しい`source_strategy`ではない。

同じ画像資料でも、権利状態と用途により
`open_fulltext`、`hybrid_reconstruction`、`licensed_reference`
のいずれにもなり得る。

## 3. 対象範囲

- ローカル画像ファイルの登録
- 複数画像を一つの資料へまとめる処理
- ページ順序
- 一ページ画像と見開き画像
- 原画像と補正画像の分離
- ファイルhash
- 重複・欠番候補
- 回転、傾き、台形歪み、影、反射、ぼけ、切れの記録
- EXIF等の付随情報
- OCR工程への引渡し
- 画像単位の再処理
- 権利・利用目的・プライバシー確認
- カメラ写真とスキャナ画像の共通manifest

## 4. 対象外

- OCRエンジンの最終決定
- OCR信頼度の最終閾値
- 数式、コード、表、図の意味的な最終確定
- AIによる画像内容の事実認定
- 著作権・利用規約上の利用可否の自動保証
- 撮影禁止場所での撮影を許可する判断
- 人物の肖像、会話、個人情報を自動的に公開可能と判断すること
- 動画、YouTube、授業録音
- クラウドストレージからの自動収集

動画と録音は`docs/spec-proposals/`の将来案として別管理する。

## 5. 対応形式

### 5.1 初期必須形式

- PNG
- JPEG / JPG
- TIFF / TIF

### 5.2 任意アダプター形式

- WebP
- HEIC / HEIF
- BMP
- 複数ページTIFF

任意形式は、利用可能なdecoderが存在するときだけ受け入れる。

読めない形式を拡張子だけで判定してはならない。

### 5.3 OCR用標準派生形式

OCRへ渡す標準派生画像はPNGとする。

```yaml
ocr_derivative:
  format: png
  preserve_original_dimensions: true
  color_mode: source_dependent
```

JPEG等の原画像をPNGへ変換しても、
元JPEGを削除または上書きしてはならない。

## 6. 保存構成

```text
data/library/<project_id>/sources/
├─ originals/
│  └─ <source_id>/
│     └─ images/
│        ├─ original-000001.jpg
│        └─ original-000002.tif
├─ preprocessed/
│  └─ <source_id>/
│     └─ pages/
│        ├─ page-000001.png
│        └─ page-000002.png
├─ manifests/
│  ├─ <source_id>-image-source.yaml
│  └─ <source_id>-image-ingestion-session.json
└─ reports/
   └─ <source_id>-image-quality-report.json
```

`originals/`はimmutableとする。

回転、切り抜き、台形補正、見開き分割、
色補正、ノイズ除去は`preprocessed/`へ保存する。

## 7. Image source metadata

```yaml
schema_version: "1.0"
source_id: database-book-photos
content_revision: 1
title: データベース書籍 撮影画像
source_strategy:
  - licensed_reference

media:
  type: image_sequence
  acquisition_method: camera_photo
  page_representation: mixed
  original_mime_types:
    - image/jpeg

rights:
  status: user_asserted_private_use
  usage_purpose: personal_learning

privacy:
  contains_people: false
  contains_personal_information: unknown
  exif_location_present: unknown

original:
  path: sources/originals/database-book-photos/images/
  manifest_path: sources/manifests/database-book-photos-image-ingestion-session.json
```

`page_representation`は次のいずれかとする。

```text
single_page
two_page_spread
mixed
non_page_image
```

## 8. 取り込みセッション

複数画像の順序と処理状態をJSON manifestで管理する。

状態:

```text
not_started
importing
review_required
ready_for_ocr
completed
failed
cancelled
```

一つの画像を取り込んだだけでは、
資料全体の順序が確定したとはみなさない。

## 9. ページ順序

初期順序候補は次から決める。

1. 利用者が指定したmanifest順
2. 明示的な連番ファイル名
3. scannerが記録した順序
4. 撮影日時
5. 自然順ソートしたファイル名

4と5だけで正式順序を確定する場合は、
人間プレビューを必須とする。

画像ファイルのOS上の列挙順をページ順として使用してはならない。

## 10. カメラ写真固有の処理

カメラ写真では次を検査する。

- 回転
- 傾き
- 台形歪み
- ページ湾曲
- 見開き中央の影
- 指、クリップ、机等の写り込み
- 反射、光沢、白飛び
- 影
- ぼけ、手ぶれ
- ページ端の欠落
- 背景と本文領域の分離
- 同一ページの再撮影
- EXIF orientation

補正は派生画像へ行う。

原画像を自動補正画像で置き換えてはならない。

見開き分割では、元画像座標をlocatorへ保存する。

```yaml
derived_page:
  page_index: 12
  original_image_id: image-000008
  crop:
    x: 0
    y: 0
    width: 1500
    height: 2200
  spread_side: left
```

## 11. スキャナ画像固有の処理

スキャナ画像では次を記録する。

- scanner種別
- 公称DPI
- color mode
- simplex / duplex
- 自動傾き補正の有無
- 自動余白除去の有無
- 裏写り補正の有無
- scannerソフトウェア名・版を取得できる場合
- 表裏順序
- blank page候補

自動blank page判定だけで画像を削除してはならない。

白紙候補としてmanifestへ残す。

## 12. 原画像の付随情報

EXIF等のmetadataを原画像から読み取れる場合は、
次を区別する。

```text
preserved_private_metadata
＝ 原資料追跡のために内部保持してよい情報

exportable_metadata
＝ 後続成果物へ渡してよい情報
```

GPS等の位置情報は既定で`exportable_metadata`へ含めない。

人物、住所、学生名、社員名、受講者名等が写り込む可能性がある場合、
`privacy_review_required`を設定する。

## 13. 品質判定

### Error

- ファイルを画像として開けない
- 0 byte
- hash計算失敗
- 同じ`image_id`が重複
- `page_index`が重複
- originalを上書きしようとした
- manifestと実ファイルが一致しない

### Warning

- 低解像度
- 回転候補
- 傾き
- ぼけ
- 影
- 反射
- ページ端の切れ
- 見開き未分割
- EXIF位置情報
- 順序が撮影日時またはファイル名推定のみ
- blank page候補
- duplicate候補

### Review required

- 読めない本文領域がある
- ページ順序を一意に決められない
- 一画像に三ページ以上が含まれる
- 同じページの異なる撮影を自動選択できない
- 人物・個人情報が含まれる可能性
- 図表や数式が撮影条件により欠けている
- 権利・利用目的が未確認

## 14. OCRへの引渡し

OCR工程へ渡す単位は派生ページ画像とする。

```json
{
  "source_id": "database-book-photos",
  "page_index": 12,
  "image_id": "image-000008-left",
  "original_image_id": "image-000008",
  "image_path": "sources/preprocessed/database-book-photos/pages/page-000012.png",
  "original_hash": "sha256:...",
  "derivative_hash": "sha256:...",
  "acquisition_method": "camera_photo",
  "quality_flags": [
    "perspective_corrected"
  ],
  "review_status": "ready_for_ocr"
}
```

OCR結果は画像manifestを上書きせず、
抽出結果として別保存する。

## 15. 権利・利用目的

自分で撮影・スキャンしたことは、
本文の著作権または再配布権を保有することを意味しない。

最低限次を記録する。

- 原資料の種類
- 利用者が原資料を利用できる根拠
- 利用目的
- 公開予定の有無
- 第三者の個人情報・肖像の有無
- 人間確認者
- 確認日時

権利未確認の画像は、個人学習以外の出力へ自動的に使用してはならない。

## 16. AI利用

AIは次に使用できる。

- 回転・本文領域・見開き候補の提案
- OCR後の低リスクな形式整理
- 画像品質warning候補の提示

AIだけで次を確定してはならない。

- 法的利用可否
- 欠落ページが存在しないこと
- 図表・数式・コードの意味
- 個人情報が存在しないこと
- 低品質画像から復元した本文の正確性

AIへ送信する場合、原画像送信の権利・プライバシー確認を行う。

## 17. テスト観点

### 自動テスト

- PNG、JPEG、TIFFを登録できる
- 壊れた画像を拒否する
- 自然順ソート
- 明示manifest順を優先する
- `page_index`重複を拒否する
- hashを保存する
- originalを上書きしない
- 見開き分割後も元座標へ戻れる
- duplicate候補を記録する
- blank page候補を削除しない
- EXIF位置情報をexportしない
- OCR handoffを生成できる

### 人間確認用サンプル

- スマートフォン写真
- 台形歪みのある写真
- 見開き写真
- 反射のある写真
- フラットベッドスキャン
- 両面scanner出力
- 縦書き
- 横書き
- 数式
- コード
- 表
- 手書きノート

## 18. 移行・互換性

既存のKindleページ画像は`acquisition_method: kindle_capture`として扱い、
カメラ・スキャナ画像と同一のOCR入力interfaceへ渡してよい。

ただしKindle capture sessionの正本は
`kindle-capture.md`のmanifestであり、
本仕様の画像取り込みsessionへ無断変換して上書きしない。

旧`data/library/<book_id>/pages/`の画像を読み込む場合は、
`legacy_input: true`、旧パス、import日時、hashを記録する。

## 19. 未決定事項

仕様確定を妨げる未決定事項はない。

次は実装またはprofile単位の調整値とする。

- ぼけ・傾き・反射の具体的閾値
- perceptual hashの距離
- HEIC decoder
- scanner固有metadataの取得範囲
- 自動見開き分割アルゴリズム
- 自動台形補正アルゴリズム

これらは実測後にprofileへ保存し、
本仕様を変更せず調整できるようにする。

## 20. 完了条件

- カメラ写真とスキャナ画像を正式な資料形式として登録できる。
- source strategyとmedia typeが分離されている。
- 原画像がimmutableである。
- 補正画像が派生物として保存される。
- ページ順序をmanifestで管理できる。
- 見開きから元画像座標へ戻れる。
- 重複、欠番、低品質候補を記録できる。
- EXIF位置情報を無断で後続へ渡さない。
- 権利・利用目的・プライバシーを記録する。
- OCR結果が原画像を上書きしない。
- 画像単位で再処理できる。
