---
document_type: command_policy
status: review
version: "1.0"
last_updated: "2026-07-19"
spec_ref: "docs/test-cases/external-connectivity-policy.md"
---

# 外部疎通・実機能テスト

## 1. 必須順序

```text
設定確認
↓
integration_smoke
↓ 成功した場合だけ
integration_live
```

`integration_live`を先に実行しない。疎通失敗をlive側のretryで隠さない。

## 2. 通常テスト

```powershell
python -m pytest -ra -m "not integration_smoke and not integration_live and not performance and not resilience"
npm test
```

通常テストは外部接続を行わない。

## 3. 疎通確認

```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
python -m pytest -ra -m integration_smoke
```

疎通確認は次だけを行う。

- Gemini: metadata/list。本文生成なし。
- VOICEVOX: `GET /speakers`。
- Tesseract: versionと言語一覧。
- ffmpeg/ffprobe: version。
- ASR: runtime/modelの存在と読込可否。
- Worker/Desktop: health/ping。
- 配布runtime: package内runtimeの存在・起動。

## 4. 実機能確認

疎通確認の成功結果を確認してから実行する。

```powershell
$env:WALKWISE_RUN_INTEGRATION_SMOKE="1"
$env:WALKWISE_RUN_INTEGRATION_LIVE="1"
python -m pytest -ra -m integration_live
```

live testは固定・短時間・最小回数とし、実利用者Projectを使用しない。

## 5. 秘密値

- API keyは環境変数または安全なsecret storeから渡す。
- command line引数、Markdown、pytest reportへ値を直接書かない。
- endpointは秘密でない場合だけ要約表示する。
- exceptionとログは値をredactする。

## 6. COEIROINK

`TASK-COEIR-001`はblockedである。公式API世代、endpoint、リリンちゃんの識別子、
利用条件が確認されるまで、smoke/liveを実行しない。

## 7. 終了後

```powershell
Remove-Item Env:WALKWISE_RUN_INTEGRATION_SMOKE -ErrorAction SilentlyContinue
Remove-Item Env:WALKWISE_RUN_INTEGRATION_LIVE -ErrorAction SilentlyContinue
```
