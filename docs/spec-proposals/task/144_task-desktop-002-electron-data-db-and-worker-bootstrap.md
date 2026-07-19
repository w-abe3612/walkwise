---
task_type: implementation_preparation
status: draft
order: 144
implementation_task_id: "TASK-DESKTOP-002"
title: "Electron起動時data/DB/worker bootstrap"
phase: "5. Workerとデスクトップ"
release_scope: "MVP"
depends_on:
  - "TASK-DESKTOP-001"
  - "TASK-DB-001"
  - "TASK-WORKER-002"
spec_refs:
  - ../../specifications/17-local-data-persistence-policy.md
  - ../../specifications/20-electron-desktop-architecture.md
  - ../../specifications/21-electron-python-worker-interface.md
planned_outputs:
  test_case_contract: "docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md"
  executable_task: "docs/tasks/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md"
  test_scaffolds:
    - "electron/tests/bootstrap.test.ts"
    - "electron/tests/worker_manager.test.ts"
  source_scaffolds:
    - "electron/main/bootstrap.ts"
    - "electron/main/database.ts"
    - "electron/main/worker_manager.ts"
  command_documents:
    - "docs/commands/desktop.md"
    - "docs/commands/database.md"
    - "docs/commands/testing.md"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
last_updated: "2026-07-19"
---
# TASK-DESKTOP-002 Electron起動時data/DB/worker bootstrap

> この文書は**STEP1の実装タスク切り出し案**である。Claude Codeへ直接実装させる契約書ではない。
> STEP2〜STEP6で契約、テストケース、テスト空実装、ソース空実装、コマンド文書を作成し、
> 人間承認後のSTEP7で`docs/tasks/`へ実行可能なタスク契約書を作成する。

## 1. 単一責務

アプリ起動時に利用者data root、DB backup/migration、stale Job復旧、Python worker実行環境を準備する。

## 2. このタスクで扱う範囲

- appData配下root
- DB open/migrate
- backup
- stale recovery
- Python executable解決
- worker spawn manager
- shutdown cleanup
- 起動失敗UI error契約

## 3. 対象外

- 各IPC use case
- 画面実装
- installer同梱

## 4. 先行タスク

- TASK-DESKTOP-001
- TASK-DB-001
- TASK-WORKER-002

## 5. 根拠仕様

- docs/specifications/17-local-data-persistence-policy.md
- docs/specifications/20-electron-desktop-architecture.md
- docs/specifications/21-electron-python-worker-interface.md

## 6. STEP2で固定する契約

次の事項を`docs/test-cases/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md`で具体化する。

- 公開クラス、関数、Protocol、dataclass、enum、公開例外
- Given／When／Then形式のテストケースID
- 正常系、異常系、境界値、入力不変、再実行時の挙動
- 外部サービスをmockする境界
- 許可ファイル、変更禁止ファイル
- STEP3・STEP4で作る空実装の正確なファイルパス

## 7. STEP3で予定するテスト空実装

- electron/tests/bootstrap.test.ts
- electron/tests/worker_manager.test.ts

テスト空実装は`pytest.mark.xfail(strict=True)`と明示的な`pytest.fail`を使用し、
`pass`、無条件`skip`、成功を装う仮assertionを使用しない。

## 8. STEP4で予定するソース空実装

- electron/main/bootstrap.ts
- electron/main/database.ts
- electron/main/worker_manager.ts

ここに記載したパスはSTEP1時点の推奨配置である。STEP2の契約作成時に、
責務が1〜3主要ソースへ収まるよう最終確定する。

## 9. STEP6で予定するコマンド文書

- docs/commands/desktop.md
- docs/commands/database.md
- docs/commands/testing.md

## 10. 推奨前提・未確定事項の扱い

- なし

## 11. 準備継続条件

- 根拠仕様と矛盾しない。
- 主要責務が一つである。
- STEP2で3〜10件程度のテストケースへ落とせる。
- 公開契約を空実装として固定できる。
- 外部サービスの実呼び出しを通常テストから分離できる。

上記を満たせない場合は、STEP2で子タスクへ分割し、元のtask IDを親追跡IDとして維持する。

## 12. STEP7で作成する実行タスク

```text
docs/tasks/TASK-DESKTOP-002-electron-data-db-and-worker-bootstrap.md
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
