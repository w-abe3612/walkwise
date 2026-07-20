---
document_type: command_reference
status: review
version: '1.1'
last_updated: '2026-07-20'
generated_from_dump: audio_book_creation_dump_2026-07-19_173616.txt
current_state_verified: '2026-07-20'
related_tasks:
- TASK-PROFILE-001
release_scopes:
- MVP
---

# profiles コマンド

## 1. 目的

character/voice profile schemaと既定値境界の検証に使用する正式な実行入口を定義する。
本書はSTEP6の実装準備成果物であり、コマンドの成功を装うものではない。
STEP3/STEP4の空実装段階では、strict xfail・明示的未実装error・opt-in skipが正常である。

## 2. 関連タスク

- `TASK-PROFILE-001` — Character・Voice profile読込と選択（MVP、本実装済み）
  - 契約: `docs/test-cases/TASK-PROFILE-001-character-and-voice-profiles.md`
  - production: `script/profiles/characters.py`, `script/profiles/voices.py`, `script/schemas/profiles.py`
  - 対象9 case(TC-PROFILE-001-01〜09)はすべてpassする。
  - 話者ごとの最終速度・音量・無音時間・採用スタイルの確定は
    `docs/spec-proposals/task/3_voice-profile-default-values.md`(status: draft、未承認)の
    責務であり本タスクの対象外。COEIROINKは`TASK-COEIR-001`が永久にblockedのため、
    MVPの`list_available()`はVOICEVOXの承認済みprofileだけを返す。

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

- `tests/test_character_profiles.py`
- `tests/test_voice_profiles.py`

現在の存在有無は[`CURRENT_STATE.md`](CURRENT_STATE.md)を正本とする。

## 5. 収集・型確認

```powershell
python -m pytest --collect-only -q tests/test_character_profiles.py tests/test_voice_profiles.py
```

## 6. 外部接続なしの対象テスト

### Host補助
```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_character_profiles.py tests/test_voice_profiles.py
```
### Docker正式
```powershell
docker compose run --rm test python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience" tests/test_character_profiles.py tests/test_voice_profiles.py
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
- STEP3空実装段階では、意図したstrict xfailまたはopt-in skipだけになる。
- Claude Code本実装後は、対象タスクのxfailを解除し、対象テストがpassする。
- 対象テスト成功後に全体回帰を実行し、既存タスクを壊していない。

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
