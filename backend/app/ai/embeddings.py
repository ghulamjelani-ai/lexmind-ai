"""Embedding generation, provider-independent of the chat model.

"mock" (deterministic, no key) for dev/tests; "voyage" calls Voyage AI's
voyage-law-2 (legal-domain embeddings). The chat model and the embedding model
are chosen separately in settings.
"""

from __future__ import annotations

from app.ai.providers.mock import MockProvider
from app.core.config import get_settings

VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"


def embed(texts: list[str], *, input_type: str | None = None) -> list[list[float]]:
    """Return one embedding vector per input text.

    input_type is "document" when indexing and "query" when searching; Voyage
    uses it to improve retrieval, the mock ignores it.
    """
    settings = get_settings()
    if settings.embedding_provider == "voyage":
        return _voyage_embed(texts, input_type)
    return MockProvider(dim=settings.ai_embedding_dim).embed(texts)


def _voyage_embed(texts: list[str], input_type: str | None) -> list[list[float]]:
    import time

    import httpx

    settings = get_settings()
    if not settings.voyage_api_key:
        raise ValueError("VOYAGE_API_KEY is not set")
    payload: dict = {"input": texts, "model": settings.voyage_model}
    if input_type:
        payload["input_type"] = input_type
    headers = {"Authorization": f"Bearer {settings.voyage_api_key}"}

    last: httpx.Response | None = None
    for attempt in range(5):
        resp = httpx.post(VOYAGE_URL, headers=headers, json=payload, timeout=30.0)
        if resp.status_code == 429:
            # Rate limited — honor Retry-After, else exponential backoff.
            wait = float(resp.headers.get("retry-after", 2**attempt))
            time.sleep(min(wait, 30.0))
            last = resp
            continue
        resp.raise_for_status()
        rows = sorted(resp.json()["data"], key=lambda d: d["index"])
        return [row["embedding"] for row in rows]

    # Exhausted retries on 429.
    if last is not None:
        last.raise_for_status()
    raise RuntimeError("Voyage embeddings failed after retries")
