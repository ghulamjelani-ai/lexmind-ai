"""Verify the configured AI providers work with your keys.

Reads settings from backend/.env. Run after setting your keys there:

    uv run python -m scripts.check_ai

- Embeddings: generates a vector for a sample sentence and prints its dimension.
- Chat (only if AI_PROVIDER=openai): sends one short message and prints the reply.
"""

from __future__ import annotations

from app.ai import embeddings
from app.ai.providers import get_provider
from app.ai.providers.base import ChatMessage
from app.core.config import get_settings


def main() -> None:
    s = get_settings()
    print(f"embedding_provider = {s.embedding_provider} (model {s.voyage_model})")
    print(f"ai_provider        = {s.ai_provider} (model {s.openai_model})")
    print(f"ai_embedding_dim   = {s.ai_embedding_dim}")
    print("-" * 40)

    vec = embeddings.embed(["A sample legal sentence about bail under section 497."])[0]
    print(f"embedding OK — dimension {len(vec)}, first values {vec[:4]}")
    if len(vec) != s.ai_embedding_dim:
        print(
            f"  WARNING: dim {len(vec)} != ai_embedding_dim {s.ai_embedding_dim}. "
            "Set AI_EMBEDDING_DIM to match and re-run the resize migration."
        )

    if s.ai_provider == "openai":
        reply = get_provider().chat(
            [
                ChatMessage("system", "You are a terse assistant."),
                ChatMessage("user", "Reply with exactly: pong"),
            ]
        )
        print(f"chat OK — reply: {reply!r}")
    else:
        print("chat: AI_PROVIDER is not 'openai' — skipping chat check.")


if __name__ == "__main__":
    main()
