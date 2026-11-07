"""Provider-agnostic LLM interface. Concrete providers implement these two
methods; everything above (gateway, RAG, chatbot) depends only on this.
"""

from __future__ import annotations

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

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return an embedding vector per input text."""
        ...
