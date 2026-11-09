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
        elif name == "openai":
            from app.ai.providers.openai_provider import OpenAIProvider

            _provider = OpenAIProvider()
        else:
            raise ValueError(
                f"Unknown AI_PROVIDER '{name}'. Use 'mock' or 'openai' "
                "(or add a provider in app/ai/providers/)."
            )
    return _provider


__all__ = ["ChatMessage", "LLMProvider", "MockProvider", "get_provider"]
