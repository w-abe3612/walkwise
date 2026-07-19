---
test_case_contract_id: CONTRACT-TASK-MIGRATION-001
implementation_task_id: TASK-MIGRATION-001
title: 旧形式・既存client互換adapter
status: review
version: '1.0'
release_scope: MVP
phase: 6. 移行・品質・配布
depends_on:
- TASK-CORE-002
- TASK-SCRIPT-001
- TASK-VOICEVOX-001
spec_refs:
- docs/specifications/15-migration-and-compatibility.md
- docs/specifications/02-process-input-output.md
test_files:
- tests/test_legacy_migration.py
- tests/test_legacy_input_priority.py
source_files:
- script/migration/legacy_models.py
- script/migration/adapters.py
- script/migration/report.py
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-MIGRATION-001 旧形式・既存client互換adapter — タスク契約書・テストケース
## 1. 目的
book.json、sections.json、旧TXT、旧VOICEVOX CLI等を新契約へ明示変換し、新規書込みは新形式へ統一する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- bookId/project_id
- sectionId/chapter_id
- full_book/book
- approval.yaml/approvals.yaml
- legacy text priority
- provenance
- legacy_input warning
- 旧client wrapper

## 4. 対象外
- 旧形式への新規書込み
- 無断ディレクトリ改名
- データ破棄

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/migration/legacy_models.py` | `LegacyBook/LegacySection/LegacyAudioInput` | 旧book.json、sections.json等を型付けする。 |
| `script/migration/adapters.py` | `migrate_legacy_project(path, destination) -> MigrationResult` | 新形式を優先し、不足時だけ旧形式を変換する。 |
| `script/migration/report.py` | `MigrationReport` | 変換、warning、provenance、未移行項目を記録する。 |

### 5.1 共通規則
- 公開関数・methodは型注釈を持つ。
- 業務上予測可能な失敗は安定したerror codeへ変換する。
- 入力正本を直接変更しない。既存正常成果物を失敗時に削除・上書きしない。
- 外部依存、時計、乱数、filesystem、DBはテストで注入または隔離可能にする。
- 本書にない公開symbolを安易に追加しない。内部helperは非公開とする。

## 6. テスト層と実行方針
| layer | 外部接続 | 目的 |
|---|---:|---|
| `unit` | なし | 純粋処理、validation、状態遷移、error変換 |
| `integration_mock` | なし | DB、filesystem、HTTP/subprocess/IPCをfixtureまたはmockで結合 |
| `integration_smoke` | 明示opt-in | 軽量な疎通確認だけを行う |
| `integration_live` | 明示opt-in | 疎通成功後だけ最小の実機能を検証する |
| `e2e` | 原則mock | UI/worker/DB/fileを含む利用者導線 |
| `performance` / `resilience` | 専用実行 | 性能・障害注入。通常pytestから除外 |

通常の`pytest`は外部API、VOICEVOX、COEIROINK、Tesseract、ffmpeg、ASR modelへ接続しない。

## 7. 外部疎通ゲート
このタスクの通常受入は外部API疎通を必要としない。外部依存を間接利用する場合も、当該adapterタスクの疎通fixtureを再利用し、本タスク独自の無秩序な実接続を追加しない。

## 8. fixture契約
- `tmp_path`配下だけを使用する一時Project/data root
- 固定timezone付きclock
- 決定的ID generator
- 秘密値を含まない設定fixture
- 成功・validation error・timeout・破損応答を返す依存stub/mock

## 9. テストケース
| ID | 優先 | layer | テスト内容 | Given | When | Then | 実装先 |
|---|---|---|---|---|---|---|---|
| TC-MIGRATION-001-01 | P0 | unit | 新形式優先 | 新旧両形式がある | read/migrate | 新形式を採用し旧形式を上書きしない | `tests/test_legacy_migration.py` |
| TC-MIGRATION-001-02 | P0 | unit | full_book正規化 | 旧unit_id=full_book | migrate | bookへ変換しprovenanceを記録 | `tests/test_legacy_input_priority.py` |
| TC-MIGRATION-001-03 | P0 | unit | 不明項目 | 変換不能field | migrate | 推測せずwarning/reportへ残す | `tests/test_legacy_migration.py` |
| TC-MIGRATION-001-04 | P1 | unit | bookId/project_id | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `LegacyBook/LegacySection/LegacyAudioInput`を通じて「bookId/project_id」を実行する | 「bookId/project_id」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_legacy_input_priority.py` |
| TC-MIGRATION-001-05 | P1 | unit | sectionId/chapter_id | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `LegacyBook/LegacySection/LegacyAudioInput`を通じて「sectionId/chapter_id」を実行する | 「sectionId/chapter_id」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_legacy_migration.py` |
| TC-MIGRATION-001-06 | P1 | unit | approval.yaml/approvals.yaml | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `LegacyBook/LegacySection/LegacyAudioInput`を通じて「approval.yaml/approvals.yaml」を実行する | 必要な承認が揃う場合だけ後工程へ進み、未承認・invalidated・changes_requestedでは安定errorで停止する。 | `tests/test_legacy_input_priority.py` |
| TC-MIGRATION-001-07 | P1 | unit | legacy text priority | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `LegacyBook/LegacySection/LegacyAudioInput`を通じて「legacy text priority」を実行する | 「legacy text priority」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_legacy_migration.py` |
| TC-MIGRATION-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `LegacyBook/LegacySection/LegacyAudioInput`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_legacy_input_priority.py` |
| TC-MIGRATION-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `LegacyBook/LegacySection/LegacyAudioInput`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_legacy_migration.py` |
| TC-MIGRATION-001-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_legacy_input_priority.py` |

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_legacy_migration.py`
- `tests/test_legacy_input_priority.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `script/migration/legacy_models.py`
- `script/migration/adapters.py`
- `script/migration/report.py`

公開symbolは5節と一致させ、未実装本体は型付きの`NotImplementedError`または言語相当の明示的未実装errorを返す。import、構文、pytest/test collectionを壊す未定義参照を残さない。

## 12. 変更許可範囲
- STEP2: 本書と`docs/test-cases/INDEX.md`、共通policy文書のみ。
- STEP3: 10節のtest fileと共通fixture設定のみ。
- STEP4: 11節のsource fileと必要なpackage `__init__`のみ。
- 承認済み仕様、DB、画面仕様の意味変更は別の仕様変更として扱う。

## 13. 完了条件
- 公開契約、正常系、異常系、境界値、入力不変、再実行時挙動がテスト可能である。
- すべてのcase IDが一意で、予定test fileへ割り当てられている。
- 外部実機能テストは、該当する場合、疎通確認fixtureを必須依存している。
- 通常pytestが外部接続や有料APIを呼ばない。
- post-MVP/blockedの範囲がMVPへ混入していない。
