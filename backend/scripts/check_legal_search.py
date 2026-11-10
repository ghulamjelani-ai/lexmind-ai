"""Verify legal web search over official Pakistani sources (reads your .env).

    uv run python -m scripts.check_legal_search
"""

from __future__ import annotations

from app.core.config import get_settings
from app.integrations.legal_search import official_domains, search_official


def main() -> None:
    s = get_settings()
    print(f"legal_search_provider = {s.legal_search_provider}")
    print(f"official domains      = {official_domains()}")
    print("-" * 40)
    query = "Pakistan Penal Code section 302 punishment for murder"
    results = search_official(query, max_results=3)
    print(f"{len(results)} official-source result(s):")
    for r in results:
        print(f"  - [{r.domain}] {r.url}")
        print(f"      {r.content[:120]}...")
    if not results:
        print("No results — set LEGAL_SEARCH_PROVIDER=tavily and TAVILY_API_KEY, or the "
              "official sites may be thinly indexed for this query.")


if __name__ == "__main__":
    main()
