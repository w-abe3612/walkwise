---
task_type: implementation_preparation
status: draft
order: 154
implementation_task_id: "TASK-RELEASE-002"
title: "性能・耐障害・最終release受入"
phase: "6. 移行・品質・配布"
release_scope: "MVP"
depends_on:
  - "TASK-E2E-001"
  - "TASK-RELEASE-001"
spec_refs:
  - ../../specifications/22-job-lifecycle-and-recovery.md
  - ../../specifications/23-distribution-and-platform-policy.md
  - ../../specifications/19-application-scope-and-mvp.md
planned_outputs:
  test_case_contract: "docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md"
  executable_task: "docs/tasks/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md"
  test_scaffolds:
    - "tests/performance/test_large_sources.py"
    - "tests/resilience/test_failure_recovery.py"
  source_scaffolds:
    - "tests/performance/test_large_sources.py"
    - "tests/resilience/test_failure_recovery.py"
    - "release/checklist.md"
  command_documents:
    - "docs/commands/performance.md"
    - "docs/commands/release.md"
    - "docs/commands/testing.md"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
last_updated: "2026-07-19"
---
# TASK-RELEASE-002 性能・耐障害・最終release受入

> この文書は**STEP1の実装タスク切り出し案**である。Claude Codeへ直接実装させる契約書ではない。
> STEP2〜STEP6で契約、テストケース、テスト空実装、ソース空実装、コマンド文書を作成し、
> 人間承認後のSTEP7で`docs/tasks/`へ実行可能なタスク契約書を作成する。

## 1. 単一責務

大規模PDF/画像、長時間Job、再起動、disk不足、破損DB、部分失敗を検証し、MVP release判定を行う。

## 2. このタスクで扱う範囲

- 性能基準の測定記録
- メモリ/処理時間
- cancel/restart
- disk full
- DB backup復旧
- 既存成果物保持
- installer smoke test
- MVP対象外非表示
- release checklist

## 3. 対象外

- post-MVP機能完成
- 性能値の根拠なき保証
- 自動公開

## 4. 先行タスク

- TASK-E2E-001
- TASK-RELEASE-001

## 5. 根拠仕様

- docs/specifications/22-job-lifecycle-and-recovery.md
- docs/specifications/23-distribution-and-platform-policy.md
- docs/specifications/19-application-scope-and-mvp.md

## 6. STEP2で固定する契約

次の事項を`docs/test-cases/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md`で具体化する。

- 公開クラス、関数、Protocol、dataclass、enum、公開例外
- Given／When／Then形式のテストケースID
- 正常系、異常系、境界値、入力不変、再実行時の挙動
- 外部サービスをmockする境界
- 許可ファイル、変更禁止ファイル
- STEP3・STEP4で作る空実装の正確なファイルパス

## 7. STEP3で予定するテスト空実装

- tests/performance/test_large_sources.py
- tests/resilience/test_failure_recovery.py

テスト空実装は`pytest.mark.xfail(strict=True)`と明示的な`pytest.fail`を使用し、
`pass`、無条件`skip`、成功を装う仮assertionを使用しない。

## 8. STEP4で予定するソース空実装

- tests/performance/test_large_sources.py
- tests/resilience/test_failure_recovery.py
- release/checklist.md

ここに記載したパスはSTEP1時点の推奨配置である。STEP2の契約作成時に、
責務が1〜3主要ソースへ収まるよう最終確定する。

## 9. STEP6で予定するコマンド文書

- docs/commands/performance.md
- docs/commands/release.md
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
docs/tasks/TASK-RELEASE-002-performance-resilience-and-release-acceptance.md
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
