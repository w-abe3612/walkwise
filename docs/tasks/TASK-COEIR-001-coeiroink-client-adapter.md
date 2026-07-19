---
document_type: claude_code_implementation_task
task_id: TASK-COEIR-001
order: 140
title: COEIROINK adapter
status: blocked
execution_gate: official_information_and_human_approval_required
release_scope: blocked
phase: 4. TTSと成果物
depends_on:
- TASK-TTS-001
- TASK-PROFILE-001
contract_ref: docs/test-cases/TASK-COEIR-001-coeiroink-client-adapter.md
preparation_ref: docs/spec-proposals/task/140_task-coeir-001-coeiroink-client-adapter.md
spec_refs:
- docs/spec-proposals/coeiroink-client.md
- docs/specifications/19-application-scope-and-mvp.md
test_files:
- tests/test_coeiroink_client.py
- tests/test_coeiroink_adapter.py
source_files:
- script/tts_clients/coeiroink/client.py
- script/tts_clients/coeiroink/adapter.py
command_documents:
- docs/commands/testing.md
- docs/commands/tts.md
documentation_repair_ownership: []
generated_from_dump: audio_book_creation_dump_2026-07-19_180714.txt
last_updated: '2026-07-19'
---
# TASK-COEIR-001 COEIROINK adapter


> **実行禁止:** このタスクはblockedである。公式API世代、endpoint、speaker/style識別子、利用条件、
> credit要件が確認され、人間が承認するまでテスト本実装・実接続・ソース本実装へ進まない。
> 推測値を固定する変更は完了扱いにしない。

## 1. 目的

公式API・実機・利用条件確認後、外部起動COEIROINKとリリンちゃんだけを共通TTS Protocolへ追加する。

## 2. 実行前ゲート

- この文書はClaude Codeへ渡すSTEP7の実行タスクである。
- 人間が本タスクを承認するまで変更を開始しない。
- 依存タスクが完了し、対象テストと全体回帰が成功していることを確認する。
- 未コミット変更を破棄する`reset`、`checkout`、一括上書きを行わない。
- 仕様と公開signatureが矛盾する場合は推測で直さず、`blocked`として報告する。

依存タスク:

- `TASK-TTS-001`
- `TASK-PROFILE-001`

## 3. 正本

優先順位:

1. 承認済み仕様・DB・画面文書
2. `docs/test-cases/TASK-COEIR-001-coeiroink-client-adapter.md`
3. STEP4ソース空実装の公開signature・型・docstring
4. STEP3テスト空実装のcase ID・Given/When/Then
5. 関連コマンド文書

仕様:

- `docs/spec-proposals/coeiroink-client.md`
- `docs/specifications/19-application-scope-and-mvp.md`

関連コマンド文書:

- `docs/commands/testing.md`
- `docs/commands/tts.md`

## 4. 変更範囲

### テスト

- `tests/test_coeiroink_client.py`
- `tests/test_coeiroink_adapter.py`

### production source

- `script/tts_clients/coeiroink/client.py`
- `script/tts_clients/coeiroink/adapter.py`

### 扱う範囲

- 動的speaker/style解決
- health/list/synthesize
- engine固有parameter変換
- 音声library未導入時の局所disable
- credits manifest
- VOICEVOX継続動作

### 対象外

- 同梱
- 非公式Docker前提
- つくよみちゃん/ディアちゃん初期対応
- API値の推測固定

他タスクの公開契約やcase IDを都合よく変更しない。共通helperが必要な場合は、既存の公開境界を維持し、
変更理由と影響範囲を完了報告へ記録する。


## 5. コマンド文書の整合性

関連するコマンド文書を実行し、対象パス・marker・環境変数・実行順序が実装と一致することを確認する。
古い欠落記述を発見した場合は、担当タスクを確認して勝手に重複修正せず、完了報告へ記録する。


## 6. 公開契約

| module / file | public symbol | 契約 |
|---|---|---|
| `script/tts_clients/coeiroink/client.py` | `CoeiroinkHttpClient.check_connectivity/list_speakers/synthesize` | 公式確認後にのみ具体endpointを固定する。 |
| `script/tts_clients/coeiroink/adapter.py` | `CoeiroinkAdapter.synthesize(request) -> SynthesisResult` | 共通TTS契約へ適合し、未導入時は局所disableする。 |
| `script/tts_clients/coeiroink/adapter.py` | `build_credits_manifest(...)` | 確認済み必須creditを出力する。 |

### 共通規則
- 公開関数・methodは型注釈を持つ。
- 業務上予測可能な失敗は安定したerror codeへ変換する。
- 入力正本を直接変更しない。既存正常成果物を失敗時に削除・上書きしない。
- 外部依存、時計、乱数、filesystem、DBはテストで注入または隔離可能にする。
- 本書にない公開symbolを安易に追加しない。内部helperは非公開とする。

## 7. テストケース

本タスクでは次のcase IDをすべて本実装する。

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

実装規則:

- Pythonは対象caseの`xfail(strict=True)`と明示的`pytest.fail`を、実際のassertionへ置き換える。
- Vitestは対象caseの`test.fails`と明示的errorを、実際の検証へ置き換える。
- case ID、Given、When、Thenを削除しない。
- 先にテストを本実装し、productionが未実装であることによるRedを確認する。
- import error、構文error、fixture欠落だけをRed確認として扱わない。
- mock対象と実接続対象を混同しない。
- 既存成果物・入力の不変性、再実行時の決定性、失敗時の部分成果物を検証する。

## 8. 実装手順

1. `git status --short`と`git diff --stat`で開始状態を記録する。
2. `docs/commands/preflight.md`を実行し、予定test fileが`109/109`存在することを確認する。
3. 正本、ソース空実装、テスト空実装を読み、公開signatureとcase IDを照合する。
4. このタスクのテストだけを本実装する。
5. 対象テストを実行し、production未実装に起因するRedを確認して記録する。
6. このタスクのsourceだけを本実装する。
7. 対象テストを再実行して成功させる。
8. 関連コマンド文書の手順を実行する。
9. 全Python回帰、TypeScript型検査、Vitest回帰を実行する。
10. 担当する古い記述を修正し、文書と実状態を一致させる。
11. 差分を確認し、完了報告を作成する。

## 9. 対象コマンド

### Python collection

```powershell
python -m pytest --collect-only -q tests/test_coeiroink_client.py tests/test_coeiroink_adapter.py
```

### 外部接続なしのPython対象テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_coeiroink_client.py tests/test_coeiroink_adapter.py
```

### Vitest対象テスト

```powershell
# Vitest対象なし
```

### 全体回帰

```powershell
python -m compileall -q script tests
python -m pytest --collect-only -q
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
npm run typecheck
npm test
```

Node依存が未導入で`package-lock.json`がない場合は、`docs/commands/environment.md`の初回固定手順に従う。
依存導入ができない環境では成功を装わず、未実行理由を報告する。


## 10. 外部疎通・実機能テスト

このタスクは外部接続gate対象である。通常テストで外部接続してはならない。

必須順序:

```text
設定確認
↓
integration_smoke
↓ 成功時のみ
integration_live
```

契約:

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

- smoke失敗時はliveを実行しない。
- live testは対応するconnectivity fixtureを必須引数にする。
- 秘密値をログ・例外・pytest reportへ出さない。
- 固定・短時間・最小回数の入力だけを使用する。


## 11. 完了条件

- case ID 12件がすべて実テストになり、対象テストがpassする。
- 対象sourceに、このタスク由来の`NotImplementedError`・明示的未実装errorが残らない。
- 対象外タスクのxfailやblocked状態を解除していない。
- 通常テストが外部API・外部runtimeへ接続しない。
- 外部gate対象の場合、smoke成功記録なしにliveを実行していない。
- Python全体、TypeScript型検査、Vitest全体の結果を報告している。
- 担当コマンド文書が実装と一致し、古い欠落記述を残していない。
- 入力正本と既存正常成果物を破壊していない。

## 12. 停止条件

次の場合は実装を推測で続行せず、`blocked`として報告する。

- 上位仕様と公開signatureが矛盾する。
- 必須fixture・runtime・公式情報が不足する。
- 依存タスクが未完了で、公開境界を確定できない。
- 権利・license・credit条件が不明な外部engineを有効化する必要がある。
- 実データ、秘密値、利用者Projectをテストへ使う必要が生じる。
- 本タスクの変更許可範囲を超える仕様変更が必要になる。

## 13. Claude Code完了報告

```text
タスクID:
開始時Git状態:
変更ファイル:
実装したcase ID:
Red確認コマンドと原因:
対象テスト結果:
全体pytest結果:
TypeScript型検査結果:
Vitest結果:
外部疎通実行の有無:
smoke結果:
live結果:
修正した古い文書記述:
未実行項目と理由:
残課題:
```
