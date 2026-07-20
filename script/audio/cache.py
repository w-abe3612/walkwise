"""script/audio/cache.py — 公開契約: AudioCache.key/get/put.

Contract: docs/test-cases/TASK-AUDIO-001-preview-and-segment-tts-cache.md
Spec: docs/specifications/02-process-input-output.md(14節: 再利用と部分再生成)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from script.core.errors import AppError, ErrorCode


@dataclass(frozen=True)
class AudioCacheKey:
    """text/tts_text/voice profile/engine versionから決定的に導出するcache識別子。"""

    value: str


@dataclass(frozen=True)
class CachedAudio:
    """AudioCacheが保持する1件の合成済み音声metadata。"""

    key: AudioCacheKey
    output_path: str
    duration_seconds: float
    sample_rate_hz: int
    channels: int


class AudioCache:
    """text/tts_text/voice profile/engine versionでcacheを識別し、再合成を回避する。"""

    def __init__(self) -> None:
        self._store: dict[str, CachedAudio] = {}

    def key(
        self,
        *,
        text: str,
        tts_text: str | None,
        voice_profile_id: str,
        voice_content_hash: str,
        engine_version: str | None = None,
    ) -> AudioCacheKey:
        """text/tts_text/voice profile(revision込み)/engine versionからcache keyを決定的に計算する。"""
        if not text:
            raise AppError(ErrorCode.VALIDATION_ERROR, "text is required")
        if not voice_profile_id:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_profile_id is required")
        if not voice_content_hash:
            raise AppError(ErrorCode.VALIDATION_ERROR, "voice_content_hash is required")

        payload = "|".join([text, tts_text or "", voice_profile_id, voice_content_hash, engine_version or ""])
        return AudioCacheKey(value=hashlib.sha256(payload.encode("utf-8")).hexdigest())

    def get(self, key: AudioCacheKey) -> CachedAudio | None:
        """既存cacheがあれば返し、なければNoneを返す(副作用なし)。"""
        if key is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "key is required")
        return self._store.get(key.value)

    def put(self, key: AudioCacheKey, audio: CachedAudio) -> None:
        """cacheへ登録する。既存正常成果物のkeyが変わらない限り上書きは同一内容のみ。"""
        if key is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "key is required")
        if audio is None:
            raise AppError(ErrorCode.VALIDATION_ERROR, "audio is required")
        self._store[key.value] = audio
