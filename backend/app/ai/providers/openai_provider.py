"""OpenAI (ChatGPT) chat provider.

Reads OPENAI_API_KEY from settings (never hardcoded). Used for the chatbot's
replies; embeddings go through app.ai.embeddings (Voyage), not here.
"""

from __future__ import annotations

from app.ai.providers.base import ChatMessage
from app.core.config import get_settings


class OpenAIProvider:
    name = "openai"

    def __init__(self) -> None:
        from openai import OpenAI

        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        kwargs: dict = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url
        self._client = OpenAI(**kwargs)
        self._model = settings.openai_model

    def chat(self, messages: list[ChatMessage]) -> str:
        # Temperature is omitted: current reasoning models (GPT-6 family) reject a
        # non-default temperature. Depth is controlled by the model's reasoning
        # effort setting instead.
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return resp.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        raise NotImplementedError("OpenAIProvider is chat-only; use app.ai.embeddings")
