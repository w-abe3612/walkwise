---
status: review
version: "1.0"
created_at: "2026-07-19"
task_id: SPEC-APP-000
task_type: preflight_audit
---

# app-management 仕様草案生成 事前監査報告

本書は `docs/tasks/20_app-management-spec-drafting-master.md` の「8. 事前監査」で
要求された事前監査の結果である。承認済み仕様ではなく、以降の草案作成 (21〜39) の
前提として使う調査記録である。

## 1. 実際に存在した承認済み仕様 (`docs/specifications/`)

存在を確認したファイル (すべて `status: approved`):

```text
00-specification-guidelines.md            v1.0
01-common-identifiers-and-versioning.md    v1.0
02-process-input-output.md                 v1.2
03-project-plan-schema.md                  v1.1
04-chapter-generation-schema.md            (存在。内容未読了 = evidence_gap)
05-script-segment-schema.md                (存在。内容未読了 = evidence_gap)
06-claims-and-sources.md                   (存在。内容未読了 = evidence_gap)
07-approval-workflow.md                    v1.1
08-character-profile-schema.md             (存在。内容未読了 = evidence_gap)
09-voice-profile-schema.md                 v1.1
10-tts-client-common-interface.md          (存在。内容未読了 = evidence_gap)
11-voicevox-client.md                      (存在。内容未読了 = evidence_gap)
13-audio-validation.md                     (存在。内容未読了 = evidence_gap)
14-audio-packaging.md                      v1.0
15-migration-and-compatibility.md          (存在。内容未読了 = evidence_gap)
16-ai-assisted-development-workflow.md     v1.2
17-file-based-data-persistence-policy.md   v1.0
18-ai-model-routing-and-cost-control.md    v1.0
audiobook-creation-pipeline.md             v1.3
kindle-capture.md                          v1.0
image-material-ingestion.md                v1.0
examples/ (ai-model-policy.yaml, image-ingestion-session.json,
           image-material-source.yaml, kindle-capture-profile.yaml,
           kindle-capture-session.json)
README.md
```

`12-coeiroink-client.md` は `docs/specifications/` には存在せず、
`docs/spec-proposals/generated-specifications/12-coeiroink-client.md` に草案として存在する
(未承認)。COEIROINK は本草案群では「未承認・provisional」として扱う。

**evidence_gap**: 04, 05, 06, 08, 10, 11, 13, 15 の内容は今回すべてを精読していない。
草案21〜39では、これらの番号を「存在する上位仕様」として参照するに留め、
内容依存の断定は避ける。人間レビュー時にこれらの精読を推奨する。

### 17番との関係 (重要)

`17-file-based-data-persistence-policy.md` (v1.0, 承認済み) は次を明記している。

> 初期実装では、MySQL、SQLiteなどのデータベースを使用しない。
> データベースの導入は… **Web管理画面を実装する場合** … に改めて検討する。

今回のタスクはまさにこの「検討する時点」に該当する。したがって本草案群は、
17番を無断で上書きするのではなく、17番が予告した検討そのものとして位置付ける。
DB導入方針が承認された場合、17番は昇格作業の一部として改訂対象になる
(`17-specification-promotion-plan.md` 相当の草案で扱う)。

## 2. 現在のCLI・スクリプト・データ保存方法

`script/` の実体:

```text
script/ai_clients/gemini/__init__.py
script/ai_clients/gemini/client.py
script/tts_clients/__init__.py
script/tts_clients/voicevox/client.py
script/tts_clients/coeiroink/client.py   (未実装。NotImplementedErrorのみ)
```

**evidence_gap / 重要な事実確認**: `script/` にはオーケストレーターCLI
(`batch_tts_sections.py`、`wav_to_mp3.py`、`capture_ocr_tts.py` 等、
`14-audio-packaging.md`や`kindle-capture.md`が「現行実装」として言及するモジュール)
が **存在しない**。存在するのはGemini APIクライアントとVOICEVOXクライアントの
単体モジュールのみである。

このことから、タスク20の前提文「現在のコマンド中心・ファイル中心のオーディオブック作成ツール」は、
「複数の承認済み仕様が定義する将来のCLI像」であり、「現時点で動いている複数コマンド群」
ではないと判断する。草案21〜39では、この区別を明記し、
存在しないコマンドを実在するかのように書かない。

`data/`、`config/`、`deliverables/` ディレクトリは現在のリポジトリに存在しない
(空、または未作成)。`book.json`、`sections.json` の実例も存在しない。
`02-process-input-output.md` 等が示すディレクトリ構成は、いずれも仕様上の推奨構成であり、
実データでの検証例ではない。

`requirements.txt`:

```text
pillow==11.3.0
pydub==0.25.1
requests==2.32.5
pytest==9.0.3
```

Web framework、DBドライバ、ORM、ASGI server等は含まれていない。

`tests/` ディレクトリは存在するが中身は0件。

## 3. 既存フロント・API・DBの有無

- フロントエンド資産: なし。
- HTTP APIサーバー: なし。
- DB: なし (17番仕様どおり導入されていない)。
- `Dockerfile` / `docker-compose.yml`: 存在するがサイズ0バイト (未記述、あるいは雛形のみ)。中身を変更しないという安全規則に従い、内容の断定・変更は行わない。
- `.env`: 存在するがサイズ0バイト。Gemini APIキー等はこのファイルに置く設計 (`ai_clients/gemini/client.py`) だが、現状は未設定と推測される。断定はしない (`evidence_gap`)。

## 4. 既存依存パッケージ

上記 `requirements.txt` の4パッケージのみ。バックエンドAPI・DB・フロント関連パッケージはインストールされていない。本タスクではいかなるパッケージも追加インストールしない。

## 5. 既存の仕様草案との重複

`docs/spec-proposals/generated-specifications/` には、資料入力パイプライン関連の未承認草案 (OCR、EPUB、PDF、Kindle、画像、ASR照合、M4B、rights等) が既に存在する。これらは「資料入力・音声出力パイプライン」の草案であり、本タスクが扱う「フロント画面・DB管理」とは対象が異なる。重複は確認されなかった。

`app-management/` サブディレクトリは今回新規作成した。既存ファイルとの名前衝突は発生していない。

`docs/tasks/APP_MANAGEMENT_SPEC_DRAFT_DECISIONS.md` に、今回の草案作成前に記録された初期仮説 (SQLite第一候補、Windows単一利用者ローカル、Vue3/SPA候補など) が存在する。これは `status: provisional` であり、本タスクの初期仮説として尊重するが、絶対视せず21〜39各タスクの「初期推奨回答は既存仕様・コードと矛盾する場合、採用せず理由を記録する」の原則に従う。

## 6. 指定ダンプ名と実ファイルの不一致

タスク20のfront matterに `requested_source_dump: "audio_book_creation_dump_2026-07-19_013737.txt"` とある。このファイルは `dumps/output/` に実在する (16,768行)。

ただし、このダンプのファイルツリー内容 (`# FILE TREE` セクション) は、`docs/tasks/` に `16_image-material-ingestion.md` と `README.md` のみを記録しており、本タスクの `20_app-management-spec-drafting-master.md` 以降のSPEC-APP-*ファイル群を含んでいない。

**evidence_gap**: ダンプはタスク作成前のスナップショットであり、現在のリポジトリ状態 (SPEC-APP-000〜019が追加済み) より古い。本監査および以降の草案は、ダンプの内容ではなく、実際にディスク上に存在するファイルを正本として調査した。ダンプは背景情報としてのみ参照する。

## 7. 変更予定ファイル (今回作成・更新する)

```text
docs/tasks/app-management-preflight-report.md   (本書)
docs/tasks/app-management-overnight-report.md   (タスク39完了時)
docs/spec-proposals/generated-specifications/app-management/**  (新規作成のみ)
```

## 8. 変更禁止ファイル (今回変更しない)

```text
script/**
tests/**
requirements.txt
Dockerfile
docker-compose.yml
docs/specifications/**  (承認済み仕様。参照のみ)
docs/spec-proposals/generated-specifications/ 配下の app-management 以外の既存ファイル
docs/tasks/20_app-management-spec-drafting-master.md ほか 21〜39番の指示書自体
```

## 9. 監査結論

- 承認済み仕様は17件超が存在し、資料入力・原稿生成・音声パイプラインについては比較的詳細に確定している。
- フロント・API・DBは仕様上も実装上も存在せず、本タスクはまさに `17-file-based-data-persistence-policy.md` が予告した検討の初回にあたる。
- 実装コードは、TTS/AIクライアント2種のみが存在し、CLIオーケストレーター・DB・フロントは一切存在しない「仕様先行・実装ほぼ空」の状態である。
- ダンプは陳腐化しており参考情報に留める。
- 以上を前提に、21〜39の草案は「白紙に近い実装状況」を正しく反映し、過大な既存実装を仮定しない。

## 10. 人間レビュー項目 (human_review_required)

- 04, 05, 06, 08, 10, 11, 13, 15番の各仕様の精読と、本監査の evidence_gap 解消。
- `.env` の実際の設定状態 (Gemini APIキー有無)。
- `Dockerfile` / `docker-compose.yml` が意図的に空なのか、作成中なのかの確認。
