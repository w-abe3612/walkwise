---
document_type: command_reference
status: review
version: '1.1'
last_updated: '2026-07-20'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
related_tasks:
- TASK-RELEASE-001
release_scopes:
- MVP
---

# backup-restore コマンド

## 1. 目的

アプリデータ、SQLite、Project成果物のbackup/restore検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-RELEASE-001` — Windows package・runtime同梱・license/privacy/backup（MVP）
  - 契約: `docs/test-cases/TASK-RELEASE-001-windows-packaging-security-licenses-and-backup.md`

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

- `electron/tests/packaging_contract.test.ts` — `TASK-RELEASE-001`完了。
  TC-01,04,07,10(計4 case)、実測pass済み(2026-07-20)。
- `tests/test_backup_restore.py` — `TASK-RELEASE-001`完了。TC-02,05,08
  (計3 case)、実測pass済み(2026-07-20)。TC-11(integration_smoke)は
  `WALKWISE_PYTHON_EXECUTABLE`/`FFMPEG_PATH`/`FFPROBE_PATH`/
  `TESSERACT_CMD`のいずれも未設定のため既定skip。
- `tests/test_license_manifest.py` — `TASK-RELEASE-001`完了。TC-03,06,09
  (計3 case)、実測pass済み(2026-07-20)。TC-12(integration_live)は
  上記env未設定のため既定skip。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_backup_restore.py tests/test_license_manifest.py
```
```powershell
npm run typecheck
```
```powershell
npm test -- electron/tests/packaging_contract.test.ts
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_backup_restore.py tests/test_license_manifest.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_backup_restore.py tests/test_license_manifest.py
```
### Vitest
```powershell
npm test -- electron/tests/packaging_contract.test.ts
```

## 7. 補助・運用コマンド

### 配布契約test
```powershell
npm test -- electron/tests/packaging_contract.test.ts
```

## 8. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-RELEASE-001: 配布runtime群

- connectivity fixture: `release_runtime_connectivity_gate`
- 注意: package内のPython/ffmpeg等の存在と起動を確認。実利用者dataは使わない。
- 秘密環境変数: なし

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
npm test -- electron/tests/packaging_contract.test.ts
```

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
npm test -- electron/tests/packaging_contract.test.ts
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
- STEP3空実装段階では、意図したstrict xfailまたはopt-in skipだけになる。
- Claude Code本実装後は、対象タスクのxfailを解除し、対象テストがpassする。
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない
  (2026-07-20実測: 対象10 case中8 case実測pass(TC-11/12は既定skip)、
  Python全体387 passed/23 deselected/44 xfailed、npm run typecheck成功、
  Vitest 73 passed/3 skipped)。

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
