---
spec_id: 15-migration-and-compatibility
title: "現行コードからの移行・互換性仕様"
status: approved
version: "1.2"
approved_at: "2026-07-18"
source_dump: "audio_book_creation_dump_2026-07-18_220811.txt"
last_updated: "2026-07-19"
legacy_kindle_source_dump: "audio_book_creation_dump_2026-07-18_193603.txt"
---

# 現行コードからの移行・互換性仕様

## 1. 目的

現行の`book.json`、`sections.json`、`text/`、VOICEVOX処理を壊さず、新しい企画・原稿・承認・セグメント・TTS仕様へ段階移行する。

## 2. 現行構成の要点

```text
data/library/<book_id>/
├── book.json
├── sections.json
├── text/raw/
├── text/corrected/
├── text/merged/
├── text/readable/
├── text/speech/
├── audio/cache/wav/
└── audio/exports/
```

現行コードは`book_config.py`へパスと設定ロジックが集約され、新構成優先・旧構成フォールバックの方針を既に持つ。これを移行レイヤーの基盤にする。

## 3. 移行原則

1. 既存データを自動で破壊・移動しない。
2. 新形式を優先して読む。
3. 新形式がなければ旧形式を読む。
4. 新規生成物は原則として新形式へ書く。
5. 旧形式への書込は互換オプションとして期限付きで残す。
6. 移行スクリプトは通常実行と分ける。

## 4. 設定移行

### book.json

`book.json`は当面維持する。次を新形式へマッピングする。

| 旧項目 | 新項目 |
|---|---|
| `bookId` | `project_id` |
| `title` | project title |
| `deliverableTitle` | packaging deliverable title |
| `enableSections` | chapter mode |
| `audioExportUnits` | packaging output units |
| `tts` | voice profile初期値 |

`book.json`は実行互換設定、`project-plan.yaml`は内容企画という責務分離を行う。

### sections.json

- `sectionId`または`fileName`を互換chapter IDとして扱う。
- `order`と`fileTitle`を新章一覧へ取り込む。
- `startPage`、`endPage`、`sourceId`は資料入力側の由来情報として保持する。

## 5. テキスト移行

新形式の入力優先順位は`02-process-input-output.md`に従う。

旧ファイルからYAMLを作る初回変換では、次を記録する。

```yaml
provenance:
  legacy_input: true
  source_path: text/merged/section1/merged_gemini_fixed.txt
  imported_at: "2026-07-18T21:00:00+09:00"
```

自動変換された原稿は`draft`扱いとし、検証・承認を経ない限り正式正本にしない。

## 6. TTS移行

### 段階1

現行`text_to_voicevox_wav`を共通クライアントから呼ぶ。出力は現行と同じunit WAVを維持する。

### 段階2

原稿セグメント単位WAVを生成し、章WAV/MP3を結合する。互換のunit WAVも任意生成する。

### 段階3

`batch_tts_sections.py`からVOICEVOX直接importを除き、TTS registryを利用する。

### 段階4

COEIROINKを追加する。

## 7. CLI互換

現行コマンドは当面維持する。

```bash
python script/text_to_speech.py --book-id ...
python script/batch_tts_sections.py --book-id ...
python script/wav_to_mp3.py --book-id ...
```

新オーケストレーターを追加する。

```bash
python script/audiobook.py run <book_id>
python script/audiobook.py tts <book_id> --chapter ch01
python script/audiobook.py approve <book_id> --target verified-script
```

旧コマンドは低レベル互換コマンドとしてdocsへ明記する。

## 8. パッケージ構成

現行`script/`を即時`src/`へ移さない。まず次を追加する。

```text
script/
├── pipeline/
├── models/
├── schemas/
├── approvals/
├── audio_processing/
└── tts_clients/
```

安定後に`src/audiobook_tool/`への移行を別提案とする。

## 9. テスト追加順

1. ID・version正規化
2. project plan schema
3. segment schema
4. claims/source validation
5. approval invalidation
6. voice profile legacy conversion
7. TTS registry
8. VOICEVOX adapter
9. COEIROINK adapter
10. audio validation
11. packaging manifest

現行方針どおり、外部サービスはmockし、純粋関数を先にテストする。

## 10. 互換期間の終了条件

次を満たすまでは旧読込を削除しない。

- 既存2冊以上を新形式へ変換し、同等の音声を出力できる。
- 新形式の回帰テストがある。
- 移行前バックアップと復元手順がある。
- READMEとdocsから旧形式の直接利用が減っている。
- 旧形式利用時のwarningが一定期間記録されている。

## 11. 実装フェーズ

### Phase A: 仕様・モデル

YAMLモデル、validator、互換readerを作る。音声処理は変えない。

### Phase B: 原稿・承認

segment、claim、approvalを導入し、YAMLから現行TXTへ変換する。

### Phase C: TTS抽象化

VOICEVOXを共通クライアントへ移行し、現行出力を維持する。

### Phase D: セグメント音声

部分再生成、manifest、音声検査、章結合を導入する。

### Phase E: COEIROINK

APIバージョンと起動方式を固定して実装する。



## 12. Kindleキャプチャに関する方針

Kindle画面キャプチャ、Kindle専用ツールの開発は、製品の恒久的対象外である
(`19-application-scope-and-mvp.md` 5.5節)。旧版実装(capture settings、
Kindleウィンドウ検出、ページ送り、1ページ試し撮り、ページ画像保存、
Tesseract OCR、互換wrapper)の移行・再利用は、本製品では行わない。

本体が旧版のページ画像・OCRテキストを取り込む場合は、`existing_image_file`を
`acquisition_method`とする一般的な画像sequenceとして
`image-material-ingestion.md`の契約経由で受け取る。旧ページ画像・OCRテキストを
自動移動・削除しない方針は維持する。

## 13. 完了条件

現行のG検定本と章なしTRPG本を新旧両方式で処理でき、旧データを削除せず新形式へ移行できること。
