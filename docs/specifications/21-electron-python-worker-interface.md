---
spec_id: 21-electron-python-worker-interface
title: "Electron-Python worker連携契約"
status: approved
version: "1.0"
approved_at: "2026-07-19"
last_updated: "2026-07-19"
spec_refs:
  - 20-electron-desktop-architecture.md
  - 22-job-lifecycle-and-recovery.md
  - 18-ai-model-routing-and-cost-control.md
---

# Electron-Python worker連携契約

## 1. 目的

Electron mainからPython CLIを子プロセスとして起動し、進捗・結果・エラーを
JSON Linesで受け渡す契約を定義する。同じ契約をPython CLI単体からも利用できる
ようにし、Electronに依存しないテスト・実行を可能にする。

## 2. 対象範囲

- プロセス起動主体
- requestの受け渡し方法
- progress/resultの出力形式
- 終了codeの規則
- cancel方法
- artifact生成イベント
- 不正JSON、途中終了、timeoutの扱い

## 3. 対象外

- Python CLI内部の処理ロジック(素材処理・原稿生成・TTS・音声パッケージングそれぞれの
  詳細は既存の承認済み仕様、および`docs/spec-proposals/`側の各提案に従う)
- Job状態機械そのもの(→`22-job-lifecycle-and-recovery.md`)

## 4. 現行実装

現行コードには、本契約に基づくPython CLIエントリポイントは存在しない。
`script/ai_clients/gemini/client.py`、`script/tts_clients/voicevox/client.py`は
関数ベースのモジュールであり、本契約が定義するCLIラッパーは今後の実装タスクで
これらを呼び出す形で追加される。

## 5. 推奨仕様

### 5.1 起動主体

Electron mainがPython CLIを子プロセスとして起動する。rendererから直接
Python CLIまたは`child_process`を起動することはない(`20-electron-desktop-architecture.md`
5.8節と一致)。

### 5.2 requestの受け渡し

```yaml
worker_request:
  transport: json_file_or_stdin
  contains:
    - job_id
    - job_type
    - parameters
```

requestはJSONファイルまたはstdinのいずれかで渡す。ファイル渡しの場合、
Electron mainが一時ファイルへrequestを書き込み、そのパスをCLI引数として渡す。

### 5.3 progressとresultの出力形式

progressとresultはJSON Lines(1行1JSON)としてstdoutへ出力する。

```json
{"event":"started","job_id":"job-001"}
{"event":"progress","current":2,"total":10,"message":"章2を処理中"}
{"event":"artifact","artifact_type":"mp3","path":"relative/path/ch01.mp3"}
{"event":"completed"}
```

イベント種別:

| event | 意味 |
|---|---|
| `started` | Job実行を開始した |
| `progress` | 進捗を更新した(`current`/`total`/`message`を含む) |
| `artifact` | 成果物を生成した(`artifact_type`/`path`を含む。`path`はProject rootからの相対path) |
| `warning` | 処理を継続可能な警告(`message`を含む) |
| `error` | 回復不能なエラー(`code`/`message`を含み、直後に非0終了する) |
| `completed` | Job実行が正常終了した |

### 5.4 stderr

stderrは技術ログ(スタックトレース、詳細なデバッグ情報)専用とする。
利用者向けの進捗・結果はstdoutのJSON Linesのみで表現し、stderrの内容を
利用者向け画面へそのまま表示しない。

### 5.5 終了codeの規則

```yaml
exit_codes:
  0: success
  1: general_error
  2: invalid_request
  3: cancelled
  124: timeout
```

- `0`: `completed`イベントを出力し正常終了した。
- `1`: 処理中に回復不能なエラーが発生した。
- `2`: requestのJSONが不正、または必須パラメータが欠落している。
- `3`: cancel要求を受けて処理を中断した。
- `124`: Electron mainが設定したtimeoutに到達し、プロセスを終了させた。

### 5.6 cancel方法

Electron mainは、対象プロセスへOS標準の終了シグナル(Windowsでは
プロセス終了相当の操作)を送ることでcancelを要求する。Python CLI側は、
シグナルを受けて安全に処理を中断できるチェックポイントを主要な処理単位
(章単位、segment単位等)ごとに設ける。中断時は途中生成物を正式パスへ
反映せず、Electron mainは終了code `3`を確認して`22`のJob状態機械における
`cancelled`へ遷移させる。

### 5.7 artifact生成イベント

`artifact`イベントのpathは、Project rootからの相対パスとし、絶対パスを
出力しない。Electron mainはこの相対パスをDB(`docs/db/05-artifacts-table.md`)
へ記録する。

### 5.8 不正JSON、途中終了、timeoutの扱い

| 状況 | Electron mainの扱い |
|---|---|
| stdoutの1行がJSONとしてparseできない | 当該行を技術ログへ記録し、Job自体は継続する(致命的エラーにしない) |
| プロセスが`completed`イベントを出力せずに終了した | 終了codeに関わらず、Jobを`failed`として記録する |
| 設定timeoutを超過して応答がない | プロセスを終了させ(終了code `124`相当として扱う)、Jobを`failed`として記録する |

### 5.9 Python CLI単体での利用

本契約は、Electronを介さずPython CLI単体でも同一の入出力形式で利用できる。
これにより、Electron環境がないテスト環境やCI(`docker compose run --rm app pytest`)
からも、同じJSON Lines契約でCLIの動作を検証できる。

## 6. 入力

- request(JSONファイルまたはstdin、5.2節)

## 7. 出力

- JSON Linesイベント(stdout、5.3節)
- 技術ログ(stderr、5.4節)
- 終了code(5.5節)

## 8. 必須項目

- `job_id`(request)
- `event`(各出力行)

## 9. 任意項目

- `message`(progress/warning/errorイベント)

## 10. バリデーション

### Error

- requestに`job_id`が欠落している。
- `artifact`イベントのpathが絶対パスである。
- stdoutへ利用者向け機密情報(APIキー等)を出力する。

### Warning

- stdoutの一部行がJSONとしてparseできない。

## 11. 状態・エラー・警告

Job状態への反映は`22-job-lifecycle-and-recovery.md`に従う。本書はイベント形式のみを定義する。

## 12. 正常例

1. Electron mainがrequestを一時ファイルへ書き込む。
2. Python CLIを子プロセスとして起動し、requestファイルのパスを引数で渡す。
3. CLIが`started`→`progress`(複数)→`artifact`(0件以上)→`completed`の順でイベントを出力する。
4. Electron mainが各イベントをDB(Job/JobEvent/Artifact)へ反映する。
5. 終了codeが`0`であることを確認する。

## 13. 異常例

| ケース | 扱い |
|---|---|
| requestのJSONが不正 | CLIが終了code `2`で即座に終了する |
| 処理中にcancel要求を受ける | CLIが安全なチェックポイントで中断し、終了code `3`で終了する |
| timeoutに到達 | Electron mainがプロセスを終了させ、Jobを`failed`にする |
| `completed`を出力せず異常終了 | Jobを`failed`にする(5.8節) |

## 14. テスト観点

- 正常系でJSON Linesイベントが順序どおり出力される。
- 不正なrequest JSONで終了code `2`になる。
- cancel要求で終了code `3`になり、途中生成物が正式パスへ反映されない。
- `completed`なしでプロセスが終了した場合にJobが`failed`になる。
- stdoutの1行がJSON不正でも、Job全体が異常終了しない(warningとして継続)。
- 同一契約をPython CLI単体で(Electronなしに)検証できる。

## 15. 移行・互換性

新規契約であり、移行対象となる既存CLIは存在しない。将来、既存の
`script/ai_clients/`、`script/tts_clients/`を呼び出すCLIラッパーを実装する際、
本契約をラッパーの公開インターフェースとする。

## 16. 未決定事項

なし。

## 17. 完了条件

- request、progress、result、エラー、終了codeの契約が定義されている。
- cancel方法が定義されている。
- artifact生成イベントの形式が定義されている。
- 不正JSON・途中終了・timeoutの扱いが定義されている。
- Python CLI単体でも同じ契約を利用できることが明記されている。
