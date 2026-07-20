---
document_type: command_reference
status: review
version: '1.1'
last_updated: '2026-07-20'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
current_state_verified: '2026-07-20'
related_tasks:
- TASK-OCR-001
release_scopes:
- MVP
---

# ocr コマンド

## 1. 目的

Tesseract疎通、OCR、スキャンPDF処理の検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-OCR-001` — OCR・スキャンPDF処理（MVP）
  - 契約: `docs/test-cases/TASK-OCR-001-ocr-and-scanned-pdf-processing.md`

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

- `tests/test_ocr_client.py`
- `tests/test_ocr_pipeline.py`

現在の存在有無は[`CURRENT_STATE.md`](CURRENT_STATE.md)を正本とする。`TASK-OCR-001`は
本実装済みであり、外部接続なしの対象10ケース(TC-OCR-001-01〜10)はpassする。
`TC-OCR-001-11`(integration_smoke)/`TC-OCR-001-12`(integration_live)は
この開発環境にTesseract runtimeが未導入のため未確認であり、`TESSERACT_CMD`が
未設定の間は既定でskipされる(secretや誤ったpass記録は行っていない)。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_ocr_client.py tests/test_ocr_pipeline.py
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_ocr_client.py tests/test_ocr_pipeline.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_ocr_client.py tests/test_ocr_pipeline.py
```

## 7. 補助・運用コマンド

### Tesseract version
```powershell
& $env:TESSERACT_CMD --version
```

## 8. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-OCR-001: Tesseract runtime

- connectivity fixture: `tesseract_connectivity_gate`
- 注意: 疎通は--versionと言語一覧。本テストは固定1行画像のみ。
- 必要設定: `TESSERACT_CMD`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_ocr_client.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_ocr_pipeline.py
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
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない。

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
