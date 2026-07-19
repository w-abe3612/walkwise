---
test_case_contract_id: CONTRACT-TASK-ASR-001
implementation_task_id: TASK-ASR-001
title: ASRによる原稿・音声照合
status: review
version: '1.0'
release_scope: post-MVP
phase: 4. TTSと成果物
depends_on:
- TASK-AUDIO-003
spec_refs:
- docs/specifications/asr-script-audio-verification.md
test_files:
- tests/test_asr_verification.py
source_files:
- script/asr/base.py
- script/asr/verification.py
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-ASR-001 ASRによる原稿・音声照合 — タスク契約書・テストケース
## 1. 目的
local Whisper-compatible adapterで音声を文字化し、実際のtts_textとsegment/章単位に補助照合する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- local adapter
- cloud off
- segment alignment
- chapter fallback
- terminology normalization
- 差分report
- ASR単独fail禁止
- review_required候補

## 4. 対象外
- クラウドASR
- 品質の最終合否
- MVP gate

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/asr/base.py` | `ASRClient Protocol: check_connectivity()/transcribe()` | local runtime/model確認と文字起こしを分離する。 |
| `script/asr/verification.py` | `ASRVerifier.verify(audio, tts_segments, terminology) -> ASRVerificationReport` | segment alignmentと章fallbackを行い差分候補を返す。 |
| `script/asr/verification.py` | `normalize_for_comparison(text, terminology) -> str` | 用語辞書を用いて比較用にだけ正規化する。 |

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
- 対象: **ローカルWhisper互換runtime**
- 必須fixture: `asr_connectivity_gate`
- 設定: `WALKWISE_ASR_ENABLED`
- 疎通確認: runtime/modelの存在・読込可否・versionを確認し、まだ音声文字起こしは行わない。
- 実機能確認: 疎通成功後、数秒の固定fixture WAVだけを文字起こしし、非空segmentとtimestamp順を確認する。
- 実機能テストは疎通fixtureを引数として必須要求する。
- 設定不足時はnetworkへ出ず、秘密値を表示せず明示的にskipする。
- 疎通失敗時は疎通テストをfailとし、その実行に属する実機能テストは理由付きskipとする。
- 疎通確認で生成物、DB更新、課金の大きい処理を行わない。避けられない最小課金は明記する。

## 8. fixture契約
- `tmp_path`配下だけを使用する一時Project/data root
- 固定timezone付きclock
- 決定的ID generator
- 秘密値を含まない設定fixture
- 成功・validation error・timeout・破損応答を返す依存stub/mock
- `asr_connectivity_gate`: 疎通結果、version、接続先の秘密でない識別情報を保持するsession scope fixture

## 9. テストケース
| ID | 優先 | layer | テスト内容 | Given | When | Then | 実装先 |
|---|---|---|---|---|---|---|---|
| TC-ASR-001-01 | P0 | unit | ASR単独fail禁止 | 大きな差分report | verify | review_required候補に留め最終failにしない | `tests/test_asr_verification.py` |
| TC-ASR-001-02 | P0 | unit | segment fallback | segment alignment不能 | verify | 章単位比較へfallbackし理由を記録 | `tests/test_asr_verification.py` |
| TC-ASR-001-03 | P0 | unit | 用語正規化 | SQL/エスキューエル辞書 | 比較 | 辞書上同義として扱い原稿自体は変更しない | `tests/test_asr_verification.py` |
| TC-ASR-001-04 | P1 | unit | local adapter | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ASRClient Protocol: check_connectivity()/transcribe()`を通じて「local adapter」を実行する | 「local adapter」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_asr_verification.py` |
| TC-ASR-001-05 | P1 | unit | cloud off | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ASRClient Protocol: check_connectivity()/transcribe()`を通じて「cloud off」を実行する | 通常・実接続テストともcloud endpointへ送信せず、network clientが呼ばれていないことを確認する。 | `tests/test_asr_verification.py` |
| TC-ASR-001-06 | P1 | unit | terminology normalization | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ASRClient Protocol: check_connectivity()/transcribe()`を通じて「terminology normalization」を実行する | 「terminology normalization」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_asr_verification.py` |
| TC-ASR-001-07 | P1 | unit | 差分report | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ASRClient Protocol: check_connectivity()/transcribe()`を通じて「差分report」を実行する | 「差分report」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_asr_verification.py` |
| TC-ASR-001-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `ASRClient Protocol: check_connectivity()/transcribe()`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_asr_verification.py` |
| TC-ASR-001-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `ASRClient Protocol: check_connectivity()/transcribe()`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_asr_verification.py` |
| TC-ASR-001-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_asr_verification.py` |
| TC-ASR-001-11 | P0 | integration_smoke | ローカルWhisper互換runtimeの疎通確認 | 実接続テストが明示的に有効化され、必要な設定が存在する | runtime/modelの存在・読込可否・versionを確認し、まだ音声文字起こしは行わない。 | ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。 | `tests/test_asr_verification.py` |
| TC-ASR-001-12 | P1 | integration_live | ローカルWhisper互換runtimeの実機能テスト | `asr_connectivity_gate`が成功済み | 疎通成功後、数秒の固定fixture WAVだけを文字起こしし、非空segmentとtimestamp順を確認する。 | 最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。 | `tests/test_asr_verification.py` |

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_asr_verification.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `script/asr/base.py`
- `script/asr/verification.py`

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
