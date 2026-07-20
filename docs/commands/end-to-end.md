---
document_type: command_reference
status: review
version: '1.2'
last_updated: '2026-07-20'
related_tasks:
- TASK-DESKTOP-003
- TASK-E2E-001
release_scopes:
- MVP
---

# end-to-end コマンド

## 1. 目的

mock中心のMVP導線とsample-book受入検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-DESKTOP-003` — Desktop最短end-to-end導線（MVP）
  - 契約: `docs/test-cases/TASK-DESKTOP-003-desktop-end-to-end-integration.md`
- `TASK-E2E-001` — サンプル1章fixture・仕様間受入検証（MVP）
  - 契約: `docs/test-cases/TASK-E2E-001-sample-book-fixtures-and-acceptance.md`

## 3. 実行前提

- リポジトリrootで実行する。
- 実行前に`git status --short`で既存変更を確認し、未コミット変更を破棄しない。
- 通常テストでは外部API、VOICEVOX、COEIROINK、Tesseract、ffmpeg、ASRへ接続しない。
- Pythonの正式な再現コマンドはDockerを基本とし、Electron/Vitestとローカルruntime疎通はhostで実行する。
- `docs/commands/preflight.md`のテストファイル存在確認が成功してから対象テストへ進む。

```powershell
git status --short
python --version
node --version
npm --version
```

## 4. 対象ファイル

- `electron/tests/e2e/mvp-flow.test.ts` — `TASK-DESKTOP-003`完了。TC-02,04,06,08,10
  (計5 case)、実測pass済み(2026-07-20)。TC-12(integration_live)は
  `WALKWISE_RUN_INTEGRATION_LIVE`未設定のため既定skip。
- `tests/integration/test_mvp_flow.py` — `TASK-DESKTOP-003`完了。TC-01,03,05,07,09
  (計5 case)、実測pass済み(2026-07-20)。TC-11(integration_smoke)は
  `WALKWISE_PYTHON_EXECUTABLE`未設定のため既定skip。
- `tests/integration/test_sample_book_e2e.py` — `TASK-E2E-001`完了。TC-01〜10
  (計10 case)、実測pass済み(2026-07-20)。TC-11(integration_smoke)/
  TC-12(integration_live)は`voicevox_connectivity_gate`を再利用し、
  `VOICEVOX_URL`未設定のため既定skip。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/integration/test_mvp_flow.py tests/integration/test_sample_book_e2e.py
```
```powershell
npm run typecheck
```
```powershell
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/integration/test_mvp_flow.py tests/integration/test_sample_book_e2e.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/integration/test_mvp_flow.py tests/integration/test_sample_book_e2e.py
```
### Vitest
```powershell
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

## 7. 補助・運用コマンド

### mock E2E Python
```powershell
python -m pytest -ra tests/integration -m "e2e and not integration_live"
```
### Electron E2E
```powershell
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

## 8. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-DESKTOP-003: Desktop統合runtime

- connectivity fixture: `desktop_connectivity_gate`
- 注意: 疎通は起動・preload・DB/worker health。本E2Eで初めてProjectを作成。
- 秘密環境変数: なし

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
npm test -- electron/tests/e2e/mvp-flow.test.ts
```

### TASK-E2E-001: 任意の実VOICEVOX

- connectivity fixture: `voicevox_connectivity_gate`
- 注意: 通常受入はmock。実VOICEVOXは任意で、疎通後のみ。
- 必要設定: `VOICEVOX_URL`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/integration/test_sample_book_e2e.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/integration/test_sample_book_e2e.py
```


## 9. 全体回帰

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```
```powershell
npm run typecheck
```
```powershell
npm test
```

## 10. 成功条件

- 対象test fileがすべて収集される。
- 未知marker、import error、TypeScript型errorがない。
- 通常テストが外部接続しない。
- `TASK-DESKTOP-003`の対象10 case(TS 5件+Python 5件)はpass済み
  (2026-07-20実測)。`TASK-E2E-001`(`test_sample_book_e2e.py`)の
  TC-01〜10(計10 case)もpass済み(2026-07-20実測)。TC-11/TC-12は
  `VOICEVOX_URL`未設定のため既定skip。
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない
  (2026-07-20実測: Python 381 passed/23 deselected/50 xfailed、
  Vitest 16 test files/76 tests、73 passed+3 skipped、変化なし)。

## 11. 停止条件

- 契約にあるtest fileが存在しない。
- 疎通確認を行わず実機能テストだけを直接実行しようとしている。
- API key、利用者データ、絶対pathなどの秘密・個人情報がログへ出る。
- `blocked`またはpost-MVPの未承認契約をMVPへ混入させる。
- 承認済み仕様と空実装signatureが矛盾する。

## 12. 実行記録

Claude Codeの完了報告には、少なくとも次を記録する。

```text
実行日時:
対象タスク:
実行コマンド:
収集件数:
pass / fail / xfail / skip:
外部疎通の有無:
外部疎通結果:
未解決事項:
```
