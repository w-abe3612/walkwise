---
spec_id: epub-text-extraction
title: "EPUBテキスト抽出"
status: review
version: "0.1"
last_updated: "2026-07-19"
generated_by:
  type: ai
  note: "旧仕様策定タスク(完了・削除済み)により生成。Git履歴を参照。"
depends_on:
  - source-storage-and-common-schema.md
spec_refs:
  - source-storage-and-common-schema.md
---

# EPUBテキスト抽出(ドラフト)

## 1. 目的

EPUBのHTML本文、目次、ルビ、脚注、画像、メタデータを共通資料形式へ変換する
仕様を定義する。

## 2. 対象範囲

- 対応EPUBバージョンとDRMの扱い
- 本文の正式な読み順の決定方法
- 目次、ルビ、脚注、画像の保存方法
- CSS・装飾の扱い
- 章・節IDとsource locatorの生成規則

## 3. 対象外

- DRM回避
- EPUB以外の電子書籍形式(Kindle独自形式など。→タスク12はKindle画面キャプチャ経由)
- OCR(EPUBはテキストベースのため対象外)

## 4. 現行実装

現行コードにEPUB抽出の実装は存在しない。

## 5. 推奨仕様

### 5.1 対応EPUBとDRM

質問1への回答: **DRMなしEPUB 2/3を対象とし、DRM回避は対象外とする。**

```yaml
epub_support:
  versions:
    - "2.0"
    - "3.0"
  drm_handling: out_of_scope
  drm_detection: warn_and_skip
```

DRM付きEPUBを検出した場合、処理を行わず`blocked`として人間へ報告する。

### 5.2 本文の読み順

質問2への回答: **package documentのspineを本文順の正本とし、
nav/NCXは見出しと目次の補助にする。**

```text
container.xml
↓ (rootfileを特定)
package document (.opf)
↓ (spineのitemref順)
本文順序の正本
```

`nav.xhtml`(EPUB3)または`toc.ncx`(EPUB2)は、章タイトル・見出し階層の
補助情報として使用し、spineと矛盾する場合はspineを優先する。
矛盾が大きく人間判断なしに順序を確定できない場合は`review_required`とする
(7節「停止・保留条件」参照)。

### 5.3 目次、ルビ、脚注、画像

質問3への回答: **原HTMLと正規化本文を分離し、ルビ・脚注・画像参照を
structuredへ保持する。**

```json
{
  "chunk_id": "sample-epub-chunk-0003",
  "source_id": "sample-epub",
  "order": 3,
  "locator": {
    "spine_index": 3,
    "xhtml_path": "OEBPS/chapter03.xhtml",
    "chapter": "第3章"
  },
  "extraction_method": "epub_html",
  "text_path": "sources/structured/sample-epub/chunk-0003.md",
  "annotations": {
    "ruby": [
      {"base": "音声", "reading": "おんせい", "char_offset": 42}
    ],
    "footnotes": [
      {"ref_id": "fn1", "text": "脚注本文", "char_offset": 120}
    ],
    "images": [
      {"src": "OEBPS/images/fig01.png", "alt": "図1", "char_offset": 200}
    ]
  },
  "warnings": []
}
```

ルビはTTS用の読み表記へ変換可能な形で原文情報として保持する
(タスク13の前処理で読み表記変換を行う際の入力になる)。
脚注は本文中の参照位置を保持し、本文へ無条件で埋め込まない
(読み上げ順序を暗黙に変えない)。

### 5.4 CSSと装飾

質問4への回答: **意味を持つ構造だけを残し、表示専用CSSは正本にしない。**

保持する意味構造:

- 見出しレベル(h1〜h6)
- 段落・リスト構造
- 強調(em/strong)は原文情報として保持(TTS上のイントネーション調整に利用可能)
- ルビ、脚注、画像参照(5.3節)

保持しない:

- フォント、色、レイアウト用CSS
- 表示専用のインラインstyle

### 5.5 章・節IDとlocator

`01-common-identifiers-and-versioning.md`のID規則に従い、
spineのitemref順を`chunk`の`order`として使用する。
`source-storage-and-common-schema.md`のchunk manifest形式へ変換する際は、
`locator.spine_index`と`locator.xhtml_path`の両方を保持し、
元HTMLへ常に追跡可能にする。

## 6. 入力

- DRMなしEPUB 2/3ファイル
- (利用者が正当に取得したもの)

## 7. 出力

- EPUB抽出manifest(5.3節形式)
- ルビ・脚注・画像の抽出例
- `source-storage-and-common-schema.md`のchunk形式への変換結果

## 8. 正常系

1. `container.xml`から`rootfile`(package document)を特定する。
2. package documentの`spine`を読み取り、本文順序を確定する。
3. `nav`/`NCX`から見出し階層を取得し、spineと整合させる。
4. 各XHTMLファイルから本文・ルビ・脚注・画像参照を抽出する。
5. 原HTMLを`extracted/`、正規化本文を`normalized/`または`structured/`へ保存する。
6. `source-storage-and-common-schema.md`のchunk manifestへ変換する。

## 9. 異常系

| ケース | 扱い |
|---|---|
| DRM検出 | `blocked`、処理しない |
| container.xml不正/欠落 | `fail` |
| spineとnav/NCXの章順が矛盾し人間判断が必要 | `review_required` |
| 未知のmedia type参照 | warning、該当要素をスキップして記録 |
| 外部参照(リモート画像・リンク) | warning、取得しない |
| 壊れたXHTML(パース不能) | 該当spine itemを`fail`、他は継続 |

## 10. バリデーション

- 全chunkの`order`がspine順と一致する。
- ルビ・脚注の参照先(`char_offset`等)が本文の範囲内にある。
- DRM付きEPUBが`structured/`まで到達しない。

## 11. テスト観点

- 章順を再現できる(spine準拠)。
- ルビと脚注を失わず保持できる。
- 元HTMLへ追跡できる(`locator.xhtml_path`)。
- DRM対象外方針が明記されている。
- spineとnav/NCXが矛盾する壊れたEPUBサンプルで`review_required`になる。
- 外部参照を自動取得しない。

## 12. 移行・互換性

- 現行実装からの移行対象なし。
- 出力formatは`source-storage-and-common-schema.md`のchunk形式に準拠する。

## 13. 未決定事項

- 縦書きEPUB(日本語小説等でよく使われるvertical writing指定)の扱い
- 複数言語混在EPUBでのruby/正規化の扱い
- 画像内テキスト(図中の文字)をOCR対象とするかどうか(タスク10との境界)
- EPUB3のメディアオーバーレイ(音声同期)への対応要否

## 14. 完了条件

- [x] 章順を再現できる。
- [x] ルビと脚注を失わず保持できる。
- [x] 元HTMLへ追跡できる。
- [x] DRM対象外方針が明記されている。
- [x] 出力ドラフトが存在し、`status: review`である。
- [x] 実装コードを変更していない。

## 15. 停止・保留条件(該当状況)

- DRM回避は要求されておらず、対象外として明記済み。
- spineと本文が矛盾する具体的ケースは未検証のため、実装時に`review_required`パスを
  必ず用意することを完了条件とした。
