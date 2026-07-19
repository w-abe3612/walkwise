from __future__ import annotations

import os
import random
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = PROJECT_ROOT / ".env"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

DEFAULT_REQUEST_TIMEOUT_SEC = 300
DEFAULT_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "8"))
DEFAULT_RETRY_WAIT_SEC = float(os.getenv("GEMINI_RETRY_WAIT_SEC", "5"))
DEFAULT_MAX_RETRY_WAIT_SEC = float(os.getenv("GEMINI_MAX_RETRY_WAIT_SEC", "90"))
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_CHARS_PER_CHUNK = 12000


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


load_env_file(ENV_PATH)

DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Gemini prompt が見つかりません: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()


def render_prompt(filename: str, **kwargs: Any) -> str:
    template = load_prompt(filename)
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Gemini prompt の変数が不足しています: {filename} -> {e}") from e


def build_endpoint(api_version: str, model: str) -> str:
    return (
        "https://generativelanguage.googleapis.com/"
        f"{api_version}/models/{model}:generateContent"
    )


def extract_text_from_candidate(data: dict[str, Any]) -> str:
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini response に candidates がありません: {data}")

    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        raise RuntimeError(f"Gemini response に parts がありません: {data}")

    texts: list[str] = []
    for part in parts:
        text = part.get("text")
        if text:
            texts.append(text)

    result = "\n".join(texts).strip()
    if not result:
        raise RuntimeError(f"Gemini response の text が空です: {data}")

    return result


def split_text_into_chunks(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if not text:
        return []

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) > max_chars:
            sentences = para.replace("。", "。\n").splitlines()
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(current) + len(sentence) + 2 <= max_chars:
                    current += sentence + "\n"
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    current = sentence + "\n"
            continue

        if len(current) + len(para) + 2 <= max_chars:
            if current:
                current += "\n\n" + para
            else:
                current = para
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para

    if current.strip():
        chunks.append(current.strip())

    return chunks


def _is_retryable_status_code(status_code: int) -> bool:
    return status_code in {408, 429, 500, 502, 503, 504}


def _parse_retry_after_seconds(response: requests.Response) -> float | None:
    raw = (response.headers.get("Retry-After") or "").strip()
    if not raw:
        return None

    try:
        return max(0.0, float(raw))
    except ValueError:
        pass

    try:
        retry_at = parsedate_to_datetime(raw)
        if retry_at.tzinfo is None:
            return None

        date_header = (response.headers.get("Date") or "").strip()
        if date_header:
            server_now = parsedate_to_datetime(date_header)
            if server_now.tzinfo is not None:
                return max(0.0, (retry_at - server_now).total_seconds())

        return None
    except Exception:
        return None


def _compute_retry_wait_sec(
    *,
    attempt: int,
    retry_wait_sec: float,
    max_retry_wait_sec: float,
    response: requests.Response | None = None,
) -> float:
    retry_after_sec = None
    if response is not None:
        retry_after_sec = _parse_retry_after_seconds(response)

    if retry_after_sec is not None:
        base_wait = retry_after_sec
    else:
        base_wait = retry_wait_sec * (2 ** (attempt - 1))

    jitter = random.uniform(0, 1.0)
    return min(max_retry_wait_sec, base_wait + jitter)


def _summarize_response_error(response: requests.Response) -> str:
    body = (response.text or "").strip().replace("\r", " ").replace("\n", " ")
    if len(body) > 240:
        body = body[:240] + "..."
    if body:
        return f"{response.status_code} {response.reason} / {body}"
    return f"{response.status_code} {response.reason}"


def call_gemini(
    *,
    api_key: str,
    api_version: str,
    model: str,
    system_instruction: str,
    user_text: str,
    timeout_sec: int = DEFAULT_REQUEST_TIMEOUT_SEC,
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_wait_sec: float = DEFAULT_RETRY_WAIT_SEC,
    response_mime_type: str | None = None,
    max_retry_wait_sec: float = DEFAULT_MAX_RETRY_WAIT_SEC,
) -> str:
    if not api_key:
        raise RuntimeError(
            "Gemini APIキーが設定されていません。"
            f" .env を確認してください: {ENV_PATH}"
        )

    payload: dict[str, Any] = {
        "system_instruction": {
            "parts": [{"text": system_instruction}],
        },
        "contents": [
            {
                "parts": [{"text": user_text}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
        },
    }

    if response_mime_type:
        payload["generationConfig"]["responseMimeType"] = response_mime_type

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    url = build_endpoint(api_version, model)
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout_sec,
            )

            if response.status_code >= 400:
                error_message = _summarize_response_error(response)

                if attempt < max_retries and _is_retryable_status_code(response.status_code):
                    wait_sec = _compute_retry_wait_sec(
                        attempt=attempt,
                        retry_wait_sec=retry_wait_sec,
                        max_retry_wait_sec=max_retry_wait_sec,
                        response=response,
                    )
                    print(
                        f"[retry {attempt}/{max_retries}] "
                        f"Gemini API 呼び出し失敗: {error_message} / {wait_sec:.1f}s 待機"
                    )
                    time.sleep(wait_sec)
                    continue

                response.raise_for_status()

            data = response.json()
            return extract_text_from_candidate(data)

        except requests.RequestException as e:
            last_error = e
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            should_retry = status_code is None or _is_retryable_status_code(int(status_code))

            if attempt < max_retries and should_retry:
                wait_sec = _compute_retry_wait_sec(
                    attempt=attempt,
                    retry_wait_sec=retry_wait_sec,
                    max_retry_wait_sec=max_retry_wait_sec,
                    response=getattr(e, "response", None),
                )
                print(
                    f"[retry {attempt}/{max_retries}] "
                    f"Gemini API 呼び出し失敗: {e} / {wait_sec:.1f}s 待機"
                )
                time.sleep(wait_sec)
                continue
            break

        except Exception as e:
            last_error = e
            break

    raise RuntimeError(f"Gemini API 呼び出しに失敗しました: {last_error}")


# ---------------------------------------------------------------------------
# STEP4 typed contract additions. Existing working implementation above is
# preserved. New public APIs remain intentionally unimplemented.
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-AI-001', 'GeminiClient.check_connectivity() -> ConnectivityResult', '認証を含む軽量なmetadata/list操作で疎通確認する。'),
    ('TASK-AI-001', 'GeminiClient.generate(request) -> AIResult', '現行HTTP処理を共通結果・errorへ適合する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-AI-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'mock生成', 'given': '固定Gemini HTTP response', 'when': 'generateする', 'then': 'AIResult text/provider/model/usageへ変換する', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-02', 'priority': 'P0', 'layer': 'unit', 'title': 'retry区分', 'given': '429/5xxと400を返すmock', 'when': 'generateする', 'then': '前者だけ上限内再試行し400は即時error', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'structured response', 'given': '不正JSONと正常JSON', 'when': 'validation hook付き生成', 'then': '正常だけ受理し不正はschema error', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-04', 'priority': 'P1', 'layer': 'unit', 'title': 'AIClient Protocol', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「AIClient Protocol」を実行する', 'then': '「AIClient Protocol」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-05', 'priority': 'P1', 'layer': 'unit', 'title': 'prompt template', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「prompt template」を実行する', 'then': '「prompt template」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-06', 'priority': 'P1', 'layer': 'unit', 'title': 'JSON/YAML response validation hook', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「JSON/YAML response validation hook」を実行する', 'then': '正常値を受理し、仕様違反を副作用前に検出して具体的なerror codeを返す。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'timeout', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を通じて「timeout」を実行する', 'then': 'timeoutを安定した共通errorへ変換し、半端な最終ファイルや成功状態を残さない。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`AIClient Protocol: check_connectivity(), generate(request) -> AIResult`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_gemini_client.py`'},
    {'id': 'TC-AI-001-11', 'priority': 'P0', 'layer': 'integration_smoke', 'title': 'Gemini APIの疎通確認', 'given': '実接続テストが明示的に有効化され、必要な設定が存在する', 'when': '認証付きの軽量なmodel metadata/list操作を1回だけ実行し、DNS/TLS/HTTP/認証/応答schemaを確認する。生成本文は要求しない。', 'then': 'ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。', 'test_file': '`tests/test_ai_client_contract.py`'},
    {'id': 'TC-AI-001-12', 'priority': 'P1', 'layer': 'integration_live', 'title': 'Gemini APIの実機能テスト', 'given': '`gemini_connectivity_gate`が成功済み', 'when': '疎通成功後、極短い固定promptを1回生成し、非空text・provider/model・usageまたはusage unavailable warningを確認する。', 'then': '最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。', 'test_file': '`tests/test_gemini_client.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/ai_clients/gemini/client.py)")

class AIResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class ConnectivityResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class GeminiClient:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def check_connectivity(self) -> ConnectivityResult:
        """認証を含む軽量なmetadata/list操作で疎通確認する。

        Public contract: ``GeminiClient.check_connectivity() -> ConnectivityResult``.
        """
        _step4_unimplemented('GeminiClient.check_connectivity')
    def generate(self, request: Any) -> AIResult:
        """現行HTTP処理を共通結果・errorへ適合する。

        Public contract: ``GeminiClient.generate(request) -> AIResult``.
        """
        _step4_unimplemented('GeminiClient.generate')
