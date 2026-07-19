---
document_type: claude_code_execution_rules
status: review
version: "1.0"
last_updated: "2026-07-19"
---

# Claude Code共通実行規則

## 1. 変更単位

- 原則として1回の作業で1タスクだけを実装する。
- 依存タスクが完了していない場合は開始しない。
- 未コミット変更を破棄しない。
- 上位仕様を推測で書き換えない。
- public signatureを変更する必要がある場合は停止し、差分を報告する。

## 2. テスト駆動順序

```text
STEP3テスト空実装を本実装
↓
production未実装によるRed確認
↓
STEP4 source空実装を本実装
↓
対象テスト成功
↓
全体回帰
↓
コマンド文書・古い状態記述の修正
```

Red確認は構文error、import error、fixture欠落ではなく、期待する業務挙動が未実装であることによる失敗でなければならない。

## 3. 外部接続

```text
設定確認
↓
integration_smoke
↓ 成功時のみ
integration_live
```

- 通常テストでは外部接続しない。
- smoke失敗時はliveを実行しない。
- API keyや秘密値を出力しない。
- COEIROINKはblocked解除まで実接続しない。

## 4. 文書修正

- `generated_from_dump`は来歴であり、現在状態の意味で上書きしない。
- 揮発性の「存在／欠落」注記は個別コマンド文書から除去する。
- 現在状態は`docs/commands/CURRENT_STATE.md`とmanifestへ集約する。
- 実測していない結果を記載しない。

## 5. 禁止事項

- `git reset --hard`、無断checkout、一括生成による既存変更の消去
- 対象外タスクのxfail解除
- post-MVP／blocked機能のMVP混入
- 実利用者データをfixtureに使用
- 失敗をskipや対象除外で隠す
- 未実装をpass、ダミーassert、空catchで隠す
