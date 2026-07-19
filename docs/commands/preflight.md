---
document_type: command_reference
status: review
version: "1.0"
last_updated: "2026-07-19"
---

# 実装準備 preflight

## 1. 目的

STEP2契約、STEP3テスト空実装、STEP4ソース空実装、STEP6コマンド文書が
一つのリポジトリに揃っていることを、本実装前に確認する。

## 2. Git差分

```powershell
git status --short
git diff --stat
```

既存変更を破棄・reset・checkoutしない。

## 3. 必要runtime

```powershell
python --version
python -m pytest --version
node --version
npm --version
docker --version
docker compose version
```

Pythonは`pyproject.toml`に従い3.12以上を使用する。

## 4. STEP2契約上のtest file存在確認

`STEP6_MANIFEST.json`に記録された109件を検査する。

```powershell
python -c "import json,pathlib,sys; m=json.loads(pathlib.Path('docs/commands/STEP6_MANIFEST.json').read_text(encoding='utf-8')); missing=[p for p in m['planned_test_files'] if not pathlib.Path(p).is_file()]; print('\n'.join(missing) if missing else 'all planned test files exist'); sys.exit(1 if missing else 0)"
```

1件でも欠落した場合は、Claude Code本実装へ進まずSTEP3成果物を復元する。

## 5. Python構文

```powershell
python -m compileall -q script tests
```

## 6. Python production import

```powershell
python -c "import importlib,pathlib; mods=[]; [mods.append('.'.join(p.with_suffix('').parts)) for p in pathlib.Path('script').rglob('*.py') if p.name != '__init__.py']; [importlib.import_module(m) for m in mods]; print(f'imported {len(mods)} modules')"
```

外部接続や本処理がimport時に開始された場合は失敗とする。

## 7. pytest collection

```powershell
python -m pytest --collect-only -q
```

通常collectionでnetwork、subprocess runtime、音声生成を開始しない。

## 8. Node依存とTypeScript

初回のみ、`package-lock.json`がまだない場合:

```powershell
npm install
git status --short package-lock.json
```

生成されたlock fileをレビューし、以後は次を正式コマンドとする。

```powershell
npm ci
npm run typecheck
npm test
```

`package-lock.json`がないまま、依存versionが毎回変わる状態を正式な受入結果にしない。

STEP3のVitest空実装段階では`test.fails`による意図した失敗反転を確認する。

## 9. Docker

```powershell
docker compose config
docker compose build test
docker compose run --rm test python -m pytest --collect-only -q
```

## 10. 合格条件

- 予定test fileが109/109存在する。
- Python構文・importが成功する。
- pytestとVitestが全空実装を収集する。
- 未知marker warningがない。
- 通常実行で外部接続しない。
- Git差分が理解できる範囲である。
