---
status: active
version: "1.1"
last_updated: "2026-07-18"
---

# 仕様策定タスク

このディレクトリには、まだ決めなければならない仕様テーマを置く。

## 1. 命名規則

```text
1_<theme>.md
2_<theme>.md
3_<theme>.md
...
```

完了したタスク元ファイルは、仕様へ反映後に削除してよい。
完了履歴は`INDEX.md`へ残す。

## 2. 参照

未完了タスク同士の依存:

```yaml
depends_on:
  - 1_sample-book-end-to-end-validation.md
```

承認済み仕様への参照:

```yaml
spec_refs:
  - ../../specifications/audiobook-creation-pipeline.md
```

承認済み仕様を`depends_on`へ書かない。

## 3. 作業方法

1. `INDEX.md`で次の未完了タスクを確認する。
2. `depends_on`が完了済みか確認する。
3. `spec_refs`の承認済み仕様を読む。
4. 決定事項を質問へ変換する。
5. 推奨回答をサンプルまたは実測で確認する。
6. 仕様書を`status: review`で作成する。
7. 人間承認後に`docs/specifications/`へ移す。
8. タスクを`done`へ変更する。
9. 不要になったタスク元ファイルを削除する。

## 4. 注意

```text
docs/spec-proposals/task/
＝ 仕様策定

docs/tasks/
＝ 承認済み仕様の実装
```

## 5. 実装準備タスク案

利用者の明示指示により、承認済み仕様から実装契約へ移る前段階の
「実装準備タスク切り出し案」も、このディレクトリで一時管理する。

```text
100_implementation-preparation-master-plan.md
IMPLEMENTATION_INDEX.md
101_task-...md 以降
```

これらは`docs/tasks/`に置くClaude Code実行タスクではない。

```text
docs/spec-proposals/task/
＝ 仕様策定タスク
＋ 人間承認前の実装準備タスク案

docs/tasks/
＝ STEP2〜STEP6と収集確認、人間承認を終えたClaude Code実行契約
```

実装準備タスク案は、STEP7で対応する`docs/tasks/TASK-...md`を作成した後、
Git履歴を残して削除してよい。`blocked`な案は根拠が解消するまで残す。
