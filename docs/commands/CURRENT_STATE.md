---
document_type: preparation_state
status: in_progress
version: "2.0"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_173616.txt"
current_state_verified: "2026-07-19"
verified_by: "TASK-DEV-001 implementation session"
---

# 実装準備状態(実測)

本書はダンプ記載の数値ではなく、`2026-07-19`にリポジトリを直接実測した結果を正本とする。
過去のダンプに基づく件数(19件存在・90件欠落・22件収集・17 xfailed / 5 skipped 等)は
すべて古い状態であり、現在の状態を示すものではない。

## 集計

| 項目 | 件数 |
|---|---:|
| STEP2タスク契約 | 54 |
| 契約上のtest file | 109 |
| 現在存在するtest file | 109 |
| 現在欠落するtest file | 0 |
| STEP6の計画command document | 38 |
| 実装完了タスク | 1 (`TASK-DEV-001`) |
| 未実装タスク(STEP3/STEP4空実装のまま) | 53 |

## 判定

STEP3のPythonテスト空実装・STEP4のソース空実装は109/109件そろっている。
`TASK-DEV-001`(Pythonパッケージ・pytest収集基盤)は本実装・Red確認・全体回帰まで
完了し、対象10ケース(TC-DEV-001-01〜10)がすべてpassする。他の53タスクは未着手であり、
strict xfail・明示的`NotImplementedError`・opt-in skipのままである。
人間承認gateの通過は`TASK-DEV-001`の変更範囲に限る。他タスクの承認gateは
それぞれの実装完了後に別途判定する。

## 現在確認できるtest file

契約上の109件すべてが存在する。個別ファイル名の一覧は
[`STEP6_MANIFEST.json`](STEP6_MANIFEST.json)の`planned_test_files`を正本とする。
本書には重複して一覧を持たない。

## 欠落test file

なし(0件)。

## 実測した確認結果(2026-07-19)

外部接続なしで次を確認した。

| 確認 | 結果 |
|---|---|
| 契約上のtest file 109件の存在確認 | 109/109 成功(欠落0) |
| Python構文 (`python -m compileall -q script tests`) | 成功 |
| Python production import (`script`配下、`__init__.py`除く) | 99 module成功、失敗0 |
| pytest collection (`--collect-only -q`) | 454件収集、未知marker warningなし |
| pytest通常実行 (`-m "not integration_smoke and not integration_live and not performance and not resilience"`) | 10 passed, 23 deselected, 421 xfailed |
| pytest通常実行 (marker指定なし) | 10 passed, 23 skipped, 421 xfailed |
| Electron/Vitest test file | 16件存在 |
| `package-lock.json` | このセッションで新規生成(`npm install`初回実行)。以後`npm ci`を正式コマンドとする。 |
| TypeScript型検査 (`npm run typecheck` / `tsc --noEmit`) | 成功、error 0件 |
| Vitest (`npm test -- --run`) | 16 test files / 76 tests、すべてpassed |
| 外部接続 | 0 |

pytestの実行方法によって「23 deselected」(`-m`でmarker除外)と「23 skipped」
(marker除外なし、conftestの動的skip)のいずれかで表示されるが、対象件数はどちらも
同じ23件であり、内容に矛盾はない。

`TASK-DEV-001`が対象とした10ケースは、この実測でxfailedからpassedへ移行した分であり、
他タスクのxfailed/skipped件数には影響していない。

## 次に必要な作業

1. `docs/tasks/`のSTEP7実行タスクを、`depends_on`の順序に従って1つずつ選び、
   TASK-DEV-001と同じ手順(テスト本実装 → Red確認 → production実装 → 対象テスト
   → 全体回帰 → 文書修正)で進める。
2. 各タスクは、自身の`documentation_repair_ownership`に列挙された文書だけを修正する。
   本書とSTEP6_MANIFEST.jsonの全体集計は、進捗に応じて実装タスク側から更新する。
3. `docs/commands/`配下の分野別コマンド文書(38件)には、本ダンプ由来の古い
   「19件/90件/22件/17 xfailed/5 skipped」という記述がまだ残っているものがある。
   該当ドキュメントの古い記述修正は、それぞれの担当タスク
   (`documentation_repair_ownership`)が実装時に行う。本書と`README.md`・
   `testing.md`・`STEP6_MANIFEST.json`の4件は本タスク(`TASK-DEV-001`)の担当として
   修正済みである。
