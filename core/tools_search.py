# -*- coding: utf-8 -*-
"""Web search implementations: Tavily (optional) + DuckDuckGo fallback + MC/Forge docs search."""
import os
import re
from html import unescape

MC_DOC_DOMAINS = [
    "minecraft.wiki",
    "docs.minecraftforge.net",
    "minecraftforge.net",
    "github.com/MinecraftForge",
    "maven.minecraftforge.net",
    "neoforged.net",
]


def _tavily_key() -> str:
    return (os.environ.get("DSH_TAVILY_API_KEY") or os.environ.get("DSH_SEARCH_API_KEY") or "").strip()


def _tavily_search(query: str, max_results: int = 5, include_domains=None) -> str | None:
    """Use Tavily search API. Returns formatted text or None if unavailable/failed."""
    key = _tavily_key()
    if not key:
        return None
    import httpx

    payload = {
        "api_key": key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }
    if include_domains:
        payload["include_domains"] = include_domains
    try:
        r = httpx.post("https://api.tavily.com/search", json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in (data.get("results") or [])[:max_results]:
            title = (item.get("title") or "").strip()
            url = (item.get("url") or "").strip()
            content = (item.get("content") or "").strip()[:500]
            results.append(f"- {title}\n  {url}\n  {content}")
        return "\n".join(results) if results else None
    except Exception:
        return None


def _ddg_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo HTML fallback (best-effort)."""
    import httpx

    try:
        r = httpx.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            timeout=20,
            follow_redirects=False,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        r.raise_for_status()
        results = []
        for m in re.finditer(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text
        ):
            href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
            results.append(f"- {unescape(title).strip()}\n  {href}")
            if len(results) >= max_results:
                break
        return "\n".join(results) if results else "(无结果或解析失败)"
    except Exception as e:
        return f"Error: 搜索失败: {e}"


def run_web_search(query: str, max_results: int = 5) -> str:
    """Web search: Tavily if configured, otherwise DuckDuckGo fallback."""
    tavily = _tavily_search(query, max_results)
    if tavily:
        return tavily
    return _ddg_search(query, max_results)


def run_search_minecraft_docs(query: str, max_results: int = 5) -> str:
    """Search Minecraft/Forge-specific documentation sites first."""
    tavily = _tavily_search(query, max_results, include_domains=MC_DOC_DOMAINS)
    if tavily:
        return tavily
    # DuckDuckGo fallback with site filters
    site_q = " OR ".join(f"site:{d}" for d in MC_DOC_DOMAINS)
    return _ddg_search(f"({query}) ({site_q})", max_results)
