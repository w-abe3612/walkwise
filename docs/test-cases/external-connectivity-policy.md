---
document_id: external-connectivity-policy
title: "外部API・外部runtime疎通テスト方針"
status: review
version: "1.0"
last_updated: "2026-07-19"
generated_from_dump: "audio_book_creation_dump_2026-07-19_163743.txt"
---

# 外部API・外部runtime疎通テスト方針

## 1. 目的

外部API、ローカルHTTP Engine、CLI runtime、subprocess workerを利用するテストについて、
いきなり実機能テストを開始せず、軽量な疎通確認を成功させてから本テストへ進む共通規則を定義する。

## 2. 必須の二段階

```text
設定確認
↓
疎通確認（integration_smoke）
↓ 成功時のみ
実機能確認（integration_live または e2e）
```

実機能テストは、対象ごとのconnectivity fixtureを引数として必須要求する。
fixtureを迂回して直接API、Engine、runtimeへ接続するテストを作らない。

## 3. 通常pytest

通常のテスト実行では次へ接続しない。

- Gemini API
- VOICEVOX Engine
- COEIROINK
- cloud OCR / cloud ASR
- ローカルTesseract、ffmpeg、ffprobe、ASR model
- 実Python worker subprocess
- OS installer

通常テストはHTTP、subprocess、filesystem、時計をmockまたはfixtureへ置き換える。

## 4. marker

| marker | 用途 | 既定 |
|---|---|---|
| `unit` | 純粋処理・validation | 実行 |
| `integration_mock` | mockを使う結合 | 実行 |
| `integration_smoke` | 疎通だけ | 除外 |
| `integration_live` | 実機能 | 除外 |
| `e2e` | end-to-end | 除外 |
| `performance` | 性能測定 | 除外 |
| `resilience` | 障害注入 | 除外 |

## 5. connectivity fixture契約

connectivity fixtureはsession scopeを基本とし、次を返す。

```text
ConnectivityResult
- available: bool
- target: str
- version: str | None
- checked_at: ISO 8601
- detail: 秘密値を含まない要約
```

規則:

- 環境変数不足時はnetworkへ接続せず、理由付きskip。
- 秘密値をログ・pytest report・exceptionへ出さない。
- timeoutは短くし、生成・保存・DB更新を行わない。
- 疎通失敗時は疎通testをfailとし、依存するlive testは理由付きskip。
- 疎通確認をretryで長時間隠さない。
- endpoint、model、speaker等の未確認値を推測して固定しない。

## 6. 対象別の疎通

### Gemini

- 認証付きの軽量なmodel metadata/list操作。
- 疎通時は本文生成を行わない。
- live testでのみ極短い固定promptを1回生成する。

### VOICEVOX

- `GET /speakers`。
- HTTP成功、JSON配列、1件以上、必要識別情報を確認。
- live testで短文の`/audio_query`と`/synthesis`を行う。

### COEIROINK

- 公式API世代とendpointが確認されるまでblocked。
- 確認前にVOICEVOXのendpointやspeaker IDを流用しない。

### Tesseract / ffmpeg / ffprobe

- 疎通は`--version`または`-version`だけ。
- fixture処理は疎通成功後に最小fixtureへ実行する。

### ASR

- runtime/modelの存在と読込可否だけを先に確認。
- 疎通成功後、数秒の固定WAVだけを文字起こしする。

### Python worker / Desktop

- workerは`health`または`ping`だけを先に実行。
- Desktopは起動、preload、DB/worker healthまでを疎通とし、
  ProjectやArtifact作成は本E2Eで行う。

## 7. 課金と副作用

- 疎通確認は原則として課金を発生させない操作を選ぶ。
- provider仕様上、最小生成が不可避なら、実機能testへ分類し、実行前に課金可能性を明記する。
- live testの入力は固定・短文・最小回数とする。
- 実利用者のProject、API data、音声成果物をfixtureとして使わない。

## 8. STEP3への要求

- provider/runtimeごとのconnectivity fixtureを`tests/conftest.py`または専用fixture moduleへ置く。
- live test関数は対応fixtureを引数に含める。
- opt-inなしでskipすることは許可するが、疎通fixtureを使わない無条件skipは禁止する。
- mock testはconnectivity fixtureへ依存しない。

## 9. 完了条件

- すべての外部実機能testが疎通fixtureへ依存する。
- 通常pytestが外部接続しない。
- 設定不足、疎通失敗、実機能失敗を区別できる。
- 秘密値と利用者dataをtest reportへ出さない。
