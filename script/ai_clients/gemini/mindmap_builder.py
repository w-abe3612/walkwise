from __future__ import annotations
from dataclasses import dataclass

DEFAULT_FALLBACK_INPUT_FILENAME = "input.txt"
DEFAULT_INPUT_FILENAME = "input.txt"
DEFAULT_OUTPUT_FILENAME = "output.txt"

@dataclass(frozen=True)
class Section:
    title: str = ""
    content: str = ""

def build_final_mindmap(*args, **kwargs):
    raise NotImplementedError("Legacy Gemini compatibility scaffold is not implemented.")
def load_sections(*args, **kwargs):
    raise NotImplementedError("Legacy Gemini compatibility scaffold is not implemented.")
def process_section(*args, **kwargs):
    raise NotImplementedError("Legacy Gemini compatibility scaffold is not implemented.")
