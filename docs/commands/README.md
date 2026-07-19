---
document_type: command_directory_guide
status: review
version: "1.1"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_173616.txt"
current_state_verified: "2026-07-19"
---

# Walkwise コマンド文書

## 1. 役割

`docs/commands/`は、Claude Codeが各タスクについて次を再現可能に実行するための正本である。

```text
テスト本実装
↓
未実装による失敗状態の確認
↓
ソースコード本実装
↓
対象テスト
↓
全体テスト
↓
文書記載コマンド確認
↓
実装完了報告
```

コマンド文書は実装そのものではない。STEP3/STEP4の空実装段階では、
strict xfail、明示的`NotImplementedError`、opt-in skipが残る。

## 2. 実行原則

- リポジトリrootで実行する。
- 最初に[`preflight.md`](preflight.md)を実行する。
- Pythonの正式な再現コマンドはDockerを基本とする。
- Electron/Vitest、GUI、ローカルVOICEVOX等はhost実行を許可する。
- 通常テストは外部API・外部runtimeへ接続しない。
- 外部実機能テストは、必ず`integration_smoke`成功後に`integration_live`を実行する。
- 性能と障害注入は専用opt-inで実行する。
- コマンド失敗をskip、xfail、対象除外によって隠さない。

## 3. 現在の状態

test fileの現在の存在件数・欠落件数、pytest collection実測値、Node依存状態は
[`CURRENT_STATE.md`](CURRENT_STATE.md)と`STEP6_MANIFEST.json`を正本とする。
本書はコマンド文書全体の役割・実行原則・構成だけを固定し、揮発する存在件数を
ここへ重複記載しない。

- 全54タスクのうち、実装が完了しpassしているのは`TASK-DEV-001`のみである
  (`docs/tasks/TASK-DEV-001-repository-and-test-baseline.md`)。他タスクはSTEP3/STEP4の
  空実装(strict xfail / `NotImplementedError` / opt-in skip)のままである。
- 個別タスクの現在の欠落・完了状況を確認する場合は、必ず`CURRENT_STATE.md`の実測値を
  読み、本書やタスク文書に残る過去のダンプ由来の数値を鵜呑みにしない。

## 4. 文書構成

- [`INDEX.md`](INDEX.md): コマンド文書一覧
- [`preflight.md`](preflight.md): 構文、依存、予定ファイル存在確認
- [`external-connectivity.md`](external-connectivity.md): 疎通→実機能の共通手順
- [`task-command-matrix.md`](task-command-matrix.md): 54タスクとコマンド文書の対応
- [`CURRENT_STATE.md`](CURRENT_STATE.md): 最新ダンプ上の準備状態
- `STEP6_MANIFEST.json`: 機械可読の対応表・欠落一覧
- その他38件: 分野別の正式コマンド

## 5. PowerShell表記

Windowsを主対象とするため、環境変数の例はPowerShellを正本とする。

```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m integration_smoke
```

実行後に環境変数を解除する場合:

```powershell
Remove-Item Env:WALKWISE_RUN_INTEGRATION_SMOKE -ErrorAction SilentlyContinue
Remove-Item Env:WALKWISE_RUN_INTEGRATION_LIVE -ErrorAction SilentlyContinue
```

## 6. Claude Codeへの禁止事項

- 文書にない外部接続を追加しない。
- 疎通確認を省略しない。
- API keyをcommand line引数へ直接書かない。
- 利用者の実Projectをtest fixtureにしない。
- `COEIROINK_URL`、speaker ID、API endpointを推測しない。
- provisional音声閾値をapprovedとして扱わない。
