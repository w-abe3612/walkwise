"""script/ai_clients/gemini — 公開契約: GeminiClient(client.py経由).

TASK-REVIEW-001 2.7節: `merged_text_fixer.py`(`fix_text_file_with_gemini`)と
`mindmap_builder.py`(`build_final_mindmap`/`load_sections`/`process_section`/`Section`)は、
いずれも全body`NotImplementedError`のlegacy互換scaffoldで、どのtask・test・
pipelineからも参照されていなかった(docs/notes/progress.mdで既に「未使用」と
確認済み)。実装を推測で追加する根拠(仕様・test caseのいずれも存在しない)がないため、
このscaffold自体を削除し、正式にdeprecateした。将来これらの機能が必要になった場合は、
`GeminiClient`(client.py)の契約へ新規taskとして追加すること。
"""

from .client import (
    DEFAULT_API_KEY,
    DEFAULT_API_VERSION,
    DEFAULT_MAX_CHARS_PER_CHUNK,
    DEFAULT_MODEL,
    DEFAULT_REQUEST_TIMEOUT_SEC,
    DEFAULT_TEMPERATURE,
    ENV_PATH,
    PROMPTS_DIR,
    call_gemini,
    load_env_file,
    load_prompt,
    render_prompt,
    split_text_into_chunks,
)

__all__ = [
    "DEFAULT_API_KEY",
    "DEFAULT_API_VERSION",
    "DEFAULT_MAX_CHARS_PER_CHUNK",
    "DEFAULT_MODEL",
    "DEFAULT_REQUEST_TIMEOUT_SEC",
    "DEFAULT_TEMPERATURE",
    "ENV_PATH",
    "PROMPTS_DIR",
    "call_gemini",
    "load_env_file",
    "load_prompt",
    "render_prompt",
    "split_text_into_chunks",
]
