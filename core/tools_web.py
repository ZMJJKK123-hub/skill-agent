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
