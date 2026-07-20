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
# STEP4 typed contract additions (TASK-AI-001). Existing working
# implementation above is preserved and reused (call_gemini's HTTP/retry
# helpers). GeminiClient adapts that existing behavior to the common
# AIClient contract in script/ai_clients/base.py.
# ---------------------------------------------------------------------------
from dataclasses import dataclass

from script.ai_clients.base import AIClientError, AIRequest, AIResult, AIUsage
from script.core.errors import AppError, ErrorCode

DEFAULT_CONNECTIVITY_TIMEOUT_SEC = 10


@dataclass(frozen=True)
class ConnectivityResult:
    """副作用のない疎通確認結果。"""

    available: bool
    provider: str = "gemini"
    detail: str | None = None


class GeminiClient:
    """現行のGemini HTTP処理(`call_gemini`と同じendpoint/retry方針)をAIClient契約へ適合する。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_version: str | None = None,
        model: str | None = None,
        session_get: Any = None,
        session_post: Any = None,
        sleep: Any = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else DEFAULT_API_KEY
        self._api_version = api_version or DEFAULT_API_VERSION
        self._model = model or DEFAULT_MODEL
        self._get = session_get or requests.get
        self._post = session_post or requests.post
        self._sleep = sleep or time.sleep

    def check_connectivity(self) -> ConnectivityResult:
        """認証を含む軽量なmetadata操作(生成なし)で疎通確認する。"""
        if not self._api_key:
            raise AppError(ErrorCode.VALIDATION_ERROR, "GEMINI_API_KEY is required")

        url = f"https://generativelanguage.googleapis.com/{self._api_version}/models/{self._model}"
        try:
            response = self._get(
                url,
                headers={"x-goog-api-key": self._api_key},
                timeout=DEFAULT_CONNECTIVITY_TIMEOUT_SEC,
            )
        except requests.RequestException as exc:
            return ConnectivityResult(available=False, detail=str(exc))

        if response.status_code >= 400:
            return ConnectivityResult(available=False, detail=_summarize_response_error(response))

        return ConnectivityResult(available=True)

    def generate(self, request: AIRequest) -> AIResult:
        """現行HTTP処理(retry/timeout方針込み)を共通結果・errorへ適合する。"""
        if request is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "request is required")
        if not self._api_key:
            raise AppError(ErrorCode.VALIDATION_ERROR, "GEMINI_API_KEY is required")

        model = request.model or self._model
        timeout_sec = request.timeout_sec or DEFAULT_REQUEST_TIMEOUT_SEC

        payload: dict[str, Any] = {
            "system_instruction": {"parts": [{"text": request.system_instruction}]},
            "contents": [{"parts": [{"text": request.user_text}]}],
            "generationConfig": {"temperature": request.temperature},
        }
        if request.response_mime_type:
            payload["generationConfig"]["responseMimeType"] = request.response_mime_type

        headers = {"Content-Type": "application/json", "x-goog-api-key": self._api_key}
        url = build_endpoint(self._api_version, model)

        last_error: Exception | None = None
        for attempt in range(1, DEFAULT_MAX_RETRIES + 1):
            try:
                response = self._post(url, headers=headers, json=payload, timeout=timeout_sec)
            except requests.Timeout as exc:
                # timeoutは安定errorへ変換して即座に停止し、半端な成功状態を残さない。
                raise AIClientError(
                    ErrorCode.EXTERNAL_UNAVAILABLE,
                    "gemini request timed out",
                    retryable=False,
                    technical_detail=str(exc),
                ) from exc
            except requests.RequestException as exc:
                last_error = exc
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                should_retry = status_code is None or _is_retryable_status_code(int(status_code))
                if attempt < DEFAULT_MAX_RETRIES and should_retry:
                    self._sleep(
                        _compute_retry_wait_sec(
                            attempt=attempt,
                            retry_wait_sec=DEFAULT_RETRY_WAIT_SEC,
                            max_retry_wait_sec=DEFAULT_MAX_RETRY_WAIT_SEC,
                            response=getattr(exc, "response", None),
                        )
                    )
                    continue
                raise AIClientError(
                    ErrorCode.EXTERNAL_UNAVAILABLE,
                    f"gemini request failed: {exc}",
                    retryable=should_retry,
                    technical_detail=str(exc),
                ) from exc

            if response.status_code >= 400:
                error_message = _summarize_response_error(response)
                if response.status_code != 400 and _is_retryable_status_code(response.status_code) and attempt < DEFAULT_MAX_RETRIES:
                    self._sleep(
                        _compute_retry_wait_sec(
                            attempt=attempt,
                            retry_wait_sec=DEFAULT_RETRY_WAIT_SEC,
                            max_retry_wait_sec=DEFAULT_MAX_RETRY_WAIT_SEC,
                            response=response,
                        )
                    )
                    continue
                # 400は即時error(retry区分: 429/5xxだけを再試行対象とする)。
                raise AIClientError(
                    ErrorCode.VALIDATION_ERROR if response.status_code == 400 else ErrorCode.EXTERNAL_UNAVAILABLE,
                    error_message,
                    retryable=_is_retryable_status_code(response.status_code) and response.status_code != 400,
                )

            data = response.json()
            text = extract_text_from_candidate(data)

            if request.validate_response is not None:
                request.validate_response(text)

            usage_data = data.get("usageMetadata") or {}
            usage = AIUsage(
                input_tokens=usage_data.get("promptTokenCount"),
                output_tokens=usage_data.get("candidatesTokenCount"),
                total_tokens=usage_data.get("totalTokenCount"),
            )
            warnings = () if usage_data else ("usage_unavailable",)

            return AIResult(text=text, provider="gemini", model=model, usage=usage, warnings=warnings)

        raise AIClientError(
            ErrorCode.EXTERNAL_UNAVAILABLE,
            f"gemini request failed after retries: {last_error}",
            retryable=True,
        )
