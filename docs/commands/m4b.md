---
document_type: command_reference
status: review
version: '1.1'
last_updated: '2026-07-20'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
related_tasks:
- TASK-M4B-001
release_scopes:
- post-MVP
---

# m4b コマンド

## 1. 目的

post-MVPのM4B生成とffmpeg連携検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-M4B-001` — M4B出力（post-MVP）
  - 契約: `docs/test-cases/TASK-M4B-001-m4b-output.md`

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

- `tests/test_m4b_output.py` — `TASK-M4B-001`完了。TC-01,03,04,05,06,07,08
  (計7 case)、実測pass済み(2026-07-20)。TC-09(integration_smoke)/
  TC-02,10(integration_live)は`FFMPEG_PATH`未設定のため既定skip。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_m4b_output.py
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_m4b_output.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_m4b_output.py
```

## 7. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-M4B-001: ffmpeg runtime

- connectivity fixture: `ffmpeg_connectivity_gate`
- 注意: post-MVP。疎通後に最小M4B fixtureだけを生成。
- 必要設定: `FFMPEG_PATH`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_m4b_output.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_m4b_output.py
```


## 8. 全体回帰

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```
```powershell
npm run typecheck
```
```powershell
npm test
```

## 9. 成功条件

- 対象test fileがすべて収集される。
- 未知marker、import error、TypeScript型errorがない。
- 通常テストが外部接続しない。
- STEP3空実装段階では、意図したstrict xfailまたはopt-in skipだけになる。
- Claude Code本実装後は、対象タスクのxfailを解除し、対象テストがpassする。
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない
  (2026-07-20実測: 対象10 case中7 case実測pass(TC-02,09,10は既定skip)、
  Python全体411 passed/23 deselected/20 xfailed、npm run typecheck成功、
  Vitest 73 passed/3 skipped)。

## 10. 停止条件

- 契約にあるtest fileが存在しない。
- 疎通確認を行わず実機能テストだけを直接実行しようとしている。
- API key、利用者データ、絶対pathなどの秘密・個人情報がログへ出る。
- `blocked`またはpost-MVPの未承認契約をMVPへ混入させる。
- 承認済み仕様と空実装signatureが矛盾する。

## 11. 実行記録

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
