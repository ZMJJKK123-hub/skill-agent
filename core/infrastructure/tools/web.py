# -*- coding: utf-8 -*-
"""Web search/fetch tool implementations (moved from core/tools.py)."""
import ipaddress
import re
import socket
from urllib.parse import urlparse


def _is_ssrf_blocked(url: str) -> bool:
    """Block requests to localhost/private/link-local/reserved IPs (simple SSRF guard)."""
    try:
        host = urlparse(url).hostname
    except Exception:
        return True
    if not host:
        return True
    host = host.rstrip(".").lower()
    if host == "localhost":
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return True
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return True
    return False


def run_web_fetch(url: str, max_chars: int = 100000) -> str:
    """抓取网页并尽量提取可读文本（去 script/style/HTML 标签），失败返回温和错误。"""
    try:
        if _is_ssrf_blocked(url):
            return "Error: URL 被 SSRF 防护拦截（不允许访问内网/私网地址）"
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