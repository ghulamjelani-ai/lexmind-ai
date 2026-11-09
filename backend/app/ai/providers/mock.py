"""Deterministic mock provider — no network, no API key.

Chat: echoes a grounded-looking answer that cites the context it was given, so
the full pipeline (auth, retrieval, sandboxing, citations) is exercised end to
end in dev and tests. Embeddings: a stable hash-based bag-of-words vector, so
semantically similar text lands near each other for retrieval tests.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Iterator

from app.ai.providers.base import ChatMessage


class MockProvider:
    name = "mock"

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def chat(self, messages: list[ChatMessage]) -> str:
        user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        # Detect actual grounding blocks (the sandbox fence), not the word
        # "CONTEXT" in the system instruction.
        has_context = any("BEGIN CONTEXT" in m.content for m in messages if m.role == "system")
        grounding = (
            "Based on the provided case documents, "
            if has_context
            else "No case context was provided, so this is a general note. "
        )
        return (
            f"{grounding}[mock response] You asked: "
            f"{user.strip()[:200]}. A qualified lawyer must verify any legal "
            "conclusion against the cited sources."
        )

    def stream_chat(self, messages: list[ChatMessage]) -> Iterator[str]:
        for word in self.chat(messages).split(" "):
            yield word + " "

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in re.findall(r"\w+", text.lower()):
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
