---
task_type: implementation_preparation
status: blocked
order: 140
implementation_task_id: "TASK-COEIR-001"
title: "COEIROINK adapter"
phase: "4. TTSと成果物"
release_scope: "blocked"
depends_on:
  - "TASK-TTS-001"
  - "TASK-PROFILE-001"
spec_refs:
  - ../../spec-proposals/coeiroink-client.md
  - ../../specifications/19-application-scope-and-mvp.md
planned_outputs:
  test_case_contract: "docs/test-cases/TASK-COEIR-001-coeiroink-client-adapter.md"
  executable_task: "docs/tasks/TASK-COEIR-001-coeiroink-client-adapter.md"
  test_scaffolds:
    - "tests/test_coeiroink_client.py"
    - "tests/test_coeiroink_adapter.py"
  source_scaffolds:
    - "script/tts_clients/coeiroink/client.py"
    - "script/tts_clients/coeiroink/adapter.py"
  command_documents:
    - "docs/commands/tts.md"
    - "docs/commands/testing.md"
generated_from_dump: "audio_book_creation_dump_2026-07-19_155428.txt"
last_updated: "2026-07-19"
---
# TASK-COEIR-001 COEIROINK adapter

> この文書は**STEP1の実装タスク切り出し案**である。Claude Codeへ直接実装させる契約書ではない。
> STEP2〜STEP6で契約、テストケース、テスト空実装、ソース空実装、コマンド文書を作成し、
> 人間承認後のSTEP7で`docs/tasks/`へ実行可能なタスク契約書を作成する。

## 1. 単一責務

公式API・実機・利用条件確認後、外部起動COEIROINKとリリンちゃんだけを共通TTS Protocolへ追加する。

## 2. このタスクで扱う範囲

- 動的speaker/style解決
- health/list/synthesize
- engine固有parameter変換
- 音声library未導入時の局所disable
- credits manifest
- VOICEVOX継続動作

## 3. 対象外

- 同梱
- 非公式Docker前提
- つくよみちゃん/ディアちゃん初期対応
- API値の推測固定

## 4. 先行タスク

- TASK-TTS-001
- TASK-PROFILE-001

## 5. 根拠仕様

- docs/spec-proposals/coeiroink-client.md
- docs/specifications/19-application-scope-and-mvp.md

## 6. STEP2で固定する契約

次の事項を`docs/test-cases/TASK-COEIR-001-coeiroink-client-adapter.md`で具体化する。

- 公開クラス、関数、Protocol、dataclass、enum、公開例外
- Given／When／Then形式のテストケースID
- 正常系、異常系、境界値、入力不変、再実行時の挙動
- 外部サービスをmockする境界
- 許可ファイル、変更禁止ファイル
- STEP3・STEP4で作る空実装の正確なファイルパス

## 7. STEP3で予定するテスト空実装

- tests/test_coeiroink_client.py
- tests/test_coeiroink_adapter.py

テスト空実装は`pytest.mark.xfail(strict=True)`と明示的な`pytest.fail`を使用し、
`pass`、無条件`skip`、成功を装う仮assertionを使用しない。

## 8. STEP4で予定するソース空実装

- script/tts_clients/coeiroink/client.py
- script/tts_clients/coeiroink/adapter.py

ここに記載したパスはSTEP1時点の推奨配置である。STEP2の契約作成時に、
責務が1〜3主要ソースへ収まるよう最終確定する。

## 9. STEP6で予定するコマンド文書

- docs/commands/tts.md
- docs/commands/testing.md

## 10. 推奨前提・未確定事項の扱い

- なし

## 11. BLOCKED

採用version、API endpoint、既定URL、speaker/style ID、利用条件、クレジット、同梱可否の公式・実機証拠が不足している。

この根拠が解消するまで、STEP2以降で実API値や利用条件を推測して固定しない。
Protocol、mock境界、局所disable方針だけは、別の準備タスクとして扱える。

## 12. STEP7で作成する実行タスク

```text
docs/tasks/TASK-COEIR-001-coeiroink-client-adapter.md
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
