---
test_case_contract_id: CONTRACT-TASK-AUDIO-003
implementation_task_id: TASK-AUDIO-003
title: 章MP3・text成果物・manifest・Build orchestration
status: review
version: '1.0'
release_scope: MVP
phase: 4. TTSと成果物
depends_on:
- TASK-AUDIO-002
- TASK-ARTIFACT-001
- TASK-JOB-001
- TASK-BUILD-001
spec_refs:
- docs/specifications/14-audio-packaging.md
- docs/specifications/02-process-input-output.md
- docs/db/05-artifacts-table.md
test_files:
- tests/test_audio_packaging.py
- tests/test_build_pipeline.py
- tests/test_production_manifest.py
source_files:
- script/audio/packaging.py
- script/pipelines/build.py
- script/schemas/production_manifest.py
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-AUDIO-003 章MP3・text成果物・manifest・Build orchestration — タスク契約書・テストケース
## 1. 目的
Build Requestのmp3/text選択に従い、章MP3、verified text、audio/production manifestを生成してArtifact登録する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- manifest順でWAV結合
- 章単位MP3
- tag metadata
- text artifact
- 複数形式同時生成
- 形式ごとversion
- validation gate
- partial failure policy
- Job progress/result
- deliverables gate

## 4. 対象外
- 全文MP3
- M4B
- UI

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/audio/packaging.py` | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact` | 形式一致を確認し章MP3をatomic生成する。 |
| `script/schemas/production_manifest.py` | `ProductionManifest.validate()/to_mapping()` | 入力revision、音声順、hash、閾値状態を記録する。 |
| `script/pipelines/build.py` | `BuildPipeline.run(build_request_id) -> BuildResult` | 承認gateから複数形式Artifact登録までを順序制御する。 |

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
| TC-AUDIO-003-01 | P0 | integration_mock | 複数形式 | Build Requestがmp3+text | run | 別file/Artifactとして両方生成し上書きしない | `tests/test_audio_packaging.py` |
| TC-AUDIO-003-02 | P0 | integration_mock | 承認gate | verified_scriptまたはpreview_audio未承認 | run | TTS/packagingを開始しない | `tests/test_build_pipeline.py` |
| TC-AUDIO-003-03 | P0 | unit | manifest順序 | 複数segment/part | package | manifest順と章音声順が一致 | `tests/test_production_manifest.py` |
| TC-AUDIO-003-04 | P1 | unit | 章単位MP3 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact`を通じて「章単位MP3」を実行する | 有効なmedia header・形式・順序を確認し、破損または形式不一致を成功扱いにしない。 | `tests/test_audio_packaging.py` |
| TC-AUDIO-003-05 | P1 | unit | tag metadata | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact`を通じて「tag metadata」を実行する | 「tag metadata」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_build_pipeline.py` |
| TC-AUDIO-003-06 | P1 | unit | 複数形式同時生成 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact`を通じて「複数形式同時生成」を実行する | 「複数形式同時生成」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_production_manifest.py` |
| TC-AUDIO-003-07 | P1 | unit | 形式ごとversion | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact`を通じて「形式ごとversion」を実行する | versionを記録し、未知・不一致・改変を検出して黙って互換扱いしない。 | `tests/test_audio_packaging.py` |
| TC-AUDIO-003-08 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_build_pipeline.py` |
| TC-AUDIO-003-09 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `ChapterPackager.package(wavs, metadata) -> ChapterArtifact`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_production_manifest.py` |
| TC-AUDIO-003-10 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_audio_packaging.py` |

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_audio_packaging.py`
- `tests/test_build_pipeline.py`
- `tests/test_production_manifest.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `script/audio/packaging.py`
- `script/pipelines/build.py`
- `script/schemas/production_manifest.py`

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
