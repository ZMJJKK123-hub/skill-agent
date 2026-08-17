# -*- coding: utf-8 -*-
"""Web search/fetch tool implementations (moved from core/tools.py)."""
import re

def run_web_fetch(url: str, max_chars: int = 100000) -> str:
    """抓取网页并尽量提取可读文本（去 script/style/HTML 标签），失败返回温和错误。"""
    try:
        import httpx
        r = httpx.get(url, timeout=20, follow_redirects=False)
        r.raise_for_status()
        text = r.text
        # 简单正文提取：去掉脚本/样式/标签，压缩空白
        text = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        truncated = len(text) > max_chars
        return text[:max_chars] + ("\n...(截断)" if truncated else "")
    except Exception as e:
        return f"Error: 抓取失败: {e}"


def run_web_search(query: str, max_results: int = 5) -> str:
    """联网搜索（DuckDuckGo HTML 端点，尽力而为，失败返回温和错误）。"""
    try:
        import httpx
        from html import unescape as _unescape
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
            results.append(f"- {_unescape(title).strip()}\n  {href}")
            if len(results) >= max_results:
                break
        return "\n".join(results) if results else "(无结果或解析失败)"
    except Exception as e:
        return f"Error: 搜索失败: {e}"

