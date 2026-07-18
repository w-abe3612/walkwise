from __future__ import annotations

from pathlib import Path


class CoeiroinkNotImplementedError(NotImplementedError):
    """COEIROINK client is reserved for future implementation."""


def synthesize_text_to_wav(*, input_path: Path, output_path: Path, **kwargs) -> None:
    raise CoeiroinkNotImplementedError(
        "COEIROINK クライアントは未実装です。"
        " script/tts_clients/coeiroink/client.py に API 呼び出しを追加してください。"
    )
