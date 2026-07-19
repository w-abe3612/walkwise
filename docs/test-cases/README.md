---
status: review
version: "1.0"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_163743.txt"
---

# タスク契約書・テストケース

## 1. 役割

`docs/test-cases/`は、承認済み仕様を実装へ移す前に、公開契約と受入テストを固定する
STEP2成果物の正本である。

ここにある文書は本実装そのものではない。次の工程が参照する。

```text
STEP2 タスク契約書・テストケース
↓
STEP3 tests配下のテスト空実装
↓
STEP4 ソースコード空実装
↓
STEP6 コマンド文書
↓
STEP7 Claude Code用実装タスク
```

## 2. 文書構成

- `INDEX.md`: 全54実装タスクの契約一覧
- `external-connectivity-policy.md`: 外部API・runtimeの疎通確認規則
- `TASK-*.md`: タスク単位の公開契約・テストケース

## 3. 状態

現在の全契約は`status: review`である。人間承認前にClaude Codeへ本実装を依頼しない。

## 4. テストケースID

```text
TC-<AREA>-<NNN>-<連番2桁>
```

例:

```text
TC-AI-001-01
TC-VOICEVOX-001-07
```

IDはSTEP3以降も変更しない。統合・削除が必要な場合は旧IDを再利用せず、理由を記録する。

## 5. 外部接続

外部APIやruntimeを使う実機能testは、必ず先に疎通確認を行う。
詳細は`external-connectivity-policy.md`を正本とする。

```text
integration_smoke
↓ 成功
integration_live
```

通常pytestでは実接続しない。

## 6. 正本の優先順位

1. 承認済み仕様、DB、画面仕様
2. 本ディレクトリの契約とテストケース
3. 人間承認済みのソース空実装
4. 人間承認済みのテスト空実装

矛盾を見つけた場合は独断で意味を変えず、blockedとして差分を報告する。

## 7. 完了後の扱い

本ディレクトリは実装完了後もテスト意図の正本として保持する。
実行タスクのように完了後削除する対象ではない。
