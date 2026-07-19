---
document_type: claude_code_implementation_task
task_id: TASK-DEV-001
order: 101
title: Pythonパッケージ・pytest収集基盤
status: review
execution_gate: human_approval_required
release_scope: MVP
phase: 0. 開発基盤
depends_on: []
contract_ref: docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md
preparation_ref: docs/spec-proposals/task/101_task-dev-001-repository-and-test-baseline.md
spec_refs:
- docs/specifications/16-ai-assisted-development-workflow.md
- docs/specifications/00-specification-guidelines.md
test_files:
- tests/test_test_environment_contract.py
source_files:
- pyproject.toml または pytest.ini
- tests/conftest.py
- script/__init__.py
command_documents:
- docs/commands/testing.md
documentation_repair_ownership:
- docs/commands/CURRENT_STATE.md
- docs/commands/README.md
- docs/commands/STEP6_MANIFEST.json
- docs/commands/testing.md
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-DEV-001 Pythonパッケージ・pytest収集基盤


## 1. 目的

以後の全Python空実装とテスト空実装を、import可能かつpytestで収集可能にする最小開発基盤を固定する。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- なし

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/specifications/16-ai-assisted-development-workflow.md`
- `docs/specifications/00-specification-guidelines.md`

関連コマンド文書:

- `docs/commands/testing.md`

## 4. 変更範囲

### テスト

- `tests/test_test_environment_contract.py`

### production source

- `pyproject.toml または pytest.ini`
- `tests/conftest.py`
- `script/__init__.py`

### 扱う範囲

- script配下のPython package境界
- pytest設定とmarker方針
- 共通fixture配置
- 外部サービスを通常テストから除外する既定値
- 構文・import・collection確認の入口

### 対象外

- 各機能の本実装
- Electronのnpm toolchain
- 実サービス統合テスト

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. 古い記述の修正責任

このタスクは、実装と同時に次の古い状態記述を修正する責任を持つ。

- `docs/commands/CURRENT_STATE.md`
- `docs/commands/README.md`
- `docs/commands/STEP6_MANIFEST.json`
- `docs/commands/testing.md`

修正方針:

1. 対象ファイル一覧の`— 現在のダンプでは欠落`および`— 存在`のような揮発性注記を削除する。
2. 個別コマンド文書はパスと実行方法を正本とし、存在状態は`CURRENT_STATE.md`へ集約する。
3. 「19件存在・90件欠落・22件収集・17 xfailed / 5 skipped」など、現在と矛盾する記述を残さない。
4. 実測せずにpass件数やNode検査結果を創作しない。
5. 修正後、`rg "現在のダンプでは欠落|90件|19件|22件のみ|17 xfailed" docs/commands`を実行し、
   意図的な履歴説明以外に古い状態が残っていないことを確認する。

さらに、次の現在値を実測結果へ更新する。

- 契約上のtest file: `109/109`
- pytest collection: `454`
- 通常実行: `431 xfailed / 23 skipped`
- 外部接続: `0`
- `current_missing_test_files`: 空配列
- `current_missing_test_file_count`: `0`

`generated_from_dump`は生成元の来歴なので、単純に最新名へ書き換えてはならない。
現在状態を示すフィールドが必要なら`verified_against_dump`または同等の明示的な項目を追加する。



## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `pyproject.toml / pytest.ini` | `pytest markers` | unit, integration_mock, integration_smoke, integration_live, e2e, performance, resilience を登録する。 |
| `tests/conftest.py` | `external_tests_enabled() -> bool` | 外部接続テストの明示的有効化を判定する。既定はFalse。 |
| `tests/conftest.py` | `require_environment(name: str) -> str` | 必要な環境変数がない場合、秘密値を表示せず明示的にskipする。 |
| `script/__init__.py` | `package boundary` | `script`を副作用なくimport可能にする。 |

### 共通規則
- 公開関数・methodは型注釈を持つ。
- 業務上予測可能な失敗は安定したerror codeへ変換する。
- 入力正本を直接変更しない。既存正常成果物を失敗時に削除・上書きしない。
- 外部依存、時計、乱数、filesystem、DBはテストで注入または隔離可能にする。
- 本書にない公開symbolを安易に追加しない。内部helperは非公開とする。

## 7. テストケース

本タスクでは次のcase IDをすべて本実装する。

| ID | 優先 | layer | テスト内容 | Given | When | Then | 実装先 |
|---|---|---|---|---|---|---|---|
| TC-DEV-001-01 | P0 | static | pytest収集 | リポジトリ直下で依存が揃い、外部サービス環境変数は未設定 | `pytest --collect-only -q`を実行する | 全テストモジュールをnetwork接続なしで収集し、未知marker warningがない | `tests/test_test_environment_contract.py` |
| TC-DEV-001-02 | P0 | contract | 外部テスト既定無効 | 通常pytest実行 | integration_smoke/live marker付きテストを収集・実行する | 明示opt-inがなければ外部接続せずskip理由が表示される | `tests/test_test_environment_contract.py` |
| TC-DEV-001-03 | P0 | unit | 秘密値非表示 | API key環境変数が設定済み | skip/error/logを生成する | 秘密値本体が出力へ含まれない | `tests/test_test_environment_contract.py` |
| TC-DEV-001-04 | P1 | unit | script配下のPython package境界 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `pytest markers`を通じて「script配下のPython package境界」を実行する | 「script配下のPython package境界」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_test_environment_contract.py` |
| TC-DEV-001-05 | P1 | unit | 共通fixture配置 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `pytest markers`を通じて「共通fixture配置」を実行する | 「共通fixture配置」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_test_environment_contract.py` |
| TC-DEV-001-06 | P1 | unit | 外部サービスを通常テストから除外する既定値 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `pytest markers`を通じて「外部サービスを通常テストから除外する既定値」を実行する | 「外部サービスを通常テストから除外する既定値」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_test_environment_contract.py` |
| TC-DEV-001-07 | P1 | unit | 構文・import・collection確認の入口 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `pytest markers`を通じて「構文・import・collection確認の入口」を実行する | 「構文・import・collection確認の入口」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_test_environment_contract.py` |
| TC-DEV-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `pytest markers`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_test_environment_contract.py` |
| TC-DEV-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `pytest markers`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_test_environment_contract.py` |
| TC-DEV-001-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_test_environment_contract.py` |

実装規則:

- Pythonは対象caseの`xfail(strict=True)`と明示的`pytest.fail`を、実際のassertionへ置き換える。
- Vitestは対象caseの`test.fails`と明示的errorを、実際の検証へ置き換える。
- case ID、Given、When、Thenを削除しない。
- 先にテストを本実装し、productionが未実装であることによるRedを確認する。
- import error、構文error、fixture欠落だけをRed確認として扱わない。
- mock対象と実接続対象を混同しない。
- 既存成果物・入力の不変性、再実行時の決定性、失敗時の部分成果物を検証する。

## 8. 実装手順

1. `git status --short`と`git diff --stat`で開始状態を記録する。
2. `docs/commands/preflight.md`を実行し、予定test fileが`109/109`存在することを確認する。
3. 正本、ソース空実装、テスト空実装を読み、公開signatureとcase IDを照合する。
4. このタスクのテストだけを本実装する。
5. 対象テストを実行し、production未実装に起因するRedを確認して記録する。
6. このタスクのsourceだけを本実装する。
7. 対象テストを再実行して成功させる。
8. 関連コマンド文書の手順を実行する。
9. 全Python回帰、TypeScript型検査、Vitest回帰を実行する。
10. 担当する古い記述を修正し、文書と実状態を一致させる。
11. 差分を確認し、完了報告を作成する。

## 9. 対象コマンド

### Python collection

```powershell
python -m pytest --collect-only -q tests/test_test_environment_contract.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_test_environment_contract.py
```

### Vitest対象テスト

```powershell
# Vitest対象なし
```

### 全体回帰

```powershell
python -m compileall -q script tests
python -m pytest --collect-only -q
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
npm run typecheck
npm test
```

Node依存が未導入で`package-lock.json`がない場合は、`docs/commands/environment.md`の初回固定手順に従う。
依存導入ができない環境では成功を装わず、未実行理由を報告する。


## 10. 外部接続

このタスク単独の外部接続は不要である。HTTP、音声engine、OCR、ffmpeg、ASRなどを間接利用する場合も、
対応adapterのmockまたは既存connectivity gateを使用し、独自の実接続経路を追加しない。


## 11. 完了条件

- case ID 10件がすべて実テストになり、対象テストがpassする。
- 対象sourceに、このタスク由来の`NotImplementedError`・明示的未実装errorが残らない。
- 対象外タスクのxfailやblocked状態を解除していない。
- 通常テストが外部API・外部runtimeへ接続しない。
- 外部gate対象の場合、smoke成功記録なしにliveを実行していない。
- Python全体、TypeScript型検査、Vitest全体の結果を報告している。
- 担当コマンド文書が実装と一致し、古い欠落記述を残していない。
- 入力正本と既存正常成果物を破壊していない。

## 12. 停止条件

次の場合は実装を推測で続行せず、`blocked`として報告する。

- 上位仕様と公開signatureが矛盾する。
- 必須fixture・runtime・公式情報が不足する。
- 依存タスクが未完了で、公開境界を確定できない。
- 権利・license・credit条件が不明な外部engineを有効化する必要がある。
- 実データ、秘密値、利用者Projectをテストへ使う必要が生じる。
- 本タスクの変更許可範囲を超える仕様変更が必要になる。

## 13. Claude Code完了報告

```text
タスクID:
開始時Git状態:
変更ファイル:
実装したcase ID:
Red確認コマンドと原因:
対象テスト結果:
全体pytest結果:
TypeScript型検査結果:
Vitest結果:
外部疎通実行の有無:
smoke結果:
live結果:
修正した古い文書記述:
未実行項目と理由:
残課題:
```
