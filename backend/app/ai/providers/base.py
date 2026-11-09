"""Provider-agnostic LLM interface. Concrete providers implement these two
methods; everything above (gateway, RAG, chatbot) depends only on this.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMProvider(Protocol):
    name: str

    def chat(self, messages: list[ChatMessage]) -> str:
        """Return the assistant's reply for a conversation."""
        ...

    def stream_chat(self, messages: list[ChatMessage]) -> Iterator[str]:
        """Yield the assistant's reply as text deltas."""
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return an embedding vector per input text."""
        ...
