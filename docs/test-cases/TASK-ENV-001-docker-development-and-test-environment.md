---
test_case_contract_id: CONTRACT-TASK-ENV-001
implementation_task_id: TASK-ENV-001
title: Docker開発・テスト実行環境
status: review
version: '1.0'
release_scope: MVP
phase: 0. 開発基盤
depends_on:
- TASK-DEV-001
spec_refs:
- docs/specifications/16-ai-assisted-development-workflow.md
- docs/specifications/23-distribution-and-platform-policy.md
test_files:
- tests/test_container_contract.py
source_files:
- Dockerfile
- docker-compose.yml
- .dockerignore
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-ENV-001 Docker開発・テスト実行環境 — タスク契約書・テストケース
## 1. 目的
Python単体テスト、mock統合テスト、静的確認を再現可能に実行するDocker環境を固定する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- DockerfileのPython test stage
- docker-composeのtest service
- 依存インストール
- ホストVOICEVOX等を要求しない通常テスト
- Windowsからのボリューム利用方針

## 4. 対象外
- Electron GUI実行
- VOICEVOX/COEIROINK同梱
- 本番installer

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `Dockerfile` | `test stage` | 固定Python版で依存導入・pytest収集・通常テストを実行できる。 |
| `docker-compose.yml` | `test service` | ホスト外部APIを要求せず、リポジトリをread/write mountしてテストを実行する。 |
| `docker-compose.yml` | `test-live service` | 明示指定時だけ外部接続用環境変数を受け取る。 |
| `.dockerignore` | `build context policy` | 秘密値・生成物・キャッシュをbuild contextへ含めない。 |

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
| TC-ENV-001-01 | P0 | integration_mock | 通常コンテナテスト | Docker Engineが利用可能 | test serviceをbuildして実行する | 外部APIなしでpytest収集と通常テストが実行できる | `tests/test_container_contract.py` |
| TC-ENV-001-02 | P0 | static | 秘密ファイル除外 | .envやdataが作業treeに存在 | Docker build contextを検査する | 秘密・利用者data・cacheがcontextへ入らない | `tests/test_container_contract.py` |
| TC-ENV-001-03 | P1 | integration_mock | DockerfileのPython test stage | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `test stage`を通じて「DockerfileのPython test stage」を実行する | 「DockerfileのPython test stage」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_container_contract.py` |
| TC-ENV-001-04 | P1 | integration_mock | docker-composeのtest service | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `test stage`を通じて「docker-composeのtest service」を実行する | 「docker-composeのtest service」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_container_contract.py` |
| TC-ENV-001-05 | P1 | unit | 依存インストール | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `test stage`を通じて「依存インストール」を実行する | 「依存インストール」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_container_contract.py` |
| TC-ENV-001-06 | P1 | unit | ホストVOICEVOX等を要求しない通常テスト | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `test stage`を通じて「ホストVOICEVOX等を要求しない通常テスト」を実行する | 「ホストVOICEVOX等を要求しない通常テスト」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_container_contract.py` |
| TC-ENV-001-07 | P1 | unit | Windowsからのボリューム利用方針 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `test stage`を通じて「Windowsからのボリューム利用方針」を実行する | 「Windowsからのボリューム利用方針」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_container_contract.py` |
| TC-ENV-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `test stage`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_container_contract.py` |
| TC-ENV-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `test stage`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_container_contract.py` |

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_container_contract.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

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

## 14. 推奨値として採用した未確定事項
- Python versionは現行依存が動作する安定版をStep2で固定する。
