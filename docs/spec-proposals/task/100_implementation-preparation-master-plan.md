---
task_type: implementation_preparation_master_plan
status: draft
version: "1.0"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
---

# Walkwise 実装準備マスタープラン

## 1. 目的

承認済み仕様を、ChatGPTが先にすべて実装準備し、その後にClaude Codeが本実装するため、
開発全体を安定task ID付きの実装単位へ分割する。

このSTEP1では、コード、テスト、コマンド、Claude Code用タスク契約書をまだ作らない。
作成するのは、後続STEPの正本となる「実装準備タスク一覧」と各タスクの境界だけである。

## 2. 正式な開発順序

```text
仕様策定
↓
仕様承認
↓
【ChatGPT】実装タスクの切り出し ← 今回
↓
【ChatGPT】タスク契約書とテストケース作成
↓
【ChatGPT】テストの空実装
↓
【ChatGPT】ソースコードの空実装
↓
【ChatGPT】コマンド文書作成
↓
【ChatGPT】Claude Code用タスク一覧更新
↓
【ChatGPT】構文・import・pytest収集確認
↓
人間による実装準備成果物の承認
↓
【Claude Code】テスト本実装
↓
【Claude Code】未実装による失敗状態の確認
↓
【Claude Code】ソースコード本実装
↓
【Claude Code】対象テスト実行
↓
【Claude Code】全体テスト実行
↓
【Claude Code】文書記載コマンド確認
↓
【Claude Code】実装完了報告
↓
【ChatGPTまたは人間】仕様適合レビュー
↓
完了
```

## 3. STEP1の成果物

- `IMPLEMENTATION_INDEX.md`
- `101_...`〜`154_...`の実装準備タスク54件
- 本マスタープラン
- 更新案`README.md`
- 更新案`INDEX.md`

## 4. タスク数

| 区分 | 件数 |
|---|---:|
| MVP | 50 |
| post-MVP | 3 |
| blocked | 1 |
| 合計 | 54 |

## 5. phase

| phase | 件数 | 主な内容 |
|---|---:|---|
| 0. 開発基盤 | 6 | pytest、Docker、設定、ID、ファイル保存、domain model |
| 1. 永続化と業務サービス | 9 | SQLite、repository、Project、Source、権利、Build、Job、Artifact、承認 |
| 2. 資料入力 | 8 | text、画像、PDF、OCR、正規化、review、EPUB |
| 3. 教材生成AI | 9 | Gemini、routing、coverage、curriculum、原稿、主張、profile、意味検証、部分再生成 |
| 4. TTSと成果物 | 8 | TTS、VOICEVOX、試聴、検査、MP3、M4B、ASR、COEIROINK |
| 5. Workerとデスクトップ | 10 | Python worker、Electron、5画面、desktop E2E |
| 6. 移行・品質・配布 | 4 | legacy、sample fixture、Windows package、release受入 |

## 6. MVPとpost-MVPの分離

次のタスクはMVPのClaude Code実装開始条件に含めない。

- `TASK-EPUB-001`
- `TASK-M4B-001`
- `TASK-ASR-001`
- `TASK-COEIR-001`

前三つはpost-MVPとして準備を継続できる。
`TASK-COEIR-001`は公式API、実機、利用条件の証拠不足により`blocked`とする。

## 7. 暫定値の扱い

音声検査は実装対象に含めるが、閾値は`provisional`のまま扱う。
結果manifestにも`threshold_status: provisional`を残し、実測前にapprovedへ変更しない。

話者profileは構造と選択契約を先に実装準備する。
速度、音高、抑揚等の最終値は人間試聴後に確定する。

ファイルlock、backup等の未確定詳細は次を推奨初期値とする。

- Project単位lock file
- 同一volume内の一時ファイルからatomic replace
- 最低1世代backup
- 承認済み成果物を自動削除しない
- 相対pathを保存する

## 8. 既存タスクの扱い

`docs/tasks/16_image-material-ingestion.md`は、実装準備工程を経ずに作られた既存タスクである。
現時点ではClaude Codeへ実行させない。

内容は`TASK-IMAGE-001`と`TASK-IMAGE-002`へ分割して継承し、
STEP7で新しいタスク契約書を作成した後、既存タスクを置換・削除する。

## 9. STEP2以降の共通規則

- 1タスク1責務
- task IDを変更しない
- テストケースIDは`TC-<AREA>-<NNN>-<NN>`
- 通常テストは外部サービスを呼ばない
- テスト空実装は`xfail(strict=True)`と明示的失敗
- ソース空実装は型付き契約と`NotImplementedError`
- Claude Codeは公開契約を変更しない
- 対象タスクの本実装開始前に、全54タスクのChatGPT準備を完了させる
- `blocked`タスクを未確認情報で実装可能扱いにしない

## 10. 人間承認gate

Claude Codeへ一つでも本実装を依頼する前に、少なくともMVP対象50件について次を満たす。

```text
STEP2 契約・テストケース作成済み
STEP3 テスト空実装作成済み
STEP4 ソース空実装作成済み
STEP6 コマンド文書作成済み
STEP7 docs/tasks作成・INDEX更新済み
Python構文確認済み
import確認済み
pytest collection確認済み
Electron/TypeScriptの構文・test collection確認済み
人間承認済み
```

post-MVPとblockedの4件は、MVP実装開始を停止しない。
ただし、MVPコードへ未承認のpost-MVP公開契約を混入させない。
