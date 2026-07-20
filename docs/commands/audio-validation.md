---
document_type: command_reference
status: review
version: '1.1'
last_updated: '2026-07-20'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
current_state_verified: '2026-07-20'
related_tasks:
- TASK-AUDIO-002
release_scopes:
- MVP
---

# audio-validation コマンド

## 1. 目的

音声形式・測定・provisional閾値・判定の検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-AUDIO-002` — 音声自動検査・provisional閾値（MVP、本実装済み）
  - 契約: `docs/test-cases/TASK-AUDIO-002-audio-validation.md`
  - production: `script/audio/validation.py`, `measurements.py`, `thresholds.py`
  - 対象10 case(TC-AUDIO-002-01〜10)のうち、外部接続なしの8 case
    (TC-01〜08)はすべてpassする。TC-09(integration_smoke)/TC-10
    (integration_live)はこの環境に`FFMPEG_PATH`/`FFPROBE_PATH`が
    未設定・実行体も未導入のため未確認(既定skip)。

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

- `tests/test_audio_thresholds.py`
- `tests/test_audio_validation.py`

現在の存在有無・pass状況は[`CURRENT_STATE.md`](CURRENT_STATE.md)を正本とする。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_audio_thresholds.py tests/test_audio_validation.py
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_audio_thresholds.py tests/test_audio_validation.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_audio_thresholds.py tests/test_audio_validation.py
```

## 7. 補助・運用コマンド

### ffmpeg version
```powershell
& $env:FFMPEG_PATH -version
```
### ffprobe version
```powershell
& $env:FFPROBE_PATH -version
```

## 8. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-AUDIO-002: ffmpeg/ffprobe runtime

- connectivity fixture: `ffmpeg_connectivity_gate`
- 注意: 疎通はversion確認。本テストは最小fixtureのprobe/measurement。
- 必要設定: `FFMPEG_PATH`, `FFPROBE_PATH`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_audio_validation.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_audio_thresholds.py
```

TC-AUDIO-002-09(疎通確認)は`tests/test_audio_validation.py`、
TC-AUDIO-002-10(実機能確認)は`tests/test_audio_thresholds.py`に実装されている
(STEP2契約のcase ID→test_file対応どおり)。


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
