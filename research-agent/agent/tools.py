"""
Tools: the agent's only way of touching the outside world.

Keeping these as plain functions (not framework-specific tool objects) means
you can unit test them in isolation and swap the search provider later
without touching the orchestration logic.
"""
import requests
from bs4 import BeautifulSoup

from config import TAVILY_API_KEY, MAX_SEARCH_RESULTS_PER_QUERY


def search_web(query: str) -> list[dict]:
    """Runs a web search via Tavily. Returns [{title, url, snippet}, ...].

    Swap this out for Bing/Serper/SearXNG etc. — the orchestrator only
    cares about the return shape, not the provider.
    """
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY not set — see .env.example")

    resp = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": MAX_SEARCH_RESULTS_PER_QUERY,
        },
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return [
        {"title": r.get("title", ""), "url": r["url"], "snippet": r.get("content", "")}
        for r in results
    ]


def fetch_and_extract(url: str, max_chars: int = 6000) -> str:
    """Fetches a page and strips it down to readable text.

    Deliberately simple (no JS rendering, no paywall handling) — this is a
    portfolio project, not a production scraper. Document that trade-off
    rather than hide it.
    """
    try:
        resp = requests.get(
            url, timeout=10, headers={"User-Agent": "research-agent/0.1"}
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        return f"[fetch failed: {e}]"

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:max_chars]
