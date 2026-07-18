---
spec_id: 16-ai-assisted-development-workflow
title: "AI支援による仕様駆動・テスト先行開発ワークフロー"
status: approved
version: "1.2"
approved_at: "2026-07-18"
last_updated: "2026-07-19"
source_dump: "audio_book_creation_dump_2026-07-18_235129.txt"
---

# AI支援による仕様駆動・テスト先行開発ワークフロー


> **教材生成AIとの区別**  
> 本書はChatGPTとClaude Codeによるソフトウェア開発工程を扱う。
> 教材作成時のGeminiモデル選択、資料構築、使用量制御は
> `18-ai-model-routing-and-cost-control.md`へ従う。

> **ディレクトリの区別**  
> 仕様を決めるためのタスクは`docs/spec-proposals/task/`へ置く。承認済み仕様から実装を切り出した後の実装タスクは`docs/tasks/`へ置く。両者を混在させない。


## 1. 本書の目的

本書は、オーディオブック作成ツールにおいて、仕様策定後の実装作業をChatGPTとClaude Codeへ分担するための正式な開発ワークフローを定義する。

本ワークフローでは、ChatGPTが仕様から実装可能な契約と空実装を作成し、Claude Codeがその契約を変更せずにテストとソースコードを完成させる。

主な目的は次のとおりである。

- 仕様と実装の乖離を防ぐ
- AIが実装中に責務や公開インターフェースを勝手に変更することを防ぐ
- テストケース、テストコード、ソースコードの対応関係を明確にする
- 小さな単位で実装と検証を繰り返せるようにする
- ChatGPTとClaude Codeの責務境界を明確にする
- 実行コマンドと検証結果を再現可能な形で残す
- 現行コードを維持しながら段階的に機能を追加する

---

## 2. 適用範囲

本書は、承認済み仕様から、実装タスク、テスト、ソースコード、コマンド、実装結果を作成する工程に適用する。

対象となる成果物は次のとおりである。

```text
docs/specifications/
docs/tasks/
docs/commands/
tests/
script/
```

現行プロジェクトは `script/` をアプリケーションコードの配置先として使用しているため、当面は新規コードも `script/` 配下へ配置する。

`src/` レイアウトへの移行は、本ワークフローとは別の独立した移行タスクとして扱う。

---

## 3. 基本方針

### 3.1 仕様駆動

実装タスクは、承認済み仕様書を根拠として作成する。

仕様書に根拠がない機能を、ChatGPTまたはClaude Codeが独自に追加してはならない。

### 3.2 テスト先行

Claude Codeは、ソースコードの本実装より先にテストを実装する。

対象テストが未実装またはソース未実装によって失敗する状態を確認した後、ソースコードを実装する。

### 3.3 入力不変

各工程は、前工程の正本を無断で書き換えない。

変更が必要な場合は、上位成果物へ差し戻す。

### 3.4 小さい実装単位

1つのタスクは、単独で完了判定できる小さな責務単位とする。

「TTS全体を実装する」のような大きすぎるタスクは禁止する。

### 3.5 公開契約の固定

ChatGPTが作成した公開クラス、公開関数、引数、戻り値、型、例外、ファイル配置を、Claude Codeが独自に変更してはならない。

### 3.6 実装後レビュー

Claude Codeによる実装完了後、ChatGPTまたは人間が仕様適合性をレビューする。

Claude Code自身の完了報告だけで、タスクを最終完了にしてはならない。

---

## 4. 正本の優先順位

成果物間で内容が矛盾した場合は、次の優先順位を適用する。

```text
1. 承認済み仕様書
2. タスク契約書
3. 実装済みテスト
4. 公開インターフェースの空実装
5. ソースコード本実装
6. コマンド文書
7. 実装完了報告
```

各成果物が正本となる範囲は次のとおりである。

| 成果物 | 正本となる内容 |
|---|---|
| 承認済み仕様書 | システム全体の要件、責務、制約 |
| タスク契約書 | 今回実装する範囲、対象外、受入条件 |
| 実装済みテスト | 外部から観測できる振る舞い |
| ソースコードの空実装 | 公開インターフェース、型、例外、責務境界 |
| ソースコード本実装 | 契約を満たす具体的な処理 |
| コマンド文書 | 正式な実行・確認方法 |
| 実装完了報告 | 実際に行った変更と検証結果 |

テストの空実装は、テストケースの粒度と対応関係の正本とする。

ソースコードの空実装は、公開インターフェースと責務境界の正本とする。

---

## 5. 役割分担

## 5.1 ChatGPTの責務

ChatGPTは、承認済み仕様をもとに次の作業を行う。

```text
細かい単位への実装タスク分割
↓
テストケースの抽出
↓
タスク契約書の作成
↓
テストコードの空実装
↓
ソースコードの空実装
↓
実行・確認コマンドの策定
↓
タスク一覧と依存関係の更新
↓
空実装の機械的確認
```

ChatGPTが決定する内容は次のとおりである。

- タスクID
- タスク名
- タスクの目的
- 対象範囲
- 対象外
- 依存タスク
- 根拠となる仕様
- 作成・変更を許可するファイル
- 公開クラス
- 公開関数
- 引数
- 戻り値
- データ型
- 例外型
- Protocolまたは抽象インターフェース
- CLI引数
- テストケース
- テストケースID
- 完了条件
- 実行コマンド
- 検証コマンド
- 成功条件
- コマンドの副作用

ChatGPTは、内部実装の細かなヘルパー関数まで過度に固定しない。

公開契約に影響しない内部ヘルパーは、Claude Codeが必要に応じて設計してよい。

## 5.2 Claude Codeの責務

Claude Codeは、ChatGPTが作成したタスク契約と空実装をもとに次の作業を行う。

```text
テストの本実装
↓
失敗状態の確認
↓
ソースコードの本実装
↓
対象テスト実行
↓
全体テスト実行
↓
コマンドの動作確認
↓
実装完了報告
```

Claude Codeが変更してよいものは次のとおりである。

- テスト関数の本体
- `NotImplementedError` となっている具体実装
- タスク内で許可された内部ヘルパー
- タスク内で許可されたmock
- タスク内で許可された設定
- 実装完了報告

Claude Codeが独自に変更してはならないものは次のとおりである。

- 公開関数名
- 公開クラス名
- 引数
- 戻り値
- 公開データ型
- 公開例外型
- ファイル配置
- タスクの対象範囲
- 承認済み仕様書
- 既存互換仕様
- タスクID
- テストケースID
- 完了条件

---

## 6. 全体ワークフロー

正式な実行順序を次のとおりとする。

```text
仕様策定
↓
仕様承認
↓
【ChatGPT】実装タスクの切り出し
↓
【ChatGPT】タスク契約書とテストケース作成
↓
【ChatGPT】テストの空実装
↓
【ChatGPT】ソースコードの空実装
↓
【ChatGPT】コマンド文書作成
↓
【ChatGPT】タスク一覧更新
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

---

## 7. タスクの粒度

1タスクは、次の条件を満たす単位とする。

- 単独で完了条件を判定できる
- 主要な責務が1つである
- 原則として1つの公開インターフェースまたは1つの利用者向け機能を扱う
- 変更対象のソースファイルは、おおむね1～3個である
- テストケースは、おおむね3～10件である
- 外部サービス境界は、原則として1種類までである
- 依存タスクがある場合は明示されている
- 対象外が明示されている
- 実行コマンドと完了条件が定義されている

次のように分割する。

```text
TASK-TTS-001 TTS共通インターフェース
TASK-TTS-002 VOICEVOXアダプター
TASK-TTS-003 COEIROINKアダプター
TASK-TTS-004 TTSクライアント選択レジストリ
```

次のようなタスクは禁止する。

```text
TTS機能を全部実装する
音声機能を完成させる
テストを全部追加する
```

---

## 8. タスクIDとテストケースID

## 8.1 タスクID

タスクIDは次の形式とする。

```text
TASK-<領域>-<連番3桁>
```

例：

```text
TASK-TTS-001
TASK-AUDIO-001
TASK-SCRIPT-001
TASK-APPROVAL-001
```

一度割り当てたタスクIDは、タスク名が変更されても変更しない。

## 8.2 テストケースID

テストケースIDは次の形式とする。

```text
TC-<領域>-<タスク連番3桁>-<ケース連番2桁>
```

例：

```text
TC-TTS-001-01
TC-TTS-001-02
TC-TTS-001-03
```

Pythonのテスト関数名にも、対応するIDを含める。

```python
def test_tc_tts_001_01_synthesize_returns_success() -> None:
    ...
```

---

## 9. `docs/tasks` の仕様

## 9.1 ディレクトリ構成

```text
docs/
└─ tasks/
   ├─ README.md
   ├─ INDEX.md
   ├─ TASK-TTS-001-common-interface.md
   ├─ TASK-TTS-002-voicevox-adapter.md
   └─ TASK-TTS-003-coeiroink-adapter.md
```

1タスクにつき1つのMarkdownファイルを作成する。

テストケースだけを別ファイルへ分離せず、タスク契約書の中に含める。

これにより、タスク範囲、テスト、コード、コマンド、完了条件を1か所で確認できるようにする。

## 9.2 タスク契約書の必須項目

```markdown
---
task_id:
status:
title:
spec_refs:
dependencies:
allowed_files:
command_refs:
---

# タスク名

## 目的

## 背景

## 対象

## 対象外

## 公開契約

## 作成・変更ファイル

## テストケース

## 空実装の内容

## Claude Codeへの実装指示

## 実行コマンド

## 完了条件

## 実装結果
```

## 9.3 `docs/tasks/INDEX.md`

`INDEX.md` は、すべての実装タスクを一覧管理する正本とする。

最低限、次の列を持つ。

| 項目 | 内容 |
|---|---|
| task_id | 安定したタスクID |
| title | タスク名 |
| status | 現在状態 |
| dependencies | 先行タスク |
| spec_refs | 根拠仕様 |
| task_file | タスク契約書 |
| test_files | 対応テスト |
| source_files | 対応ソース |
| command_refs | 確認コマンド |
| result | 最終結果 |

タスク状態は次のとおりとする。

```text
draft
approved
scaffolded
ready_for_claude
implementing
verification
blocked
done
```

### 状態の意味

- `draft`: タスク内容を作成中
- `approved`: タスク契約が承認済み
- `scaffolded`: テストとソースの空実装が作成済み
- `ready_for_claude`: 構文、import、収集確認が完了
- `implementing`: Claude Codeが実装中
- `verification`: 実装後の確認中
- `blocked`: 仕様矛盾や外部要因で停止
- `done`: 最終レビューまで完了

---

## 10. テストケース文書の仕様

各テストケースは、Given、When、Thenで記述する。

```markdown
### TC-TTS-001-01 正常な音声生成結果

#### Given

- 正常な `SynthesisRequest` がある
- 有効な話者IDが指定されている

#### When

- `synthesize` を呼び出す

#### Then

- `AudioResult` が返る
- `status` は `success` である
- 出力ファイルのパスが保持される
```

各ケースには、必要に応じて次も記載する。

- 前提条件
- 入力
- mock対象
- 期待値
- 発生すべき例外
- 副作用
- ファイル出力
- 再実行時の挙動

---

## 11. テスト空実装の仕様

## 11.1 基本方針

テスト空実装は、テストケースの粒度と対応関係を固定するために作成する。

空実装であってもpytestから収集できる状態にする。

## 11.2 `pass` の禁止

次の実装は禁止する。

```python
def test_example() -> None:
    pass
```

テストが未実装であるにもかかわらず、成功として扱われるためである。

## 11.3 無条件 `skip` の禁止

次のような無条件skipも禁止する。

```python
@pytest.mark.skip(reason="未実装")
def test_example() -> None:
    ...
```

未実装テストが長期間残っても検出しづらいためである。

## 11.4 `xfail(strict=True)` の使用

テスト空実装は、原則として `pytest.mark.xfail(strict=True)` と明示的失敗を使用する。

```python
import pytest


@pytest.mark.xfail(
    strict=True,
    reason="TASK-TTS-001: テストおよび実装が未完成",
)
def test_tc_tts_001_01_synthesize_returns_success() -> None:
    """
    Given:
        正常なSynthesisRequestがある。
    When:
        TTSクライアントで音声を生成する。
    Then:
        AudioResultが返される。
    """
    pytest.fail("TASK-TTS-001 test implementation pending")
```

`strict=True` により、実装後にテストが成功したにもかかわらず `xfail` を削除し忘れた場合も失敗として検出する。

## 11.5 Claude Codeによる変更

Claude Codeは、テスト本実装時に次を行う。

```text
xfailマーカーを削除
↓
テスト本体を実装
↓
ソース未実装による失敗を確認
↓
ソースコードを実装
↓
テスト成功を確認
```

## 11.6 未実装と既存不具合の区別

通常のpytest結果では次のように扱う。

```text
既存機能の不具合
＝ FAIL

計画済み未実装テスト
＝ XFAIL
```

対象タスク完了時には、次を満たす必要がある。

```text
対象タスクのXFAILが0件
対象タスクのskipが0件
対象タスクのTODOが0件
```

---

## 12. ソースコード空実装の仕様

## 12.1 目的

ソースコードの空実装は、公開インターフェース、責務境界、データ型、例外契約を固定するために作成する。

## 12.2 抽象契約

抽象的なクライアント契約には、原則として `Protocol` を使用する。

```python
from typing import Protocol


class TTSClient(Protocol):
    def health_check(self) -> bool:
        ...

    def synthesize(self, request: "SynthesisRequest") -> "AudioResult":
        ...
```

必要な場合は抽象基底クラスを使用してよい。

## 12.3 具体実装

具体クラスや具体関数の未実装部分は、`NotImplementedError` を送出する。

```python
def synthesize(request: SynthesisRequest) -> AudioResult:
    raise NotImplementedError("TASK-TTS-001")
```

次は禁止する。

```python
def synthesize(request):
    pass
```

```python
def synthesize(request):
    return None
```

```python
def synthesize(request):
    return AudioResult(status="success")
```

未実装であることを隠す仮戻り値は禁止する。

## 12.4 空実装で確定する項目

ChatGPTは、空実装時に次を確定する。

- ファイル配置
- 公開クラス名
- 公開関数名
- 引数
- 戻り値
- 型注釈
- dataclassなどの公開データ型
- enum
- 公開例外
- Protocol
- CLI引数
- docstring
- タスクIDとの対応

## 12.5 空実装で確定しない項目

次はClaude Codeへ委ねる。

- 非公開ヘルパー関数
- 内部アルゴリズム
- 内部変数名
- 公開契約に影響しないリファクタリング
- mockの内部実装
- ログメッセージの細部

---

## 13. コマンド文書の仕様

## 13.1 ディレクトリ構成

```text
docs/
└─ commands/
   ├─ README.md
   ├─ testing.md
   ├─ tts.md
   ├─ audio-validation.md
   └─ packaging.md
```

コマンドはタスク単位ではなく、用途別の文書へ集約する。

タスク契約書からコマンドIDを参照する。

## 13.2 コマンドID

```text
CMD-<領域>-<連番3桁>
```

例：

```text
CMD-TEST-001
CMD-TTS-001
CMD-AUDIO-001
```

## 13.3 コマンド定義の必須項目

```markdown
## CMD-TEST-003 TTS共通契約テスト

### 目的

### 前提条件

### 正式コマンド

### ローカル補助コマンド

### 成功条件

### 失敗時の確認事項

### 副作用

### 関連タスク
```

## 13.4 正式な実行環境

再現性を重視し、Docker上のコマンドを正式なコマンドとする。

```text
canonical_command
＝ Docker

convenience_command
＝ ローカルPython
```

ただし、VOICEVOX、COEIROINK、GUI操作など、ホスト上のサービスや画面操作が必要なものは例外とし、その理由と前提条件を明記する。

---

## 14. 外部サービスを使用するテスト

VOICEVOX、COEIROINK、Geminiなどの外部サービスを、通常の単体テストで直接呼び出してはならない。

テストを次の種類へ分離する。

```text
単体テスト
＝ 純粋関数、モデル、変換、バリデーション

mock統合テスト
＝ HTTP要求、応答、タイムアウト、エラー変換

実サービス統合テスト
＝ 専用markerと専用コマンド

手動確認
＝ 音質、発音、速度、抑揚、キャラクター適合
```

推奨するpytest markerは次のとおりである。

```text
unit
integration
external
manual
planned
```

通常の全体テストでは、外部サービスを必要とするテストを除外する。

```bash
docker compose run --rm app \
  pytest -m "not external and not manual"
```

実サービス統合テストは明示的に実行する。

```bash
docker compose run --rm app \
  pytest -m external tests/integration/
```

---

## 15. ChatGPTによる実装準備完了条件

ChatGPTが作成したタスクをClaude Codeへ渡す前に、次を満たす必要がある。

- 根拠となる承認済み仕様が明記されている
- タスクIDが割り当てられている
- 目的と対象外が明記されている
- 依存タスクが明記されている
- 許可された変更ファイルが明記されている
- テストケースIDが割り当てられている
- テスト空実装がpytestから収集される
- ソース空実装がimport可能である
- Python構文エラーがない
- 公開インターフェースが型注釈付きで定義されている
- 未実装部分が明示的に失敗する
- コマンド文書が作成されている
- 成功条件が定義されている
- `docs/tasks/INDEX.md` が更新されている
- タスク状態が `ready_for_claude` である
- 人間による実装準備承認が完了している

---

## 16. Claude Codeの実装手順

Claude Codeは、タスクごとに次の順序で実行する。

### 16.1 タスク契約の確認

次を確認する。

- 根拠仕様
- 対象
- 対象外
- 依存タスク
- 許可ファイル
- 公開契約
- テストケース
- コマンド
- 完了条件

### 16.2 テスト本実装

- `xfail` を削除する
- Given、When、Thenに対応するテストを実装する
- 外部サービスはmockする
- 正常系だけでなく異常系も実装する

### 16.3 Red確認

ソースコードを実装する前に対象テストを実行し、期待した理由で失敗することを確認する。

テストコードの誤りやimportエラーによる失敗をRed確認として扱ってはならない。

### 16.4 ソース本実装

- 公開契約を変更せず実装する
- `NotImplementedError` を除去する
- 必要な内部ヘルパーを追加する
- タスク外のリファクタリングを行わない

### 16.5 対象テスト実行

タスク文書に記載された対象テストを実行する。

### 16.6 全体テスト実行

既存テストを含む全体テストを実行し、回帰がないことを確認する。

### 16.7 コマンド確認

`docs/commands` に記載された正式コマンドを実際に確認する。

### 16.8 完了報告

変更内容、テスト結果、未解決事項、仕様との差異を記録する。

---

## 17. 仕様矛盾を発見した場合

Claude Codeが、仕様、タスク、既存コードの間に矛盾を発見した場合、公開契約へ影響する変更を独自判断で実施してはならない。

タスクを `blocked` とし、次の形式で報告する。

```markdown
## BLOCKED

- task_id: TASK-TTS-001
- conflict_type: interface_conflict
- affected_spec:
  - docs/specifications/10-tts-client-common-interface.md
- affected_files:
  - script/tts_clients/voicevox/client.py
- problem:
  現行VOICEVOXクライアントの戻り値と新しいAudioResultが両立しない。
- attempted:
  既存呼び出し箇所とテストを確認した。
- proposed_options:
  1. 互換ラッパーを追加する。
  2. すべての呼び出し側を変更する。
- recommended:
  互換ラッパーを追加する。
```

次の変更は、公開契約に影響しない限りClaude Codeが判断してよい。

- 内部ヘルパーの追加
- private関数の分割
- ローカル変数の整理
- mockの実装方法
- ログ出力の内部構成

---

## 18. Claude Code実装完了報告

Claude Codeは、タスクごとに実装完了報告を作成する。

タスク契約書の末尾へ追記するか、別の結果ファイルとして保存する。

推奨形式は次のとおりである。

```markdown
# TASK-TTS-001 実装結果

## 変更したファイル

- tests/test_tts_client_contract.py
- script/tts_clients/base.py

## 実装した内容

- SynthesisRequest
- AudioResult
- TTSClient Protocol
- 共通例外

## 実行したコマンド

- CMD-TEST-003
- CMD-TEST-ALL

## テスト結果

- 対象テスト: 8 passed
- 全体テスト: 126 passed
- failed: 0
- errors: 0
- xfail: 0
- skip: 0

## コマンド確認

- CMD-TEST-003: 成功
- CMD-TEST-ALL: 成功

## 未解決事項

なし

## 仕様との差異

なし
```

---

## 19. 実装後レビュー

Claude Codeの実装後、ChatGPTまたは人間は次を確認する。

- 仕様外の機能が追加されていないか
- 公開インターフェースが変更されていないか
- タスク対象外のファイルが変更されていないか
- テストが実装詳細へ過度に依存していないか
- 正常系と異常系が揃っているか
- `xfail`、`skip`、`TODO` が残っていないか
- 既存互換性が壊れていないか
- 不要なリファクタリングが含まれていないか
- コマンド文書が実際の実行方法と一致しているか
- 全体テストに回帰がないか
- 実装完了報告と実際の変更が一致しているか

レビューに合格した場合、タスク状態を `done` とする。

問題がある場合は差し戻し、`implementing` または `verification` へ戻す。

---

## 20. 推奨ディレクトリ構成

```text
docs/
├─ spec-proposals/
│  └─ 16-ai-assisted-development-workflow.md
├─ tasks/
│  ├─ README.md
│  ├─ INDEX.md
│  ├─ TASK-TTS-001-common-interface.md
│  ├─ TASK-TTS-002-voicevox-adapter.md
│  └─ TASK-TTS-003-coeiroink-adapter.md
└─ commands/
   ├─ README.md
   ├─ testing.md
   ├─ tts.md
   ├─ audio-validation.md
   └─ packaging.md

tests/
├─ test_tts_client_contract.py
├─ test_voicevox_client.py
└─ test_coeiroink_client.py

script/
└─ tts_clients/
   ├─ __init__.py
   ├─ base.py
   ├─ voicevox/
   │  └─ client.py
   └─ coeiroink/
      └─ client.py
```

現行の `script/` と `tests/` を維持し、新しいワークフロー用に `docs/tasks/` と `docs/commands/` を追加する。

---

## 21. 確定設定

本ワークフローでは、次の設定を正式な初期値として採用する。

```yaml
development_workflow:
  specification_owner:
    - chatgpt
    - human
  scaffold_owner:
    - chatgpt
  implementation_owner:
    - claude_code
  final_review_owner:
    - chatgpt
    - human

canonical_order:
  - approved_specification
  - task_contract
  - implemented_tests
  - public_interface
  - implementation
  - command_documentation
  - implementation_report

task_granularity:
  responsibility_per_task: 1
  recommended_source_files:
    minimum: 1
    maximum: 3
  recommended_test_cases:
    minimum: 3
    maximum: 10
  external_service_boundaries_per_task:
    maximum: 1

test_scaffold:
  allow_pass: false
  allow_unconditional_skip: false
  use_strict_xfail: true
  require_test_case_id: true
  require_given_when_then: true
  require_pytest_collection: true

source_scaffold:
  allow_pass: false
  allow_placeholder_return: false
  concrete_stub_behavior: raise_not_implemented
  prefer_protocol_for_interfaces: true
  require_type_hints: true
  public_contract_change_by_claude: prohibited

claude_code:
  implement_tests_first: true
  confirm_red_state: true
  implement_source_after_tests: true
  run_target_tests: true
  run_full_tests: true
  verify_documented_commands: true
  completion_report_required: true
  report_spec_conflicts_as_blocked: true
  unrelated_refactoring: prohibited

review:
  scaffold_approval_required: true
  post_implementation_review_required: true

commands:
  canonical_environment: docker
  local_commands_are_convenience_only: true
  require_expected_result: true
  require_side_effect_description: true
  require_command_id: true

external_tests:
  default_test_suite_uses_real_services: false
  mock_http_boundaries: true
  require_explicit_external_marker: true
  manual_audio_review_required_for:
    - pronunciation
    - speed
    - intonation
    - character_fit

paths:
  specifications: docs/specifications
  tasks: docs/tasks
  commands: docs/commands
  tests: tests
  source: script
```

---

## 22. 完了条件

本ワークフロー仕様は、次の状態になった時点で導入完了とする。

- `docs/tasks/` が作成されている
- `docs/tasks/README.md` が作成されている
- `docs/tasks/INDEX.md` が作成されている
- `docs/commands/` が作成されている
- `docs/commands/README.md` が作成されている
- 最初の実装タスクが本仕様に従って作成されている
- テスト空実装がpytestから収集できる
- ソース空実装がimportできる
- Claude Codeがタスク契約に従って実装できる
- 対象テストと全体テストを実行できる
- 実装完了報告を残せる
- 実装後レビューを実行できる

---

## 23. 確定事項まとめ

- ChatGPTは仕様、タスク分割、テストケース、空実装、コマンドを担当する
- Claude Codeはテスト本実装、ソース本実装、テスト実行、コマンド確認を担当する
- 人間またはChatGPTによる実装後レビューを必須とする
- 承認済み仕様書を最上位の正本とする
- タスクは1責務単位へ小さく分割する
- 1タスクの変更ソースは原則1～3ファイルとする
- 1タスクのテストケースは原則3～10件とする
- テスト空実装で `pass` を使用しない
- 無条件の `skip` を使用しない
- テスト空実装には `xfail(strict=True)` を使用する
- ソース空実装で `pass` や仮戻り値を使用しない
- 具体実装の空本体は `NotImplementedError` とする
- 抽象契約には原則として `Protocol` を使用する
- Claude Codeによる公開契約の変更を禁止する
- 仕様矛盾は `blocked` として報告する
- 通常テストでは実サービスを呼び出さない
- 外部サービスのテストはmock、明示的統合テスト、手動確認へ分離する
- Dockerコマンドを正式な実行方法とする
- ローカルコマンドは補助的な実行方法とする
- コマンドにはID、前提条件、成功条件、副作用を記載する
- タスクとテストには追跡可能なIDを付ける
- 実装完了報告を必須とする
- 現行の `script/` 構成を当面維持する
- `docs/tasks/` と `docs/commands/` を新設する
