---
test_case_contract_id: CONTRACT-TASK-IMAGE-002
implementation_task_id: TASK-IMAGE-002
title: 画像前処理・品質flag・見開き分割
status: review
version: '1.0'
release_scope: MVP
phase: 2. 資料入力
depends_on:
- TASK-IMAGE-001
spec_refs:
- docs/specifications/image-material-ingestion.md
- docs/specifications/source-preprocessing.md
test_files:
- tests/test_image_preprocessing.py
- tests/test_image_quality_flags.py
source_files:
- script/source_processing/images/preprocess.py
- script/source_processing/images/quality.py
generated_from_dump: audio_book_creation_dump_2026-07-19_163743.txt
last_updated: '2026-07-19'
---
# TASK-IMAGE-002 画像前処理・品質flag・見開き分割 — タスク契約書・テストケース
## 1. 目的
原画像を変更せず、OCR向け派生PNG、回転/傾き/台形/contrast候補、品質flag、見開きmappingを生成する。
本書はSTEP2の正本であり、STEP3のテスト空実装、STEP4のソース空実装、STEP7のClaude Code用実装タスクが守る公開契約と受入条件を定義する。
## 2. 正本と競合時の優先順位
1. `docs/specifications/`、`docs/db/`、`docs/screens/`の承認済み仕様
2. 本書の業務ルール、公開symbol、テストケースID
3. STEP4で作成し人間承認されたソース空実装のsignature・型・docstring
4. STEP3で作成し人間承認されたテスト空実装

上位と矛盾した場合は推測で修正せず、タスクを`blocked`として差分を報告する。
## 3. 対象範囲
- 決定的な低リスク補正
- before/after hash
- 品質warning
- blank候補は削除しない
- 見開き分割とlocator対応
- 再処理可能なparameter manifest

## 4. 対象外
- 生成AIによる画像補正
- 原画像上書き
- 高リスク箇所の自動承認

## 5. 公開契約
| module / file | public symbol | 契約 |
|---|---|---|
| `script/source_processing/images/preprocess.py` | `ImagePreprocessor.process(page, options) -> PreprocessedPage` | 原画像を変えずOCR用PNGと変換manifestを生成する。 |
| `script/source_processing/images/preprocess.py` | `split_spread(page) -> tuple[PreprocessedPage, PreprocessedPage]` | 左右locatorを保持して見開きを分割する。 |
| `script/source_processing/images/quality.py` | `assess_image_quality(page) -> ImageQualityReport` | blank/blur/skew/contrast/vertical候補をflag化する。 |

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
| TC-IMAGE-002-01 | P0 | unit | 原画像不変 | 回転・contrast処理対象 | preprocessする | 原画像hash不変で派生PNGとparametersを保存 | `tests/test_image_preprocessing.py` |
| TC-IMAGE-002-02 | P0 | unit | blank候補 | ほぼ白紙の画像 | quality評価する | 削除せずblank_candidate warningにする | `tests/test_image_quality_flags.py` |
| TC-IMAGE-002-03 | P0 | unit | 見開きlocator | 見開き画像 | splitする | 左右の元page座標対応を保持する | `tests/test_image_preprocessing.py` |
| TC-IMAGE-002-04 | P1 | unit | 決定的な低リスク補正 | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「決定的な低リスク補正」を実行する | 「決定的な低リスク補正」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。 | `tests/test_image_quality_flags.py` |
| TC-IMAGE-002-05 | P1 | unit | before/after hash | 承認済み仕様に適合する最小入力と、必要な依存をmockした状態 | `ImagePreprocessor.process(page, options) -> PreprocessedPage`を通じて「before/after hash」を実行する | 同一の正規化入力から同一SHA-256を返し、内容差分があればhashが変化する。 | `tests/test_image_preprocessing.py` |
| TC-IMAGE-002-06 | P0 | unit | 必須入力欠落 | 主ID、必須path、必須設定のいずれかが欠落した入力 | `ImagePreprocessor.process(page, options) -> PreprocessedPage`を実行する | 副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。 | `tests/test_image_quality_flags.py` |
| TC-IMAGE-002-07 | P1 | unit | 再実行時の決定性 | 同じ入力、同じ設定、同じ依存応答 | `ImagePreprocessor.process(page, options) -> PreprocessedPage`を2回実行する | 仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。 | `tests/test_image_preprocessing.py` |
| TC-IMAGE-002-08 | P0 | unit | 入力・既存成果物の不変性 | hash取得済みの入力と既存正常成果物 | 正常処理または意図的な失敗を発生させる | 入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。 | `tests/test_image_quality_flags.py` |

## 10. STEP3テスト空実装への引継ぎ
- `tests/test_image_preprocessing.py`
- `tests/test_image_quality_flags.py`

各テスト関数は本書のcase IDをdocstringまたはmarkerへ記録する。空実装段階では`pytest.mark.xfail(strict=True)`と明示的`pytest.fail`を使い、`pass`、無条件skip、常に成功する仮assertionを禁止する。ただし疎通・実接続テストは外部test opt-inがない場合のみ契約どおりskip可能とする。

## 11. STEP4ソース空実装への引継ぎ
- `script/source_processing/images/preprocess.py`
- `script/source_processing/images/quality.py`

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
