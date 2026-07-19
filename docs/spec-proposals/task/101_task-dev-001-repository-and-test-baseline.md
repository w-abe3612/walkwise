---
task_type: implementation_preparation
status: draft
order: 101
implementation_task_id: "TASK-DEV-001"
title: "Pythonパッケージ・pytest収集基盤"
phase: "0. 開発基盤"
release_scope: "MVP"
depends_on: []
spec_refs:
  - ../../specifications/16-ai-assisted-development-workflow.md
  - ../../specifications/00-specification-guidelines.md
planned_outputs:
  test_case_contract: "docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md"
  executable_task: "docs/tasks/TASK-DEV-001-repository-and-test-baseline.md"
  test_scaffolds:
    - "tests/test_test_environment_contract.py"
  source_scaffolds:
    - "pyproject.toml または pytest.ini"
    - "tests/conftest.py"
    - "script/__init__.py"
  command_documents:
    - "docs/commands/testing.md"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
last_updated: "2026-07-19"
---
# TASK-DEV-001 Pythonパッケージ・pytest収集基盤

> この文書は**STEP1の実装タスク切り出し案**である。Claude Codeへ直接実装させる契約書ではない。
> STEP2〜STEP6で契約、テストケース、テスト空実装、ソース空実装、コマンド文書を作成し、
> 人間承認後のSTEP7で`docs/tasks/`へ実行可能なタスク契約書を作成する。

## 1. 単一責務

以後の全Python空実装とテスト空実装を、import可能かつpytestで収集可能にする最小開発基盤を固定する。

## 2. このタスクで扱う範囲

- script配下のPython package境界
- pytest設定とmarker方針
- 共通fixture配置
- 外部サービスを通常テストから除外する既定値
- 構文・import・collection確認の入口

## 3. 対象外

- 各機能の本実装
- Electronのnpm toolchain
- 実サービス統合テスト

## 4. 先行タスク

- なし

## 5. 根拠仕様

- docs/specifications/16-ai-assisted-development-workflow.md
- docs/specifications/00-specification-guidelines.md

## 6. STEP2で固定する契約

次の事項を`docs/test-cases/TASK-DEV-001-repository-and-test-baseline.md`で具体化する。

- 公開クラス、関数、Protocol、dataclass、enum、公開例外
- Given／When／Then形式のテストケースID
- 正常系、異常系、境界値、入力不変、再実行時の挙動
- 外部サービスをmockする境界
- 許可ファイル、変更禁止ファイル
- STEP3・STEP4で作る空実装の正確なファイルパス

## 7. STEP3で予定するテスト空実装

- tests/test_test_environment_contract.py

テスト空実装は`pytest.mark.xfail(strict=True)`と明示的な`pytest.fail`を使用し、
`pass`、無条件`skip`、成功を装う仮assertionを使用しない。

## 8. STEP4で予定するソース空実装

- pyproject.toml または pytest.ini
- tests/conftest.py
- script/__init__.py

ここに記載したパスはSTEP1時点の推奨配置である。STEP2の契約作成時に、
責務が1〜3主要ソースへ収まるよう最終確定する。

## 9. STEP6で予定するコマンド文書

- docs/commands/testing.md

## 10. 推奨前提・未確定事項の扱い

- 正式コマンドはDockerとするが、このタスクではローカル収集確認も定義する。

## 11. 準備継続条件

- 根拠仕様と矛盾しない。
- 主要責務が一つである。
- STEP2で3〜10件程度のテストケースへ落とせる。
- 公開契約を空実装として固定できる。
- 外部サービスの実呼び出しを通常テストから分離できる。

上記を満たせない場合は、STEP2で子タスクへ分割し、元のtask IDを親追跡IDとして維持する。

## 12. STEP7で作成する実行タスク

```text
docs/tasks/TASK-DEV-001-repository-and-test-baseline.md
```

この実行タスクには、Claude Codeが次を順番どおり行う指示を含める。

```text
テスト本実装
↓
未実装によるRed確認
↓
ソースコード本実装
↓
対象テスト
↓
全体テスト
↓
文書記載コマンド
↓
実装完了報告
↓
ChatGPTまたは人間による仕様適合レビュー
```

## 13. STEP1完了条件

- 安定したtask IDが割り当てられている。
- 依存関係とrelease scopeが明記されている。
- 根拠仕様、対象、対象外が区別されている。
- STEP2〜STEP7の成果物予定が追跡できる。
- この文書だけを根拠にClaude Codeへ本実装を依頼しないことが明記されている。
