"""LLM provider selection. The provider is configured (not hardcoded), so there
is no vendor lock-in. `mock` needs no API key and powers dev + tests; real
providers plug in here and read their key from settings.
"""

from __future__ import annotations

from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.mock import MockProvider
from app.core.config import get_settings

_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        settings = get_settings()
        name = settings.ai_provider.lower()
        if name == "mock":
            _provider = MockProvider(dim=settings.ai_embedding_dim)
        else:
            # Real providers (e.g. an OpenAI/Anthropic-compatible client) register
            # here, reading settings.ai_api_key. Until one is wired, fail loudly
            # rather than silently degrading.
            raise ValueError(
                f"AI provider '{name}' is not wired yet. Set AI_PROVIDER=mock for "
                "dev, or add the provider implementation in app/ai/providers/."
            )
    return _provider


__all__ = ["ChatMessage", "LLMProvider", "MockProvider", "get_provider"]
