---
document_type: command_reference
status: review
version: '1.0'
last_updated: '2026-07-19'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
related_tasks:
- TASK-TTS-001
- TASK-VOICEVOX-001
- TASK-AUDIO-001
- TASK-COEIR-001
- TASK-UI-003
release_scopes:
- MVP
- blocked
---

# tts コマンド

## 1. 目的

TTS共通契約、VOICEVOX、preview/cache、将来engine境界の検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-TTS-001` — TTS共通Protocol・registry・エラー契約（MVP）
  - 契約: `docs/test-cases/TASK-TTS-001-tts-client-interface-and-registry.md`
- `TASK-VOICEVOX-001` — VOICEVOX adapter・話者一覧・合成（MVP）
  - 契約: `docs/test-cases/TASK-VOICEVOX-001-voicevox-client-adapter.md`
- `TASK-AUDIO-001` — 試聴・segment TTS・WAV cache（MVP）
  - 契約: `docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md`
- `TASK-COEIR-001` — COEIROINK adapter（blocked）
  - 契約: `docs/test-cases/TASK-COEIR-001-coeiroink-client-adapter.md`
- `TASK-UI-003` — 出力・声設定・試聴画面（MVP）
  - 契約: `docs/test-cases/TASK-UI-003-build-settings-and-voice-preview-screen.md`

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

- `electron/renderer/tests/BuildSettings.test.ts` — 存在
- `electron/tests/build_voice_ipc.test.ts` — 存在
- `tests/test_audio_cache.py` — 現在のダンプでは欠落
- `tests/test_audio_preview.py` — 現在のダンプでは欠落
- `tests/test_audio_synthesis.py` — 現在のダンプでは欠落
- `tests/test_coeiroink_adapter.py` — 現在のダンプでは欠落
- `tests/test_coeiroink_client.py` — 現在のダンプでは欠落
- `tests/test_tts_client_contract.py` — 現在のダンプでは欠落
- `tests/test_tts_registry.py` — 現在のダンプでは欠落
- `tests/test_voicevox_adapter.py` — 現在のダンプでは欠落
- `tests/test_voicevox_client.py` — 現在のダンプでは欠落

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_audio_cache.py tests/test_audio_preview.py tests/test_audio_synthesis.py tests/test_coeiroink_adapter.py tests/test_coeiroink_client.py tests/test_tts_client_contract.py tests/test_tts_registry.py tests/test_voicevox_adapter.py tests/test_voicevox_client.py
```
```powershell
npm run typecheck
```
```powershell
npm test -- electron/renderer/tests/BuildSettings.test.ts electron/tests/build_voice_ipc.test.ts
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_audio_cache.py tests/test_audio_preview.py tests/test_audio_synthesis.py tests/test_coeiroink_adapter.py tests/test_coeiroink_client.py tests/test_tts_client_contract.py tests/test_tts_registry.py tests/test_voicevox_adapter.py tests/test_voicevox_client.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_audio_cache.py tests/test_audio_preview.py tests/test_audio_synthesis.py tests/test_coeiroink_adapter.py tests/test_coeiroink_client.py tests/test_tts_client_contract.py tests/test_tts_registry.py tests/test_voicevox_adapter.py tests/test_voicevox_client.py
```
### Vitest
```powershell
npm test -- electron/renderer/tests/BuildSettings.test.ts electron/tests/build_voice_ipc.test.ts
```

## 7. 補助・運用コマンド

### VOICEVOX speakers診断
```powershell
Invoke-RestMethod -Method Get -Uri "$env:VOICEVOX_URL/speakers"
```

## 8. 外部疎通確認と実機能テスト

必ず次の順序で実行する。疎通確認が失敗した場合、実機能テストへ進まない。

```text
設定確認 → integration_smoke → 成功時のみ integration_live
```

### TASK-VOICEVOX-001: VOICEVOX Engine API

- connectivity fixture: `voicevox_connectivity_gate`
- 注意: 疎通はGET /speakers。本テストは短文のaudio_query→synthesis。
- 必要設定: `VOICEVOX_URL`

#### 1. 疎通確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m "integration_smoke" tests/test_voicevox_client.py
```
疎通確認が成功した実行記録を残してから次へ進む。

#### 2. 実機能確認
```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m "integration_live" tests/test_voicevox_adapter.py
```

### TASK-COEIR-001: COEIROINK API

- connectivity fixture: `coeiroink_connectivity_gate`
- 注意: blocked。公式API世代・endpoint確認前はsmoke/liveを実行しない。
- **状態: blocked。公式仕様のevidence gapが解消するまでsmoke/liveコマンドを実行しない。**


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
