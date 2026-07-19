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
# STEP4 typed contract additions. Existing working implementation above is
# preserved. New public APIs remain intentionally unimplemented.
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

STEP4_PUBLIC_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    ('TASK-VOICEVOX-001', 'VoicevoxHttpClient.check_connectivity() -> ConnectivityResult', 'GET /speakersのHTTP・JSON schemaを確認する。'),
    ('TASK-VOICEVOX-001', 'list_speakers() -> list[SpeakerInfo]', 'UUID、表示名、style IDを動的取得する。'),
    ('TASK-VOICEVOX-001', 'create_audio_query()/synthesize_wave()', '短文queryとWAV合成を行い非音声応答を拒否する。'),
)
STEP4_TEST_CASES: tuple[dict[str, str], ...] = (
    {'id': 'TC-VOICEVOX-001-01', 'priority': 'P0', 'layer': 'integration_mock', 'title': 'speaker変換', 'given': 'mock /speakers response', 'when': 'list_speakers', 'then': 'UUID/name/style IDを保持し表示名分岐しない', 'test_file': '`tests/test_voicevox_client.py`'},
    {'id': 'TC-VOICEVOX-001-02', 'priority': 'P0', 'layer': 'integration_mock', 'title': '合成mock', 'given': 'mock query/synthesis', 'when': 'adapter synthesize', 'then': 'parameter mappingとRIFF validationを行う', 'test_file': '`tests/test_voicevox_adapter.py`'},
    {'id': 'TC-VOICEVOX-001-03', 'priority': 'P0', 'layer': 'unit', 'title': 'format不一致', 'given': '異なるsample rateの2WAV', 'when': 'merge', 'then': 'audio_format_mismatch', 'test_file': '`tests/test_voicevox_client.py`'},
    {'id': 'TC-VOICEVOX-001-04', 'priority': 'P1', 'layer': 'unit', 'title': '/speakers health/list', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`VoicevoxHttpClient.check_connectivity() -> ConnectivityResult`を通じて「/speakers health/list」を実行する', 'then': '表示名へ依存せずengineの識別子から解決し、不在時はspeaker_not_foundまたは局所disableになる。', 'test_file': '`tests/test_voicevox_adapter.py`'},
    {'id': 'TC-VOICEVOX-001-05', 'priority': 'P1', 'layer': 'unit', 'title': '/audio_query', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`VoicevoxHttpClient.check_connectivity() -> ConnectivityResult`を通じて「/audio_query」を実行する', 'then': '有効なmedia header・形式・順序を確認し、破損または形式不一致を成功扱いにしない。', 'test_file': '`tests/test_voicevox_client.py`'},
    {'id': 'TC-VOICEVOX-001-06', 'priority': 'P1', 'layer': 'unit', 'title': '/synthesis', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`VoicevoxHttpClient.check_connectivity() -> ConnectivityResult`を通じて「/synthesis」を実行する', 'then': '「/synthesis」の承認済み仕様を満たし、戻り値・永続化・eventが再実行可能かつ決定的である。', 'test_file': '`tests/test_voicevox_adapter.py`'},
    {'id': 'TC-VOICEVOX-001-07', 'priority': 'P1', 'layer': 'unit', 'title': 'timeout/error変換', 'given': '承認済み仕様に適合する最小入力と、必要な依存をmockした状態', 'when': '`VoicevoxHttpClient.check_connectivity() -> ConnectivityResult`を通じて「timeout/error変換」を実行する', 'then': 'timeoutを安定した共通errorへ変換し、半端な最終ファイルや成功状態を残さない。', 'test_file': '`tests/test_voicevox_client.py`'},
    {'id': 'TC-VOICEVOX-001-08', 'priority': 'P0', 'layer': 'unit', 'title': '必須入力欠落', 'given': '主ID、必須path、必須設定のいずれかが欠落した入力', 'when': '`VoicevoxHttpClient.check_connectivity() -> ConnectivityResult`を実行する', 'then': '副作用を開始する前に安定したvalidation errorを返し、既存ファイル・DB・成果物を変更しない。', 'test_file': '`tests/test_voicevox_adapter.py`'},
    {'id': 'TC-VOICEVOX-001-09', 'priority': 'P1', 'layer': 'unit', 'title': '再実行時の決定性', 'given': '同じ入力、同じ設定、同じ依存応答', 'when': '`VoicevoxHttpClient.check_connectivity() -> ConnectivityResult`を2回実行する', 'then': '仕様上追記が必要なversion以外は同じ論理結果を返し、重複外部呼出し・重複正式成果物を発生させない。', 'test_file': '`tests/test_voicevox_client.py`'},
    {'id': 'TC-VOICEVOX-001-10', 'priority': 'P0', 'layer': 'unit', 'title': '入力・既存成果物の不変性', 'given': 'hash取得済みの入力と既存正常成果物', 'when': '正常処理または意図的な失敗を発生させる', 'then': '入力と既存正常成果物のbyte/hashが変化せず、派生物・一時物・新versionだけが変更対象になる。', 'test_file': '`tests/test_voicevox_adapter.py`'},
    {'id': 'TC-VOICEVOX-001-11', 'priority': 'P0', 'layer': 'integration_smoke', 'title': 'VOICEVOX Engine APIの疎通確認', 'given': '実接続テストが明示的に有効化され、必要な設定が存在する', 'when': '`GET /speakers`を1回実行し、HTTP成功、1件以上のspeaker、UUID・style IDを含むJSON配列を確認する。', 'then': 'ConnectivityResultを返す。失敗時は原因を秘密値なしで報告し、実機能テストを開始しない。', 'test_file': '`tests/test_voicevox_client.py`'},
    {'id': 'TC-VOICEVOX-001-12', 'priority': 'P1', 'layer': 'integration_live', 'title': 'VOICEVOX Engine APIの実機能テスト', 'given': '`voicevox_connectivity_gate`が成功済み', 'when': '疎通成功後、短い固定文で`/audio_query`→`/synthesis`を1回実行し、RIFF/WAVEとして読める音声を確認する。', 'then': '最小の実機能結果を検証する。疎通fixtureなしでこのテストを単独実行できない。', 'test_file': '`tests/test_voicevox_adapter.py`'},
)

def _step4_unimplemented(symbol: str) -> None:
    raise NotImplementedError(f"STEP4 source scaffold is not implemented: {symbol} (script/tts_clients/voicevox/client.py)")

class ConnectivityResult:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class SpeakerInfo:
    """Typed data placeholder; fields are finalized during task implementation."""
    def __init__(self, **data: Any) -> None:
        self.data = dict(data)
    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

class VoicevoxHttpClient:
    """Public service/adapter scaffold fixed by STEP2."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
    def check_connectivity(self) -> ConnectivityResult:
        """GET /speakersのHTTP・JSON schemaを確認する。

        Public contract: ``VoicevoxHttpClient.check_connectivity() -> ConnectivityResult``.
        """
        _step4_unimplemented('VoicevoxHttpClient.check_connectivity')

def list_speakers() -> list[SpeakerInfo]:
    """UUID、表示名、style IDを動的取得する。

    Public contract: ``list_speakers() -> list[SpeakerInfo]``.
    """
    _step4_unimplemented('list_speakers')
