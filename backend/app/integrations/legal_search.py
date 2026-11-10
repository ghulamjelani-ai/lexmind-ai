"""Web search over OFFICIAL Pakistani legal sources only.

Queries a search index (Tavily) restricted to the official-source domains — this
is ToS-clean (we query a search index, not the government sites directly) and
avoids scraping. When no provider is configured it returns no results, and the
research agent falls back to manual-link + pending (never fabricates).
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from app.core.config import get_settings
from app.core.legal_sources import OFFICIAL_SOURCES

TAVILY_URL = "https://api.tavily.com/search"


def official_domains() -> list[str]:
    domains = []
    for s in OFFICIAL_SOURCES:
        host = urlparse(s.url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        if host:
            domains.append(host)
    return sorted(set(domains))


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    domain: str


def search_official(query: str, *, max_results: int = 5) -> list[SearchResult]:
    settings = get_settings()
    provider = settings.legal_search_provider.lower()
    if provider == "tavily":
        return _tavily(query, max_results, settings)
    return []  # "none" or unknown — no automated search available


def _tavily(query: str, max_results: int, settings) -> list[SearchResult]:
    import time

    import httpx

    if not settings.tavily_api_key:
        return []
    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "max_results": max_results,
        "include_domains": official_domains(),
        "search_depth": "advanced",
        "include_raw_content": False,
    }
    for attempt in range(4):
        resp = httpx.post(TAVILY_URL, json=payload, timeout=30.0)
        if resp.status_code == 429:
            time.sleep(min(float(resp.headers.get("retry-after", 2**attempt)), 20.0))
            continue
        resp.raise_for_status()
        out: list[SearchResult] = []
        for r in resp.json().get("results", []):
            url = r.get("url", "")
            out.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=url,
                    content=r.get("content", ""),
                    domain=urlparse(url).netloc.lower(),
                )
            )
        return out
    return []
