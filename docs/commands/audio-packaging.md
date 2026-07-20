---
document_type: command_reference
status: complete
version: '1.1'
last_updated: '2026-07-20'
related_tasks:
- TASK-AUDIO-003
release_scopes:
- MVP
---

# audio-packaging コマンド

## 1. 目的

章MP3、verified text、production manifest、build orchestrationの検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-AUDIO-003` — 章MP3・text成果物・manifest・Build orchestration（MVP）
  - 契約: `docs/test-cases/TASK-AUDIO-003-chapter-packaging-manifests-and-build-orchestration.md`

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

- `tests/test_audio_packaging.py` — TC-01, TC-04, TC-07, TC-10(計4 case)
- `tests/test_build_pipeline.py` — TC-02, TC-05, TC-08(計3 case)
- `tests/test_production_manifest.py` — TC-03, TC-06, TC-09(計3 case)

対象10 caseはすべて実装済み・実測passを確認済み(2026-07-20)。
本タスク単独の外部接続(ffmpeg実行)は不要であり、`ChapterPackager`の
テストは常にfake `mp3_encoder`を注入する(実ffmpeg encoder関数は
`script/audio/packaging.py`の`make_ffmpeg_mp3_encoder()`として実装
済みだが、本タスクの自動テストからは呼び出されない)。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_audio_packaging.py tests/test_build_pipeline.py tests/test_production_manifest.py
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_audio_packaging.py tests/test_build_pipeline.py tests/test_production_manifest.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_audio_packaging.py tests/test_build_pipeline.py tests/test_production_manifest.py
```

## 7. 全体回帰

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
```
```powershell
npm run typecheck
```
```powershell
npm test
```

## 8. 成功条件

- 対象test fileがすべて収集される。
- 未知marker、import error、TypeScript型errorがない。
- 通常テストが外部接続しない。
- 対象10 caseがすべてpassする(2026-07-20実測で確認済み)。
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない
  (2026-07-20実測: 336 passed, 23 deselected, 95 xfailed、予期しない
  failなし)。

## 9. 停止条件

- 契約にあるtest fileが存在しない。
- 疎通確認を行わず実機能テストだけを直接実行しようとしている。
- API key、利用者データ、絶対pathなどの秘密・個人情報がログへ出る。
- `blocked`またはpost-MVPの未承認契約をMVPへ混入させる。
- 承認済み仕様と空実装signatureが矛盾する。

## 10. 実行記録

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
