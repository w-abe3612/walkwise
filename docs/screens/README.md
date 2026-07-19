---
status: active
version: "1.0"
last_updated: "2026-07-19"
---

# 承認済み画面仕様

## 1. 役割

このディレクトリには、承認済みの画面構成、画面責務、表示項目、操作、状態、
画面遷移を置く。`docs/screens/`は承認済み画面仕様の正本である。

## 2. 格納対象

- 各画面の目的、route/window内navigation ID
- 表示項目、入力項目、操作
- Electron mainへ要求するIPC(`docs/specifications/20-electron-desktop-architecture.md`の
  IPCチャネルと対応させる)
- empty/loading/success/error/disabled状態
- キーボード操作、破壊操作の確認
- 関連DB table、関連する承認済み仕様
- MVP対象外の明記

## 3. 格納禁止対象

- 未承認・provisional・blockedな画面追加案(→`docs/spec-proposals/`)
- DBテーブル定義(→`docs/db/`)
- 実際のVueコンポーネントコード

## 4. 昇格・削除のライフサイクル

1. 画面追加・変更案は、まず`docs/spec-proposals/`へ提案として作成する。
2. MVP範囲(`docs/specifications/19-application-scope-and-mvp.md`)と整合し、
   既存承認済み画面と矛盾しないことを人間が確認した場合のみ、本ディレクトリへ昇格する。
3. 昇格後、対応する提案ファイルは削除する。

## 5. 正本の優先順位

```text
1. docs/specifications/ (製品全体の方針・アーキテクチャ)
2. docs/db/ (DBスキーマ)
3. docs/screens/<NN>-<screen名>.md (個別画面仕様)
```

画面仕様が承認済みDBスキーマと矛盾する場合、DBスキーマ側を正本とし、
画面仕様側を修正する。

## 6. ファイル命名規則

```text
01-project-list-and-create.md
02-project-workspace-and-source-import.md
03-build-settings.md
04-job-progress.md
05-artifacts.md
```

`<連番2桁>-<screen名(kebab-case)>.md`とする。

## 7. 画面数を増やしすぎない

MVPでは5画面を基本とする。設定・診断機能が必要な場合、専用画面を追加せず、
各画面へ最小限の表示として統合することを優先する。画面追加は、
4節の昇格手順を経てから行う。
