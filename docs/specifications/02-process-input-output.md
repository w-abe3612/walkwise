---
spec_id: 02-process-input-output
title: "各プロセスの入力・出力仕様"
status: approved
version: "1.2"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_235129.txt"
---


# 各プロセスの入力・出力仕様

## 1. 目的

オーディオブック作成全体パイプラインを構成する各工程について、
入力、出力、正本、実行主体、承認ゲート、保存場所を定義する。

本仕様は`audiobook-creation-pipeline.md`の下位仕様である。

## 2. 対象範囲

- シリーズ計画
- 作品登録
- 資料一覧
- 資料登録・画像取り込み・抽出・正規化
- トピックマップ
- カリキュラム
- 作品企画
- 章仕様
- 初稿
- 主張抽出
- 出典対応
- 原稿変換
- 検証済み原稿
- 試聴音声
- 本番TTS
- 音声検査
- 章MP3
- 音声manifest
- 制作manifest
- deliverables

## 3. 対象外

- OCRエンジン固有の処理
- PDF・EPUB抽出ライブラリ
- COEIROINK APIの具体値
- 音声検査の最終閾値
- M4B
- ASR照合
- ファイルロック実装

## 4. 正式な処理順序

```text
シリーズ計画
↓
作品登録
↓
資料戦略決定
↓
資料候補・検索語の提案
↓
資料一覧作成
↓
利用目的・資料役割確認
↓
資料登録または資料入力
（PDF、EPUB、画面キャプチャ専用ツール由来の画像sequence、カメラ写真、スキャナ画像、手動本文）
↓
画像取り込み・資料抽出・OCR・正規化
↓
source summary・topic index作成
↓
coverage map作成
↓
不足・重複・矛盾分析
↓
必要に応じて資料追加または再処理
↓
トピックマップ作成
↓
カリキュラム・章構成再構築
↓
資料・カリキュラム承認
↓
作品企画作成
↓
作品企画承認
↓
章仕様作成
↓
初稿生成
↓
技術的主張抽出
↓
出典対応付け
↓
内容検証
↓
理解しやすさ変換
↓
音声向け変換
↓
キャラクター表現
↓
意味保存の最終検証
↓
検証済み原稿承認
↓
試聴音声生成
↓
試聴音声承認
↓
本番TTS
↓
音声検査
↓
章単位MP3生成
↓
音声・制作manifest生成
↓
正式成果物出力
```

## 5. 物理ディレクトリと論理ID

論理上の作品識別子は`project_id`である。

物理ディレクトリ名は移行期間中、旧`book_id`または`project_id`を使用できる。

```text
data/library/<project_directory>/
```

新規作品では次をSHOULDとする。

```text
project_directory = project_id
```

既存ディレクトリを自動改名してはならない。

## 6. 推奨ディレクトリ

```text
data/
├─ series/
│  └─ <series_id>/
│     └─ series-plan.yaml
└─ library/
   └─ <project_directory>/
      ├─ book.json
      ├─ sections.json
      ├─ project/
      │  ├─ project-plan.yaml
      │  ├─ sources.yaml
      │  ├─ approvals.yaml
      │  ├─ characters/
      │  └─ voices/
      ├─ sources/
      │  ├─ originals/
      │  ├─ preprocessed/
      │  ├─ extracted/
      │  ├─ normalized/
      │  ├─ structured/
      │  ├─ manifests/
      │  └─ reports/
      ├─ curriculum/
      │  ├─ topic-map.yaml
      │  └─ curriculum.yaml
      ├─ chapters/
      │  └─ <chapter_id>/
      │     ├─ chapter-spec.yaml
      │     ├─ draft/script.yaml
      │     ├─ narration/simplified.yaml
      │     ├─ narration/audio-adapted.yaml
      │     ├─ narration/character-styled.yaml
      │     ├─ verified/script.yaml
      │     ├─ claims.yaml
      │     └─ reports/
      ├─ text/
      ├─ audio/
      │  ├─ cache/wav/segments/
      │  ├─ preview/
      │  ├─ chapters/
      │  ├─ manifests/
      │  ├─ reports/
      │  └─ exports/
      ├─ deliverables/
      └─ logs/
```

## 7. 正本

| 対象 | 正本 |
|---|---|
| シリーズ計画 | `series-plan.yaml` |
| 作品企画 | `project/project-plan.yaml` |
| 資料一覧 | `project/sources.yaml` |
| 資料・カリキュラム | `sources/structured/`、`curriculum/` |
| 承認 | `project/approvals.yaml` |
| 章要件 | `chapters/<chapter_id>/chapter-spec.yaml` |
| 初稿 | `chapters/<chapter_id>/draft/script.yaml` |
| 検証済み原稿 | `chapters/<chapter_id>/verified/script.yaml` |
| 主張 | `chapters/<chapter_id>/claims.yaml` |
| 音声順序 | `audio/manifests/<chapter_id>.json` |
| 音声検査 | `audio/reports/` |
| 正式出力一覧 | 制作manifest |

音声パイプラインは、検証済み原稿の`text`を変更してはならない。

## 8. プロセス表

| 工程 | 主な入力 | 主な出力 | 正本 | 主体 |
|---|---|---|---|---|
| シリーズ計画 | 制作候補 | `series-plan.yaml` | シリーズ計画 | 人間・AI補助 |
| 作品登録 | 分野、目的、読者 | 初期`project-plan.yaml` | 作品企画 | 人間 |
| 資料一覧 | 資料候補 | `project/sources.yaml` | 資料一覧 | 人間・AI補助 |
| 資料登録 | 原資料、URL、画像群、手動本文 | originals、metadata、ingestion manifest | 原資料 | 自動・人間 |
| 画像取り込み | カメラ写真・スキャナ画像 | preprocessed pages、quality report | 原画像からの派生 | 自動・人間確認 |
| 資料抽出 | 原資料・preprocessed pages | extracted | 原資料からの派生 | 自動 |
| 資料正規化 | extracted | normalized、structured | 構造化資料 | 自動・人間確認 |
| topic map | 資料、目次、シラバス | `curriculum/topic-map.yaml` | topic map | AI補助 |
| curriculum | topic map | `curriculum/curriculum.yaml` | カリキュラム | AI補助・人間 |
| 資料・カリキュラム承認 | sources、curriculum | approval | approvals | 人間 |
| 作品企画 | 承認済みcurriculum | `project-plan.yaml` | 作品企画 | AI補助・人間 |
| 作品企画承認 | project plan | approval | approvals | 人間 |
| 章仕様 | 企画、資料 | `chapter-spec.yaml` | 章仕様 | AI補助・人間 |
| 初稿 | 章仕様、資料 | draft `script.yaml` | 初稿 | AI |
| 主張抽出 | 初稿 | `claims.yaml` | 主張 | AI |
| 出典対応 | claims、sources | evidence、fact-check | 主張検証 | AI補助 |
| 理解しやすさ変換 | 初稿 | `simplified.yaml` | 派生物 | AI |
| 音声向け変換 | simplified | `audio-adapted.yaml` | 派生物 | AI |
| キャラクター変換 | audio-adapted | `character-styled.yaml` | 派生物 | AI |
| 最終検証 | 変換原稿、claims | verified `script.yaml` | 検証済み原稿 | AI補助・人間 |
| 原稿承認 | verified script | approval | approvals | 人間 |
| 試聴 | verified script、voice profile | preview音声 | 音声派生物 | 自動 |
| 試聴承認 | preview音声 | approval | approvals | 人間 |
| 本番TTS | 承認済み原稿 | segment WAV | WAV中間物 | 自動 |
| 音声検査 | WAV、manifest | validation report | 検査結果 | 自動・人間 |
| 章出力 | 合格WAV | 章MP3 | 章音声 | 自動 |
| manifest | 全成果物 | audio/production manifest | manifest | 自動 |
| 正式出力 | 承認済み成果物 | deliverables | 完成成果物 | 自動 |


## 8.1 AIタスククラス

各AI工程は次の論理層を指定する。

| 工程 | 論理層 |
|---|---|
| 目次整理、topic抽出、主張候補抽出、形式変換 | `economy_structuring` |
| 初稿、分かりやすさ変換、音声向け変換 | `standard_generation` |
| 出典間矛盾、難しい技術検証、最終意味レビュー | `high_assurance_review` |

初期モデル割当てと昇格条件は
`18-ai-model-routing-and-cost-control.md`へ従う。

資料全文を工程ごとに再送せず、
`topic-index.yaml`と`chunk-manifest.json`から必要チャンクだけを解決する。

## 9. 承認ゲート

- `materials_curriculum`未承認: 作品企画の正式承認と章原稿の本生成を停止する。
- `planning`未承認: 初稿の本生成を停止する。
- `verified_script`未承認: 本番TTSを停止する。
- `preview_audio`未承認: deliverablesへの出力を停止する。

## 10. 形式

| 形式 | 用途 |
|---|---|
| YAML | 企画、設定、資料メタデータ、原稿、承認 |
| JSON | manifest、検査結果、大量機械生成結果 |
| Markdown | レビュー報告、差分説明 |
| TXT | 既存処理との互換入力 |
| PNG | OCR用標準派生画像、losslessページ画像 |
| JPEG | カメラ写真等の原画像 |
| TIFF | スキャナ画像等の原画像 |
| WAV | TTS中間音声 |
| MP3 | 初期正式音声 |

## 11. 手動資料からの開始

資料入力パイプラインが未完成でも、
次のいずれかを共通資料として登録できれば後続処理を開始してよい。

- ユーザーが用意した本文
- 手動で作成した構造化資料
- 外部ツールで抽出した本文
- 既存OCR結果
- カメラ写真・スキャナ画像（後続開始前にOCRまたは手動構造化が必要）
- URLと人間が確認した引用位置

## 12. 音声入力解決優先順位

```text
1. chapters/<chapter_id>/verified/script.yaml の segments[].tts_text
2. chapters/<chapter_id>/verified/script.yaml の segments[].text
3. text/speech/<unit>/text.txt
4. text/merged/<unit>/speak_dedicated.txt
5. text/merged/<unit>/fixed.txt
6. text/merged/<unit>/merged_gemini_fixed.txt
7. text/merged/<unit>/merged.txt
```

旧形式を使用した場合はmanifestへ`legacy_input: true`を記録する。

## 13. 入力不変

- 入力ファイルを直接上書きしない。
- 原資料、抽出、正規化、構造化を分離する。
- 初稿、各変換、検証済み原稿を分離する。
- 音声出力は一時ファイルへ作成後、検査して置換する。
- 失敗時に既存正常ファイルを削除しない。

## 14. 再利用と部分再生成

| 変更 | 再処理 |
|---|---|
| 資料本文 | 影響するtopic、claim、原稿 |
| curriculum | 作品企画、章仕様、原稿 |
| 章仕様 | 対象章の原稿以降 |
| text | 対象segment音声と章MP3 |
| tts_text | 対象segment音声と章MP3 |
| character profile | 影響する原稿と音声 |
| voice profile | 影響する音声 |
| MP3タグ | MP3のみ |

## 15. Error

- 必須入力欠落
- YAMLまたはJSON読込失敗
- 参照ID不正
- 未承認資料・カリキュラムからの本生成
- 未承認企画からの初稿本生成
- 未承認原稿からの本番TTS
- 未承認試聴音声からのdeliverables
- 未検証技術的主張
- 音声破損
- manifest順序重複
- 出力書込失敗

## 16. Warning

- 旧入力へフォールバック
- `tts_text`がなく`text`を使用
- source locatorが粗い
- 一つの資料へ偏っている
- voice profileが暫定
- キャッシュが古い可能性
- MP3タグ情報が不足

## 17. 現行実装との関係

現行処理は1 unitにつき1WAVを生成する。

移行期間は、YAML原稿を一時TXTへ連結して現行関数へ渡すアダプターを許可する。

## 18. テスト観点

- 手動資料から開始できる。
- 新形式が旧形式より優先される。
- 新形式がない場合だけ旧形式を読む。
- 入力ファイルが変更されない。
- 4段階承認ゲートを迂回できない。
- 変更segmentだけを再生成する。
- 未承認成果物がdeliverablesへ入らない。
- 章MP3とmanifestを初期正式成果物として生成できる。
- M4Bなしで完了できる。

## 19. 完了条件

サンプル1章を、作品登録から章MP3と制作manifestまで通し、
各成果物が一意の正本を持ち、前工程を上書きせず、
4段階承認で正式出力を制御できること。
