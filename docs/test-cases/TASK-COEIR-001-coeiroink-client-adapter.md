---
test_case_contract_id: CONTRACT-TASK-COEIR-001
implementation_task_id: TASK-COEIR-001
title: COEIROINK adapter
status: review
version: '1.0'
release_scope: blocked
phase: 4. TTSと成果物
depends_on:
- TASK-TTS-001
- TASK-PROFILE-001
spec_refs:
- docs/spec-proposals/coeiroink-client.md
- docs/specifications/19-application-scope-and-mvp.md
test_files:
- tests/test_coeiroink_client.py
- tests/test_coeiroink_adapter.py
source_files:
- script/tts_clients/coeiroink/client.py
- script/tts_clients/coeiroink/adapter.py
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-COEIR-001 COEIROINK adapter — タスク契約書・テストケース
## 1. 目的
公式API・実機・利用条件確認後、外部起動COEIROINKとリリンちゃんだけを共通TTS Protocolへ追加する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- 動的speaker/style解決
- health/list/synthesize
- engine固有parameter変換
- 音声library未導入時の局所disable
- credits manifest
- VOICEVOX継続動作

## 4. 対象外
- 同梱
- 非公式Docker前提
- つくよみちゃん/ディアちゃん初期対応
- API値の推測固定

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/tts_clients/coeiroink/client.py` | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize` | 公式確認後にのみ具体endpointを固定する。 |
| `script/tts_clients/coeiroink/adapter.py` | `CoeiroinkAdapter.synthesize(request) -> SynthesisResult` | 共通TTS契約へ適合し、未導入時は局所disableする。 |
| `script/tts_clients/coeiroink/adapter.py` | `build_credits_manifest(...)` | 確認済み必須creditを出力する。 |

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
- 対象: **COEIROINK API**
- 必須fixture: `coeiroink_connectivity_gate`
- 設定: `COEIROINK_URL`
- 疎通確認: 公式API世代・health/list endpoint確定後、話者一覧または公式health endpointを1回実行し、versionと応答schemaを確認する。
- 実機能確認: 疎通成功かつリリンちゃんの識別子解決後、極短い固定文を合成し、有効な音声応答とcredits metadataを確認する。
- 実機能テストは疎通fixtureを引数として必須要求する。
- 設定不足時はnetworkへ出ず、秘密値を表示せず明示的にskipする。
- 疎通失敗時は疎通テストをfailとし、その実行に属する実機能テストは理由付きskipとする。
- 疎通確認で生成物、DB更新、課金の大きい処理を行わない。避けられない最小課金は明記する。
- 本タスクは外部仕様のevidence gapが解消するまで`blocked`であり、実endpointを推測して空実装へ固定しない。

## 8. fixture契約
- `tmp_path`配下だけを使用する一時Project/data root
- 固定timezone付きclock
- 決定的ID generator
- 秘密値を含まない設定fixture
- 成功・validation error・timeout・破損応答を返す依存stub/mock
- `coeiroink_connectivity_gate`: 疎通結果、version、接続先の秘密でない識別情報を保持するsession scope fixture

## 9. テストケース
| ID | 優先 | layer | テスト内容 | Given | When | Then | 実装先 |
|---|---|---|---|---|---|---|---|
| TC-COEIR-001-01 | P0 | contract | blocked保持 | 公式endpoint/ID未確定 | STEP3/4へ進める判断 | 実APIの具体値を固定せずblockedを維持 | `tests/test_coeiroink_client.py` |
| TC-COEIR-001-02 | P0 | unit | 局所disable | COEIROINK/音声library不在 | registry/list | VOICEVOXやアプリ全体は利用可能 | `tests/test_coeiroink_adapter.py` |
| TC-COEIR-001-03 | P0 | integration_mock | 動的話者 | 公式API応答が利用可能 | list | リリンちゃんをIDから解決しhardcodeしない | `tests/test_coeiroink_client.py` |
| TC-COEIR-001-04 | P1 | unit | health/list/synthesize | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize`を通じて「health/list/synthesize」を実行する | 必要項目を欠かさず安定順で返し、空一覧も正常結果として扱う。 | `tests/test_coeiroink_adapter.py` |
| TC-COEIR-001-05 | P1 | unit | engine固有parameter変換 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize`を通じて「engine固有parameter変換」を実行する | 「engine固有parameter変換」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_coeiroink_client.py` |
| TC-COEIR-001-06 | P1 | unit | 音声library未導入時の局所disable | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize`を通じて「音声library未導入時の局所disable」を実行する | 有効なmedia header・形式・順序を確認し、破損または形式不一致を成功扱いにしない。 | `tests/test_coeiroink_adapter.py` |
| TC-COEIR-001-07 | P1 | unit | credits manifest | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize`を通じて「credits manifest」を実行する | 必須ID・revision・hash・provenanceを含む決定的なmanifestを生成し、参照切れを拒否する。 | `tests/test_coeiroink_client.py` |
| TC-COEIR-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_coeiroink_adapter.py` |
| TC-COEIR-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_coeiroink_client.py` |
| TC-COEIR-001-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_coeiroink_adapter.py` |
| TC-COEIR-001-11 | P0 | integration_smoke | COEIROINK APIの疎通確認 | 実接続テストが明示的に有効化され、必要な設定が存在する | 公式API世代・health/list endpoint確定後、話者一覧または公式health endpointを1回実行し、versionと応答schemaを確認する。 | ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。 | `tests/test_coeiroink_client.py` |
| TC-COEIR-001-12 | P1 | integration_live | COEIROINK APIの実機能テスト | `coeiroink_connectivity_gate`が成功済み | 疎通成功かつリリンちゃんの識別子解決後、極短い固定文を合成し、有効な音声応答とcredits metadataを確認する。 | 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。 | `tests/test_coeiroink_adapter.py` |

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_coeiroink_client.py`
- `tests/test_coeiroink_adapter.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `script/tts_clients/coeiroink/client.py`
- `script/tts_clients/coeiroink/adapter.py`

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
