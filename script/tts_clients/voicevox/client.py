from __future__ import annotations

import argparse
import io
import os
import re
import wave
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")
DEFAULT_TIMEOUT = (10, 300)

DEFAULT_SPEAKER = 3
DEFAULT_SPEED_SCALE = 1.6
DEFAULT_PITCH_SCALE = 0.0
DEFAULT_INTONATION_SCALE = 1.0
DEFAULT_VOLUME_SCALE = 1.0

DEFAULT_MAX_TEXT_LENGTH = 300


class VoicevoxClientError(RuntimeError):
    """VOICEVOX クライアント関連エラー。"""


def _normalize_base_url(base_url: str | None) -> str:
    resolved = (base_url or "").strip() or DEFAULT_BASE_URL
    return resolved.rstrip("/")


def _read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"入力ファイルが空です: {path}")
    return text


def split_text_for_voicevox(
    text: str,
    *,
    max_length: int = DEFAULT_MAX_TEXT_LENGTH,
) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []

    paragraphs = [part.strip() for part in normalized.split("\n") if part.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for paragraph in paragraphs:
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[。！？!?])", paragraph)
            if sentence.strip()
        ] or [paragraph]

        for sentence in sentences:
            if len(sentence) > max_length:
                if current:
                    flush()
                for start in range(0, len(sentence), max_length):
                    piece = sentence[start : start + max_length].strip()
                    if piece:
                        chunks.append(piece)
                continue

            candidate = sentence if not current else current + sentence
            if len(candidate) <= max_length:
                current = candidate
            else:
                flush()
                current = sentence

        flush()

    return [chunk for chunk in chunks if chunk]


def _request(
    method: str,
    url: str,
    *,
    timeout: tuple[int, int] = DEFAULT_TIMEOUT,
    **kwargs: Any,
) -> requests.Response:
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        raise VoicevoxClientError(f"VOICEVOX API 呼び出しに失敗しました: {url} -> {e}") from e


def check_voicevox_running(*, base_url: str = DEFAULT_BASE_URL) -> None:
    _request("GET", f"{_normalize_base_url(base_url)}/speakers")


def create_audio_query(
    *,
    text: str,
    speaker: int = DEFAULT_SPEAKER,
    base_url: str = DEFAULT_BASE_URL,
    timeout: tuple[int, int] = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    normalized_text = text.strip()
    if not normalized_text:
        raise ValueError("audio_query に渡す text が空です。")

    response = _request(
        "POST",
        f"{_normalize_base_url(base_url)}/audio_query",
        params={
            "text": normalized_text,
            "speaker": int(speaker),
        },
        timeout=timeout,
    )

    data = response.json()
    if not isinstance(data, dict):
        raise VoicevoxClientError("VOICEVOX /audio_query の応答が object ではありません。")
    return data


def apply_voice_settings(
    audio_query: dict[str, Any],
    *,
    speed_scale: float = DEFAULT_SPEED_SCALE,
    pitch_scale: float = DEFAULT_PITCH_SCALE,
    intonation_scale: float = DEFAULT_INTONATION_SCALE,
    volume_scale: float = DEFAULT_VOLUME_SCALE,
) -> dict[str, Any]:
    if not isinstance(audio_query, dict):
        raise TypeError("audio_query は dict 形式である必要があります。")

    updated = dict(audio_query)
    updated["speedScale"] = float(speed_scale)
    updated["pitchScale"] = float(pitch_scale)
    updated["intonationScale"] = float(intonation_scale)
    updated["volumeScale"] = float(volume_scale)
    return updated


def synthesize_wave(
    *,
    audio_query: dict[str, Any],
    speaker: int = DEFAULT_SPEAKER,
    base_url: str = DEFAULT_BASE_URL,
    timeout: tuple[int, int] = DEFAULT_TIMEOUT,
) -> bytes:
    response = _request(
        "POST",
        f"{_normalize_base_url(base_url)}/synthesis",
        params={"speaker": int(speaker)},
        headers={"Content-Type": "application/json"},
        json=audio_query,
        timeout=timeout,
    )

    content_type = response.headers.get("Content-Type", "")
    if "audio" not in content_type and not response.content.startswith(b"RIFF"):
        raise VoicevoxClientError(
            f"VOICEVOX /synthesis の応答が wav ではありません: Content-Type={content_type}"
        )
    return response.content


def merge_wav_bytes(wav_list: list[bytes]) -> bytes:
    valid_wavs = [wav_bytes for wav_bytes in wav_list if wav_bytes]
    if not valid_wavs:
        raise ValueError("結合対象の wav データがありません。")

    output_buffer = io.BytesIO()
    with wave.open(output_buffer, "wb") as output_wav:
        expected_format = None

        for index, wav_bytes in enumerate(valid_wavs, start=1):
            with wave.open(io.BytesIO(wav_bytes), "rb") as input_wav:
                current_format = (
                    input_wav.getnchannels(),
                    input_wav.getsampwidth(),
                    input_wav.getframerate(),
                    input_wav.getcomptype(),
                )

                if expected_format is None:
                    expected_format = current_format
                    output_wav.setnchannels(input_wav.getnchannels())
                    output_wav.setsampwidth(input_wav.getsampwidth())
                    output_wav.setframerate(input_wav.getframerate())
                    output_wav.setcomptype(input_wav.getcomptype(), input_wav.getcompname())
                elif current_format != expected_format:
                    raise VoicevoxClientError(
                        "wav のフォーマットが一致しないため結合できません: "
                        f"{expected_format} != {current_format} (chunk={index})"
                    )

                output_wav.writeframes(input_wav.readframes(input_wav.getnframes()))

    return output_buffer.getvalue()


def text_to_voicevox_wav(
    *,
    input_path: Path,
    output_path: Path,
    speaker: int = DEFAULT_SPEAKER,
    base_url: str = DEFAULT_BASE_URL,
    speed_scale: float = DEFAULT_SPEED_SCALE,
    pitch_scale: float = DEFAULT_PITCH_SCALE,
    intonation_scale: float = DEFAULT_INTONATION_SCALE,
    volume_scale: float = DEFAULT_VOLUME_SCALE,
    max_text_length: int = DEFAULT_MAX_TEXT_LENGTH,
    timeout: tuple[int, int] = DEFAULT_TIMEOUT,
) -> Path:
    source_text = _read_text(input_path)
    chunks = split_text_for_voicevox(source_text, max_length=max_text_length)
    if not chunks:
        raise ValueError(f"音声化できるテキストがありません: {input_path}")

    check_voicevox_running(base_url=base_url)

    wav_chunks: list[bytes] = []
    total = len(chunks)

    for index, chunk in enumerate(chunks, start=1):
        print(f"[VOICEVOX {index}/{total}] {len(chunk)} chars")
        query = create_audio_query(
            text=chunk,
            speaker=speaker,
            base_url=base_url,
            timeout=timeout,
        )
        query = apply_voice_settings(
            query,
            speed_scale=speed_scale,
            pitch_scale=pitch_scale,
            intonation_scale=intonation_scale,
            volume_scale=volume_scale,
        )
        wav_chunks.append(
            synthesize_wave(
                audio_query=query,
                speaker=speaker,
                base_url=base_url,
                timeout=timeout,
            )
        )

    merged_wav = merge_wav_bytes(wav_chunks)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(merged_wav)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="テキストファイルを VOICEVOX で wav に変換します。"
    )
    parser.add_argument("--input", required=True, help="入力テキストファイル")
    parser.add_argument("--output", required=True, help="出力 wav ファイル")
    parser.add_argument("--speaker", type=int, default=DEFAULT_SPEAKER, help="VOICEVOX の話者ID")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="VOICEVOX Engine のURL")
    parser.add_argument("--speed-scale", type=float, default=DEFAULT_SPEED_SCALE, help="話速")
    parser.add_argument("--pitch-scale", type=float, default=DEFAULT_PITCH_SCALE, help="音高")
    parser.add_argument("--intonation-scale", type=float, default=DEFAULT_INTONATION_SCALE, help="抑揚")
    parser.add_argument("--volume-scale", type=float, default=DEFAULT_VOLUME_SCALE, help="音量")
    parser.add_argument(
        "--max-text-length",
        type=int,
        default=DEFAULT_MAX_TEXT_LENGTH,
        help="1回の synthesis に渡す最大文字数",
    )
    args = parser.parse_args()

    output_path = text_to_voicevox_wav(
        input_path=Path(args.input),
        output_path=Path(args.output),
        speaker=args.speaker,
        base_url=args.base_url,
        speed_scale=args.speed_scale,
        pitch_scale=args.pitch_scale,
        intonation_scale=args.intonation_scale,
        volume_scale=args.volume_scale,
        max_text_length=args.max_text_length,
    )
    print(f"saved: {output_path}")


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_INTONATION_SCALE",
    "DEFAULT_MAX_TEXT_LENGTH",
    "DEFAULT_PITCH_SCALE",
    "DEFAULT_SPEAKER",
    "DEFAULT_SPEED_SCALE",
    "DEFAULT_TIMEOUT",
    "DEFAULT_VOLUME_SCALE",
    "VoicevoxClientError",
    "apply_voice_settings",
    "check_voicevox_running",
    "create_audio_query",
    "merge_wav_bytes",
    "split_text_for_voicevox",
    "synthesize_wave",
    "text_to_voicevox_wav",
]


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# STEP4 typed contract additions (TASK-VOICEVOX-001). Existing working
# implementation above is preserved and reused (check_voicevox_running,
# create_audio_query, apply_voice_settings, synthesize_wave,
# merge_wav_bytes, split_text_for_voicevox). VoicevoxHttpClient adapts that
# existing behavior to the common TTSClient contract in
# script/tts_clients/base.py.
# ---------------------------------------------------------------------------
from dataclasses import dataclass
from typing import Callable

from script.tts_clients.base import TTSClientError, TTSErrorCode
from script.tts_clients.models import SpeakerInfo

DEFAULT_CONNECTIVITY_TIMEOUT_SEC = 10


@dataclass(frozen=True)
class ConnectivityResult:
    """副作用のない疎通確認結果。"""

    available: bool
    detail: str = ""
    speaker_count: int | None = None


class VoicevoxHttpClient:
    """VOICEVOX Engine APIをTTS共通契約(TTSClient)へ適合させるHTTP client。"""

    engine_name = "voicevox"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        session_get: Callable[..., Any] | None = None,
        session_post: Callable[..., Any] | None = None,
        timeout: tuple[int, int] = DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = _normalize_base_url(base_url)
        self._get = session_get or requests.get
        self._post = session_post or requests.post
        self._timeout = timeout

    def check_connectivity(self) -> ConnectivityResult:
        """GET /speakersのHTTP・JSON schemaを確認する。副作用のない疎通確認結果を返す。"""
        try:
            response = self._get(f"{self._base_url}/speakers", timeout=DEFAULT_CONNECTIVITY_TIMEOUT_SEC)
        except requests.Timeout as exc:
            return ConnectivityResult(available=False, detail=f"timeout: {exc}")
        except requests.RequestException as exc:
            return ConnectivityResult(available=False, detail=str(exc))

        if response.status_code >= 400:
            return ConnectivityResult(available=False, detail=f"HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError as exc:
            return ConnectivityResult(available=False, detail=f"invalid JSON: {exc}")

        if not isinstance(data, list) or not data:
            return ConnectivityResult(available=False, detail="`/speakers` did not return a non-empty JSON array")

        for entry in data:
            if not isinstance(entry, dict) or "speaker_uuid" not in entry or "styles" not in entry:
                # 局所disable: 壊れたspeaker一覧を疎通失敗として扱い、例外にしない。
                return ConnectivityResult(available=False, detail="`/speakers` entry missing required identifiers")

        return ConnectivityResult(available=True, speaker_count=len(data))

    def list_speakers(self) -> list[SpeakerInfo]:
        """`/speakers`応答をUUID/表示名/style ID付きの共通SpeakerInfoへ変換する。"""
        try:
            response = self._get(f"{self._base_url}/speakers", timeout=self._timeout)
        except requests.Timeout as exc:
            raise TTSClientError(TTSErrorCode.TIMEOUT, engine_detail=str(exc)) from exc
        except requests.RequestException as exc:
            raise TTSClientError(TTSErrorCode.CONNECTION_ERROR, engine_detail=str(exc)) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise TTSClientError(TTSErrorCode.INVALID_AUDIO_RESPONSE, engine_detail=f"invalid JSON: {exc}") from exc

        if not isinstance(data, list):
            raise TTSClientError(TTSErrorCode.INVALID_AUDIO_RESPONSE, engine_detail="`/speakers` did not return a JSON array")

        speakers: list[SpeakerInfo] = []
        for entry in data:
            speaker_uuid = entry.get("speaker_uuid")
            speaker_name = entry.get("name", "")
            for style in entry.get("styles", []):
                style_id = style.get("id")
                if speaker_uuid is None or style_id is None:
                    continue
                style_name = style.get("name", "")
                speakers.append(
                    SpeakerInfo(
                        speaker_id=str(style_id),
                        display_name=f"{speaker_name} ({style_name})".strip(),
                        engine=self.engine_name,
                        style_ids=(str(style_id),),
                    )
                )
        return speakers

    def create_audio_query(self, *, text: str, speaker_id: int) -> dict[str, Any]:
        """短文からaudio_queryを取得する。空文字・非音声応答は共通errorへ変換する。"""
        if not text.strip():
            raise TTSClientError(TTSErrorCode.TEXT_EMPTY)

        try:
            response = self._post(
                f"{self._base_url}/audio_query",
                params={"text": text.strip(), "speaker": int(speaker_id)},
                timeout=self._timeout,
            )
        except requests.Timeout as exc:
            raise TTSClientError(TTSErrorCode.TIMEOUT, engine_detail=str(exc)) from exc
        except requests.RequestException as exc:
            raise TTSClientError(TTSErrorCode.QUERY_FAILED, engine_detail=str(exc)) from exc

        if response.status_code >= 400:
            if response.status_code == 404:
                raise TTSClientError(TTSErrorCode.SPEAKER_NOT_FOUND, engine_detail=f"speaker={speaker_id}")
            raise TTSClientError(TTSErrorCode.QUERY_FAILED, engine_detail=f"HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError as exc:
            raise TTSClientError(TTSErrorCode.QUERY_FAILED, engine_detail=f"invalid JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise TTSClientError(TTSErrorCode.QUERY_FAILED, engine_detail="`/audio_query` did not return an object")
        return data

    def synthesize_wave(self, *, audio_query: dict[str, Any], speaker_id: int) -> bytes:
        """audio_queryからWAVを合成する。非音声応答は成功扱いにしない。"""
        try:
            response = self._post(
                f"{self._base_url}/synthesis",
                params={"speaker": int(speaker_id)},
                headers={"Content-Type": "application/json"},
                json=audio_query,
                timeout=self._timeout,
            )
        except requests.Timeout as exc:
            raise TTSClientError(TTSErrorCode.TIMEOUT, engine_detail=str(exc)) from exc
        except requests.RequestException as exc:
            raise TTSClientError(TTSErrorCode.SYNTHESIS_FAILED, engine_detail=str(exc)) from exc

        if response.status_code >= 400:
            raise TTSClientError(TTSErrorCode.SYNTHESIS_FAILED, engine_detail=f"HTTP {response.status_code}")

        content_type = response.headers.get("Content-Type", "")
        if "audio" not in content_type and not response.content.startswith(b"RIFF"):
            raise TTSClientError(
                TTSErrorCode.INVALID_AUDIO_RESPONSE, engine_detail=f"Content-Type={content_type}"
            )
        return response.content

    def merge_waves(self, wav_chunks: list[bytes]) -> bytes:
        """part単位WAVを順序どおり結合する。形式不一致は共通errorへ変換する。"""
        try:
            return merge_wav_bytes(wav_chunks)
        except VoicevoxClientError as exc:
            raise TTSClientError(TTSErrorCode.AUDIO_FORMAT_MISMATCH, engine_detail=str(exc)) from exc
