# -*- coding: utf-8 -*-
"""消息规范化：多模态内容转纯文本、文件下载、MOD 需求识别（由 main.py 迁出）。"""
import re
import uuid
from pathlib import Path


def safe_input_name(filename: str, fallback_ext: str = "") -> str:
    name = Path(filename or "").name.strip()
    if not name:
        name = f"file_{uuid.uuid4().hex[:8]}{fallback_ext}"
    return name


def download_remote_file(url: str, filename: str, inputs_dir: Path) -> tuple[str, bool]:
    """下载清小搭 OSS 上的文件/图片 URL 到工作区 inputs/，返回 (相对路径, 是否成功)。"""
    try:
        from core.infrastructure.tools.web import _is_ssrf_blocked
        if _is_ssrf_blocked(url):
            return "下载被 SSRF 防护拦截（不允许访问内网/私网地址）", False
        inputs_dir.mkdir(parents=True, exist_ok=True)
        import httpx
        r = httpx.get(url, timeout=60, follow_redirects=False)
        r.raise_for_status()
        safe_name = safe_input_name(filename)
        target = inputs_dir / safe_name
        counter = 1
        while target.exists():
            target = inputs_dir / f"{Path(safe_name).stem}_{counter}{Path(safe_name).suffix}"
            counter += 1
        target.write_bytes(r.content)
        return f"inputs/{target.name}", True
    except Exception as e:
        return f"下载失败: {e}", False


def content_to_text(content, inputs_dir: Path) -> str:
    """content 可能是 str，也可能是多模态数组；文本原样，文件/图片下载后给路径。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if not isinstance(item, dict):
                parts.append(str(item))
                continue
            t = item.get("type", "")
            if t == "text":
                parts.append(str(item.get("text", "")))
            elif t == "image_url":
                url = ((item.get("image_url") or {}).get("url") or "")
                if url:
                    raw_name = Path(url.split("?")[0]).name or "image.png"
                    rel, ok = download_remote_file(url, raw_name, inputs_dir)
                    parts.append(f"[图片已保存: {rel}]" if ok else f"[图片输入{rel}]")
                else:
                    parts.append("[图片输入]")
            elif t == "input_audio":
                parts.append("[音频输入暂不支持]")
            elif t == "file":
                file_obj = item.get("file") or {}
                url = file_obj.get("url") or ""
                filename = file_obj.get("filename") or ""
                if url:
                    rel, ok = download_remote_file(url, filename, inputs_dir)
                    parts.append(f"[文件已保存: {rel}]" if ok else f"[文件输入{rel}]")
                elif file_obj.get("file_id"):
                    parts.append("[文件输入(file_id)暂不支持]")
                else:
                    parts.append(f"[文件输入:{filename}]" if filename else "[文件输入]")
        return "\n".join(p for p in parts if p)
    return str(content)


def normalize_messages(messages: list | None, session_id: str = "") -> list[dict]:
    """过滤掉 tool 消息/多模态数组，保留纯文本 system/user/assistant 序列。"""
    if not isinstance(messages, list):
        return []

    # 延迟导入：personas 反向依赖本模块的 last_user_content（避免环）
    from personas import PERSONA_PROMPTS, resolve_persona_key
    from daemon_api import session_workdir

    inputs_dir = session_workdir(session_id) / "inputs"
    out: list[dict] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = m.get("role", "")
        if role not in ("system", "user", "assistant"):
            continue
        content = content_to_text(m.get("content", ""), inputs_dir)
        out.append({"role": role, "content": content})

    if not out:
        out = [{"role": "user", "content": "你好"}]

    persona_key = resolve_persona_key(session_id, session_workdir)
    if persona_key in PERSONA_PROMPTS:
        instruction = f"[人格设定] {PERSONA_PROMPTS[persona_key]} 请始终以这个人格回应。"
        if not any(isinstance(m, dict) and "[人格设定]" in str(m.get("content", "")) for m in out):
            out.insert(0, {"role": "user", "content": instruction})
    return out


def is_mod_request(messages: list) -> bool:
    """判断用户这次是否涉及 MOD 制作/修改需求。"""
    for m in messages:
        if not isinstance(m, dict):
            continue
        if m.get("role") not in ("user", "system"):
            continue
        content = m.get("content", "")
        if not isinstance(content, str):
            continue
        low = content.lower()
        if re.search(r"(?i)(/mod|(?<![a-z])mod(?![a-z])|模组|mod制作|我的世界.*(?:mod|模组)|forge)", low):
            return True
    return False


def last_user_content(messages) -> str:
    """返回消息列表里最新一条用户消息内容；没有则返回空字符串。"""
    if not isinstance(messages, list):
        return ""
    for m in reversed(messages):
        if isinstance(m, dict) and m.get("role") == "user":
            content = m.get("content", "")
            if isinstance(content, str):
                return content.strip()
    return ""
